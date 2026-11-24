from __future__ import annotations
import argparse, json, logging, os, signal, sys, threading, time
from dataclasses import dataclass
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.parametrizations import spectral_norm
import pennylane as qml

DTYPE = torch.float32
N_FOCUS = 8


# ---------------------------------------------------------------------------
class SwiGLU(nn.Module):
    def __init__(self, i, o):
        super().__init__()
        # Spectral norm strictly bounds the Lipschitz constant to prevent noise amplification
        self.w1 = spectral_norm(nn.Linear(i, o))
        self.w2 = spectral_norm(nn.Linear(i, o))

    def forward(self, x):
        return F.silu(self.w1(x)) * self.w2(x)


class QuantumEngine(nn.Module):
    def __init__(self, n_qubits, n_layers):
        super().__init__()
        self.n_qubits, self.n_layers = n_qubits, n_layers

        # Fast C++ Lightning backend if installed, else default qubit
        self.device_name = "default.qubit"
        self.diff_method = "backprop"
        try:
            self.dev = qml.device("lightning.qubit", wires=n_qubits)
            self.device_name, self.diff_method = "lightning.qubit", "adjoint"
        except Exception:
            self.dev = qml.device("default.qubit", wires=n_qubits)

        @qml.qnode(self.dev, interface="torch", diff_method=self.diff_method)
        def circuit(inputs, weights):
            iy = inputs[:, :n_qubits]
            iz = inputs[:, n_qubits:]
            for i in range(n_layers):
                qml.AngleEmbedding(iy, wires=range(n_qubits), rotation="Y")
                qml.AngleEmbedding(iz, wires=range(n_qubits), rotation="Z")
                qml.StronglyEntanglingLayers(weights[:, i], wires=range(n_qubits))
            return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]

        self.circuit = circuit
        logging.info("QuantumEngine: backend=%s diff=%s", self.device_name, self.diff_method)

    def forward(self, x, w):
        return torch.stack(self.circuit(x.to(DTYPE), w.to(DTYPE)), dim=-1)


class QWeightGen(nn.Module):
    def __init__(self, latent, n_layers, n_qubits):
        super().__init__()
        self.n_layers, self.n_qubits = n_layers, n_qubits
        t = n_layers * n_qubits * 3
        self.net = nn.Sequential(SwiGLU(latent, 256), nn.LayerNorm(256),
                                 SwiGLU(256, t), nn.LayerNorm(t))

    def forward(self, z):
        return (torch.tanh(self.net(z)) * torch.pi).view(-1, self.n_layers, self.n_qubits, 3)


class HealingSanitizer(nn.Module):
    """
    Robust MAD-based sanitizer with two phases:
      - Warmup: fast EMA (m=0.1) of batch medians/MADs.
      - Steady state: slow EMA (m=0.01), so the tracker stays robust to
        gradual drift while still resisting up to ~50% contamination.
    Outliers are suppressed smoothly via exponential decay past z_cut.
    """
    def __init__(self, input_dim, z_cut=3.0, warmup_steps=50):
        super().__init__()
        self.z_cut = z_cut
        self.register_buffer("running_median", torch.zeros(input_dim))
        self.register_buffer("running_mad", torch.ones(input_dim))
        self.register_buffer("steps_seen", torch.tensor(0, dtype=torch.long))
        self.warmup_steps = warmup_steps  # plain int: no GPU sync

    def _update_stats(self, x):
        flat = x.detach().reshape(-1, x.shape[-1])
        batch_median = flat.median(dim=0).values
        batch_mad = (flat - batch_median).abs().median(dim=0).values.clamp_min(1e-6)

        self.steps_seen += 1
        m = 0.10 if int(self.steps_seen.item()) <= self.warmup_steps else 0.01
        self.running_median.mul_(1 - m).add_(batch_median, alpha=m)
        self.running_mad.mul_(1 - m).add_(batch_mad, alpha=m)

    def forward(self, x):
        if self.training and int(self.steps_seen.item()) < 5:
            # First handful of batches: pass-through, stats are meaningless.
            return x, 0.0

        if self.training:
            self._update_stats(x)

        med = self.running_median.view(1, 1, -1)
        diff = x - med
        # 1.4826 rescales MAD to an approximate standard deviation
        z = diff.abs() / (self.running_mad * 1.4826 + 1e-6).view(1, 1, -1)
        mask = (z > self.z_cut)
        # Smooth exponential suppression only beyond z_cut
        suppression = torch.exp(-0.5 * (z - self.z_cut).clamp(min=0.0))
        healed = med + diff * suppression
        return healed, mask.float().mean().item()


class HybridCore(nn.Module):
    def __init__(self, input_dim=16, hidden=96, n_qubits=8, n_layers=6,
                 n_classes=4, dropout=0.15):
        super().__init__()
        self.encoder = nn.Sequential(
            SwiGLU(input_dim, hidden), nn.LayerNorm(hidden), nn.Dropout(dropout),
            SwiGLU(hidden, hidden), nn.LayerNorm(hidden))
        self.to_quantum = nn.Sequential(nn.Linear(hidden, n_qubits * 2),
                                        nn.LayerNorm(n_qubits * 2))
        self.q_engine = QuantumEngine(n_qubits, n_layers)
        self.q_weight_gen = QWeightGen(hidden, n_layers, n_qubits)
        self.q_proj = nn.Sequential(nn.Linear(n_qubits, hidden), nn.SiLU(),
                                    nn.Linear(hidden, hidden), nn.LayerNorm(hidden))
        self.fusion_gate = nn.Sequential(nn.Linear(hidden * 2, hidden), nn.Sigmoid())
        self.head = nn.Sequential(SwiGLU(hidden, hidden), nn.LayerNorm(hidden),
                                  nn.Dropout(dropout), nn.Linear(hidden, n_classes))

    def forward_flat(self, flat, fid_flat):
        """Shared hybrid path: encode -> FiLM -> quantum -> gated fusion -> head."""
        h = self.encoder(flat)
        h = self.film(h, fid_flat)  # FiLM injected here; v11 skipped this in standalone use
        q_in = torch.tanh(self.to_quantum(h)) * 2.0 * torch.pi
        q_w = self.q_weight_gen(h)
        qf = self.q_engine(q_in, q_w)
        if qf.dtype != h.dtype:
            qf = qf.to(h.dtype)
        q_up = self.q_proj(qf)
        g = self.fusion_gate(torch.cat([h, q_up], dim=-1))
        return self.head(g * h + (1.0 - g) * q_up)

    def forward(self, x, focus_ids):
        """Standalone 2D use: (B, D) + (B,) focus ids."""
        return self.forward_flat(x.to(DTYPE), focus_ids)


class FocusFiLM(nn.Module):
    def __init__(self, n_focus, hidden):
        super().__init__()
        self.emb = nn.Embedding(n_focus, hidden)
        self.to_gain = nn.Linear(hidden, hidden)
        self.to_bias = nn.Linear(hidden, hidden)
        nn.init.normal_(self.to_gain.weight, std=0.02)
        nn.init.zeros_(self.to_gain.bias)
        # FIX: small weights (not zeros) so the bias branch is alive at init,
        # with zero bias so the whole FiLM starts as identity.
        nn.init.normal_(self.to_bias.weight, std=0.02)
        nn.init.zeros_(self.to_bias.bias)

    def forward(self, h, fid):
        e = self.emb(fid)
        return h * (1.0 + torch.tanh(self.to_gain(e))) + self.to_bias(e)


class SovereignEngine(nn.Module):
    def __init__(self, core, film, input_dim, gru_hidden=64, gru_layers=1,
                 sanitizer=None):
        super().__init__()
        self.core = core
        self.film = film  # registered so it appears in state_dict
        self.sanitizer = sanitizer or HealingSanitizer(input_dim)
        self.gru = nn.GRU(input_dim, gru_hidden, num_layers=gru_layers, batch_first=True)
        # batch_first=True everywhere: no silent transpose bugs
        self.attention = nn.MultiheadAttention(gru_hidden, num_heads=4,
                                               dropout=0.1, batch_first=True)
        self.att_norm = nn.LayerNorm(gru_hidden)
        self.gru_proj = nn.Linear(gru_hidden, input_dim)
        self.residual_weight = nn.Parameter(torch.tensor(0.5))

    def forward(self, x, focus_ids):
        x = x.to(DTYPE)
        if x.dim() == 2:  # single-step input
            x = x.unsqueeze(1)
        B, T, D = x.shape

        x_s, anomaly_rate = self.sanitizer(x)
        gru_out, _ = self.gru(x_s)                     # (B, T, H)
        attn_out, _ = self.attention(gru_out, gru_out, gru_out)
        attn_out = self.att_norm(gru_out + attn_out)   # residual + norm
        proj = self.gru_proj(attn_out)

        w = torch.sigmoid(self.residual_weight)
        mixed = w * x_s + (1.0 - w) * proj             # (B, T, D)

        flat = mixed.reshape(B * T, D)
        # repeat_interleave: index = b*T + t must match flat ordering
        fid_flat = focus_ids.repeat_interleave(T)
        fused = self.core.forward_flat(flat, fid_flat)
        logits = fused.reshape(B, T, -1)
        return logits[:, -1], anomaly_rate


def make_walk_data(n_sequences, seq_len, dim, n_classes, n_universes, seed):
    g = torch.Generator().manual_seed(seed)
    base_dirs = torch.randn(n_classes, dim, generator=g, dtype=DTYPE)
    base_dirs = base_dirs / base_dirs.norm(dim=-1, keepdim=True).clamp_min(1e-6)
    perms = [torch.arange(n_classes)]
    pairs = [(0, 1), (2, 3), (1, 2), (0, 3)]
    for u in range(1, n_universes):
        p = torch.arange(n_classes).clone()
        a, b = pairs[(u - 1) % len(pairs)]
        p[a], p[b] = p[b].clone(), p[a].clone()
        perms.append(p)
    seqs, ys, us = [], [], []
    per_cell = n_sequences // (n_classes * n_universes)
    assert per_cell > 0, "n_sequences too small for the class x universe grid"
    for u in range(n_universes):
        perm = perms[u]
        for c in range(n_classes):
            direction = base_dirs[c]
            starts = torch.randn(per_cell, dim, generator=g, dtype=DTYPE) * 0.6
            t_axis = torch.arange(seq_len, dtype=DTYPE).view(1, seq_len, 1)
            walk = starts.unsqueeze(0) + t_axis * direction.view(1, 1, -1)
            walk = walk + torch.randn(1, seq_len, per_cell, dim, generator=g, dtype=DTYPE) * 0.35
            seqs.append(walk)
            ys.append(torch.full((per_cell,), int(perm[c]), dtype=torch.long))
            us.append(torch.full((per_cell,), u, dtype=torch.long))
    # seqs are (1, T, per_cell, D) -> to (T, B_total, D)
    X = torch.cat([s.reshape(-1, s.shape[2], s.shape[3]) for s in seqs], dim=1)
    Y = torch.cat(ys, 0); U = torch.cat(us, 0)
    idx = torch.randperm(X.shape[1], generator=g)
    return X[:, idx], Y[idx], U[idx], perms, base_dirs


def to_batch_first(x_tbd):
    """(T, B, D) legacy layout -> (B, T, D) used by v12."""
    return x_tbd.transpose(0, 1).contiguous()


def perturbation_test(engine, X_va_tbd, Y_va, U_va, seed=0):
    print("\n" + "=" * 78)
    print("HEALING SANITIZER PERTURBATION TEST")
    print("=" * 78)
    print(f"{'noise_sigma':>12} {'anomaly_rate':>14} {'agree':>8} {'accuracy':>10}")
    print("-" * 78)
    g = torch.Generator().manual_seed(seed)
    X_va = to_batch_first(X_va_tbd)
    engine.eval()
    with torch.no_grad():
        base_logits, _ = engine(X_va, U_va)
        base_pred = base_logits.argmax(-1)
    for sigma in (0.0, 0.5, 1.0, 2.0, 4.0):
        x_pert = X_va + sigma * torch.randn(X_va.shape, generator=g)
        engine.eval()
        with torch.no_grad():
            logits, rate = engine(x_pert, U_va)
            pred = logits.argmax(-1)
            agree = (pred == base_pred).float().mean().item()
            acc = (pred == Y_va).float().mean().item()
        print(f"{sigma:>12.2f} {rate:>14.4f} {agree:>8.3f} {acc:>10.3f}")
    print("\n(agree = same prediction as unperturbed input; accuracy = correct vs labels)")


class Daemon:
    """
    Hardened file-watching daemon.
    Protocol: producers write `name.pt.tmp`, then atomically rename to `name.pt`.
    The daemon additionally waits one poll cycle after first seeing a file so
    partially-written files are never consumed, and loads with
    weights_only=True so a dropped file can never execute pickled code.
    """
    def __init__(self, engine, watch_dir: Path, log_path: Path, poll_s=2.0,
                 stable_cycles: int = 1):
        self.engine = engine
        self.watch_dir = watch_dir
        self.log_path = log_path
        self.poll_s = poll_s
        self.stable_cycles = stable_cycles
        self.stop_event = threading.Event()
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        (self.watch_dir / "processed").mkdir(exist_ok=True)

    def _handle_signal(self, signum, _frame):
        print(f"\n[daemon] got signal {signum}, shutting down")
        self.stop_event.set()

    def _load_payload(self, f: Path):
        payload = torch.load(f, weights_only=True)  # tensors/ints only, no RCE
        x = payload["x"]
        if x.dim() == 2:
            x = x.unsqueeze(1)
        tags = payload["focus_ids"].long()
        if tags.shape[0] != x.shape[0]:
            raise ValueError(f"focus_ids len {tags.shape[0]} != batch {x.shape[0]}")
        return x, tags

    def _process(self, f: Path, log):
        x, tags = self._load_payload(f)
        self.engine.eval()
        with torch.no_grad():
            logits, rate = self.engine(x, tags)
        record = {
            "ts": time.time(),
            "file": f.name,
            "anomaly_rate": rate,
            "predictions": logits.argmax(-1).tolist(),
        }
        log.write(json.dumps(record) + "\n")
        log.flush()
        print(f"[daemon] {f.name}: anomaly={rate:.4f} preds={record['predictions']}")

    def run(self):
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        print(f"[daemon] watching {self.watch_dir}  logging to {self.log_path}")
        seen: dict[str, int] = {}
        with self.log_path.open("a") as log:
            while not self.stop_event.is_set():
                for f in sorted(self.watch_dir.glob("*.pt")):
                    if self.stop_event.is_set():
                        break
                    try:
                        # stability check: skip files newer than stable_cycles polls
                        age = seen.get(f.name, 0)
                        seen[f.name] = age + 1
                        if age < self.stable_cycles:
                            continue
                        self._process(f, log)
                        f.rename(self.watch_dir / "processed" / f.name)
                        seen.pop(f.name, None)
                    except Exception as e:
                        print(f"[daemon] error on {f.name}: {e}")
                        f.rename(self.watch_dir / "processed" / (f.name + ".failed"))
                        seen.pop(f.name, None)
                self.stop_event.wait(self.poll_s)  # interruptible sleep
        print("[daemon] stopped")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=300)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--compile", action="store_true", help="torch.compile the forward (training only)")
    p.add_argument("--sanitizer-z-cut", type=float, default=3.0)
    p.add_argument("--warmup-steps", type=int, default=50)
    p.add_argument("--checkpoint", type=str, default="sovereign_v12.pth")
    p.add_argument("--daemon", action="store_true")
    p.add_argument("--daemon-watch-dir", type=str, default="daemon_inbox")
    p.add_argument("--daemon-log", type=str, default="sovereign_daemon.log")
    p.add_argument("--daemon-poll", type=float, default=2.0)
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    torch.manual_seed(42)
    print("=" * 82)
    print("SOVEREIGN v12 (fixed)")
    print(f"  HealingSanitizer z_cut={args.sanitizer_z_cut} warmup={args.warmup_steps}")
    print("=" * 82)

    # Data is produced in (T, B, D) legacy layout; engine expects (B, T, D).
    X_tbd, Y, U, perms, dirs = make_walk_data(1200, 5, 16, 4, 3, 43)
    X = to_batch_first(X_tbd)
    n_total = X.shape[0]
    n_val = int(n_total * 0.3)
    split = torch.randperm(n_total, generator=torch.Generator().manual_seed(7))
    tr_idx, va_idx = split[n_val:], split[:n_val]
    X_tr, Y_tr, U_tr = X[tr_idx], Y[tr_idx], U[tr_idx]
    X_va, Y_va, U_va = X[va_idx], Y[va_idx], U[va_idx]

    core = HybridCore(16, 96, 8, 6, 4)
    film = FocusFiLM(N_FOCUS, 96)
    core.film = film  # FiLM is part of core.forward_flat; register it there
    sanitizer = HealingSanitizer(16, z_cut=args.sanitizer_z_cut,
                                 warmup_steps=args.warmup_steps)
    engine = SovereignEngine(core, film, 16, gru_hidden=64, sanitizer=sanitizer)

    # FIX: compile a WRAPPER, never the saved modules, so state_dict keys stay clean.
    train_engine = engine
    if args.compile:
        try:
            train_engine = torch.compile(engine)
            print("[+] torch.compile enabled (training/eval wrapper only)")
        except Exception as e:
            logging.warning("torch.compile unavailable: %s", e)

    opt = torch.optim.AdamW(engine.parameters(), lr=2e-3, weight_decay=1e-3)
    lossf = nn.CrossEntropyLoss(label_smoothing=0.1)

    print("\n[+] training...")
    best = 0.0
    step_times = []
    for step in range(1, args.steps + 1):
        engine.train()
        idx = torch.randint(0, X_tr.shape[0], (args.batch_size,))
        xb, yb, ub = X_tr[idx], Y_tr[idx], U_tr[idx]
        t0 = time.perf_counter()
        logits, rate = train_engine(xb, ub)
        loss = lossf(logits, yb)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(engine.parameters(), 1.0)
        opt.step()
        if step > 10:  # skip compile warmup
            step_times.append(time.perf_counter() - t0)

        if step % 25 == 0 or step == 1:
            engine.eval()
            with torch.no_grad():
                vl, vrate = train_engine(X_va, U_va)
                va = (vl.argmax(-1) == Y_va).float().mean().item()
            best = max(best, va)
            msg = (f"Step {step:>3} | tr_loss {loss.item():.4f} | "
                   f"va_acc {va:.3f} | anomaly_rate {vrate:.4f}")
            if step_times:
                import statistics
                msg += f" | {statistics.median(step_times) * 1000:.1f} ms/step"
            print(msg)

    # FIX: save EVERYTHING from the uncompiled engine.
    torch.save({
        "model": engine.state_dict(),
        "config": {"input_dim": 16, "hidden": 96, "n_qubits": 8, "n_layers": 6,
                   "n_classes": 4, "gru_hidden": 64, "n_focus": N_FOCUS,
                   "z_cut": args.sanitizer_z_cut},
    }, args.checkpoint)
    print(f"[+] saved {args.checkpoint} (best va_acc {best:.3f}) -- complete state")

    perturbation_test(engine, X_tbd[:, va_idx], Y_va, U_va)

    if args.daemon:
        d = Daemon(engine, Path(args.daemon_watch_dir), Path(args.daemon_log),
                   poll_s=args.daemon_poll)
        d.run()


if __name__ == "__main__":
    main()
