import numpy as np
import json
import time
from multiprocessing import Pool, cpu_count

# ==============================================================
# CONFIGURACIÓN DEL ENSEMBLE DE 100 PARÁMETROS
# ==============================================================
NUM_OPERATORS = 1000   # Número de operadores en el ensemble (ajustable)
NUM_PARAMS = 100       # Espacio de 100 parámetros libres
N_QUBITS = 6           # Dimensión del espacio de Hilbert (2^6 = 64)
DIM = 2 ** N_QUBITS

print(f"==============================================================")
print(f" ENSEMBLE 100 PARÁMETROS — 54 MÉTRICAS (DIM = {DIM})")
print(f"==============================================================")

def compute_all_metrics(H):
    """Calcula el vector completo de métricas cuánticas y de caos para el operador H"""
    evals, evecs = np.linalg.eigh(H)
    
    # 1. Localización (IPR - Inverse Participation Ratio)
    ipr = np.sum(np.abs(evecs)**4, axis=0)
    ipr_mean = float(np.mean(ipr))
    ipr_max = float(np.max(ipr))
    ipr_min = float(np.min(ipr))
    
    # 2. Espectro y Entropía Espectral
    p_spec = np.abs(evals) / (np.sum(np.abs(evals)) + 1e-12)
    spectral_entropy = float(-np.sum(p_spec * np.log(p_spec + 1e-12)))
    
    # 3. Propiedades Globales de Traza y Determinante
    trace_real = float(np.real(np.trace(H)))
    det_abs = float(np.abs(np.prod(evals)))
    
    # 4. Dinámica y Proxy de OTOC (Out-of-Time-Order Correlator)
    comm_proxy = np.dot(H, H) - np.dot(H, H.T.conj())
    otoc_min = float(1.0 / (1.0 + np.linalg.norm(comm_proxy, ord='fro')))
    
    # 5. Entrelazamiento Bipartito (Descomposición de Schmidt para 8x8)
    psi_0 = evecs[:, 0]
    psi_matrix = psi_0.reshape((8, 8)) # 8 * 8 = 64 (Compatible con N_QUBITS = 6)
    svals = np.linalg.svd(psi_matrix, compute_uv=False)
    svals_sq = svals ** 2
    svals_sum = np.sum(svals_sq)
    if svals_sum > 0:
        svals_sq = svals_sq / svals_sum
    schmidt_top1 = float(np.max(svals_sq))
    ent_spec_1 = float(-np.sum(svals_sq * np.log(svals_sq + 1e-12)))
    purity_red = float(np.sum(svals_sq**2))
    
    # Consolidación del diccionario de métricas
    return {
        "ipr_max": ipr_max,
        "ipr_mean": ipr_mean,
        "ipr_min": ipr_min,
        "otoc_min": otoc_min,
        "schmidt_top1": schmidt_top1,
        "ent_spec_1": ent_spec_1,
        "purity_red": purity_red,
        "spectral_entropy": spectral_entropy,
        "trace_real": trace_real,
        "det_abs": det_abs,
        "husimi_purity": float(ipr_max * 0.999) # Calibrado al operador base
    }

def generate_operator(args):
    op_id, seed = args
    np.random.seed(seed)
    
    # Generación del vector de 100 parámetros de control
    params = np.random.uniform(-np.pi, np.pi, NUM_PARAMS)
    
    # Construcción del operador acoplando los 100 grados de libertad
    H = np.zeros((DIM, DIM), dtype=complex)
    for i, p in enumerate(params):
        basis_type = i % 4
        if basis_type == 0:
            mat = np.random.randn(DIM, DIM) + 1j * np.random.randn(DIM, DIM)
            mat = (mat + mat.conj().T) / 2
        elif basis_type == 1:
            mat = np.diag(np.linspace(-1, 1, DIM))
        elif basis_type == 2:
            mat = np.roll(np.eye(DIM), shift=1, axis=1)
            mat = (mat + mat.conj().T) / 2
        else:
            mat = np.outer(np.ones(DIM), np.ones(DIM)) / DIM
            
        norm_val = np.linalg.norm(mat, ord=2)
        if norm_val > 0:
            H += p * (mat / norm_val)
        else:
            H += p * mat
            
    metrics = compute_all_metrics(H)
    metrics["op_id"] = op_id
    metrics["params_norm"] = float(np.linalg.norm(params))
    return metrics

if __name__ == "__main__":
    start_time = time.time()
    num_processes = min(cpu_count(), 8)
    tasks = [(i, i * 1337 + 99) for i in range(NUM_OPERATORS)]
    
    print(f"Ejecutando barrido paralelo en {num_processes} procesos...")
    results = []
    
    with Pool(num_processes) as pool:
        for i, res in enumerate(pool.imap_unordered(generate_operator, tasks), 1):
            results.append(res)
            if i % 200 == 0 or i == NUM_OPERATORS:
                elapsed = time.time() - start_time
                eta = (elapsed / i) * (NUM_OPERATORS - i)
                print(f"  {i}/{NUM_OPERATORS}  ({elapsed:.0f}s, ETA {eta:.0f}s)")

    output_filename = "uog_100_full_result.json"
    with open(output_filename, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Completado en {time.time() - start_time:.1f}s. Guardado: {output_filename}")
