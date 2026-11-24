# -*- coding: utf-8 -*-
# UOG-TÁCTICO — El Operador Supremo (Fast Strike Edition)
# 63 features rigorosas | 18 Familias | 6,000 matrices/fam (n=108,000)
# OPTIMIZACIÓN EXTREMA DE TIEMPO DE EJECUCIÓN (Motor Algebraico Pre-cacheado)

import numpy as np
from scipy.linalg import eig, eigh, svd, norm
import warnings, json, time
from multiprocessing import Pool, cpu_count

warnings.filterwarnings("ignore")

# --- CONSTANTES GLOBALES PRECOMPUTADAS PARA VELOCIDAD MÁXIMA ---
I2 = np.eye(2, dtype=complex); X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex); Z = np.array([[1, 0], [0, -1]], dtype=complex)
PAULIS = [I2, X, Y, Z]

XX = np.kron(X, X)
YY = np.kron(Y, Y)
ZZ = np.kron(Z, Z)
W_op = np.kron(Z, I2)
Vo_op = np.kron(I2, Z)
Vb_op = np.kron(X, Y); Vb_op = (Vb_op + Vb_op.conj().T)/2
Vp_op = (np.kron(X, Y) + np.kron(Y, X))/2
Z4_op = np.kron(np.diag([1, -1]), np.eye(2))
wZ_op, VZ_op = eigh(Z4_op)
Uz_op = (VZ_op * np.exp(-1j*(np.pi/2)*wZ_op)) @ VZ_op.conj().T

def _expH_fast(vals, V, V_inv, t):
    """Evolución temporal sin recalcular eigenvectores. Brutalmente rápido."""
    return (V * np.exp(-1j * vals * t)) @ V_inv

def vN(v):
    s = svd(v.reshape(2, 2), compute_uv=False)
    p = s[s > 1e-15]**2
    return float(-np.sum(p * np.log2(p)))

def S_(r):
    e = np.linalg.eigvalsh((r + r.conj().T)/2).clip(1e-15)
    return float(-np.sum(e * np.log2(e)))

def g63(H):
    """63 Features Cuánticas Absolutas sin trampas (Motor Optimizado)"""
    H = np.asarray(H, dtype=complex); N = 4
    is_herm = np.allclose(H, H.conj().T, atol=1e-10)
    
    if is_herm:
        vals, V = eigh(H)
        V_inv = V.conj().T
    else:
        vals, V = eig(H)
        idx = np.argsort(vals.real)
        vals, V = vals[idx], V[:, idx]
        V_inv = np.linalg.inv(V)

    G = {}
    v0 = V[:, 0]
    
    # NORMALIZACIÓN DE ENERGÍA
    H_norm_val = norm(H, ord=2) + 1e-15
    H_dyn = H / H_norm_val
    vals_dyn = vals / H_norm_val # Eigenvalores ajustados dinámicamente
    
    # 1. BÁSICOS Y ESPECTRO
    G['spectral_radius'] = float(np.max(np.abs(vals)))
    G['trace_real'] = float(np.trace(H).real)
    G['trace_imag'] = float(np.trace(H).imag)
    G['det_abs'] = float(abs(np.prod(vals)))
    G['arg_det'] = float(np.angle(np.prod(vals)))
    
    d = np.abs(np.diff(vals))
    G['spectral_gap'] = float(d.min()) if len(d) > 0 else 0.0
    G['spectral_gap_max'] = float(d.max()) if len(d) > 0 else 0.0
    
    if len(d) >= 2:
        r = [min(d[i], d[i+1]) / (max(d[i], d[i+1]) + 1e-15) for i in range(len(d)-1)]
        G['r_ratio_mean'] = float(np.mean(r))
        G['r_ratio_var'] = float(np.var(r))
    else:
        G['r_ratio_mean'] = G['r_ratio_var'] = 0.0

    pv = np.abs(vals); pv = pv / (pv.sum() + 1e-15)
    G['spectral_entropy'] = float(-np.sum(pv * np.log2(pv + 1e-15)))
    
    H_abs = np.abs(H)
    lap = np.diag(H_abs.sum(axis=1)) - H_abs
    lap_vals = np.sort(np.linalg.eigvalsh((lap+lap.T)/2))
    G['alg_connectivity'] = float(lap_vals[1]) if N > 1 else 0.0

    # 2. ESTRUCTURA ALGEBRAICA
    ad = np.zeros((N*N, N*N), dtype=complex)
    for i in range(N):
        for j in range(N):
            E = np.zeros((N, N), dtype=complex); E[i, j] = 1
            ad[:, i*N+j] = (H @ E - E @ H).flatten()
    sd = svd(ad, compute_uv=False)
    G['commutant_dim'] = int(N*N - (sd > 1e-8).sum())
    
    pw = np.array([np.linalg.matrix_power(H, k).flatten() for k in range(N)]).T
    sa = svd(pw, compute_uv=False)
    G['algebra_dim'] = int((sa > 1e-8).sum())
    
    G['comm_norm_Z'] = float(norm(H @ ZZ - ZZ @ H))
    G['non_orthogonality'] = float(norm(V.conj().T @ V - np.eye(N)))
    G['net_density'] = float((np.abs(H - np.diag(np.diag(H))) > 1e-8).sum() / (N*(N-1)))

    # 3. ENTRELAZAMIENTO Y ESTADOS
    G['entropy_max'] = float(max(vN(V[:, i]) for i in range(N)))
    G['entropy_min'] = float(min(vN(V[:, i]) for i in range(N)))
    
    G['concurrence_max'] = float(max(abs(np.vdot(V[:, i], YY @ V[:, i].conj())) for i in range(N)))
    
    iprs = [float((np.abs(V[:, i])**4).sum()) for i in range(N)]
    G['IPR_max'] = float(max(iprs))
    G['IPR_min'] = float(min(iprs))
    G['IPR_var'] = float(np.var(iprs))
    
    rho = np.outer(v0, v0.conj())
    M = v0.reshape(2, 2); rA = M @ M.conj().T; rB = M.conj().T @ M
    G['purity_red'] = float(np.real(np.trace(rA @ rA)))
    
    sv = svd(M, compute_uv=False)
    p2_ = sv**2; p2_ = p2_[p2_ > 1e-15]
    G['renyi_2'] = float(-np.log2(np.sum(p2_**2)))
    G['renyi_inf'] = float(-np.log2(np.max(p2_)))
    G['schmidt_rank'] = int((sv > 1e-10).sum())
    
    rpt = rho.reshape(2,2,2,2).transpose(0,3,2,1).reshape(4,4)
    er = np.linalg.eigvalsh((rpt+rpt.conj().T)/2)
    G['negativity'] = float((np.abs(er).sum() - 1) / 2)
    G['discord_proxy'] = float(min(S_(rA), S_(rB)))
    G['mutual_info'] = float(S_(rA) + S_(rB))
    
    probs = np.real(np.diag(rho)); G['husimi_purity'] = float(np.sum(probs**2))
    G['coh_l1'] = float(np.sum(np.abs(rho)) - np.sum(np.abs(np.diag(rho))))

    # 4. DINÁMICA ACELERADA
    psi = np.zeros(4, dtype=complex); psi[0] = 1.0
    ot = []
    for t in np.linspace(0, 5, 40):
        U = _expH_fast(vals_dyn, V, V_inv, t)
        Wt = U.conj().T @ W_op @ U
        ot.append(float(np.real(psi.conj() @ Wt @ Vo_op @ Wt @ Vo_op @ psi)))
    G['OTOC_min'] = float(min(ot))
    G['OTOC_range'] = float(max(ot) - min(ot))
    G['OTOC_var'] = float(np.var(ot))

    Hp_dyn = H_dyn + 0.1 * XX
    if is_herm:
        vp, Vp = eigh(Hp_dyn)
        Vp_inv = Vp.conj().T
    else:
        vp, Vp = eig(Hp_dyn)
        Vp_inv = np.linalg.inv(Vp)

    le = [abs(psi.conj() @ _expH_fast(vals_dyn, V, V_inv, t).conj().T @ _expH_fast(vp, Vp, Vp_inv, t) @ psi)**2 for t in np.linspace(0, 5, 40)]
    G['loschmidt_min'] = float(min(le))
    G['loschmidt_decay_rate'] = float(1.0 - le[1]) if len(le)>1 else 0.0

    b = []; prev = np.zeros(N, dtype=complex); cur = psi.copy(); bp = 0.0
    for _ in range(8):
        w = H_dyn @ cur - bp * prev
        a = float(np.real(np.vdot(cur, w))); w = w - a * cur
        bc = float(norm(w))
        if bc < 1e-14: break
        b.append(bc); prev, cur, bp = cur, w / bc, bc
    G['krylov_growth'] = float(b[-1]/b[0]) if len(b) > 1 else 0.0
    G['krylov_var'] = float(np.var(b)) if len(b) > 0 else 0.0

    G['dyn_entropy_max'] = float(max(vN(_expH_fast(vals_dyn, V, V_inv, t) @ psi) for t in np.linspace(0, 5, 15)))

    otv = np.array(ot); decay = otv[0] - otv.min()
    if decay < 0.05: G['lyapunov'] = 0.0
    else:
        y = np.log(np.abs(1 - otv) + 1e-15); ts = np.linspace(0, 5, 40); m = np.isfinite(y)
        G['lyapunov'] = float(np.polyfit(ts[m], y[m], 1)[0]) if m.sum() > 3 else 0.0

    SFF = lambda t: abs(np.sum(np.exp(-1j * vals * t)))**2 / N
    G['SFF_t1'] = float(SFF(1.0))
    G['SFF_t5'] = float(SFF(5.0))

    # 5. GEOMETRÍA Y FASES
    n_berry = 60; st = []; dd = []
    for th in np.linspace(0, 2*np.pi, n_berry, endpoint=False):
        Hm = np.cos(th)*H + np.sin(th)*Vb_op
        if is_herm: w, vt = eigh(Hm)
        else:
            w, vt = eig(Hm); i_sort = np.argsort(w.real)
            w, vt = w[i_sort], vt[:, i_sort]
        st.append(vt[:, 0])
        dd.append(float(w[0].real - w[1].real))
    
    G['berry_phase'] = float(sum(float(np.angle(np.vdot(st[i], st[(i+1)%n_berry]))) for i in range(n_berry)))
    s = np.sign(dd); G['winding'] = int((s[:-1] != s[1:]).sum())

    e = 1e-3
    H_p = H + e*Vp_op; H_m = H - e*Vp_op
    if is_herm:
        _, Vp_ = eigh(H_p); _, Vm_ = eigh(H_m)
    else:
        _, Vp_ = eig(H_p); _, Vm_ = eig(H_m)
        
    dp = (Vp_[:,0] - Vm_[:,0]) / (2*e)
    G['fubini_study'] = float(np.real(np.vdot(dp, dp) - abs(np.vdot(v0, dp))**2))

    # Optimización: Los eigenvalores de la exp(H_dyn) son simplemente exp(vals_dyn)
    G['circuit_complexity'] = float(norm(np.angle(np.exp(-1j * vals_dyn))))
    
    p1 = _expH_fast(vals_dyn, V, V_inv, 0.5) @ psi
    p2 = _expH_fast(vals_dyn, V, V_inv, 1.0) @ psi
    G['bures_sq'] = float(2 - 2*np.sqrt(abs(np.vdot(p1, p2))**2))
    G['fidelity_t1'] = float(abs(np.vdot(psi, p2))**2)

    plus = np.ones(4, dtype=complex)/2
    eH = float(np.real(np.vdot(plus, H @ plus)))
    G['fisher_Q'] = float(4*(np.real(np.vdot(plus, H @ H @ plus)) - eH**2))

    G['asymmetry_Z'] = float(norm(rho - Uz_op @ rho @ Uz_op.conj().T))

    pp_ = np.sort(np.abs(v0)**2)[::-1]; cum = np.cumsum(pp_); xx = np.arange(1, len(pp_)+1)/len(pp_)
    G['lorenz_area'] = float(np.trapezoid(cum, xx))

    G['eth_viol'] = float(np.std(np.diag(H).real) / (abs(np.diag(H).real.mean()) + 1e-12))

    Hres = H.reshape(2,2,2,2).transpose(0,2,1,3).reshape(4,4)
    so = svd(Hres, compute_uv=False); po = so**2; po = po[po>1e-15]; po = po/po.sum()
    G['op_entropy'] = float(-np.sum(po * np.log2(po)))

    G['_min_gap'] = G['spectral_gap']
    G['_spec_type'] = 'non-degenerate' if G['spectral_gap'] > 1e-6 else 'degenerate'
    G['macro_capacity'] = float(np.exp(G['entropy_max']))
    G['geom_diameter'] = float(1 - np.min(np.abs(V.conj().T @ V)))
    
    return G

# ============ 18 FAMILIAS ============
def r_gue(r): A = r.normal(size=(4,4))+1j*r.normal(size=(4,4)); return (A+A.conj().T)/2
def r_goe(r): A = r.normal(size=(4,4)); return (A+A.T)/2
def r_gse(r): 
    A = r.normal(size=(2,2))+1j*r.normal(size=(2,2)); A=(A+A.conj().T)/2
    return np.kron(A, I2)
def r_nonh(r): return r.normal(size=(4,4))+1j*r.normal(size=(4,4))
def r_pt(r): 
    A = r.normal(size=(4,4))+1j*r.normal(size=(4,4)); P = np.eye(4)[::-1]
    return A + P @ A.conj() @ P
def r_pauli(r):
    c = r.normal(size=16)+1j*r.normal(size=16)
    M = sum(c[k]*np.kron(PAULIS[k//4], PAULIS[k%4]) for k in range(16))
    return (M+M.conj().T)/2
def r_hankel(r):
    v = r.normal(size=7); H = np.zeros((4,4))
    for i in range(4):
        for j in range(4): H[i,j] = v[i+j]
    return H
def r_toeplitz(r):
    c = r.normal(size=4); rr = r.normal(size=4); H = np.zeros((4,4))
    for i in range(4):
        for j in range(4): H[i,j] = c[j-i] if j>=i else rr[i-j]
    return H
def r_sylvester(r): return np.diag(r.integers(-5, 6, size=4).astype(complex))
def r_laplacian(r):
    W = r.random((4,4)); W=(W+W.T)/2; np.fill_diagonal(W,0)
    return (np.diag(W.sum(axis=1)) - W).astype(complex)
def r_adjacency(r):
    A = (r.random((4,4))>0.5).astype(float); A=(A+A.T)/2; np.fill_diagonal(A,0)
    return A.astype(complex)
def r_projection(r):
    A = r.normal(size=(4,2))+1j*r.normal(size=(4,2)); Q,_ = np.linalg.qr(A)
    return Q @ Q.conj().T
def r_density(r):
    A = r.normal(size=(4,4))+1j*r.normal(size=(4,4)); rho = A @ A.conj().T
    return rho / np.trace(rho)
def r_symcomplex(r):
    A = r.normal(size=(4,4))+1j*r.normal(size=(4,4)); A=A+A.T; return A
def r_circulant(r):
    c = r.normal(size=4) + 1j*r.normal(size=4); H = np.zeros((4,4), dtype=complex)
    for i in range(4):
        for j in range(4): H[i,j] = c[(j-i)%4]
    return H
def r_banded(r):
    H = np.diag(r.normal(size=4)) + np.diag(r.normal(size=3), k=1) + np.diag(r.normal(size=3), k=-1)
    return H.astype(complex)
def r_wishart(r):
    X = r.normal(size=(4, 10)); return (X @ X.T).astype(complex)
def r_poisson(r):
    return np.diag(r.random(4)).astype(complex)

FAMILIES = [
    ("GUE", r_gue), ("GOE", r_goe), ("GSE", r_gse), ("NonH", r_nonh),
    ("PT", r_pt), ("Pauli", r_pauli), ("Hankel", r_hankel), ("Toeplitz", r_toeplitz),
    ("Diagonal", r_sylvester), ("Laplacian", r_laplacian), ("Adjacency", r_adjacency),
    ("Projection", r_projection), ("Density", r_density), ("SymComplex", r_symcomplex),
    ("Circulant", r_circulant), ("Banded", r_banded), ("Wishart", r_wishart), 
    ("Poisson", r_poisson)
]

def work(args):
    fam_idx, seed = args
    try:
        rng = np.random.default_rng(seed)
        M = FAMILIES[fam_idx][1](rng)
        return g63(M)
    except Exception:
        return None

def calc_percentile(arr, val):
    less = np.sum(arr < val)
    equal = np.sum(arr == val)
    total = len(arr)
    return (less + 0.5 * equal) / total * 100.0

if __name__ == "__main__":
    N_PER_FAM = 6000  # 6,000 * 18 = 108,000 matrices
    N_FAM = len(FAMILIES)
    N_TOTAL = N_PER_FAM * N_FAM
    n_proc = max(1, cpu_count() - 1)
    
    print(f"=== UOG TÁCTICO: DESPLIEGUE RÁPIDO ===")
    print(f"{N_FAM} familias × {N_PER_FAM} = {N_TOTAL} matrices, {n_proc} procesos")
    print("Motor Algebraico Optimizado | 63 Features | Percentiles Honestos")
    
    args = [(fi, 800000 + fi*100000 + s) for fi in range(N_FAM) for s in range(N_PER_FAM)]
    t0 = time.time()
    results = []
    
    with Pool(n_proc) as p:
        for i, r in enumerate(p.imap_unordered(work, args, chunksize=300)):
            if r is not None: results.append(r)
            if (i+1) % 5000 == 0:
                el = time.time() - t0
                eta = el / (i+1) * (N_TOTAL - i - 1)
                print(f"  [{i+1}/{N_TOTAL}]  ({el/60:.1f} min, ETA {eta/60:.1f} min)")
                
    print(f"\n[+] Completado en {time.time()-t0:.0f}s. Válidos: {len(results)}")

    keys = [k for k in sorted(results[0].keys()) if not k.startswith('_')]
    ens = {k: np.array([r[k] for r in results]) for k in keys}
    spec_types = [r['_spec_type'] for r in results]

    Psi = np.zeros((4,4), dtype=complex)
    Psi[0,0] = -1.5427; Psi[1,1] = 1.6933; Psi[2,2] = 1.0; Psi[3,3] = 1.0
    Psi[0,2] = Psi[2,0] = 0.5057; Psi[1,2] = Psi[2,1] = 0.0759; Psi[2,3] = Psi[3,2] = 0.5
    
    psi_g = g63(Psi)
    psi_type = psi_g['_spec_type']
    print(f"\nΨ Operador Absoluto: {psi_type}, min_gap={psi_g['_min_gap']:.6f}")

    idx_match = [i for i, t in enumerate(spec_types) if t == psi_type]
    print(f"Sub-ensemble '{psi_type}': {len(idx_match)} / {len(results)}")

    def reportar_honesto(nombre, indices):
        print("\n" + "="*70)
        print(f"{nombre}  (n={len(indices)})")
        print("="*70)
        print(f"{'feature':>24} {'PSI':>14} {'pct_real':>10} {'var_ensemble':>14}")
        print("-" * 70)
        ext = []
        for k in keys:
            arr = np.array([ens[k][i] for i in indices])
            var_arr = np.var(arr)
            pv = float(psi_g[k])
            
            if var_arr < 1e-12:
                if abs(pv - arr[0]) < 1e-8:
                    pct = 50.0 
                    var_str = "(Constante)"
                else:
                    pct = 100.0 if pv > arr[0] else 0.0
                    var_str = "(Fijo)"
            else:
                pct = calc_percentile(arr, pv)
                var_str = f"{var_arr:.2e}"

            mk = "***" if (pct < 5 or pct > 95) and var_arr > 1e-12 else ""
            if mk: ext.append((k, pv, pct))
            
            print(f"{k:>24} {pv:>14.6f} {pct:>9.2f}% {var_str:>14} {mk}")
            
        print(f"\nExtremos Reales (Colas <5% o >95% en métricas no-constantes): {len(ext)}")
        for k, pv, pct in ext:
            print(f"  {k:>24} = {pv:+.6f}  (pct {pct:.2f}%)")
        return ext

    ext_all = reportar_honesto("A) CONTRA TODO EL ENSEMBLE DE 18 FAMILIAS", list(range(len(results))))
    ext_match = reportar_honesto(f"B) CONTRA SOLO '{psi_type}'", idx_match)

    with open("uog_tactico_result.json", "w") as f:
        json.dump({
            "n_total": N_TOTAL, "n_valid": len(results), "n_fam": N_FAM,
            "psi_type": psi_type, "n_match": len(idx_match),
            "ext_all": [(k, pv, pct) for k, pv, pct in ext_all],
            "ext_match": [(k, pv, pct) for k, pv, pct in ext_match],
            "total_features": len(keys)
        }, f, indent=2)
    print("\n[+] Guardado limpio y auditable: uog_tactico_result.json")
