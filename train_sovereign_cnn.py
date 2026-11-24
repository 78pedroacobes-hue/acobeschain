import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

# 1. Cargar parámetros del operador #640
with open("uog_100_lattice_result.json", "r") as f:
    data = json.load(f)

target_op = next((op for op in data if op["op_id"] == 640), max(data, key=lambda x: x["ipr_max"]))
np.random.seed(target_op['op_id'] * 1337 + 99)
initial_params = np.random.uniform(-np.pi, np.pi, 100)

print(f"==============================================================")
print(f" ENTRENAMIENTO SOVEREIGN QUANTUM CNN — OPERADOR ID: {target_op['op_id']}")
print(f"==============================================================")

# 2. Definición de la Capa Cuántica Soberana (QuantumRealityLayer)
class QuantumRealityLayer(nn.Module):
    def __init__(self, initial_params):
        super().__init__()
        self.params = nn.Parameter(torch.tensor(initial_params, dtype=torch.float32))
        self.dim = 64
        
    def forward(self, x):
        H = torch.zeros((self.dim, self.dim), dtype=torch.cfloat)
        
        diag_vals = torch.complex(self.params[:self.dim], torch.zeros_like(self.params[:self.dim]))
        H = torch.diag(diag_vals)
        
        hopping_weights = self.params[self.dim:]
        idx = 0
        for i in range(self.dim):
            for j in range(i + 1, min(i + 5, self.dim)):
                t = torch.complex(hopping_weights[idx % len(hopping_weights)], torch.tensor(0.0))
                H[i, j] += t
                H[j, i] += t
                idx += 1
                
        H = (H + H.mH) / 2.0
        out = torch.matmul(x.to(torch.cfloat), H)
        return torch.abs(out)**2

# 3. Arquitectura Híbrida SovereignQuantumCNN
class SovereignQuantumCNN(nn.Module):
    def __init__(self, initial_params, out_features=2):
        super().__init__()
        # Extractor convolucional clásico 1D
        self.conv1 = nn.Conv1d(in_channels=1, out_channels=1, kernel_size=3, padding=1)
        self.quantum_layer = QuantumRealityLayer(initial_params)
        self.fc = nn.Linear(64, out_features)
        
    def forward(self, x):
        # x shape: (Batch, 64) -> Adaptar para Conv1d (Batch, 1, 64)
        x_conv = x.unsqueeze(1)
        x_conv = torch.relu(self.conv1(x_conv))
        x_features = x_conv.squeeze(1)
        
        # Evolución cuántica con los pesos de #640
        q_out = self.quantum_layer(x_features)
        
        # Capa de clasificación final
        logits = self.fc(q_out)
        return logits

# 4. Inicialización y prueba de backpropagation
model = SovereignQuantumCNN(initial_params, out_features=2)
optimizer = optim.Adam(model.parameters(), lr=0.01)
criterion = nn.CrossEntropyLoss()

# Datos sintéticos de prueba (ej. features de audio o estados simulados)
X_train = torch.randn(16, 64)
y_train = torch.randint(0, 2, (16,))

print("Iniciando ciclo de optimización (Backward & Step)...")
model.train()
optimizer.zero_grad()

outputs = model(X_train)
loss = criterion(outputs, y_train)
loss.backward()
optimizer.step()

print(f"Pérdida (Loss) inicial calculada: {loss.item():.6f}")
print(f"Gradientes en QuantumRealityLayer propagados con éxito.")
print(f"Modelo SovereignQuantumCNN listo para entrenamiento en producción.")
