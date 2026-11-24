import numpy as np

# ATFB-P1 Bell-Diagonal Validation v1.1
# Mejoras: 1) Validación estricta de probs 2) Wilson CI 3) Monte Carlo a nivel de medida desde rho'

def bell_states():
    s = 1/np.sqrt(2)
    return [
        np.array([s,0,0,s], dtype=complex),
        np.array([s,0,0,-s], dtype=complex),
        np.array([0,s,s,0], dtype=complex),
        np.array([0,s,-s,0], dtype=complex),
    ]
BELLS = bell_states()
PHI_PLUS = BELLS[0]

def rho_from_probs(p, label=""):
    # MEJORA 1: Validación estricta, no normalización silenciosa
    p = np.array(p, dtype=float)
    if np.any(p < -1e-9):
        raise ValueError(f"{label} Prob negativa: {p}")
    if np.any(p < 0):
        p = np.maximum(p, 0)
    s = p.sum()
    if s <= 1e-12:
        raise ValueError(f"{label} Suma cero: {p}")
    if abs(s - 1.0) > 1e-6:
        raise ValueError(f"{label} Suma != 1: sum={s:.6f} p={p}. Corrige el input, no lo normalizo.")
    rho = np.zeros((4,4), dtype=complex)
    for pi, psi in zip(p, BELLS):
        rho += pi * np.outer(psi, psi.conj())
    return rho

def werner_probs(F):
    q = (1-F)/3.0
    return [F, q, q, q]

def build_cnot_16(control, target):
    U = np.zeros((16,16), dtype=complex)
    for inp in range(16):
        bits = [(inp >> (3-i)) & 1 for i in range(4)]
        out_bits = bits.copy()
        if bits[control] == 1:
            out_bits[target] ^= 1
        out_idx = sum(b << (3-i) for i,b in enumerate(out_bits))
        U[out_idx, inp] = 1.0
    return U

CNOT_A = build_cnot_16(0,2)
CNOT_B = build_cnot_16(1,3)
U_ATFB = CNOT_B @ CNOT_A

def atfb_p1(p_primary, p_aux):
    rho_p = rho_from_probs(p_primary, "Primary")
    rho_a = rho_from_probs(p_aux, "Aux")
    rho_in = np.kron(rho_p, rho_a)
    rho_prime = U_ATFB @ rho_in @ U_ATFB.conj().T
    P = np.zeros((16,16), dtype=complex)
    for a1b1 in range(4):
        for a2b2 in [0,3]:
            idx = a1b1*4 + a2b2
            P[idx, idx] = 1.0
    rho_acc = P @ rho_prime @ P.conj().T
    rho_tilde = np.zeros((4,4), dtype=complex)
    for i in range(4):
        for j in range(4):
            rho_tilde[i,j] = sum(rho_acc[i*4+k, j*4+k] for k in range(4))
    p_success = np.trace(rho_tilde).real
    if p_success <= 1e-12:
        return {"p_success": 0.0, "F_out": 0.0, "rho_prime": rho_prime, "rho_out": rho_tilde}
    rho_out = rho_tilde / p_success
    F_out = (PHI_PLUS.conj() @ rho_out @ PHI_PLUS).real
    return {"p_success": float(p_success), "F_out": float(F_out),
            "Delta_F": float(F_out - p_primary[0]), "F_tele_out": float((2*F_out+1)/3),
            "beneficial": bool(F_out > p_primary[0]), "rho_prime": rho_prime, "rho_out": rho_out}

def wilson_ci(k, n, z=1.96):
    # MEJORA 2: Wilson 95% CI, no Wald
    if n == 0:
        return 0.0, 0.0, 1.0
    phat = k/n
    denom = 1 + z**2/n
    centre = (phat + z**2/(2*n)) / denom
    delta = z * np.sqrt((phat*(1-phat) + z**2/(4*n)) / n) / denom
    return phat, max(0.0, centre-delta), min(1.0, centre+delta)

def monte_carlo_from_rho(rho_prime, N, seed=24052026):
    # MEJORA 3: Muestrear medidas desde rho' de verdad
    # Prob de cada base |A1 B1 A2 B2> = diag(rho')
    # Aceptar si A2B2 = 00 o 11, es decir, últimos 2 bits = 00 o 11
    probs = np.real(np.diag(rho_prime))
    probs = np.maximum(probs, 0); probs = probs / probs.sum()
    rng = np.random.default_rng(seed)
    samples = rng.choice(16, size=N, p=probs)
    # bits: A1=bit3, B1=bit2, A2=bit1, B2=bit0. Aceptar si A2==B2
    accepts = 0
    for s in samples:
        a2 = (s >> 1) & 1
        b2 = s & 1
        if a2 == b2:
            accepts += 1
    return accepts

print("=== ATFB-P1 v1.1 ===")
print("\nCheck 1: Validación estricta - debe fallar con input malo")
try:
    rho_from_probs([0.8, 0.1, 0.1, 0.05], "Test malo suma 1.05")
    print("FAIL: No detectó suma != 1")
except ValueError as e:
    print(f"PASS: Detectó suma != 1 -> {e}")
try:
    rho_from_probs([0.8, -0.1, 0.2, 0.1], "Test negativo")
    print("FAIL: No detectó negativo")
except ValueError as e:
    print(f"PASS: Detectó negativo -> {e}")

print("\nCheck 2: Reproducibilidad v1.0 - Werner 0.842")
r = atfb_p1(werner_probs(0.842), werner_probs(0.842))
print(f"F_out={r['F_out']:.6f} (esperado 0.877039) p={r['p_success']:.6f} (esperado 0.811524)")

print("\nCheck 3: Asimétrico crítico - Regla de selección")
for name, fp, fa in [("Prim 0.90 / Aux 0.60 - MAL", 0.90, 0.60), ("Prim 0.60 / Aux 0.90 - BIEN", 0.60, 0.90)]:
    rr = atfb_p1(werner_probs(fp), werner_probs(fa))
    print(f"{name}: F_out={rr['F_out']:.4f} Delta={rr['Delta_F']:+.4f} Benef={rr['beneficial']}")

print("\nCheck 4: Monte Carlo desde rho' + Wilson CI")
N=10000
r = atfb_p1(werner_probs(0.842), werner_probs(0.842))
accepts = monte_carlo_from_rho(r["rho_prime"], N)
phat, lo, hi = wilson_ci(accepts, N)
print(f"N={N} Aceptados={accepts} p_hat={phat:.4f} Wilson95%=[{lo:.4f}, {hi:.4f}] Teórico={r['p_success']:.4f} Dentro={lo <= r['p_success'] <= hi}")
print("Este Monte Carlo SÍ muestrea la medida del circuito, no una Bernoulli con p_teórico.")

print("\nCheck 5: Asimétrico con Monte Carlo desde rho'")
r2 = atfb_p1(werner_probs(0.60), werner_probs(0.90))
acc2 = monte_carlo_from_rho(r2["rho_prime"], N, seed=123)
phat2, lo2, hi2 = wilson_ci(acc2, N)
print(f"Prim 0.60 / Aux 0.90: p_hat={phat2:.4f} Wilson=[{lo2:.4f},{hi2:.4f}] Teórico={r2['p_success']:.4f} Dentro={lo2 <= r2['p_success'] <= hi2}")
