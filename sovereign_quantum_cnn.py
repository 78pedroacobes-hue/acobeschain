import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

# =====================================================================
# MODULE 1: SIMULATED QUANTUM LAYER (Entangled Acobes Unitary Operator)
# =====================================================================
class QuantumRealityLayer(nn.Module):
    """
    Capa cuántica parametrizada con rotaciones SU(2) estables y entrelazamiento
    circular (C-Phase) para maximizar la correlación entre estados del sistema.
    """
    def __init__(self, num_qubits=4, entanglement_layers=2):
        super().__init__()
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        self.entanglement_layers = entanglement_layers
        
        # Parámetros entrenables para múltiples capas variacionales
        self.theta = nn.Parameter(torch.randn(entanglement_layers, num_qubits, 3) * 0.05)
        
        # Registro de buffers para soporte automático de GPU/CPU (.to(device))
        self.register_buffer("I", torch.eye(2, dtype=torch.complex64))
        self.register_buffer("X", torch.tensor([[0, 1], [1, 0]], dtype=torch.complex64))
        self.register_buffer("Y", torch.tensor([[0, -1j], [1j, 0]], dtype=torch.complex64))
        self.register_buffer("Z", torch.tensor([[1, 0], [0, -1]], dtype=torch.complex64))
        
        # Pre-cálculo de matriz de entrelazamiento circular (CZ en anillo)
        self.register_buffer("entangler", self._build_ring_entangler())

    def _build_ring_entangler(self):
        """Construye una matriz unitaria fija de entrelazamiento en anillo."""
        E = torch.eye(self.dim, dtype=torch.complex64)
        for q in range(self.num_qubits):
            target = (q + 1) % self.num_qubits
            # Aplica fase -1 cuando ambos qubits (q y target) están en estado |1>
            for state_idx in range(self.dim):
                bit_q = (state_idx >> (self.num_qubits - 1 - q)) & 1
                bit_t = (state_idx >> (self.num_qubits - 1 - target)) & 1
                if bit_q == 1 and bit_t == 1:
                    E[state_idx, state_idx] *= -1.0
        return E

    def _construct_unitary(self):
        """Construye el operador unitario global U(theta) con entrelazamiento."""
        U_total = torch.eye(self.dim, dtype=torch.complex64, device=self.theta.device)
        
        for layer in range(self.entanglement_layers):
            U_layer = torch.tensor([[1.0 + 0j]], dtype=torch.complex64, device=self.theta.device)
            
            for i in range(self.num_qubits):
                params = self.theta[layer, i]
                # Norma estabilizada para evitar NaN en el gradiente cuando theta -> 0
                angle = torch.sqrt(torch.sum(params ** 2) + 1e-12)
                axis = params / angle
                
                pauli_comb = axis[0] * self.X + axis[1] * self.Y + axis[2] * self.Z
                R = torch.cos(angle) * self.I - 1j * torch.sin(angle) * pauli_comb
                U_layer = torch.kron(U_layer, R)
            
            # Combinar rotaciones locales con entrelazamiento colectivo
            U_total = self.entangler @ U_layer @ U_total
            
        return U_total

    def forward(self, x):
        # Proyección a estado complejo (parte real e imaginaria aprendida)
        real_part, imag_part = torch.chunk(x, 2, dim=-1)
        quantum_state = torch.complex(real_part, imag_part)
        
        # Normalización L2 segura en el espacio de Hilbert
        norm = torch.linalg.vector_norm(quantum_state, ord=2, dim=-1, keepdim=True).clamp(min=1e-8)
        quantum_state = quantum_state / norm
        
        # Evolución unitaria eficiente sin expansión de memoria por lote
        U = self._construct_unitary()
        transformed_state = torch.matmul(quantum_state, U.T)
        
        # Densidades de probabilidad (Regla de Born)
        return transformed_state.real ** 2 + transformed_state.imag ** 2


# =====================================================================
# MODULE 2: HIGH-DIMENSIONAL HYBRID QUANTUM-CLASSICAL CNN
# =====================================================================
class SovereignQuantumCNN(nn.Module):
    def __init__(self, input_length=64, num_qubits=4, out_features=2):
        super().__init__()
        self.num_qubits = num_qubits
        self.hilbert_dim = 2 ** num_qubits
        
        self.classical_features = nn.Sequential(
            nn.Conv1d(in_channels=1, out_channels=8, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm1d(8),
            nn.SiLU(),
            nn.Conv1d(8, 16, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm1d(16),
            nn.SiLU(),
            nn.AdaptiveAvgPool1d(4), # Asegura tamaño fijo independiente de input_length
            nn.Flatten()
        )
        
        # Puente denso: comprime las 64 características (16*4) en (2 * hilbert_dim)
        # para alimentar tanto la amplitud real como la fase imaginaria sin perder información
        self.hilbert_bridge = nn.Sequential(
            nn.Linear(16 * 4, self.hilbert_dim * 2),
            nn.LayerNorm(self.hilbert_dim * 2)
        )
        
        self.quantum_layer = QuantumRealityLayer(num_qubits=num_qubits, entanglement_layers=2)
        
        self.decoder = nn.Sequential(
            nn.Linear(self.hilbert_dim, 32),
            nn.GELU(),
            nn.Dropout(0.15),
            nn.Linear(32, out_features)
        )

    def forward(self, x):
        if x.ndim == 2:
            x = x.unsqueeze(1)
            
        features = self.classical_features(x)
        encoded_state = self.hilbert_bridge(features)
        quantum_probs = self.quantum_layer(encoded_state)
        return self.decoder(quantum_probs)


# =====================================================================
# PIPELINE EXECUTION & VERIFICATION
# =====================================================================
if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[+] Inicializando Red Convolucional Cuántica Híbrida en: {device}")
    
    X_sample = torch.randn(32, 64, device=device)
    y_sample = torch.randint(0, 2, (32,), device=device)

    model = SovereignQuantumCNN(input_length=64, num_qubits=4, out_features=2).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.005, weight_decay=0.01)

    # Forward Pass
    output = model(X_sample)
    loss = criterion(output, y_sample)
    print(f"[+] Pase hacia adelante exitoso. Pérdida Inicial: {loss.item():.4f}")
    
    # Backward Pass con Gradient Clipping para mayor estabilidad
    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()
    print("[+] Gradientes calculados, estabilizados y aplicados en el Espacio de Hilbert.")
