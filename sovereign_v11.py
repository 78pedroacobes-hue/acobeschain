"""
sovereign_v11.py — tightened, with all v10 fixes applied.

v11 changelog vs v10:
  - Batch sampling without replacement (was: torch.randint with replacement)
  - Perturbation test uses real labels (was: "agreement proxy", meaningless)
  - No .item() sync inside forward; anomaly rate returned as a tensor
  - Sanitizer warmup uses exact sum/sumsq/count (was: biased fixed-momentum EMA)
  - make_walk_data no longer silently drops n_sequences remainder
  - Daemon uses threading.Event.wait for immediate SIGTERM response
  - Full-batch validation, OneCycle LR, best-checkpoint saving
  - FGSM test added alongside the noise test
  - Dropped unused imports (logging, os, sys)
"""
from __future__ import annotations
import argparse, json, signal, threading, time
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
import pennylane as qml

DTYPE = torch.float32
N_FOCUS = 8
INPUT_DIM = 16


# ---------------------------------------------------------------------------
class SwiGLU(nn.Module):
    def __init__(self, i, o):
        super().__init__()
        self.w1 = nn.Linear(i, o)
        self.w2 = nn.Linear(i, o)

    def forward(self, x):
        return F.silu(self.w1(x)) * self.w2(x)


class QuantumEngine(nn.Module):
    def __init__(self, n_qubits, n_layers, backend="default.qubit"):
        super().__init__()
        self.n_qubits, self.n_layers = n_qubits, n_layers
        self.dev = qml.device(backend, wires=n_qubits)

        @qml.qnode(self.dev, interface="torch", diff_method="backprop")
        def circuit(inputs, weights):
            iy = inputs[:, :n_qubits]
            iz = inputs[:, n_qubits:]
            for i in range(n_layers):
                qml.AngleEmbedding(iy, wires=range(n_qubits), rotation="Y")
                qml.AngleEmbedding(iz, wires=range(n_qubits), rotation="Z")
                qml.StronglyEntanglingLayers(weights[:, i:i + 1], wires=range(n_qubits))
            return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]

        self.circuit = circuit

    def forward(self, x, w):
        return torch.stack(self.circuit(x.to(DTYPE), w.to(DTYPE)), dim=-1)


class QWeightGen(nn.Module):
    def __init__(self, latent, n_layers, n_qubits):
        super().__init__()
        self.n_layers, self.n_qubits = n_layers, n_qubits
        t = n_layers * n_qubits * 3
        self.net = nn.Sequential(
            SwiGLU(latent, 256), nn.LayerNorm(256),
            SwiGLU(256, t), nn.LayerNorm(t),
        )

    def forward(self, z):
        return (torch.tanh(self.net(z)) * torch.pi).view(-1, self.n_layers, self.n_qubits, 3)


class InputSanitizer(nn.Module):
    """
    Per-feature z-score clamp with exact warmup statistics.

    WHAT IT DOES:
      - Accumulates sum, sum-of-squares, and count for `warmup_batches` batches.
      - At freeze, mean/var are the exact empirical moments of the warmup data.
        (v10 used a fixed-momentum EMA which is biased at freeze time.)
      - After freeze, any feature with |z| > z_cut is pulled partway back toward
        the running mean, proportional to how far past the cutoff it is.

    WHAT IT DOES NOT DO:
      - It is not adversarial training. It does not detect FGSM/PGD.
        A crafted perturbation inside |z| < z_cut passes through untouched.
      - It is a preprocessing step, not a defense against a determined attacker.

    z_cut=3.0 touches ~0.3% of Gaussian data, which is where the mask fires.
    Values above 5.0 are a no-op on Gaussian inputs.
    """
    def __init__(self, input_dim, z_cut=3.0, warmup_batches=50, pull=0.8):
        super().__init__()
        self.z_cut = z_cut
        self.pull = pull
        self.warmup_remaining = warmup_batches
        self.register_buffer("sum_x", torch.zeros(input_dim))
        self.register_buffer("sum_x2", torch.zeros(input_dim))
        self.register_buffer("count", torch.tensor(0.0))

    def _current_stats(self):
        n = self.count.clamp_min(1.0)
        mean = self.sum_x / n
        var = (self.sum_x2 / n - mean * mean).clamp_min(1e-6)
        return mean, var

    def _update_stats(self, x):
        if self.warmup_remaining <= 0:
            return
        flat = x.detach().reshape(-1, x.shape[-1])
        self.sum_x.add_(flat.sum(dim=0))
        self.sum_x2.add_((flat * flat).sum(dim=0))
        self.count.add_(float(flat.shape[0]))
        self.warmup_remaining -= 1

    def forward(self, x):
        if self.training:
            self._update_stats(x)
        mean, var = self._current_stats()
        std = torch.sqrt(var) + 1e-6
        diff = x - mean.view(1, 1, -1)
        z = diff.abs() / std.view(1, 1, -1)
        mask = z > self.z_cut
        excess = (z - self.z_cut).clamp(0.0, 1.0)
        sign = torch.sign(diff)
        pulled = x - sign * excess * self.pull * std.view(1, 1, -1)
        shielded = torch.where(mask, pulled, x)
        # return as a detached tensor — no .item() sync in the hot path
        anomaly_rate = mask.to(x.dtype).mean().detach()
        return shielded, anomaly_rate


class HybridCore(nn.Module):
    def __init__(self, input_dim=16, hidden=96, n_qubits=8, n_layers=6,
                 n_classes=4, dropout=0.15):
        super().__init__()
        self.encoder = nn.Sequential(
            SwiGLU(input_dim, hidden), nn.LayerNorm(hidden), nn.Dropout(dropout),
            SwiGLU(hidden, hidden), nn.LayerNorm(hidden),
        )
        self.to_quantum = nn.Sequential(
            nn.Linear(hidden, n_qubits * 2), nn.LayerNorm(n_qubits * 2),
        )
        self.q_engine = QuantumEngine(n_qubits, n_layers)
        self.q_weight_gen = QWeightGen(hidden, n_layers, n_qubits)
        self.q_proj = nn.Sequential(
            nn.Linear(n_qubits, hidden), nn.SiLU(),
            nn.Linear(hidden, hidden), nn.LayerNorm(hidden),
        )
        self.fusion_gate = nn.Sequential(nn.Linear(hidden * 2, hidden), nn.Sigmoid())
        self.head = nn.Sequential(
            SwiGLU(hidden, hidden), nn.LayerNorm(hidden),
            nn.Dropout(dropout), nn.Linear(hidden, n_classes),
        )

    def forward(self, x):
        x = x.to(DTYPE)
        h = self.encoder(x)
        q_in = torch.tanh(self.to_quantum(h)) * 2.0 * torch.pi
        q_w = self.q_weight_gen(h)
        qf = self.q_engine(q_in, q_w)
        if qf.dtype != h.dtype:
            qf = qf.to(h.dtype)
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
        nn.init.zeros_(self.to_bias.weight)
        nn.init.zeros_(self.to_bias.bias)

    def forward(self, h, fid):
        e = self.emb(fid)
        return h * (1.0 + torch.tanh(self.to_gain(e))) + self.to_bias(e)


class SovereignEngine(nn.Module):
    def __init__(self, core, film, input_dim, gru_hidden=64, gru_layers=1, sanitizer=None):
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
        if single:
            x = x.unsqueeze(0)

        x_s, anomaly_rate = self.sanitizer(x)
        gru_out, _ = self.gru(x_s)
        proj = self.gru_proj(gru_out)
        w = torch.sigmoid(self.residual_weight)
        mixed = w * x_s + (1.0 - w) * proj

        T, B, D = mixed.shape
        flat = mixed.reshape(T * B, D)
        fid_flat = focus_ids.repeat(T) if focus_ids.dim() == 1 else focus_ids

        h = self.core.encoder(flat)
        h = self.film(h, fid_flat)
        q_in = torch.tanh(self.core.to_quantum(h)) * 2.0 * torch.pi
        q_w = self.core.q_weight_gen(h)
        qf = self.core.q_engine(q_in, q_w)
        if qf.dtype != h.dtype:
            qf = qf.to(h.dtype)
        q_up = self.core.q_proj(qf)
        g = self.core.fusion_gate(torch.cat([h, q_up], dim=-1))
        fused = g * h + (1.0 - g) * q_up
        logits = self.core.head(fused).reshape(T, B, -1)
        return logits[-1], anomaly_rate


# ---------------------------------------------------------------------------
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

    total_cells = n_classes * n_universes
    per_cell = n_sequences // total_cells
    remainder = n_sequences - per_cell * total_cells
    # distribute remainder across the first `remainder` cells — no silent drop
    cell_sizes = [per_cell + (1 if i < remainder else 0) for i in range(total_cells)]

    seqs, ys, us = [], [], []
    for u in range(n_universes):
        perm = perms[u]
        for c in range(n_classes):
            n_here = cell_sizes[u * n_classes + c]
            if n_here == 0:
                continue
            direction = base_dirs[c]
            starts = torch.randn(n_here, dim, generator=g, dtype=DTYPE) * 0.6
            t_axis = torch.arange(seq_len, dtype=DTYPE).view(seq_len, 1, 1)
            walk = starts.unsqueeze(0) + t_axis * direction.view(1, 1, -1)
            walk = walk + torch.randn(seq_len, n_here, dim, generator=g, dtype=DTYPE) * 0.35
            seqs.append(walk)
            ys.append(torch.full((n_here,), int(perm[c]), dtype=torch.long))
            us.append(torch.full((n_here,), u, dtype=torch.long))

    X = torch.cat(seqs, dim=1)
    Y = torch.cat(ys, 0)
    U = torch.cat(us, 0)
    idx = torch.randperm(X.shape[1], generator=g)
    return X[:, idx], Y[idx], U[idx], perms, base_dirs


@torch.no_grad()
def evaluate(engine, X, Y, U, batch_size=128):
    """Full-set evaluation. Returns (accuracy, mean_anomaly_rate)."""
    engine.eval()
    correct = 0
    total = 0
    rate_acc = torch.zeros(())
    n_batches = 0
    for i in range(0, X.shape[1], batch_size):
        xb = X[:, i:i + batch_size]
        yb = Y[i:i + batch_size]
        ub = U[i:i + batch_size]
        logits, rate = engine(xb, ub)
        correct += (logits.argmax(-1) == yb).sum().item()
        total += yb.shape[0]
        rate_acc = rate_acc + rate.detach()
        n_batches += 1
    acc = correct / max(total, 1)
    rate = float((rate_acc / max(n_batches, 1)).item())
    return acc, rate


# ---------------------------------------------------------------------------
def perturbation_test(engine, X_va, Y_va, U_va, seed=0):
    print("\n" + "=" * 78)
    print("SANITIZER GAUSSIAN-NOISE TEST (labels are real)")
    print("=" * 78)
    print(f"{'noise_sigma':>12} {'anomaly_rate':>14} {'accuracy':>10}")
    print("-" * 78)
    g = torch.Generator().manual_seed(seed)
    engine.eval()
    for sigma in (0.0, 0.5, 1.0, 2.0, 4.0):
        noise = sigma * torch.randn(X_va.shape, generator=g)
        with torch.no_grad():
            logits, rate = engine(X_va + noise, U_va)
            acc = (logits.argmax(-1) == Y_va).float().mean().item()
        print(f"{sigma:>12.2f} {rate.item():>14.4f} {acc:>10.3f}")

    print("\n" + "=" * 78)
    print("FGSM ADVERSARIAL TEST (single-step, gradients through sanitizer)")
    print("=" * 78)
    print(f"{'epsilon':>10} {'anomaly_rate':>14} {'accuracy':>10}")
    print("-" * 78)
    criterion = nn.CrossEntropyLoss()
    engine.eval()
    for eps in (0.0, 0.05, 0.1, 0.2, 0.5):
        x_in = X_va.clone().detach().requires_grad_(True)
        logits_clean, _ = engine(x_in, U_va)
        loss = criterion(logits_clean, Y_va)
        grad = torch.autograd.grad(loss, x_in)[0]
        x_adv = (X_va + eps * grad.sign()).detach()
        with torch.no_grad():
            logits, rate = engine(x_adv, U_va)
            acc = (logits.argmax(-1) == Y_va).float().mean().item()
        print(f"{eps:>10.2f} {rate.item():>14.4f} {acc:>10.3f}")

    print("\n(noise test: anomaly_rate should climb with sigma, accuracy should hold.)")
    print("(FGSM test: if sanitizer has teeth, small eps should barely dent accuracy.)")


# ---------------------------------------------------------------------------
class Daemon:
    """
    Watches a directory for .pt files. For each file:
      - loads {"x": (T,B,D) tensor, "focus_ids": (B,) tensor}
      - runs the engine
      - appends a JSON record to the log
      - moves the file to processed/
    Uses threading.Event.wait for poll so SIGTERM responds immediately.
    """
    def __init__(self, engine, watch_dir, log_path, poll_s=2.0):
        self.engine = engine
        self.watch_dir = Path(watch_dir)
        self.log_path = Path(log_path)
        self.poll_s = poll_s
        self._stop = threading.Event()
        self.watch_dir.mkdir(exist_ok=True)
        (self.watch_dir / "processed").mkdir(exist_ok=True)

    def _handle_signal(self, signum, _frame):
        print(f"\n[daemon] got signal {signum}, shutting down")
        self._stop.set()

    def run(self):
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        print(f"[daemon] watching {self.watch_dir}  logging to {self.log_path}")

        with self.log_path.open("a") as log:
            while not self._stop.is_set():
                for f in list(self.watch_dir.glob("*.pt")):
                    if self._stop.is_set():
                        break
                    try:
                        payload = torch.load(f, weights_only=False)
                        x = payload["x"]
                        tags = payload["focus_ids"]
                        self.engine.eval()
                        with torch.no_grad():
                            logits, rate = self.engine(x, tags)
                        record = {
                            "ts": time.time(),
                            "file": f.name,
                            "anomaly_rate": float(rate.item()),
                            "predictions": logits.argmax(-1).tolist(),
                        }
                        log.write(json.dumps(record) + "\n")
                        log.flush()
                        print(f"[daemon] {f.name}: anomaly={record['anomaly_rate']:.4f} "
                              f"preds={record['predictions']}")
                        f.rename(self.watch_dir / "processed" / f.name)
                    except Exception as e:
                        print(f"[daemon] error on {f.name}: {e}")
                        f.rename(self.watch_dir / "processed" / (f.name + ".failed"))
                self._stop.wait(self.poll_s)


# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--steps", type=int, default=300)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=3e-3)
    p.add_argument("--sanitizer-z-cut", type=float, default=3.0)
    p.add_argument("--warmup-batches", type=int, default=50)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--daemon", action="store_true",
                   help="after training, run as a file-watching daemon")
    p.add_argument("--daemon-watch-dir", type=str, default="daemon_inbox")
    p.add_argument("--daemon-log", type=str, default="sovereign_daemon.log")
    p.add_argument("--daemon-poll", type=float, default=2.0)
    p.add_argument("--ckpt", type=str, default="sovereign_v11_hardened.pth")
    args = p.parse_args()

    torch.manual_seed(args.seed)
    print("=" * 82)
    print("SOVEREIGN v11")
    print(f"  sanitizer z_cut={args.sanitizer_z_cut}  warmup_batches={args.warmup_batches}")
    print(f"  steps={args.steps}  batch={args.batch_size}  lr={args.lr}  seed={args.seed}")
    print("=" * 82)

    X, Y, U, perms, dirs = make_walk_data(1200, 5, INPUT_DIM, 4, 3, 43)
    n_total = X.shape[1]
    n_val = int(n_total * 0.3)
    split = torch.randperm(n_total, generator=torch.Generator().manual_seed(7))
    tr_idx, va_idx = split[n_val:], split[:n_val]
    X_tr, Y_tr, U_tr = X[:, tr_idx], Y[tr_idx], U[tr_idx]
    X_va, Y_va, U_va = X[:, va_idx], Y[va_idx], U[va_idx]
    print(f"\n[+] data: train={X_tr.shape[1]}  val={X_va.shape[1]}  seq_len={X.shape[0]}")

    core = HybridCore(INPUT_DIM, 96, 8, 6, 4).to(DTYPE)
    film = FocusFiLM(N_FOCUS, 96)
    sanitizer = InputSanitizer(INPUT_DIM,
                               z_cut=args.sanitizer_z_cut,
                               warmup_batches=args.warmup_batches)
    engine = SovereignEngine(core, film, INPUT_DIM, gru_hidden=64, sanitizer=sanitizer)

    opt = torch.optim.AdamW(engine.parameters(), lr=args.lr, weight_decay=1e-3)
    lossf = nn.CrossEntropyLoss(label_smoothing=0.1)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=args.lr, total_steps=args.steps,
        pct_start=0.2, anneal_strategy="cos",
    )

    print("\n[+] training...")
    best_acc = 0.0
    best_state = None
    N_tr = X_tr.shape[1]

    for step in range(1, args.steps + 1):
        engine.train()
        # sample WITHOUT replacement — randint would repeat examples in a batch
        idx = torch.randperm(N_tr)[:args.batch_size]
        xb, yb, ub = X_tr[:, idx], Y_tr[idx], U_tr[idx]

        logits, _rate = engine(xb, ub)  # not .item()'d — no sync
        loss = lossf(logits, yb)

        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(engine.parameters(), 1.0)
        opt.step()
        sched.step()

        if step % 25 == 0 or step == 1:
            va, vrate = evaluate(engine, X_va, Y_va, U_va)
            if va > best_acc:
                best_acc = va
                best_state = {k: v.detach().clone() for k, v in engine.state_dict().items()}
            print(f"Step {step:>3} | lr {sched.get_last_lr()[0]:.2e} | "
                  f"tr_loss {loss.item():.4f} | va_acc {va:.3f} | "
                  f"anomaly {vrate:.4f} | best {best_acc:.3f}")

    if best_state is not None:
        engine.load_state_dict(best_state)
    torch.save(best_state if best_state is not None else engine.state_dict(), args.ckpt)
    print(f"\n[+] saved {args.ckpt}  (best va_acc {best_acc:.3f})")

    perturbation_test(engine, X_va, Y_va, U_va)

    if args.daemon:
        d = Daemon(engine,
                   Path(args.daemon_watch_dir),
                   Path(args.daemon_log),
                   poll_s=args.daemon_poll)
        d.run()
    else:
        print("\n(tip: --daemon watches a folder for .pt files with {x, focus_ids})")


if __name__ == "__main__":
    main()
