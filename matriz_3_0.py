#!/usr/bin/env python3
"""
MATRIZ 3.0 — Orquestador Central del Sandbox Soberano
"""
from __future__ import annotations
import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import torch
import torch.nn as nn

from reality_anchor import build_bitflip_ops, recover_state, simulate_matrix_interference
from silver_in_9_11 import DTYPE, FocusFiLM, HealingSanitizer, HybridCore, N_FOCUS, SovereignEngine
from sovereign_channel_lock import SovereignChannelLock
from timeline_compressor import build_3q_hadamard

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def run_timeline_stage(error_prob: float = 0.25) -> dict:
    state = torch.zeros(8, dtype=torch.complex64)
    state[0] = 1.0 + 0.0j
    h3 = build_3q_hadamard()
    superposed = torch.matmul(h3, state)
    phase_gate = torch.exp(torch.tensor(1j * math.pi * 45.0, dtype=torch.complex64))
    compressed = superposed.clone()
    compressed[7] = compressed[7] * phase_gate
    target = torch.zeros(8, dtype=torch.complex64)
    target[7] = 1.0 + 0.0j
    ops = build_bitflip_ops()
    noisy, flipped = simulate_matrix_interference(target, ops, error_prob=error_prob)
    anchored = recover_state(noisy, ops, flipped)
    return {
        "prob_111_compressed": round(float((compressed[7].abs() ** 2).item()), 4),
        "prob_111_noisy": round(float((noisy[7].abs() ** 2).item()), 4),
        "flipped_qubits": flipped,
        "prob_111_anchored": round(float((anchored[7].abs() ** 2).item()), 4),
    }

def run_hybrid_smoke(steps: int = 25, z_cut: float = 3.0, warmup: int = 10) -> dict:
    g = torch.Generator().manual_seed(42)
    x_seq = torch.randn(5, 32, 16, generator=g, dtype=DTYPE)
    y_lbl = torch.randint(0, 4, (32,), generator=g)
    focus_ids = torch.randint(0, N_FOCUS, (32,), generator=g)

    core = HybridCore(input_dim=16, hidden=96, n_qubits=8, n_layers=6, n_classes=4).to(DTYPE)
    film = FocusFiLM(N_FOCUS, 96)
    sanitizer = HealingSanitizer(input_dim=16, z_cut=z_cut, warmup_steps=warmup)
    engine = SovereignEngine(core, film, input_dim=16, gru_hidden=64, sanitizer=sanitizer)

    optimizer = torch.optim.AdamW(engine.parameters(), lr=2e-3, weight_decay=1e-3)
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    last_loss = 0.0
    last_rate = 0.0

    engine.train()
    for _ in range(steps):
        logits, rate = engine(x_seq, focus_ids)
        loss = criterion(logits, y_lbl)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(engine.parameters(), 1.0)
        optimizer.step()
        last_loss = float(loss.item())
        last_rate = float(rate)

    engine.eval()
    with torch.no_grad():
        eval_logits, eval_rate = engine(x_seq, focus_ids)
        acc = float((eval_logits.argmax(-1) == y_lbl).float().mean().item())

    return {
        "steps": steps,
        "final_loss": round(last_loss, 4),
        "train_anomaly_rate": round(last_rate, 4),
        "eval_anomaly_rate": round(float(eval_rate), 4),
        "batch_acc": round(acc, 4),
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="Matriz 3.0 Sandbox Runner")
    parser.add_argument("--steps", type=int, default=25)
    parser.add_argument("--error-prob", type=float, default=0.25)
    parser.add_argument("--out", type=str, default="logs/matriz_3_run.json")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    lock = SovereignChannelLock(channel_id="MATRIZ_3_CORE", log_dir=base_dir / "logs")
    gate_result = lock.intercept_request({"source": "matriz_3", "action": "status_check"})
    
    timeline_result = run_timeline_stage(error_prob=args.error_prob)
    hybrid_result = run_hybrid_smoke(steps=args.steps)

    report = {
        "matrix_version": "3.0",
        "timestamp": utc_now(),
        "channel_gate": gate_result,
        "timeline_qec": timeline_result,
        "hybrid_engine": hybrid_result,
    }

    out_path = base_dir / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("=== MATRIZ 3.0 EJECUTADA ===")
    print(json.dumps(report, indent=2))
    print(f"\n[+] Reporte guardado en: {out_path}")

if __name__ == "__main__":
    main()
