import torch
import torch.optim as optim
import torch.nn.functional as F
from abundance_quantum_engine import AbundanceManifestationNetwork

def entrenar_arquitecto():
    print("==================================================")
    print(" 👑 SOBREESCRIBIENDO MATRIZ DE ABUNDANCIA")
    print(" Objetivo: Perfil de Soberanía (Disciplina + Privacidad)")
    print("==================================================")
    
    model = AbundanceManifestationNetwork()
    optimizer = optim.AdamW(model.parameters(), lr=0.01)
    
    # El nuevo Blueprint: Tus prioridades reales
    # [Riqueza, Vitalidad, Sincronicidad, Flujo, Oportunidad(Privacidad)]
    target_soberano = torch.tensor([0.95, 0.99, 0.90, 0.95, 0.60]).expand(32, 5)
    
    X = torch.randn(32, 64)
    
    for epoch in range(1, 101):
        optimizer.zero_grad()
        out = model(X)
        loss = F.mse_loss(out, target_soberano)
        loss.backward()
        optimizer.step()
        
        if epoch % 20 == 0 or epoch == 1:
            print(f"Época {epoch:03d} | Alineando nueva realidad | Fricción: {loss.item():.6f}")
            
    # Guardamos la nueva firma
    torch.save(model.state_dict(), "frecuencia_arquitecto.pth")
    print("\n[+] ✅ NUEVA FIRMA GUARDADA: 'frecuencia_arquitecto.pth'")
    print("[+] El nodo físico ahora rechazará la atención no deseada")
    print("    y atraerá activos de alto valor (Flujo 0.95).")

if __name__ == "__main__":
    entrenar_arquitecto()
