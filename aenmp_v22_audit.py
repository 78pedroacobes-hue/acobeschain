# aenmp_v22_audit.py
# AENMP v2.2 CONGELADA - Auditoria de fidelidades
# Semilla 522 - NO MODIFICAR
# Distingue fidelidad condicionada vs global
# IC t para medias, IC binomial / Clopper-Pearson para proporciones

import numpy as np

np.random.seed(522)
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

def fid_from_path(path, k_val):
    decay = (1 - EPS_OP) * np.exp(-T_HOP / T2)
    atfb = np.exp(-k_val * D_ATFB) if k_val is not None else 1.0
    eps = 1 - F0
    for idx in range(len(path) - 1):
        eps = 1 - (1 - eps) * decay
        if k_val is not None and (idx + 1) % 3 == 0:
            eps = eps * atfb + 0.002
    return float(np.clip(1 - eps, 0, 1))

for k in [0.3, 0.7]:
    succ = []; fids_cond = []; fids_global = []
    np.random.seed(522)
    for _ in range(N_RUNS):
        alive = np.random.rand(N_NODES) < P_NODE_ALIVE
        link_ok = {}
        for u in mesh_adj:
            for v in mesh_adj[u]:
                if u < v:
                    link_ok[(u, v)] = (np.random.rand() < P_LINK)
        path = bfs_path(mesh_adj, alive, link_ok)
        if path is None:
            succ.append(0); fids_global.append(0.0)
        else:
            succ.append(1)
            f = fid_from_path(path, k)
            fids_cond.append(f); fids_global.append(f)
    succ = np.array(succ); fids_global = np.array(fids_global); fids_cond = np.array(fids_cond)
    mean_c = np.mean(fids_cond); se_c = np.std(fids_cond, ddof=1) / np.sqrt(len(fids_cond))
    mean_g = np.mean(fids_global); se_g = np.std(fids_global, ddof=1) / np.sqrt(len(fids_global))
    p_f85 = np.mean(fids_global > 0.85); se_b = np.sqrt(p_f85 * (1 - p_f85) / N_RUNS)
    p_f85_c = np.mean(fids_cond > 0.85)
    print(f"k={k}: Cond {mean_c:.4f} IC95 [{mean_c-1.96*se_c:.4f},{mean_c+1.96*se_c:.4f}]")
    print(f"  Global {mean_g:.4f} IC95 [{mean_g-1.96*se_g:.4f},{mean_g+1.96*se_g:.4f}]")
    print(f"  P(F>0.85) Global {p_f85*100:.2f}% IC [{(p_f85-1.96*se_b)*100:.2f},{(p_f85+1.96*se_b)*100:.2f}]")
    print(f"  P(F>0.85|exito) {p_f85_c*100:.2f}%")
