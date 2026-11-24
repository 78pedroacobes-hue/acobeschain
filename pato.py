import pennylane as qml
import torch
import torch.nn as nn
import numpy as np

# Initialize Quantum Device (Default Qubit / Local Node Simulator)
dev = qml.device("default.qubit", wires=4)

@qml.qnode(dev, interface="torch", diff_method="parameter-shift")
def sovereign_quantum_circuit(inputs, weights):
    # Encoding Layer: Map input tensor features into rotation angles
    for i in range(4):
        qml.RY(inputs[i], wires=i)
    
    # Variational Core: Multi-layer entangling architecture
    qml.templates.StronglyEntanglingLayers(weights, wires=range(4))
    
    # Measurement expectation values across all qubits
    return [qml.expval(qml.PauliZ(i)) for i in range(4)]

class SovereignQNN(nn.Module):
    def __init__(self, n_layers=3):
        super().__init__()
        # Weight shape for StronglyEntanglingLayers: (n_layers, n_wires, 3)
        weight_shapes = {"weights": (n_layers, 4, 3)}
        self.qlayer = qml.qnn.TorchLayer(sovereign_quantum_circuit, weight_shapes)
        self.fc = nn.Linear(4, 1)

    def forward(self, x):
        x = self.qlayer(x)
        return torch.sigmoid(self.fc(x))

# Execution Test
if __name__ == "__main__":
    model = SovereignQNN(n_layers=3)
    sample_input = torch.tensor([0.5, -0.2, 0.8, 0.1], dtype=torch.float32)
    output = model(sample_input)
    print(f"[ * ] Sovereign QNN Node Initialized Successfully.")
    print(f"[ * ] Inference Output Tensor: {output.item():.6f}")

