import argparse
import math
import os
import sys
import time
import torch

def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def build_3q_hadamard() -> torch.Tensor:
    inv_sqrt2 = 1.0 / math.sqrt(2.0)
    h1 = torch.tensor([[1.0, 1.0], [1.0, -1.0]], dtype=torch.complex64) * inv_sqrt2
    return torch.kron(torch.kron(h1, h1), h1)
