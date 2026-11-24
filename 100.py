import numpy as np
import json
import time
from multiprocessing import Pool, cpu_count

# Configuración del espacio de 100 parámetros
NUM_OPERATORS = 10000  # Ajustable según potencia de cómputo
NUM_PARAMS = 100
N_QUBITS = 6  # Dimensión del espacio de Hilbert (2^6 = 64)
DIM = 2 ** N_QUBITS

print(f"Iniciando barrido de ensemble: {NUM_OPERATORS} operadores, {NUM_PARAMS} parámetros, dimensión Hilbert = {DIM}")

def generate_operator(args):
    op_id, seed = args
    np.random.seed(seed)
    
    # Generación de un operador hermitiano aleatorio con 100 grados de libertad (parámetros de control)
    params = np.random.uniform(-np.pi, np.pi, NUM_PARAMS)
    
    # Construcción del hamiltoniano/operador acoplando los 100 parámetros
    # Usamos matrices de Pauli aleatorias o generadores de Lie como base
    H = np.zeros((DIM, DIM), dtype=complex)
    for i, p in enumerate(params):
        # Base de operadores locales/correlacionados modulados por el parámetro p_i
        basis_idx = i % 3
        if basis_idx == 0:
            mat = np.random.randn(DIM, DIM) + 1j * np.random.randn(DIM, DIM)
            mat = (mat + mat.conj().T) / 2
        elif basis_idx == 1:
            mat = np.diag(np.linspace(-1, 1, DIM)) * np.cos(p)
        else:
            mat = np.roll(np.eye(DIM), shift=(i % DIM), axis=1)
            mat = (mat + mat.conj().T) / 2
        
        H += p * mat / np.linalg.norm(mat, ord=2)
        
    # Diagonalización y cálculo de métricas clave (IPR, OTOC proxy, Pureza, etc.)
    evals, evecs = np.linalg.eigh(H)
    
    # Inverse Participation Ratio (IPR) promedio
    ipr = np.sum(np.abs(evecs)**4, axis=0)
    ipr_mean = float(np.mean(ipr))
    ipr_max = float(np.max(ipr))
    
    # Entropía espectral y traza
    p_spec = np.abs(evals) / np.sum(np.abs(evals))
    spectral_entropy = float(-np.sum(p_spec * np.log(p_spec + 1e-12)))
    
    return {
        "op_id": op_id,
        "params_norm": float(np.linalg.norm(params)),
        "ipr_mean": ipr_mean,
        "ipr_max": ipr_max,
        "spectral_entropy": spectral_entropy,
        "ground_energy": float(evals[0])
    }

if __name__ == "__main__":
    start_time = time.time()
    num_processes = min(cpu_count(), 8)
    
    tasks = [(i, i * 42 + 7) for i in range(NUM_OPERATORS)]
    
    print(f"Ejecutando en {num_processes} procesos...")
    results = []
    
    with Pool(num_processes) as pool:
        for i, res in enumerate(pool.imap_unordered(generate_operator, tasks), 1):
            results.append(res)
            if i % 1000 == 0 or i == NUM_OPERATORS:
                elapsed = time.time() - start_time
                eta = (elapsed / i) * (NUM_OPERATORS - i)
                print(f"  {i}/{NUM_OPERATORS}  ({elapsed:.0f}s, ETA {eta:.0f}s)")

    # Guardar resultados en JSON
    output_filename = "uog_100_params_result.json"
    with open(output_filename, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Completado en {time.time() - start_time:.1f}s. Guardado: {output_filename}")
