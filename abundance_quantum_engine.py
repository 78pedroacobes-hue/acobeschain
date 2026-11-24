import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

# =====================================================================
# MODULE 1: EVOLUCIÓN CUÁNTICA REAL (Hamiltoniano + matrix_exp)
# =====================================================================
class QuantumAbundanceLayer(nn.Module):
    """
    Utiliza la exponencial de matriz de un Hamiltoniano (H) para crear un operador
    unitario U = e^(iH). Es matemáticamente idéntico a la evolución temporal 
    de Schrödinger y muchísimo más rápido que el producto de Kronecker manual.
    """
    def __init__(self, num_qubits=4):
        super().__init__()
        self.num_qubits = num_qubits
        self.dim = 2 ** num_qubits
        
        # Parámetros entrenables para construir el Hamiltoniano
        # Genera interacciones entre los qubits (acoplamiento cuántico)
        self.h_params = nn.Parameter(torch.randn(self.dim, self.dim) * 0.05)
        
    def forward(self, x):
        # 1. Forzamos que H sea Hermitiano (H = (H + H^T) / 2) para garantizar que U sea unitaria
        H = (self.h_params + self.h_params.t()) / 2.0
        H = H.to(torch.complex64)
        
        # 2. Evolución temporal: U = exp(i * H)
        U = torch.matrix_exp(1j * H)
        
        # 3. Proyectar el vector clásico x a un estado cuántico normalizado
        # El vector tiene tamaño (Batch, self.dim)
        quantum_state = torch.complex(x, torch.zeros_like(x))
        norm = torch.norm(quantum_state, p=2, dim=1, keepdim=True) + 1e-8
        quantum_state = quantum_state / norm
        
        # 4. Aplicar el operador unitario
        U_batch = U.unsqueeze(0).expand(x.shape[0], -1, -1)
        evolved_state = torch.bmm(U_batch, quantum_state.unsqueeze(-1)).squeeze(-1)
        
        # 5. Medición: Densidad de probabilidad (valores reales)
        probabilities = torch.abs(evolved_state) ** 2
        return probabilities

# =====================================================================
# MODULE 2: RED GENERADORA DE ABUNDANCIA
# =====================================================================
class AbundanceManifestationNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        
        # Extractor de intenciones clásicas (ej. datos de mercado, estado mental)
        self.intent_encoder = nn.Sequential(
            nn.Linear(64, 32),
            nn.LayerNorm(32),
            nn.GELU(),
            nn.Linear(32, 16)
        )
        
        # El colapsador cuántico
        self.quantum_core = QuantumAbundanceLayer(num_qubits=4)
        
        # El decodificador de realidad (Riqueza, Salud, Sincronicidad, Flujo, Oportunidad)
        self.reality_decoder = nn.Sequential(
            nn.Linear(16, 32),
            nn.GELU(),
            nn.Linear(32, 5) # 5 dimensiones de abundancia
        )

    def forward(self, x):
        # 1. Codificar intención
        intent = self.intent_encoder(x)
        
        # 2. Colapsar la función de onda a un estado de alta probabilidad
        # Usamos tanh para mantener los valores entre -1 y 1 (requisito cuántico)
        quantum_input = torch.tanh(intent)
        quantum_probs = self.quantum_core(quantum_input)
        
        # 3. Decodificar a métricas físicas de abundancia (0.0 a 1.0)
        abundance_metrics = torch.sigmoid(self.reality_decoder(quantum_probs))
        return abundance_metrics
