# aenmp_k_explain_jump.py
# Explica el salto 38.96% -> 100% entre k=0.64 y k=0.65
# NO toca v2.2 ni aenmp_k_sweep_v1.py
# Semilla 522, mismas topologias (Common Random Numbers)
# Muestra: distribucion de longitudes, F por longitud, k critico por longitud
# Y refinamiento 0.001 para media y proporcion

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
    den = 1 + z*z/n
    centre = (p + z*z/(2*n)) / den
    half = z * math.sqrt((p*(1-p)/n + z*z/(4*n*n))) / den
    return (max(0.0, centre-half), min(1.0, centre+half))

def clopper_pearson(p, n):
    try:
        from scipy.stats import beta as beta_dist
        k = int(round(p*n))
        lo = 0.0 if k == 0 else float(beta_dist.ppf(0.025, k, n-k+1))
        hi = 1.0 if k == n else float(beta_dist.ppf(0.975, k+1, n-k))
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

def fid_from_hops(hops, k):
    decay = (1 - EPS_OP) * math.exp(-T_HOP / T2)
    atfb = math.exp(-k * D_ATFB)
    eps = 1 - F0
    for idx in range(hops):
        eps = 1 - (1 - eps) * decay
        if (idx + 1) % 3 == 0:
            eps = eps * atfb + 0.002
    return float(min(1.0, max(0.0, 1 - eps)))

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

lengths = [len(p)-1 for p in topologies if p is not None]
cnt = {}
for h in lengths:
    cnt[h] = cnt.get(h, 0) + 1
print(f"Exitos: {len(lengths)} de {N_RUNS}")
for h in sorted(cnt):
    print(f"hops={h}: {cnt[h]} rutas ({cnt[h]/len(lengths)*100:.2f}% exitos)")

print("F por longitud:")
for h in sorted(cnt):
    f64 = fid_from_hops(h, 0.64); f65 = fid_from_hops(h, 0.65)
    print(f"hops={h}: F(0.64)={f64:.4f} | F(0.65)={f65:.4f} | cruza={f64<=0.85<f65}")

print("Refinamiento media 0.431-0.44 paso 0.001:")
for k_int in range(431, 441):
    k = k_int / 1000.0
    fids = [fid_from_hops(len(p)-1, k) for p in topologies if p is not None]
    fc = np.array(fids); mean = float(np.mean(fc)); se = float(np.std(fc, ddof=1) / np.sqrt(len(fc)))
    print(f"k={k:.3f}: Cond {mean:.4f} IC95 [{mean-1.96*se:.4f},{mean+1.96*se:.4f}] IC>0.85? {mean-1.96*se>0.85}")

print("Refinamiento proporcion 0.641-0.65 paso 0.001:")
for k_int in range(641, 651):
    k = k_int / 1000.0
    fids = [fid_from_hops(len(p)-1, k) for p in topologies if p is not None]
    fc = np.array(fids); p85c = float(np.mean(fc > 0.85))
    w = wilson(p85c, len(fc)); c = clopper_pearson(p85c, len(fc))
    print(f"k={k:.3f}: P>0.85|exito {p85c*100:.2f}% Wilson [{w[0]*100:.2f},{w[1]*100:.2f}] CP [{c[0]*100:.2f},{c[1]*100:.2f}]")
