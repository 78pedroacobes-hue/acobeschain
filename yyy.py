"""silver_in_9_11.py -- The Sovereign v11 Architecture with Tachyon Shielding."""
from __future__ import annotations
import torch, pennylane as qml
import torch.nn as nn, torch.nn.functional as F
from torch.nn.utils.parametrizations import spectral_norm

DTYPE, N_FOCUS = torch.float32, 8

class SwiGLU(nn.Module):
    def __init__(self, i, o):
        super().__init__()
        self.w1, self.w2 = nn.Linear(i, o), spectral_norm(nn.Linear(i, o))
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
            iy, iz = inputs[:, :n_qubits], inputs[:, n_qubits:]
            for i in range(n_layers):
                qml.AngleEmbedding(iy, wires=range(n_qubits), rotation="Y")
                qml.AngleEmbedding(iz, wires=range(n_qubits), rotation="Z")
                qml.StronglyEntanglingLayers(weights[:, i:i+1], wires=range(n_qubits))
            return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
        self.circuit = circuit
    def forward(self, x, w): return torch.stack(self.circuit(x.to(DTYPE), w.to(DTYPE)), dim=-1)

class QWeightGen(nn.Module):
    def __init__(self, latent, n_layers, n_qubits):
        super().__init__()
        self.n_layers, self.n_qubits = n_layers, n_qubits
        t = n_layers * n_qubits * 3
        self.net = nn.Sequential(SwiGLU(latent, 256), nn.LayerNorm(256), SwiGLU(256, t), nn.LayerNorm(t))
    def forward(self, z): return (torch.tanh(self.net(z)) * torch.pi).view(-1, self.n_layers, self.n_qubits, 3)

class HealingSanitizer(nn.Module):
    def __init__(self, input_dim, z_cut=3.0, warmup_steps=50):
        super().__init__()
        self.z_cut, self.warmup_remaining = z_cut, warmup_steps
        self.register_buffer("running_median", torch.zeros(input_dim))
        self.register_buffer("running_mad", torch.ones(input_dim))
        self.register_buffer("frozen", torch.tensor(0))

    def _update_stats(self, x):
        if self.frozen.item() == 0 and self.warmup_remaining > 0:
            flat = x.detach().reshape(-1, x.shape[-1])
            bm = flat.median(dim=0).values
            bmad = (flat - bm).abs().median(dim=0).values.clamp_min(1e-6)
            self.running_median.mul_(0.95).add_(bm, alpha=0.05)
            self.running_mad.mul_(0.95).add_(bmad, alpha=0.05)
            self.warmup_remaining -= 1
            if self.warmup_remaining == 0: self.frozen.fill_(1)

    def forward(self, x):
        if self.training: self._update_stats(x)
        diff = x - self.running_median.view(1, 1, -1)
        z = diff.abs() / (self.running_mad * 1.4826 + 1e-6).view(1, 1, -1)
        mask = (z > self.z_cut).float()
        suppression = torch.exp(-0.5 * (z - self.z_cut).clamp(min=0.0))
        return self.running_median.view(1, 1, -1) + diff * suppression, mask.mean().item()

class TachyonAcausalProtection(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.f_proj, self.b_proj = nn.Linear(dim, dim), nn.Linear(dim, dim)
        self.meta_gate = nn.Sequential(nn.Linear(dim * 2, dim), nn.Tanh(), nn.Linear(dim, dim), nn.Sigmoid())
    def forward(self, x):
        T, B, D = x.shape
        psi_f = self.f_proj(x)
        idx_rev = torch.arange(T - 1, -1, -1, device=x.device)
        phi_b = self.b_proj(x.index_select(0, idx_rev)).index_select(0, idx_rev)
        t_gate = self.meta_gate(torch.cat([psi_f, phi_b], dim=-1))
        return t_gate * x + (1.0 - t_gate) * (psi_f * phi_b).tanh()

class HybridCore(nn.Module):
    def __init__(self, input_dim=16, hidden=96, n_qubits=8, n_layers=6, n_classes=4, dropout=0.15):
        super().__init__()
        self.encoder = nn.Sequential(SwiGLU(input_dim, hidden), nn.LayerNorm(hidden), nn.Dropout(dropout), SwiGLU(hidden, hidden), nn.LayerNorm(hidden))
        self.to_quantum = nn.Sequential(nn.Linear(hidden, n_qubits * 2), nn.LayerNorm(n_qubits * 2))
        self.q_engine = QuantumEngine(n_qubits, n_layers)
        self.q_weight_gen = QWeightGen(hidden, n_layers, n_qubits)
        self.q_proj = nn.Sequential(nn.Linear(n_qubits, hidden), nn.SiLU(), nn.Linear(hidden, hidden), nn.LayerNorm(hidden))
        self.fusion_gate = nn.Sequential(nn.Linear(hidden * 2, hidden), nn.Sigmoid())
        self.head = nn.Sequential(SwiGLU(hidden, hidden), nn.LayerNorm(hidden), nn.Dropout(dropout), nn.Linear(hidden, n_classes))

    def forward(self, h):
        q_in = torch.tanh(self.to_quantum(h)) * 2.0 * torch.pi
        q_w = self.q_weight_gen(h)
        qf = self.q_engine(q_in, q_w).to(h.dtype)
        q_up = self.q_proj(qf)
        g = self.fusion_gate(torch.cat([h, q_up], dim=-1))
        return self.head(g * h + (1.0 - g) * q_up)

class FocusFiLM(nn.Module):
    def __init__(self, n_focus, hidden):
        super().__init__()
        self.emb = nn.Embedding(n_focus, hidden)
        self.to_gain, self.to_bias = nn.Linear(hidden, hidden), nn.Linear(hidden, hidden)
        nn.init.normal_(self.to_gain.weight, std=0.02); nn.init.zeros_(self.to_gain.bias)
        nn.init.zeros_(self.to_bias.weight); nn.init.zeros_(self.to_bias.bias)
    def forward(self, h, fid):
        e = self.emb(fid)
        return h * (1.0 + torch.tanh(self.to_gain(e))) + self.to_bias(e)

class SovereignEngine(nn.Module):
    def __init__(self, core, film, input_dim, gru_hidden=64, gru_layers=1, sanitizer=None):
        super().__init__()
        self.core, self.film = core, film
        self.sanitizer = sanitizer or HealingSanitizer(input_dim)
        self.tachyon_shield = TachyonAcausalProtection(dim=input_dim)
        self.gru = nn.GRU(input_dim, gru_hidden, num_layers=gru_layers, batch_first=False)
        self.attention = nn.MultiheadAttention(embed_dim=gru_hidden, num_heads=4, dropout=0.1)
        self.gru_proj = nn.Linear(gru_hidden, input_dim)
        self.residual_weight = nn.Parameter(torch.tensor(0.5))

    def forward(self, x, focus_ids):
        x = x.to(DTYPE)
        single = (x.dim() == 2)
        if single: x = x.unsqueeze(0)
        
        x_protected = self.tachyon_shield(x)
        x_s, anomaly_rate = self.sanitizer(x_protected)
        gru_out, _ = self.gru(x_s)
        attn_out, _ = self.attention(gru_out, gru_out, gru_out)
        proj = self.gru_proj(attn_out)
        w = torch.sigmoid(self.residual_weight)
        mixed = w * x_s + (1.0 - w) * proj

        T, B, D = mixed.shape
        flat = mixed.reshape(T * B, D)
        h = self.film(self.core.encoder(flat), focus_ids.repeat(T))
        out = self.core(h).view(T, B, -1)
        return out.squeeze(0) if single else out

if __name__ == "__main__":
    print("Initializing Sovereign v11...")
    core = HybridCore(input_dim=16, hidden=96, n_qubits=8, n_layers=4)
    film = FocusFiLM(n_focus=N_FOCUS, hidden=96)
    engine = SovereignEngine(core, film, input_dim=16)
    try:
        engine.gru = torch.compile(engine.gru)
        engine.attention = torch.compile(engine.attention)
        print("Compiled classical layers.")
    except Exception: pass
    t_in, t_f = torch.randn(10, 2, 16), torch.zeros(2, dtype=torch.long)
    print(f"System Ready. Test shape out: {engine(t_in, t_f).shape}")

