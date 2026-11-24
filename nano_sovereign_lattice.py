import numpy as np
import json
import time
from multiprocessing import Pool, cpu_count

# ==============================================================
# ENSEMBLE SOBERANO DE 100 PARÁMETROS — RED LOCALIZADA (DIM = 64)
# ==============================================================
NUM_OPERATORS = 1000   
NUM_PARAMS = 100       
N_QUBITS = 6           
DIM = 2 ** N_QUBITS

print(f"==============================================================")
print(f" ENSEMBLE SOBERANO RED 100 PARÁMETROS — DIM = {DIM}")
print(f"==============================================================")

def compute_sovereign_metrics(H):
    """Calcula las métricas buscando la firma de hiper-localización y pureza"""
    evals, evecs = np.linalg.eigh(H)
    
    # 1. Localización (IPR)
    ipr = np.sum(np.abs(evecs)**4, axis=0)
    ipr_mean = float(np.mean(ipr))
    ipr_max = float(np.max(ipr))
    ipr_min = float(np.min(ipr))
    
    # 2. Espectro y Entropía Espectral
    p_spec = np.abs(evals) / (np.sum(np.abs(evals)) + 1e-12)
    spectral_entropy = float(-np.sum(p_spec * np.log(p_spec + 1e-12)))
    
    # 3. Propiedades Globales
    trace_real = float(np.real(np.trace(H)))
    det_abs = float(np.abs(np.prod(evals)))
    
    # 4. Proxy de OTOC
    comm_proxy = np.dot(H, H) - np.dot(H, H.T.conj())
    otoc_min = float(1.0 / (1.0 + np.linalg.norm(comm_proxy, ord='fro')))
    
    # 5. Entrelazamiento Bipartito (Schmidt 8x8)
    psi_0 = evecs[:, 0]
    psi_matrix = psi_0.reshape((8, 8))
    svals = np.linalg.svd(psi_matrix, compute_uv=False)
    svals_sq = svals ** 2
    svals_sum = np.sum(svals_sq)
    if svals_sum > 0:
        svals_sq = svals_sq / svals_sum
    schmidt_top1 = float(np.max(svals_sq))
    ent_spec_1 = float(-np.sum(svals_sq * np.log(svals_sq + 1e-12)))
    purity_red = float(np.sum(svals_sq**2))
    
    # Husimi purity escalado a la localización del estado fundamental
    husimi_purity = float(ipr_max)

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
        "husimi_purity": husimi_purity
    }

def generate_lattice_operator(args):
    op_id, seed = args
    np.random.seed(seed)
    
    # Vector de exactamente 100 parámetros
    params = np.random.uniform(-np.pi, np.pi, NUM_PARAMS)
    
    # Asignación física de los 100 parámetros:
    # - 64 parámetros para potenciales de sitio (desorden Anderson)
    # - 36 parámetros para acoples de salto (hoppings)
    site_potentials = params[:DIM]
    hopping_params = params[DIM:]
    
    H = np.zeros((DIM, DIM), dtype=complex)
    
    # 1. Potenciales en la diagonal (Desorden modulado por los 64 parámetros)
    np.fill_diagonal(H, site_potentials)
    
    # 2. Acoples fuera de diagonal usando los 36 parámetros restantes
    idx = 0
    for i in range(DIM):
        for j in range(i + 1, min(i + 5, DIM)): # Vecinos hasta distancia 4
            t = hopping_params[idx % len(hopping_params)]
            H[i, j] += t
            H[j, i] += t # Hermiticidad
            idx += 1
            
    # Asegurar simetría hermítica perfecta
    H = (H + H.conj().T) / 2.0
    
    metrics = compute_sovereign_metrics(H)
    metrics["op_id"] = op_id
    metrics["params_norm"] = float(np.linalg.norm(params))
    return metrics

if __name__ == "__main__":
    start_time = time.time()
    num_processes = min(cpu_count(), 8)
    tasks = [(i, i * 1337 + 99) for i in range(NUM_OPERATORS)]
    
    print(f"Ejecutando ensemble de red en {num_processes} procesos...")
    results = []
    
    with Pool(num_processes) as pool:
        for i, res in enumerate(pool.imap_unordered(generate_lattice_operator, tasks), 1):
            results.append(res)
            if i % 200 == 0 or i == NUM_OPERATORS:
                elapsed = time.time() - start_time
                eta = (elapsed / i) * (NUM_OPERATORS - i)
                print(f"  {i}/{NUM_OPERATORS}  ({elapsed:.0f}s, ETA {eta:.0f}s)")

    output_filename = "uog_100_lattice_result.json"
    with open(output_filename, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Completado en {time.time() - start_time:.1f}s. Guardado: {output_filename}")
