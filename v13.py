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
N_UNIVERSES = 3


class GatedLinear(nn.Module):
    def __init__(self, i, o):
        super().__init__()
        self.w1 = spectral_norm(nn.Linear(i, o))
        self.w2 = spectral_norm(nn.Linear(i, o))

    def forward(self, x):
        return F.silu(self.w1(x)) * self.w2(x)


class QuantumEngine(nn.Module):
    def __init__(self, n_qubits, n_layers):
        super().__init__()
        self.n_qubits, self.n_layers = n_qubits, n_layers

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
                qml.StronglyEntanglingLayers(weights[:, i : i + 1],
                                             wires=range(n_qubits))
            return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]

        self.circuit = circuit
        logging.info("QuantumEngine: backend=%s diff=%s",
                     self.device_name, self.diff_method)

    def forward(self, x, w):
        return torch.stack(self.circuit(x.to(DTYPE), w.to(DTYPE)), dim=-1)


class QWeightGen(nn.Module):
    def __init__(self, latent, n_layers, n_qubits):
        super().__init__()
        self.n_layers, self.n_qubits = n_layers, n_qubits
        t = n_layers * n_qubits * 3
        self.net = nn.Sequential(GatedLinear(latent, 256), nn.LayerNorm(256),
                                 GatedLinear(256, t), nn.LayerNorm(t))

    def forward(self, z):
        return (torch.tanh(self.net(z)) * torch.pi).view(
            -1, self.n_layers, self.n_qubits, 3)


class HealingSanitizer(nn.Module):
    def __init__(self, input_dim, z_cut=3.0, warmup_steps=50):
        super().__init__()
        self.z_cut = z_cut
        self.register_buffer("running_median", torch.zeros(input_dim))
        self.register_buffer("running_mad", torch.ones(input_dim))
        self.register_buffer("steps_seen", torch.tensor(0, dtype=torch.long))
        self.warmup_steps = warmup_steps
        self._train_step = 0

    def _update_stats(self, x):
        flat = x.detach().reshape(-1, x.shape[-1])
        batch_median = flat.median(dim=0).values
        batch_mad = (flat - batch_median).abs().median(dim=0).values.clamp_min(1e-6)

        self.steps_seen += 1
        self._train_step += 1
        m = 0.10 if self._train_step <= self.warmup_steps else 0.01
        self.running_median.mul_(1 - m).add_(batch_median, alpha=m)
        self.running_mad.mul_(1 - m).add_(batch_mad, alpha=m)

    def forward(self, x):
        if self.training:
            self._train_step += 1
            if self._train_step < 5:
                return x, x.new_zeros(())
            self._update_stats(x)

        med = self.running_median.view(1, 1, -1)
        diff = x - med
        scale = (self.running_mad * 1.4826).clamp_min(1e-3)
        z = diff.abs() / scale.view(1, 1, -1)
        mask = z > self.z_cut
        suppression = torch.exp(-0.5 * (z - self.z_cut).clamp(min=0.0))
        healed = med + diff * suppression
        return healed, mask.float().mean().detach()


class FocusFiLM(nn.Module):
    def __init__(self, n_focus, hidden):
        super().__init__()
        self.emb = nn.Embedding(n_focus, hidden)
        self.to_gain = nn.Linear(hidden, hidden)
        self.to_bias = nn.Linear(hidden, hidden)
        nn.init.zeros_(self.to_gain.weight)
        nn.init.zeros_(self.to_gain.bias)
        nn.init.normal_(self.to_bias.weight, std=0.02)
        nn.init.zeros_(self.to_bias.bias)

    def forward(self, h, fid):
        e = self.emb(fid)
        return h * (1.0 + torch.tanh(self.to_gain(e))) + self.to_bias(e)


class HybridCore(nn.Module):
    def __init__(self, input_dim=16, hidden=96, n_qubits=8, n_layers=6,
                 n_classes=4, n_focus=8, dropout=0.15):
        super().__init__()
        self.film = FocusFiLM(n_focus, hidden)
        self.encoder = nn.Sequential(
            GatedLinear(input_dim, hidden), nn.LayerNorm(hidden), nn.Dropout(dropout),
            GatedLinear(hidden, hidden), nn.LayerNorm(hidden))
        self.to_quantum = nn.Sequential(nn.Linear(hidden, n_qubits * 2),
                                        nn.LayerNorm(n_qubits * 2))
        self.q_engine = QuantumEngine(n_qubits, n_layers)
        self.q_weight_gen = QWeightGen(hidden, n_layers, n_qubits)
        self.q_proj = nn.Sequential(nn.Linear(n_qubits, hidden), nn.SiLU(),
                                    nn.Linear(hidden, hidden), nn.LayerNorm(hidden))
        self.fusion_gate = nn.Sequential(nn.Linear(hidden * 2, hidden), nn.Sigmoid())
        self.head = nn.Sequential(GatedLinear(hidden, hidden), nn.LayerNorm(hidden),
                                  nn.Dropout(dropout), nn.Linear(hidden, n_classes))

    def forward_flat(self, flat, fid_flat):
        h = self.encoder(flat)
        h = self.film(h, fid_flat)
        q_in = torch.tanh(self.to_quantum(h)) * 2.0 * torch.pi
        q_w = self.q_weight_gen(h)
        qf = self.q_engine(q_in, q_w)
        if qf.dtype != h.dtype:
            qf = qf.to(h.dtype)
        q_up = self.q_proj(qf)
        g = self.fusion_gate(torch.cat([h, q_up], dim=-1))
        return self.head(g * h + (1.0 - g) * q_up)

    def forward(self, x, focus_ids):
        return self.forward_flat(x.to(DTYPE), focus_ids)


class SovereignEngine(nn.Module):
    def __init__(self, core, input_dim, gru_hidden=64, gru_layers=1, sanitizer=None):
        super().__init__()
        self.core = core
        self.sanitizer = sanitizer or HealingSanitizer(input_dim)
        self.gru = nn.GRU(input_dim, gru_hidden, num_layers=gru_layers,
                          batch_first=True)
        self.attention = nn.MultiheadAttention(gru_hidden, num_heads=4,
                                               dropout=0.1, batch_first=True)
        self.att_norm = nn.LayerNorm(gru_hidden)
        self.gru_proj = nn.Linear(gru_hidden, input_dim)
        self.residual_weight = nn.Parameter(torch.tensor(0.5))

    def forward(self, x, focus_ids):
        x = x.to(DTYPE)
        if x.dim() == 2:
            x = x.unsqueeze(1)
        B, T, D = x.shape

        x_s, anomaly_rate = self.sanitizer(x)
        gru_out, _ = self.gru(x_s)
        attn_out, _ = self.attention(gru_out, gru_out, gru_out)
        attn_out = self.att_norm(gru_out + attn_out)
        proj = self.gru_proj(attn_out)

        w = torch.sigmoid(self.residual_weight)
        mixed = w * x_s + (1.0 - w) * proj

        flat = mixed.reshape(B * T, D)
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
            t_axis = torch.arange(seq_len, dtype=DTYPE).view(1, seq_len, 1, 1)
            walk = starts.view(1, 1, per_cell, dim) + t_axis * direction.view(1, 1, 1, dim)
            walk = walk + torch.randn(1, seq_len, per_cell, dim,
                                      generator=g, dtype=DTYPE) * 0.35
            seqs.append(walk)
            ys.append(torch.full((per_cell,), int(perm[c]), dtype=torch.long))
            us.append(torch.full((per_cell,), u, dtype=torch.long))
    X = torch.cat([s.reshape(-1, s.shape[2], s.shape[3]) for s in seqs], dim=1)
    Y = torch.cat(ys, 0); U = torch.cat(us, 0)
    idx = torch.randperm(X.shape[1], generator=g)
    return X[:, idx], Y[idx], U[idx], perms, base_dirs


def to_batch_first(x_tbd):
    return x_tbd.transpose(0, 1).contiguous()


def _scalar(v):
    return v.item() if torch.is_tensor(v) else float(v)


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
            logits, rate = engine(x_pert, U_va)
            pred = logits.argmax(-1)
            agree = (pred == base_pred).float().mean().item()
            acc = (pred == Y_va).float().mean().item()
            print(f"{sigma:>12.2f} {_scalar(rate):>14.4f} "
                  f"{agree:>8.3f} {acc:>10.3f}")
    print("\n(agree = same prediction as unperturbed input; accuracy = correct vs labels)")


def focus_sensitivity_test(engine, X_va, Y_va, U_va, n_universes):
    print("\n" + "=" * 78)
    print("FOCUS SENSITIVITY TEST")
    print("=" * 78)
    engine.eval()
    with torch.no_grad():
        base_logits, _ = engine(X_va, U_va)
        alt_logits, _ = engine(X_va, (U_va + 1) % n_universes)
        base_pred = base_logits.argmax(-1)
        alt_pred = alt_logits.argmax(-1)
        base_acc = (base_pred == Y_va).float().mean().item()
        alt_acc = (alt_pred == Y_va).float().mean().item()
        change = (base_pred != alt_pred).float().mean().item()
    print(f"  accuracy with true focus:      {base_acc:.3f}")
    print(f"  accuracy with shifted focus:   {alt_acc:.3f}")
    print(f"  fraction of predictions changed: {change:.3f}")
    if change < 0.01:
        print("  WARNING: model ignores focus_ids — will not generalize to new universes.")
    elif alt_acc < base_acc * 0.85:
        print("  OK: model relies on focus_ids (expected).")
    else:
        print("  ~ model is only mildly focus-sensitive; consider stronger FiLM.")


class Daemon:
    def __init__(self, engine, watch_dir: Path, log_path: Path, poll_s=2.0,
                 stable_cycles: int = 1, n_focus: int = N_FOCUS):
        self.engine = engine
        self.watch_dir = watch_dir
        self.log_path = log_path
        self.poll_s = poll_s
        self.stable_cycles = stable_cycles
        self.n_focus = n_focus
        self.stop_event = threading.Event()
        self.watch_dir.mkdir(parents=True, exist_ok=True)
        (self.watch_dir / "processed").mkdir(exist_ok=True)

    def _handle_signal(self, signum, _frame):
        print(f"\n[daemon] got signal {signum}, shutting down")
        self.stop_event.set()

    def _load_payload(self, f: Path):
        payload = torch.load(f, weights_only=True)
        x = payload["x"]
        if x.dim() == 2:
            x = x.unsqueeze(1)
        tags = payload["focus_ids"].long()
        if tags.shape[0] != x.shape[0]:
            raise ValueError(f"focus_ids len {tags.shape[0]} != batch {x.shape[0]}")
        if (tags < 0).any() or (tags >= self.n_focus).any():
            print(f"[daemon] warning: clamping out-of-range focus_ids in {f.name}")
            tags = tags.clamp_(0, self.n_focus - 1)
        return x, tags

    def _process(self, f: Path, log):
        x, tags = self._load_payload(f)
        self.engine.eval()
        with torch.no_grad():
            logits, rate = self.engine(x, tags)
        record = {
            "ts": time.time(),
            "file": f.name,
            "anomaly_rate": _scalar(rate),
            "predictions": logits.argmax(-1).tolist(),
        }
        log.write(json.dumps(record) + "\n")
        log.flush()
        print(f"[daemon] {f.name}: anomaly={record['anomaly_rate']:.4f} "
              f"preds={record['predictions']}")

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
                self.stop_event.wait(self.poll_s)
        print("[daemon] stopped")


def _config_dict(args):
    return {"input_dim": 16, "hidden": 96, "n_qubits": 8, "n_layers": 6,
            "n_classes": 4, "gru_hidden": 64, "n_focus": N_FOCUS,
            "z_cut": args.sanitizer_z_cut}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=300)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--compile", action="store_true")
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

    X_tbd, Y, U, perms, dirs = make_walk_data(1200, 5, 16, 4, N_UNIVERSES, 43)
    X = to_batch_first(X_tbd)
    n_total = X.shape[0]
    n_val = int(n_total * 0.3)
    split = torch.randperm(n_total, generator=torch.Generator().manual_seed(7))
    tr_idx, va_idx = split[n_val:], split[:n_val]
    X_tr, Y_tr, U_tr = X[tr_idx], Y[tr_idx], U[tr_idx]
    X_va, Y_va, U_va = X[va_idx], Y[va_idx], U[va_idx]

    core = HybridCore(16, 96, 8, 6, 4, n_focus=N_FOCUS)
    sanitizer = HealingSanitizer(16, z_cut=args.sanitizer_z_cut,
                                 warmup_steps=args.warmup_steps)
    engine = SovereignEngine(core, 16, gru_hidden=64, sanitizer=sanitizer)

    train_engine = engine
    if args.compile:
        try:
            train_engine = torch.compile(engine)
            print("[!] torch.compile enabled (see notes on qnode graph breaks)")
        except Exception as e:
            logging.warning("torch.compile failed: %s", e)
            train_engine = engine

    opt = torch.optim.AdamW(engine.parameters(), lr=2e-3, weight_decay=1e-3)
    lossf = nn.CrossEntropyLoss(label_smoothing=0.1)

    print("\n[+] training...")
    best = 0.0
    step_times = []
    import statistics
    for step in range(1, args.steps + 1):
        engine.train()
        idx = torch.randint(0, X_tr.shape[0], (args.batch_size,))
        xb, yb, ub = X_tr[idx], Y_tr[idx], U_tr[idx]
        t0 = time.perf_counter()
        logits, _rate = train_engine(xb, ub)
        loss = lossf(logits, yb)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(engine.parameters(), 1.0)
        opt.step()
        if step > 10:
            step_times.append(time.perf_counter() - t0)

        if step % 25 == 0 or step == 1:
            engine.eval()
            with torch.no_grad():
                vl, vrate = train_engine(X_va, U_va)
                va = (vl.argmax(-1) == Y_va).float().mean().item()
            improved = va > best
            if improved:
                best = va
                torch.save({"model": engine.state_dict(),
                            "config": _config_dict(args)}, args.checkpoint)
            msg = (f"Step {step:>3} | tr_loss {loss.item():.4f} | "
                   f"va_acc {va:.3f} | anomaly_rate {_scalar(vrate):.4f}")
            if improved:
                msg += " *"
            if step_times:
                msg += f" | {statistics.median(step_times) * 1000:.1f} ms/step"
            print(msg)

    last_path = (args.checkpoint.replace(".pth", "_last.pth")
                 if ".pth" in args.checkpoint else args.checkpoint + "_last.pth")
    torch.save({"model": engine.state_dict(), "config": _config_dict(args)}, last_path)
    print(f"[+] best checkpoint: {args.checkpoint}  (best va_acc {best:.3f})")
    print(f"[+] last checkpoint: {last_path}")

    if Path(args.checkpoint).exists():
        ckpt = torch.load(args.checkpoint, weights_only=True)
        engine.load_state_dict(ckpt["model"])
        print(f"[+] loaded best model from {args.checkpoint} for evaluation")

    perturbation_test(engine, X_tbd[:, va_idx], Y_va, U_va)
    focus_sensitivity_test(engine, X_va, Y_va, U_va, n_universes=N_UNIVERSES)

    if args.daemon:
        d = Daemon(engine, Path(args.daemon_watch_dir), Path(args.daemon_log),
                   poll_s=args.daemon_poll, n_focus=N_FOCUS)
        d.run()


if __name__ == "__main__":
    main()
