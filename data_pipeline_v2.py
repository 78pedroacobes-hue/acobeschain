import torch
import time

# =====================================================================
# PIPELINE DE OBSERVACIÓN V2 (AUDITADO)
# =====================================================================

# CONFIGURACIÓN: True = Datos simulados (Pruebas) | False = APIs Reales
MOCK_DATA = True 

# Definimos las 6 dimensiones (Separamos Privacidad de Oportunidad)
DIMENSIONS = ["Riqueza", "Vitalidad", "Sincronía", "Flujo", "Privacidad", "Oportunidad"]

# 1. TU OBJETIVO (Target Vector)
# Ahora son 6 dimensiones. Alta privacidad (0.95), alta oportunidad (0.90).
TARGET_VECTOR = torch.tensor([0.95, 0.99, 0.90, 0.95, 0.95, 0.90])

def get_observations():
    """
    Obtiene los datos actuales.
    Si MOCK_DATA es True, usa valores claramente etiquetados como ficticios.
    Si es False, aquí irían las llamadas a APIs (Web3, Termux API, etc.)
    """
    if MOCK_DATA:
        print("[!] MODO PRUEBA ACTIVADO: Usando datos simulados (MOCK_DATA).")
        print("    (Los valores a continuación NO son una evaluación de tu vida real).")
        # Datos simulados
        current = torch.tensor([
            0.65,  # Riqueza
            0.85,  # Vitalidad
            0.50,  # Sincronía
            0.40,  # Flujo
            0.20,  # Privacidad (Baja privacidad actualmente)
            0.75   # Oportunidad (Oportunidades moderadas)
        ])
    else:
        print("[*] MODO REAL: Conectando a APIs... (No implementado aún)")
        # Aquí irían las llamadas reales (ej. web3.eth.get_balance, etc.)
        current = torch.zeros(6) 
        
    return current

def calculate_delta(current_state):
    """
    Calcula la distancia euclidiana (L2) entre el estado actual y el objetivo.
    """
    # Delta por dimensión (valor absoluto de la diferencia)
    dimension_gaps = torch.abs(TARGET_VECTOR - current_state)
    
    # Fricción total (Norma L2 / Distancia Euclidiana)
    total_friction = torch.norm(dimension_gaps, p=2).item()
    
    return dimension_gaps, total_friction

if __name__ == "__main__":
    print("==================================================")
    print(" 📡 PIPELINE DE OBSERVACIÓN V2 (AUDITADO)")
    print("==================================================")
    
    # 1. Obtener estado actual (Realidad)
    current_state = get_observations()
    
    # 2. Calcular la brecha (Delta)
    gaps, total_friction = calculate_delta(current_state)
    
    # 3. Mostrar resultados de forma transparente
    print("\n[*] Comparativa de Dimensiones (0.0 a 1.0):")
    print(f"    {'DIMENSIÓN':<12} | {'REALIDAD':<10} | {'OBJETIVO':<10} | {'BRECHA (Delta)'}")
    print("-" * 60)
    
    for i in range(len(DIMENSIONS)):
        print(f"    {DIMENSIONS[i]:<12} | {current_state[i].item():.2f}       | {TARGET_VECTOR[i].item():.2f}       | -{gaps[i].item():.2f}")
        
    print("-" * 60)
    print(f"[*] Fricción Total (Distancia Euclidiana L2): {total_friction:.4f}")
    print("    (Nota: 0.0 = Alineación perfecta, > 2.0 = Alta fricción)")
    print("==================================================")
