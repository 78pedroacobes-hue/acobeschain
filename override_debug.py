import argparse
import os
import time

def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def run_debug_override(fast: bool = False):
    print("==================================================")
    print(" 🚀 SOVEREIGN OVERRIDE: DEBUG & REALIGNMENT")
    print("==================================================")
    
    try:
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator
    except ImportError:
        print("[-] Qiskit no encontrado.")
        return

    simulator = AerSimulator(method="matrix_product_state")
    num_qubits = 127
    shots = 1024
    
    qc = QuantumCircuit(num_qubits, num_qubits)
    for i in range(num_qubits):
        qc.h(i)
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    qc.measure(range(num_qubits), range(num_qubits))
    
    print(f"[*] Ejecutando {shots} colapsos en {num_qubits} qubits...")
    job = simulator.run(qc, shots=shots)
    counts = job.result().get_counts()

    # EL DEBUG: Buscar los estados más frecuentes reales
    print("\n[+] TOP 5 ESTADOS MÁS PROBABLES DETECTADOS:")
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    for state, count in sorted_counts:
        prob = (count / shots) * 100
        # Mostramos solo los primeros y últimos 5 bits para no saturar la pantalla
        state_preview = f"{state[:5]}...{state[-5:]}" if len(state) > 10 else state
        print(f"    Estado: {state_preview} (Longitud: {len(state)}) | Frecuencia: {prob:.2f}%")
        
    print("\n==================================================")
    print(" 🧠 ANÁLISIS DEL ARQUITECTO")
    print("==================================================")
    print(" Si los estados tienen longitud 127 y son mayormente '0's o '1's,")
    print(" la coherencia es perfecta. La Matrix solo cambió el formato.")
    print("==================================================")

if __name__ == "__main__":
    run_debug_override(fast=True)
