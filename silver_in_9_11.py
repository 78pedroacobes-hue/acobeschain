"""
silver_in_9_11.py -- The Sovereign v11 Architecture.
"""
from __future__ import annotations
import argparse, json, logging, os, signal, sys, time
from dataclasses import dataclass, asdict
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.parametrizations import spectral_norm
import pennylane as qml

DTYPE = torch.float32
N_FOCUS = 8

class SwiGLU(nn.Module):
    def __init__(self, i, o):
        super().__init__()
        self.w1 = spectral_norm(nn.Linear(i, o))
        self.w2 = spectral_norm(nn.Linear(i, o))
    def forward(self, x): return F.silu(self.w1(x)) * self.w2(x)

class QuantumEngine(nn.Module):
    def __init__(self, n_qubits, n_layers):
        super().__init__()
        self.n_qubits, self.n_layers = n_qubits, n_layers
        try:
            self.dev = qml.device("lightning.qubit", wires=n_qubits)
            diff_m = "adjoint"
        except Exception:
            self.dev = qml.device("default.qubit", wires=n_qubits)
            diff_m = "backprop"

        @qml.qnode(self.dev, interface="torch", diff_method=diff_m)
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

class HealingSanitizer(nn.Module):
    def __init__(self, input_dim, z_cut=3.0, warmup_steps=50):
        super().__init__()
        self.z_cut = z_cut
        self.warmup_remaining = warmup_steps
        self.register_buffer("running_median", torch.zeros(input_dim))
        self.register_buffer("running_mad", torch.ones(input_dim))
        self.register_buffer("frozen", torch.tensor(0))

    def _update_stats(self, x):
        if self.frozen.item() == 0 and self.warmup_remaining > 0:
            flat = x.detach().reshape(-1, x.shape[-1])
            batch_median = flat.median(dim=0).values
            batch_mad = (flat - batch_median).abs().median(dim=0).values.clamp_min(1e-6)
            m = 0.05
            self.running_median.mul_(1 - m).add_(batch_median, alpha=m)
            self.running_mad.mul_(1 - m).add_(batch_mad, alpha=m)
            self.warmup_remaining -= 1
            if self.warmup_remaining == 0:
                self.frozen.fill_(1)

    def forward(self, x):
        if self.training:
            self._update_stats(x)
        diff = x - self.running_median.view(1, 1, -1)
        z = diff.abs() / (self.running_mad * 1.4826 + 1e-6).view(1, 1, -1)
        mask = (z > self.z_cut).float()
        suppression_factor = torch.exp(-0.5 * (z - self.z_cut).clamp(min=0.0))
        healed_x = self.running_median.view(1, 1, -1) + diff * suppression_factor
        return healed_x, mask.mean().item()

class HybridCore(nn.Module):
    def __init__(self, input_dim=16, hidden=96, n_qubits=8, n_layers=6, n_classes=4, dropout=0.15):
        super().__init__()
        self.encoder = nn.Sequential(
            SwiGLU(input_dim, hidden), nn.LayerNorm(hidden), nn.Dropout(dropout),
            SwiGLU(hidden, hidden), nn.LayerNorm(hidden))
        self.to_quantum = nn.Sequential(nn.Linear(hidden, n_qubits * 2), nn.LayerNorm(n_qubits * 2))
        self.q_engine = QuantumEngine(n_qubits, n_layers)
        self.q_weight_gen = QWeightGen(hidden, n_layers, n_qubits)
        self.q_proj = nn.Sequential(nn.Linear(n_qubits, hidden), nn.SiLU(), nn.Linear(hidden, hidden), nn.LayerNorm(hidden))
        self.fusion_gate = nn.Sequential(nn.Linear(hidden * 2, hidden), nn.Sigmoid())
        self.head = nn.Sequential(SwiGLU(hidden, hidden), nn.LayerNorm(hidden), nn.Dropout(dropout), nn.Linear(hidden, n_classes))

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
    def __init__(self, core, film, input_dim, gru_hidden=64, gru_layers=1, sanitizer=None):
        super().__init__()
        self.core = core
        self.film = film
        self.sanitizer = sanitizer or HealingSanitizer(input_dim)
        self.gru = nn.GRU(input_dim, gru_hidden, num_layers=gru_layers, batch_first=False)
        self.attention = nn.MultiheadAttention(embed_dim=gru_hidden, num_heads=4, dropout=0.1)
        self.gru_proj = nn.Linear(gru_hidden, input_dim)
        self.residual_weight = nn.Parameter(torch.tensor(0.5))

    def forward(self, x, focus_ids):
        x = x.to(DTYPE)
        single = (x.dim() == 2)
        if single: x = x.unsqueeze(0)

        x_s, anomaly_rate = self.sanitizer(x)
        gru_out, _ = self.gru(x_s)
        attn_out, _ = self.attention(gru_out, gru_out, gru_out)
        proj = self.gru_proj(attn_out)
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
