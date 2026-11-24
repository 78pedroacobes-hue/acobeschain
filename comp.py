import argparse
import os
import time


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def run_sovereign_override(
    num_qubits: int = 127,
    shots: int = 1024,
    fast: bool = False,
    do_clear: bool = True,
) -> None:
    s_med = 0.05 if fast else 1.5

    if do_clear and not fast:
        clear_screen()

    print("==================================================")
    print(" 🚀 SOVEREIGN IBM OVERRIDE (MASTER KEY PROTOCOL)")
    print("==================================================")
    print(" [*] Bypassing IBM Queue... Accessing Local Aer Engine")
    print(f" [*] Target Hardware: {num_qubits}-Qubit Mesh Emulation")
    print(" [*] Objective: Collapse the 48-hour manifestation")
    print("==================================================\n")
    time.sleep(s_med)

    try:
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator
    except ImportError as exc:
        raise ImportError(
            "Qiskit and qiskit-aer are required. Install them with: pip install qiskit qiskit-aer"
        ) from exc

    # Use matrix_product_state so 127-qubit linear entanglement stays tractable in memory
    try:
        simulator = AerSimulator(method="matrix_product_state")
        backend_mode = "matrix_product_state"
    except Exception:
        simulator = AerSimulator()
        backend_mode = "automatic"

    print(f"[+] Local Aer Engine initialized (method={backend_mode}).\n")
    time.sleep(s_med)

    qc = QuantumCircuit(num_qubits, num_qubits)

    print(f"[*] Applying Hadamard to all {num_qubits} qubits...")
    for i in range(num_qubits):
        qc.h(i)

    print(f"[*] Entangling the {num_qubits}-qubit Reality Mesh...")
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)

    qc.measure(range(num_qubits), range(num_qubits))
    print("[+] Circuit constructed and verified.\n")
    time.sleep(s_med)

    print(f"[*] Executing {shots} timeline collapses (Shots)...")
    job = simulator.run(qc, shots=shots)
    result = job.result()
    counts = result.get_counts()

    all_zeros = "0" * num_qubits
    all_ones = "1" * num_qubits

    prob_zeros = counts.get(all_zeros, 0) / shots
    prob_ones = counts.get(all_ones, 0) / shots
    total_coherence = prob_zeros + prob_ones

    print("\n==================================================")
    print(" 📊 OVERRIDE RESULTS")
    print("==================================================")
    print(f" Total Shots (Timelines processed): {shots}")
    print(f" State |000...0> (Collapse to baseline): {prob_zeros * 100:.2f}%")
    print(f" State |111...1> (Sovereign Manifestation): {prob_ones * 100:.2f}%")
    print(f" Total Coherence (Signal Purity): {total_coherence * 100:.2f}%")

    if total_coherence > 0.8:
        print("\n[+] ACCESS GRANTED. The Master Key worked.")
        print(f"    The {num_qubits}-qubit mesh is coherent.")
    else:
        print("\n[-] Coherence drop detected. Re-run the override to stabilize.")

    print("\n [!] ARCHITECT PROTOCOL:")
    print("     The access is confirmed. The reality is primed.")
    print("     Let the 48 hours unfold.")
    print("==================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--qubits", type=int, default=127, help="number of qubits in the mesh")
    parser.add_argument("--shots", type=int, default=1024, help="number of simulation shots")
    parser.add_argument("--fast", action="store_true", help="shorten delays")
    parser.add_argument("--no-clear", action="store_true", help="do not clear terminal")
    args = parser.parse_args()
    run_sovereign_override(
        num_qubits=args.qubits,
        shots=args.shots,
        fast=args.fast,
        do_clear=args.no_clear,
    )

