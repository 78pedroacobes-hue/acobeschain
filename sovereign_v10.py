"""
sovereign_v10.py -- tightened.

v10 changelog vs the previous draft:
  - DefenseShield -> InputSanitizer, threshold lowered so it actually fires
  - Stats freeze after warmup (no more training-time feedback loop)
  - Perturbation test at end: proves the sanitizer does something
  - Daemon mode reads real files from a watch directory, logs to disk
  - Renamed to match what the code does
"""
from __future__ import annotations
import argparse, json, logging, os, signal, sys, time
from dataclasses import dataclass, asdict
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
import pennylane as qml

DTYPE = torch.float32
N_FOCUS = 8


# ---------------------------------------------------------------------------
class SwiGLU(nn.Module):
    def __init__(self, i, o):
        super().__init__()
        self.w1 = nn.Linear(i, o); self.w2 = nn.Linear(i, o)
    def forward(self, x): return F.silu(self.w1(x)) * self.w2(x)


class QuantumEngine(nn.Module):
    def __init__(self, n_qubits, n_layers, backend="default.qubit"):
        super().__init__()
        self.n_qubits, self.n_layers = n_qubits, n_layers
        self.dev = qml.device(backend, wires=n_qubits)

        @qml.qnode(self.dev, interface="torch", diff_method="backprop")
        def circuit(inputs, weights):
            iy = inputs[:, :n_qubits]; iz = inputs[:, n_qubits:]
            for i in range(n_layers):
                qml.AngleEmbedding(iy, wires=range(n_qubits), rotation="Y")
                qml.AngleEmbedding(iz, wires=range(n_qubits), rotation="Z")
                qml.StronglyEntanglingLayers(weights[:, i:i+1], wires=range(n_qubits))
            return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
        self.circuit = circuit

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


class InputSanitizer(nn.Module):
    """
    Per-feature z-score clamp.

    WHAT IT DOES:
      - Tracks per-feature running mean/var for `warmup_steps` batches.
      - After warmup, stats are frozen.
      - At inference, any feature with |z| > `z_cut` gets pulled partway back
        toward the running mean. Bigger deviations get pulled more.

    WHAT IT DOES NOT DO:
      - It is not adversarial training. It does not detect FGSM/PGD.
        A cleverly crafted perturbation within |z| < z_cut passes through.
      - It is a preprocessing step, not a defense against a determined attacker.

    Threshold note: z_cut=3.0 means ~0.3% of Gaussian data gets touched.
    That's the level where the mask actually fires. Anything above 5.0
    on Gaussian inputs is a no-op.
    """
    def __init__(self, input_dim, z_cut=3.0, warmup_steps=50, pull=0.8):
        super().__init__()
        self.z_cut = z_cut
        self.pull = pull
        self.warmup_remaining = warmup_steps
        self.register_buffer("running_mean", torch.zeros(input_dim))
        self.register_buffer("running_var", torch.ones(input_dim))
        self.register_buffer("frozen", torch.tensor(0))

    def _update_stats(self, x):
        flat = x.detach().reshape(-1, x.shape[-1])
        bm = flat.mean(dim=0)
        bv = flat.var(dim=0, unbiased=False).clamp_min(1e-6)
        if self.frozen.item() == 0 and self.warmup_remaining > 0:
            m = 0.05
            self.running_mean.mul_(1 - m).add_(bm, alpha=m)
            self.running_var.mul_(1 - m).add_(bv, alpha=m)
            self.warmup_remaining -= 1
            if self.warmup_remaining == 0:
                self.frozen.fill_(1)

    def forward(self, x):
        if self.training:
            self._update_stats(x)
        diff = x - self.running_mean.view(1, 1, -1)
        z = diff.abs() / (torch.sqrt(self.running_var) + 1e-6).view(1, 1, -1)
        mask = (z > self.z_cut).float()
        # proportional pull: how far past the cutoff, capped at 1
        excess = (z - self.z_cut).clamp(0.0, 1.0)
        # direction: sign of diff
        sign = torch.sign(diff)
        # pull back toward mean by `pull * excess` fraction
        pulled = x - sign * excess * self.pull * torch.sqrt(self.running_var + 1e-6).view(1, 1, -1)
        shielded = torch.where(mask > 0, pulled, x)
        return shielded, mask.mean().item()


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

    def forward(self, x):
        x = x.to(DTYPE)
        h = self.encoder(x)
        q_in = torch.tanh(self.to_quantum(h)) * 2.0 * torch.pi
        q_w = self.q_weight_gen(h)
        qf = self.q_engine(q_in, q_w)
        if qf.dtype != h.dtype: qf = qf.to(h.dtype)
        q_up = self.q_proj(qf)
        g = self.fusion_gate(torch.cat([h, q_up], dim=-1))
        return self.head(g * h + (1.0 - g) * q_up)


class FocusFiLM(nn.Module):
    def __init__(self, n_focus, hidden):
        super().__init__()
        self.emb = nn.Embedding(n_focus, hidden)
        self.to_gain = nn.Linear(hidden, hidden)
        self.to_bias = nn.Linear(hidden, hidden)
        nn.init.normal_(self.to_gain.weight, std=0.02)
        nn.init.zeros_(self.to_gain.bias)
        nn.init.zeros_(self.to_bias.weight); nn.init.zeros_(self.to_bias.bias)
    def forward(self, h, fid):
        e = self.emb(fid)
        return h * (1.0 + torch.tanh(self.to_gain(e))) + self.to_bias(e)


class SovereignEngine(nn.Module):
    def __init__(self, core, film, input_dim, gru_hidden=64, gru_layers=1,
                 sanitizer=None):
        super().__init__()
        self.core = core
        self.film = film
        self.sanitizer = sanitizer or InputSanitizer(input_dim)
        self.gru = nn.GRU(input_dim, gru_hidden, num_layers=gru_layers, batch_first=False)
        self.gru_proj = nn.Linear(gru_hidden, input_dim)
        self.residual_weight = nn.Parameter(torch.tensor(0.5))

    def forward(self, x, focus_ids):
        x = x.to(DTYPE)
        single = (x.dim() == 2)
        if single: x = x.unsqueeze(0)

        x_s, anomaly_rate = self.sanitizer(x)
        gru_out, _ = self.gru(x_s)
        proj = self.gru_proj(gru_out)
        w = torch.sigmoid(self.residual_weight)
        mixed = w * x_s + (1.0 - w) * proj

        T, B, D = mixed.shape
        flat = mixed.reshape(T * B, D)
        fid_flat = focus_ids.repeat(T)
        h = self.core.encoder(flat)
        h = self.film(h, fid_flat)
        q_in = torch.tanh(self.core.to_quantum(h)) * 2.0 * torch.pi
        q_w = self.core.q_weight_gen(h)
        qf = self.core.q_engine(q_in, q_w)
        if qf.dtype != h.dtype: qf = qf.to(h.dtype)
        q_up = self.core.q_proj(qf)
        g = self.core.fusion_gate(torch.cat([h, q_up], dim=-1))
        fused = g * h + (1.0 - g) * q_up
        logits = self.core.head(fused).reshape(T, B, -1)
        return logits[-1], anomaly_rate


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
    for u in range(n_universes):
        perm = perms[u]
        for c in range(n_classes):
            direction = base_dirs[c]
            starts = torch.randn(per_cell, dim, generator=g, dtype=DTYPE) * 0.6
            t_axis = torch.arange(seq_len, dtype=DTYPE).view(seq_len, 1, 1)
            walk = starts.unsqueeze(0) + t_axis * direction.view(1, 1, -1)
            walk = walk + torch.randn(seq_len, per_cell, dim, generator=g, dtype=DTYPE) * 0.35
            seqs.append(walk)
            ys.append(torch.full((per_cell,), int(perm[c]), dtype=torch.long))
            us.append(torch.full((per_cell,), u, dtype=torch.long))
    X = torch.cat(seqs, dim=1); Y = torch.cat(ys, 0); U = torch.cat(us, 0)
    idx = torch.randperm(X.shape[1], generator=g)
    return X[:, idx], Y[idx], U[idx], perms, base_dirs


# ---------------------------------------------------------------------------
def perturbation_test(engine, X_va, U_va, seed=0):
    """
    Inject noise at several magnitudes and measure:
      - sanitizer anomaly rate
      - accuracy change
    This is what proves the sanitizer does something.
    """
    print("\n" + "=" * 78)
    print("SANITIZER PERTURBATION TEST")
    print("=" * 78)
    print(f"{'noise_sigma':>12} {'anomaly_rate':>14} {'accuracy':>10}")
    print("-" * 78)
    g = torch.Generator().manual_seed(seed)
    for sigma in (0.0, 0.5, 1.0, 2.0, 4.0):
        x_pert = X_va + sigma * torch.randn(X_va.shape, generator=g)
        engine.eval()
        with torch.no_grad():
            logits, rate = engine(x_pert, U_va[:X_va.shape[1]])
            # we don't have labels here; use a proxy: prediction consistency vs sigma=0
            logits0, _ = engine(X_va, U_va[:X_va.shape[1]])
            agree = (logits.argmax(-1) == logits0.argmax(-1)).float().mean().item()
        print(f"{sigma:>12.2f} {rate:>14.4f} {agree:>10.3f}")
    print("\n(anomaly_rate should climb with sigma; accuracy/agreement should")
    print(" stay high if the sanitizer is pulling outliers back toward clean)")


# ---------------------------------------------------------------------------
# DAEMON MODE -- reads real files, logs to real disk
# ---------------------------------------------------------------------------
class Daemon:
    """
    Watches a directory for .npy or .pt files. For each file:
      - loads the tensor
      - runs the engine
      - appends result to log
      - moves the file to processed/
    Handles SIGTERM/SIGINT for clean shutdown.
    """
    def __init__(self, engine, watch_dir: Path, log_path: Path, poll_s=2.0):
        self.engine = engine
        self.watch_dir = watch_dir
        self.log_path = log_path
        self.poll_s = poll_s
        self.running = True
        self.watch_dir.mkdir(exist_ok=True)
        (self.watch_dir / "processed").mkdir(exist_ok=True)

    def _handle_signal(self, signum, _frame):
        print(f"\n[daemon] got signal {signum}, shutting down")
        self.running = False

    def run(self):
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        print(f"[daemon] watching {self.watch_dir}  logging to {self.log_path}")
        print(f"[daemon] drop .pt files containing a (T, B, D) tensor + tags to feed")

        with self.log_path.open("a") as log:
            while self.running:
                found = list(self.watch_dir.glob("*.pt"))
                for f in found:
                    if not self.running: break
                    try:
                        payload = torch.load(f, weights_only=False)
                        x = payload["x"]; tags = payload["focus_ids"]
                        self.engine.eval()
                        with torch.no_grad():
                            logits, rate = self.engine(x, tags)
                        record = {
                            "ts": time.time(),
                            "file": f.name,
                            "anomaly_rate": rate,
                            "predictions": logits.argmax(-1).tolist(),
                        }
                        log.write(json.dumps(record) + "\n"); log.flush()
                        print(f"[daemon] {f.name}: anomaly={rate:.4f} "
                              f"preds={record['predictions']}")
                        f.rename(self.watch_dir / "processed" / f.name)
                    except Exception as e:
                        print(f"[daemon] error on {f.name}: {e}")
                        f.rename(self.watch_dir / "processed" / (f.name + ".failed"))
                time.sleep(self.poll_s)


# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=300)
    p.add_argument("--sanitizer-z-cut", type=float, default=3.0)
    p.add_argument("--warmup-steps", type=int, default=50)
    p.add_argument("--daemon", action="store_true",
                   help="after training, run as file-watching daemon")
    p.add_argument("--daemon-watch-dir", type=str, default="daemon_inbox")
    p.add_argument("--daemon-log", type=str, default="sovereign_daemon.log")
    p.add_argument("--daemon-poll", type=float, default=2.0)
    args = p.parse_args()

    torch.manual_seed(42)
    print("=" * 82)
    print("SOVEREIGN v10 -- tightened")
    print(f"  sanitizer z_cut={args.sanitizer_z_cut}  warmup={args.warmup_steps}")
    print("=" * 82)

    X, Y, U, perms, dirs = make_walk_data(1200, 5, 16, 4, 3, 43)
    n_total = X.shape[1]
    n_val = int(n_total * 0.3)
    split = torch.randperm(n_total, generator=torch.Generator().manual_seed(7))
    tr_idx, va_idx = split[n_val:], split[:n_val]
    X_tr, Y_tr, U_tr = X[:, tr_idx], Y[tr_idx], U[tr_idx]
    X_va, Y_va, U_va = X[:, va_idx], Y[va_idx], U[va_idx]

    core = HybridCore(16, 96, 8, 6, 4).to(DTYPE)
    film = FocusFiLM(N_FOCUS, 96)
    sanitizer = InputSanitizer(16, z_cut=args.sanitizer_z_cut,
                               warmup_steps=args.warmup_steps)
    engine = SovereignEngine(core, film, 16, gru_hidden=64, sanitizer=sanitizer)

    opt = torch.optim.AdamW(engine.parameters(), lr=2e-3, weight_decay=1e-3)
    lossf = nn.CrossEntropyLoss(label_smoothing=0.1)

    print("\n[+] training...")
    best = 0.0
    for step in range(1, args.steps + 1):
        engine.train()
        idx = torch.randint(0, X_tr.shape[1], (16,))
        xb, yb, ub = X_tr[:, idx], Y_tr[idx], U_tr[idx]
        logits, rate = engine(xb, ub)
        loss = lossf(logits, yb)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(engine.parameters(), 1.0)
        opt.step()

        if step % 25 == 0 or step == 1:
            engine.eval()
            with torch.no_grad():
                vl, vrate = engine(X_va, U_va[:X_va.shape[1]])
                va = (vl.argmax(-1) == Y_va).float().mean().item()
            best = max(best, va)
            print(f"Step {step:>3} | tr_loss {loss.item():.4f} | "
                  f"va_acc {va:.3f} | anomaly_rate {vrate:.4f}")

    torch.save({
        "core": core.state_dict(),
        "film": film.state_dict(),
        "gru": engine.gru.state_dict(),
        "sanitizer": engine.sanitizer.state_dict(),
    }, "sovereign_v10_hardened.pth")
    print(f"[+] saved sovereign_v10_hardened.pth  (best va_acc {best:.3f})")

    perturbation_test(engine, X_va, U_va)

    if args.daemon:
        d = Daemon(engine, Path(args.daemon_watch_dir), Path(args.daemon_log),
                   poll_s=args.daemon_poll)
        d.run()
    else:
        print("\n(tip: --daemon watches a folder for .pt files with {x, focus_ids})")


if __name__ == "__main__":
    main()
