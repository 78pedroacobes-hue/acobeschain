# aenmp_k_sweep.py
# Barrido fino de k - NUEVO ARCHIVO
# NO sobrescribe aenmp_v22_audit.py ni chsh_*.py
# Semilla 522, N=10,000 por valor de k
# CLAVE: mismas realizaciones aleatorias para todos los k (Common Random Numbers)

import numpy as np

N_RUNS = 10000
N_NODES = 21
P_LINK = 0.90
P_NODE_ALIVE = 0.95
F0 = 0.92
EPS_OP = 0.015
T2 = 100.0
T_HOP = 5.0
D_ATFB = 3

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
    decay = (1 - EPS_OP) * np.exp(-T_HOP / T2)
    atfb = np.exp(-k * D_ATFB)
    eps = 1 - F0
    for idx in range(len(path) - 1):
        eps = 1 - (1 - eps) * decay
        if (idx + 1) % 3 == 0:
            eps = eps * atfb + 0.002
    return float(np.clip(1 - eps, 0, 1))

# 1. Pre-generar realizaciones UNA VEZ
np.random.seed(522)
topologies = []
for _ in range(N_RUNS):
    alive = np.random.rand(N_NODES) < P_NODE_ALIVE
    link_ok = {}
    for u in mesh_adj:
        for v in mesh_adj[u]:
            if u < v:
                link_ok[(u, v)] = (np.random.rand() < P_LINK)
    topologies.append(bfs_path(mesh_adj, alive, link_ok))

# 2. Evaluar cada k sobre LAS MISMAS topologias
ks = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]
for k in ks:
    fids_global = []; fids_cond = []
    for path in topologies:
        if path is None:
            fids_global.append(0.0)
        else:
            f = fid_from_path(path, k)
            fids_global.append(f); fids_cond.append(f)
    fg = np.array(fids_global); fc = np.array(fids_cond)
    mean_c = np.mean(fc); se_c = np.std(fc, ddof=1) / np.sqrt(len(fc))
    mean_g = np.mean(fg); se_g = np.std(fg, ddof=1) / np.sqrt(len(fg))
    p85 = np.mean(fg > 0.85); se_b = np.sqrt(p85 * (1 - p85) / N_RUNS)
    p85c = np.mean(fc > 0.85)
    print(f"k={k:.2f}: Cond {mean_c:.4f} IC95 [{mean_c-1.96*se_c:.4f},{mean_c+1.96*se_c:.4f}] | Global {mean_g:.4f} | P>0.85 Global {p85*100:.2f}% | P>0.85|exito {p85c*100:.2f}% | Cumple media>=0.85? {'SI' if mean_c>=0.85 else 'NO'}")
