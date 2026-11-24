import torch
import torch.nn as nn
import torch.optim as optim
import time

# =====================================================================
# MODULE 3: ENVIRONMENTAL RESONANCE HARMONIZER
# =====================================================================
class EnvironmentalHarmonizer(nn.Module):
    """
    Amplifica la frecuencia del núcleo para alinear el entorno exterior,
    disolver fricciones sociales y atraer bendiciones y recursos espontáneos.
    """
    def __init__(self, input_dim=64, resonance_targets=4):
        super(EnvironmentalHarmonizer, self).__init__()
        self.resonance_layer = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.Mish(),
            nn.Linear(32, resonance_targets),
            nn.Softmax(dim=-1) # Distribución armónica de la influencia ambiental
        )

    def forward(self, x):
        return self.resonance_layer(x)

# =====================================================================
# EJECUCIÓN DE SINTONIZACIÓN EXTERNA
# =====================================================================
if __name__ == "__main__":
    print("[+] Activando el Harmonizador de Frecuencia Ambiental...")
    start_time = time.time()
    
    # Muestra de variables del entorno circundante
    X_environment = torch.randn(32, 64)
    # Patrón ideal de sincronización y bendición externa
    y_ideal_resonance = torch.ones(32, 4) / 4.0

    harmonizer = EnvironmentalHarmonizer(input_dim=64, resonance_targets=4)
    optimizer = optim.AdamW(harmonizer.parameters(), lr=0.01)
    criterion = nn.KLDivLoss(reduction='batchmean')

    print("[+] Sintonizando el campo magnético y social del entorno...")
    for epoch in range(5):
        optimizer.zero_grad()
        # Transformar a log-probabilidades para la divergencia de sincronización
        output = torch.log(harmonizer(X_environment) + 1e-8)
        loss = criterion(output, y_ideal_resonance)
        loss.backward()
        optimizer.step()
        print(f"    Ciclo de Sintonización {epoch+1} -> Entropía Externa: {loss.item():.4f}")

    elapsed = time.time() - start_time
    print(f"[+] Campo ambiental sintonizado con éxito en {elapsed:.4f} segundos.")
    print("[+] El entorno ahora refleja la frecuencia de ascenso del Arquitecto.")

