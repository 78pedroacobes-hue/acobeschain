# -*- coding: utf-8 -*-
# =============================================================================
#  PROYECTO   : TACHYON-PSI OPERATOR CLASSIFICATION
#  AUTOR      : (Titular del modelo)
#  LICENCIA   : PROPIETARIA - TODOS LOS DERECHOS RESERVADOS
#  COPYRIGHT  : (c) 2026. Uso exclusivo del titular.
# =============================================================================

import numpy as np
import json
import scipy.linalg as spla
from numpy.linalg import eigvalsh, eigh, eig, matrix_rank, cond

np.set_printoptions(precision=10, suppress=True, linewidth=180)

def titulo(t):
    print("\n" + "="*80)
    print(t)
    print("="*80)

# ============================================================
# 0. OPERADOR BASE
# ============================================================
titulo("0. OPERADOR BASE")

I2 = np.eye(2, dtype=complex)
X  = np.array([[0,1],[1,0]], dtype=complex)
Y  = np.array([[0,-1j],[1j,0]], dtype=complex)
Z  = np.array([[1,0],[0,-1]], dtype=complex)
I4 = np.eye(4, dtype=complex)

Psi = np.zeros((4,4), dtype=complex)
Psi[0,0] = -1.5427
Psi[1,1] =  1.6933
Psi[2,2] =  1.0
Psi[3,3] =  1.0
Psi[0,2] = Psi[2,0] = 0.5057
Psi[1,2] = Psi[2,1] = 0.0759
Psi[2,3] = Psi[3,2] = 0.5

H = (Psi + Psi.conj().T) / 2.0
print("H = Psi (Hermitizado):")
print(H)

# ============================================================
# 1. HERMITICIDAD, NORMAS Y ESPECTRO
# ============================================================
titulo("1. HERMITICIDAD, NORMAS Y ESPECTRO")

print(f"H Hermitiana:   {np.allclose(H, H.conj().T)}")
print(f"traza(H):       {np.trace(H).real}")
print(f"det(H):         {np.linalg.det(H).real}")
print(f"||H||_F:        {np.linalg.norm(H, 'fro')}")
print(f"||H||_2:        {np.linalg.norm(H, 2)}")
print(f"||H||_1:        {np.linalg.norm(H, 1)}")
print(f"Rango:          {matrix_rank(H)}")
print(f"Condicion:      {cond(H)}")

vals, vecs = eigh(H)
print(f"\nAutovalores:")
for i, v in enumerate(vals):
    print(f"  lambda_{i} = {v:+.10f}")
print("Autovectores (columnas):")
print(vecs)

n_pos  = int(np.sum(vals >  1e-12))
n_neg  = int(np.sum(vals < -1e-12))
n_zero = int(np.sum(np.abs(vals) < 1e-12))
print(f"\nSignature (p,q,z) = ({n_pos},{n_neg},{n_zero})")
print(f"Traza de |H|:  {np.sum(np.abs(vals)):.10f}")
print(f"Traza de H^2:  {np.sum(vals**2):.10f}")

# ============================================================
# 2. POTENCIAS Y CAYLEY-HAMILTON
# ============================================================
titulo("2. POTENCIAS Y CAYLEY-HAMILTON")

print(f"traza(H^2) = {np.trace(H @ H).real:.10f}")
print(f"traza(H^3) = {np.trace(H @ H @ H).real:.10f}")
print(f"traza(H^4) = {np.trace(np.linalg.matrix_power(H,4)).real:.10f}")

coefs = np.poly(H)
print(f"Polinomio caracteristico (coefs):")
print(coefs)

ch = np.zeros_like(H)
for c, p in zip(coefs, [np.linalg.matrix_power(H,4), np.linalg.matrix_power(H,3),
                        np.linalg.matrix_power(H,2), H, I4]):
    ch += c * p
print(f"||Cayley-Hamilton|| = {np.linalg.norm(ch):.3e}")

# ============================================================
# 3. SIMETRIA PT
# ============================================================
titulo("3. SIMETRIA PT")

P = np.array([
    [1,0,0,0],
    [0,0,1,0],
    [0,1,0,0],
    [0,0,0,1],
], dtype=complex)

def PT_act(M):
    return P @ M.conj() @ P

PT_H = PT_act(H)
print("PT H PT^-1 =")
print(PT_H)
print(f"\n[PT, H] = 0 ?  {np.allclose(PT_H, H)}")
print(f"||PT H PT^-1 - H||_F = {np.linalg.norm(PT_H - H):.3e}")

print("\nPT-invariancia de autovectores:")
for i in range(4):
    v = vecs[:, i]
    pv = P @ v.conj()
    overlap = np.vdot(v, pv)
    print(f"  v_{i}: <v_i|PT|v_i> = {overlap.real:+.6f}  |.| = {abs(overlap):.6f}")

# ============================================================
# 4. METRICA DE KREIN
# ============================================================
titulo("4. METRICA DE KREIN")

eta = H.copy()
eig_eta = eigvalsh(eta)
print(f"Signature de eta = H: ({np.sum(eig_eta>0)}, {np.sum(eig_eta<0)})")

print("\nNormas de Krein de autovectores de H:")
for i in range(4):
    v = vecs[:, i]
    nk = np.real(v.conj() @ eta @ v)
    tipo = "espacio" if nk > 0 else "tiempo"
    print(f"  v_{i}: <v_i|H|v_i> = {nk:+.10f}  [{tipo}]")

lhs = H.conj().T @ eta
rhs = eta @ H
print(f"\nH† eta - eta H = 0 ?  {np.allclose(lhs, rhs)}")
print(f"||H† eta - eta H|| = {np.linalg.norm(lhs - rhs):.3e}")

# ============================================================
# 5. PSEUDO-HERMITICIDAD
# ============================================================
titulo("5. PSEUDO-HERMITICIDAD")

alpha = 0.5
eta_pos = spla.expm(-alpha * H)
eig_eta_pos = eigvalsh(eta_pos)
print(f"eta = exp(-{alpha}*H)")
print(f"Autovalores de eta: {eig_eta_pos}")
print(f"eta positivo definido: {np.all(eig_eta_pos > 0)}")
print(f"[H, eta] = 0 ?  {np.allclose(H @ eta_pos, eta_pos @ H)}")

# ============================================================
# 6. PUNTOS EXCEPCIONALES
# ============================================================
titulo("6. PUNTOS EXCEPCIONALES")

V = 1j * np.kron(X, Y)
lambdas = np.linspace(0, 3, 400)
conds = []
gaps = []
for lam in lambdas:
    Hl = H + lam * V
    w = np.linalg.eigvals(Hl)
    w = np.sort_complex(w)
    gaps.append(np.min(np.abs(np.diff(w))))
    _, vr = np.linalg.eig(Hl)
    conds.append(np.linalg.cond(vr))
gaps = np.array(gaps)
conds = np.array(conds)
idx_c = np.argmax(conds)
idx_g = np.argmin(gaps)
print(f"Max condicionamiento: {conds[idx_c]:.4e} en lambda = {lambdas[idx_c]:.4f}")
print(f"Min gap espectral:    {gaps[idx_g]:.6e} en lambda = {lambdas[idx_g]:.4f}")

# ============================================================
# 7. ENTRELAZAMIENTO DE AUTOESTADOS
# ============================================================
titulo("7. ENTRELAZAMIENTO DE AUTOESTADOS")

def vN_entropy(state):
    M = state.reshape(2,2)
    s = np.linalg.svd(M, compute_uv=False)
    s = s[s > 1e-15]
    p = s**2
    return -np.sum(p * np.log2(p))

def concurrence(state):
    tilde = np.kron(Y, Y) @ state.conj()
    return abs(np.vdot(state, tilde))

print("Entropia de von Neumann y concurrencia de cada autovector:")
for i in range(4):
    v = vecs[:, i]
    S = vN_entropy(v)
    C = concurrence(v)
    print(f"  v_{i}: S = {S:.6f} bits,  concurrencia = {C:.6f}")

# ============================================================
# 8. ESTADISTICA ESPECTRAL
# ============================================================
titulo("8. ESTADISTICA ESPECTRAL")

spacings = np.diff(np.sort(vals))
print(f"Espaciamientos: {spacings}")
r_ratios = []
for i in range(len(spacings)-1):
    s1, s2 = spacings[i], spacings[i+1]
    r = min(s1,s2)/max(s1,s2)
    r_ratios.append(r)
r_mean = np.mean(r_ratios) if r_ratios else 0
print(f"<r> (ratio de espaciamientos) = {r_mean:.6f}")
print(f"  GOE predice ~0.5307")
print(f"  Poisson predice ~0.3863")

# ============================================================
# 9. OTOC (Out-of-Time-Order Correlator)
# ============================================================
titulo("9. OTOC")

W = np.kron(Z, I2)
Vop = np.kron(I2, Z)
psi00 = np.zeros(4, dtype=complex); psi00[0] = 1.0

def U_t(t):
    return spla.expm(-1j * H * t)

t_grid = np.linspace(0, 5, 51)
otoc = []
for t in t_grid:
    U = U_t(t)
    Wt = U.conj().T @ W @ U
    val = psi00.conj() @ Wt @ Vop @ Wt @ Vop @ psi00
    otoc.append(np.real(val))
otoc = np.array(otoc)
print(f"OTOC(t=0)  = {otoc[0]:.6f}")
print(f"OTOC(t=5)  = {otoc[-1]:.6f}")
print(f"OTOC max   = {otoc.max():.6f}")
print(f"OTOC min   = {otoc.min():.6f}")

# ============================================================
# 10. LOSCHMIDT ECHO
# ============================================================
titulo("10. LOSCHMIDT ECHO")

delta = 0.1
Hp = H + delta * np.kron(X, X)
le = []
for t in t_grid:
    U = U_t(t)
    Up = spla.expm(-1j * Hp * t)
    amp = psi00.conj() @ U.conj().T @ Up @ psi00
    le.append(np.abs(amp)**2)
le = np.array(le)
print(f"LE(t=0) = {le[0]:.6f}")
print(f"LE(t=5) = {le[-1]:.6f}")
print(f"LE min  = {le.min():.6f}")

# ============================================================
# 11. COMPLEJIDAD DE KRYLOV
# ============================================================
titulo("11. COMPLEJIDAD DE KRYLOV")

def lanczos(H, psi0, max_iter=10):
    n = len(psi0)
    b = []
    psi_prev = np.zeros(n, dtype=complex)
    psi_cur = psi0 / np.linalg.norm(psi0)
    b_prev = 0.0
    for _ in range(max_iter):
        w = H @ psi_cur - b_prev * psi_prev
        alpha = np.real(np.vdot(psi_cur, w))
        w = w - alpha * psi_cur
        b_cur = np.linalg.norm(w)
        if b_cur < 1e-14:
            break
        b.append(b_cur)
        psi_prev = psi_cur
        psi_cur = w / b_cur
        b_prev = b_cur
    return np.array(b)

b_coefs = lanczos(H, psi00, max_iter=8)
print(f"Coeficientes de Lanczos b_n: {b_coefs}")
if len(b_coefs) > 1:
    ratios = b_coefs[1:]/b_coefs[:-1]
    print(f"Ratios b_n/b_(n-1): {ratios}")

K_proxy = []
for t in t_grid:
    U = U_t(t)
    psi_t = U @ psi00
    p_ret = np.abs(np.vdot(psi00, psi_t))**2
    K_proxy.append(1 - p_ret)
K_proxy = np.array(K_proxy)
print(f"Krylov proxy K(0)  = {K_proxy[0]:.6f}")
print(f"Krylov proxy K(5)  = {K_proxy[-1]:.6f}")

# ============================================================
# 12. ENTROPIA REDUCIDA DURANTE EVOLUCION
# ============================================================
titulo("12. ENTROPIA REDUCIDA DURANTE EVOLUCION")

def reduced_A(state):
    M = state.reshape(2,2)
    return M @ M.conj().T

def vN_density(rho):
    vals = np.linalg.eigvalsh(rho)
    vals = vals[vals > 1e-15]
    return -np.sum(vals * np.log2(vals))

S_A = []
for t in t_grid:
    U = U_t(t)
    psi_t = U @ psi00
    S_A.append(vN_density(reduced_A(psi_t)))
S_A = np.array(S_A)
print(f"S_A(0)  = {S_A[0]:.6f}")
print(f"S_A(5)  = {S_A[-1]:.6f}")
print(f"S_A max = {S_A.max():.6f}")

# ============================================================
# 13. EXPORTACION
# ============================================================
titulo("13. EXPORTACION JSON")

resultados = {
    "licencia": "PROPIETARIA - TODOS LOS DERECHOS RESERVADOS",
    "H": H.real.tolist(),
    "autovalores_H": vals.tolist(),
    "autovectores_H": vecs.real.tolist(),
    "signature": {"p": n_pos, "q": n_neg, "z": n_zero},
    "PT_simetria": bool(np.allclose(PT_H, H)),
    "Krein_normas": [float(np.real(vecs[:,i].conj() @ H @ vecs[:,i])) for i in range(4)],
    "pseudo_hermiticidad_alpha": alpha,
    "exceptional_point_lambda": float(lambdas[idx_c]),
    "exceptional_point_max_cond": float(conds[idx_c]),
    "espectral_r_mean": float(r_mean),
    "otoc_t": t_grid.tolist(),
    "otoc_vals": otoc.tolist(),
    "loschmidt_t": t_grid.tolist(),
    "loschmidt_vals": le.tolist(),
    "lanczos_b": b_coefs.tolist(),
    "krylov_proxy": K_proxy.tolist(),
    "entropia_reducida": S_A.tolist(),
}

with open("tachyon_classification.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False)

print("Guardado: tachyon_classification.json")
