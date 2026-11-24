import argparse
import os
import sys
import time
import torch

def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def build_bitflip_ops() -> list[torch.Tensor]:
    eye2 = torch.eye(2, dtype=torch.complex64)
    x_gate = torch.tensor([[0.0, 1.0], [1.0, 0.0]], dtype=torch.complex64)
    return [
        torch.kron(torch.kron(x_gate, eye2), eye2),
        torch.kron(torch.kron(eye2, x_gate), eye2),
        torch.kron(torch.kron(eye2, eye2), x_gate),
    ]

def simulate_matrix_interference(
    state: torch.Tensor,
    ops: list[torch.Tensor],
    error_prob: float = 0.5,
) -> tuple[torch.Tensor, list[int]]:
    noisy_state = state.clone()
    flipped_qubits: list[int] = []

    for qubit_idx, op in enumerate(ops):
        if torch.rand(1).item() < error_prob:
            noisy_state = torch.matmul(op, noisy_state)
            flipped_qubits.append(qubit_idx)

    return noisy_state, flipped_qubits

def recover_state(noisy_state: torch.Tensor, ops: list[torch.Tensor], flipped_qubits: list[int]) -> torch.Tensor:
    restored = noisy_state.clone()
    for qubit_idx in flipped_qubits:
        restored = torch.matmul(ops[qubit_idx], restored)
    return restored
