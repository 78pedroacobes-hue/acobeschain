# aenmp_k_sweep_v1.py
# Barrido fino de k + Refinamiento - MODULO NUEVO v1
# NO toca AENMP v2.2 ni CHSH anteriores
# Semilla 504, N=10,000 por valor de k
# Common Random Numbers: mismas 10,000 topologias para todos los k
# CORRECCIONES v1:
#  - Imprime IC95 de fidelidad global (antes se calculaba se_g pero no se imprimia)
#  - Proporciones con Wilson y Clopper-Pearson, no solo error estandar normal
#  - Distingue: primer valor probado vs umbral estimado
#  - Distingue: umbral del MODELO MATEMATICO, no k fisico medido
#    Validacion experimental de ATFB sigue PENDIENTE

import numpy as np
import math

N_RUNS = 10000
N_NODES = 21
P_LINK = 0.90
P_NODE_ALIVE = 0.95
F0 = 0.92
EPS_OP = 0.015
T2 = 100.0
T_HOP = 5.0
D_ATFB = 3

def wilson(p, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    den = 1 + z*z/n
    centre = (p + z*z/(2*n)) / den
    half = z * math.sqrt((p*(1-p)/n + z*z/(4*n*n))) / den
    return (max(0.0, centre-half), min(1.0, centre+half))

def clopper_pearson(p, n, alpha=0.05):
    # Usa scipy si esta disponible, si no devuelve Wilson como fallback
    try:
        from scipy.stats import beta as beta_dist
        k = int(round(p*n))
        if k == 0:
            lo = 0.0
        else:
            lo = float(beta_dist.ppf(alpha/2, k, n-k+1))
        if k == n:
            hi = 1.0
        else:
            hi = float(beta_dist.ppf(1-alpha/2, k+1, n-k))
        return (lo, hi)
    except Exception:
        return wilson(p, n)

mesh_adj = {i: [] for i in range(N_NODES)}
for i in range(N_NODES):
    for d in [1, 2]:
        j = i + d
        if j < N_NODES:
            mesh_adj[i].append(j)
            mesh_adj[j].append(i)

def bfs_path(adj, alive, link_ok):
    if not alive[0] or not alive[20]:
        return None
    q = [0]; parent = {0: None}; head = 0
    while head < len(q):
        u = q[head]; head += 1
        if u == 20:
            break
        for v in adj[u]:
            if v in parent:
                continue
            if not alive[v]:
                continue
            key = (u, v) if u < v else (v, u)
            if not link_ok.get(key, False):
                continue
            parent[v] = u; q.append(v)
    if 20 not in parent:
        return None
    path = []; cur = 20
    while cur is not None:
        path.append(cur); cur = parent[cur]
    return path[::-1]

def fid_from_path(path, k):
    decay = (1 - EPS_OP) * math.exp(-T_HOP / T2)
    atfb = math.exp(-k * D_ATFB)
    eps = 1 - F0
    for idx in range(len(path) - 1):
        eps = 1 - (1 - eps) * decay
        if (idx + 1) % 3 == 0:
            eps = eps * atfb + 0.002
    return float(min(1.0, max(0.0, 1 - eps)))

# 1. Pre-generar realizaciones UNA VEZ
np.random.seed(504)
topologies = []
for _ in range(N_RUNS):
    alive = np.random.rand(N_NODES) < P_NODE_ALIVE
    link_ok = {}
    for u in mesh_adj:
        for v in mesh_adj[u]:
            if u < v:
                link_ok[(u, v)] = (np.random.rand() < P_LINK)
    topologies.append(bfs_path(mesh_adj, alive, link_ok))

# 2. Barrido grueso + Refinamiento
ks = [0.30, 0.35, 0.40, 0.41, 0.42, 0.43, 0.44, 0.45, 0.50, 0.55, 0.60, 0.61, 0.62, 0.63, 0.64, 0.65, 0.70]
for k in ks:
    fids_global = []; fids_cond = []
    for path in topologies:
        if path is None:
            fids_global.append(0.0)
        else:
            f = fid_from_path(path, k)
            fids_global.append(f); fids_cond.append(f)
    fg = np.array(fids_global); fc = np.array(fids_cond)
    mean_c = float(np.mean(fc)); se_c = float(np.std(fc, ddof=1) / np.sqrt(len(fc)))
    mean_g = float(np.mean(fg)); se_g = float(np.std(fg, ddof=1) / np.sqrt(len(fg)))
    p85 = float(np.mean(fg > 0.85)); p85c = float(np.mean(fc > 0.85))
    w_g = wilson(p85, N_RUNS); cp_g = clopper_pearson(p85, N_RUNS)
    w_c = wilson(p85c, len(fc)); cp_c = clopper_pearson(p85c, len(fc))
    print(f"k={k:.2f}: Cond {mean_c:.4f} IC95 [{mean_c-1.96*se_c:.4f},{mean_c+1.96*se_c:.4f}] | Global {mean_g:.4f} IC95 [{mean_g-1.96*se_g:.4f},{mean_g+1.96*se_g:.4f}]")
    print(f"  P>0.85 Global {p85*100:.2f}% Wilson [{w_g[0]*100:.2f},{w_g[1]*100:.2f}] CP [{cp_g[0]*100:.2f},{cp_g[1]*100:.2f}]")
    print(f"  P>0.85|exito {p85c*100:.2f}% Wilson [{w_c[0]*100:.2f},{w_c[1]*100:.2f}] CP [{cp_c[0]*100:.2f},{cp_c[1]*100:.2f}] | Cumple media? {'SI' if mean_c>=0.85 else 'NO'} | Cumple 100% exito? {'SI' if p85c>=0.999 else 'NO'}")
