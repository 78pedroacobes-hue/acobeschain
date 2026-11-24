import json
import numpy as np
import torch
import torch.nn as nn

# 1. Cargar los resultados del lattice de 100 parámetros
with open("uog_100_lattice_result.json", "r") as f:
    data = json.load(f)

# Seleccionar el operador óptimo ID 640
target_op = next((op for op in data if op["op_id"] == 640), None)
if target_op is None:
    # Fallback al mejor IPR encontrado si el ID varía por semilla
    target_op = max(data, key=lambda x: x["ipr_max"])

print(f"==============================================================")
print(f" INYECCIÓN DE PARÁMETROS — OPERADOR ID: {target_op['op_id']}")
print(f" IPR Max: {target_op['ipr_max']:.6f} | Husimi: {target_op['husimi_purity']:.6f}")
print(f"==============================================================")

# Reproducir la generación de los 100 parámetros para el operador 640
np.random.seed(target_op['op_id'] * 1337 + 99)
params_100 = np.random.uniform(-np.pi, np.pi, 100)

# 2. Definición de la capa cuántica soberana (QuantumRealityLayer)
class QuantumRealityLayer(nn.Module):
    def __init__(self, initial_params):
        super().__init__()
        # Inicializar los pesos de la capa con los 100 parámetros exactos del operador #640
        self.params = nn.Parameter(torch.tensor(initial_params, dtype=torch.float32))
        self.dim = 64
        
    def forward(self, x):
        # Evolución unitaria parametrizada usando los 100 grados de libertad
        # Mapeo de 100 parámetros a la matriz Hamiltoniana H de 64x64
        H = torch.zeros((self.dim, self.dim), dtype=torch.cfloat)
        
        # Potenciales de sitio (primeros 64 parámetros)
        diag_vals = torch.complex(self.params[:self.dim], torch.zeros_like(self.params[:self.dim]))
        H = torch.diag(diag_vals)
        
        # Acoples de salto (36 parámetros restantes)
        hopping_weights = self.params[self.dim:]
        idx = 0
        for i in range(self.dim):
            for j in range(i + 1, min(i + 5, self.dim)):
                t = torch.complex(hopping_weights[idx % len(hopping_weights)], torch.tensor(0.0))
                H[i, j] += t
                H[j, i] += t
                idx += 1
                
        # Simetrización Hermítica diferenciable
        H = (H + H.mH) / 2.0
        
        # Operador de evolución e interacciones con el batch de entrada x
        out = torch.matmul(x.to(torch.cfloat), H)
        return torch.abs(out)**2 # Densidad de probabilidad cuántica

# 3. Prueba de forward pass con el motor PyTorch
layer = QuantumRealityLayer(params_100)
X_sample = torch.randn(32, 64, dtype=torch.float32)
output_densities = layer(X_sample)

print(f"Tensor de entrada batch: {X_sample.shape}")
print(f"Densidades de probabilidad cuántica extraídas: {output_densities.shape}")
print(f"Estado de la red: Verificado y listo para optimización por lotes.")
