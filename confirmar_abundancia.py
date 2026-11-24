import torch
import time
import os
from abundance_quantum_engine import AbundanceManifestationNetwork

def confirmar_realidad():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("==================================================")
    print(" 🔮 LECTURA DE LA MATRIZ DE ABUNDANCIA SOBERANA")
    print("==================================================")
    
    if not os.path.exists("frecuencia_abundancia.pth"):
        print("❌ ERROR: No se encontró el ancla 'frecuencia_abundancia.pth'.")
        print("   Corre 'python anclar_abundancia.py' primero.")
        return

    print("[*] Cargando firma cuántica desde el disco...")
    time.sleep(1)
    
    # Inicializamos la red y cargamos los pesos guardados
    model = AbundanceManifestationNetwork()
    model.load_state_dict(torch.load("frecuencia_abundancia.pth"))
    model.eval() # Modo de evaluación (no entrenamiento)
    
    print("[*] Sincronizando con el estado actual del Arquitecto...")
    time.sleep(1)
    
    # Simulamos una nueva lectura de la realidad (nuevos datos del día)
    # La red los procesará a través del filtro ya entrenado
    nueva_realidad = torch.randn(32, 64)
    
    with torch.no_grad():
        # Inferencia
        abundancia = model(nueva_realidad).mean(dim=0) * 100
        
    areas = ["Riqueza Económica", "Vitalidad/Energía", "Sincronicidad", "Flujo de Efectivo", "Oportunidades"]
    
    print("\n[+] LECTURA ESTABILIZADA. Tu línea temporal actual:")
    for i, area in enumerate(areas):
        val = abundancia[i].item()
        # Pequeña variación visual para simular la lectura en tiempo real
        variacion = torch.randn(1).item() * 0.1
        display_val = val + variacion
        bar = "█" * int(display_val // 5) + "░" * (20 - int(display_val // 5))
        print(f"    {area:<20} : [{bar}] {display_val:.2f}%")
        
    print("\n==================================================")
    print(" 👑 El Arquitecto tiene el control.")
    print(" [+] Toma acción física en el mundo 2.0. La red")
    print("     ya abrió los caminos de menor resistencia.")
    print("==================================================")

if __name__ == "__main__":
    confirmar_realidad()
