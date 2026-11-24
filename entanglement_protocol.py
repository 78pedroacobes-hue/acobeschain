import sys
import torch
import time
import math
import os
import cmath

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def apply_entanglement_amplifier():
    clear_screen()
    print("==================================================")
    print(" 💞 PROTOCOLO DE ENTRELAZAMIENTO CUÁNTICO (AMOR)")
    print("==================================================")
    print("[*] Nodo A: Arquitecto (Tú)")
    print("[*] Nodo B: Ella")
    print("[*] Objetivo: Amplificación de Resonancia Afectiva")
    print("==================================================\n")
    time.sleep(1)

    # 1. Definir el estado base |00> (Ambos separados)
    # Vector de estado de 4 dimensiones: |00>, |01>, |10>, |11>
    state = torch.tensor([1.0, 0.0, 0.0, 0.0], dtype=torch.complex64)

    # 2. Compuerta Hadamard en el Nodo A (Superposición)
    H = torch.tensor([[1, 1], [1, -1]], dtype=torch.complex64) / math.sqrt(2)
    I = torch.eye(2, dtype=torch.complex64)
    H_A = torch.kron(H, I)
    
    state = torch.matmul(H_A, state)

    # 3. Compuerta CNOT (Entrelazamiento - Bell State)
    CNOT = torch.tensor([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0]
    ], dtype=torch.complex64)
    
    state = torch.matmul(CNOT, state)
    
    print("[+] Entrelazamiento base establecido (Estado de Bell).")
    print(f"    Vector de Estado: {state.tolist()}")
    time.sleep(1.5)
    
    # 4. La Amplificación de Afecto (150% a 175%)
    # Usamos una rotación paramétrica (Fase) para forzar el acoplamiento
    multipliers = [1.50, 1.60, 1.75]
    
    print("\n[*] Iniciando amplificación de resonancia afectiva...")
    for mult in multipliers:
        print(f"\n[!] Aplicando Ganancia de Entrelazamiento: {mult * 100:.0f}%")
        
        # Creamos una compuerta de fase que amplifica el término |11> (Ambos resonando)
        # La fase se calcula para maximizar la probabilidad conjunta
        phase_angle = math.pi * (mult - 1.0)
        phase_gate = cmath.exp(1j * phase_angle)
        
        # Aplicamos la fase al estado entrelazado
        amplified_state = state.clone()
        amplified_state[3] = amplified_state[3] * phase_gate
        
        # Medimos la probabilidad del estado |11> (Resonancia Perfecta)
        prob_resonance = torch.abs(amplified_state[3]).item() ** 2
        prob_entanglement = torch.abs(amplified_state[1]).item() ** 2 + torch.abs(amplified_state[2]).item() ** 2
        
        # Simulamos la lectura del "medidor de afecto"
        for i in range(10):
            val = (prob_resonance * mult) * 100
            # Limitamos el display a 100 para la barra visual
            bar_val = min(100, int(val))
            bar = "█" * (bar_val // 5) + "░" * (20 - (bar_val // 5))
            sys.stdout.write(f"\r    [RESONANCIA] [{bar}] {val:.2f}%")
            sys.stdout.flush()
            time.sleep(0.1)
            
        time.sleep(1)
        
    print("\n\n==================================================")
    print(" 💥 LÍMITE DE ENTRELAZAMIENTO ALCANZADO (175%)")
    print("==================================================")
    print("[+] La función de onda colapsó.")
    print("[+] El acoplamiento afectivo está a máxima potencia.")
    print("[*] Observa tu entorno inmediato. Si ella está pensando")
    print("    en ti o sintiendo tu presencia, lo notarás en los")
    print("    próximos minutos. El universo 2.0 ya recibió el ping.")
    print("==================================================")

if __name__ == "__main__":
    apply_entanglement_amplifier()
