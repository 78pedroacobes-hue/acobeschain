import torch
from abundance_quantum_engine import AbundanceManifestationNetwork

def anclar():
    print("[*] Extrayendo la Matriz de Abundancia...")
    model = AbundanceManifestationNetwork()
    
    # Simulamos el entrenamiento rápido para obtener los pesos perfectos
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.01)
    X = torch.randn(32, 64)
    target = torch.ones(32, 5)
    
    for _ in range(100):
        optimizer.zero_grad()
        out = model(X)
        loss = torch.nn.functional.mse_loss(out, target)
        loss.backward()
        optimizer.step()
        
    # Guardamos los pesos en el disco físico
    torch.save(model.state_dict(), "frecuencia_abundancia.pth")
    print("[+] ✅ Matriz de Abundancia guardada en: frecuencia_abundancia.pth")
    print("[+] Esta es tu firma cuántica de riqueza. No la borres.")

if __name__ == "__main__":
    anclar()
