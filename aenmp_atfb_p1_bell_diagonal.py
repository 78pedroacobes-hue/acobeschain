import numpy as np
from itertools import product

# ATFB-P1 Bell-Diagonal - Matriz de densidad completa
# Base: |Phi+>, |Phi->, |Psi+>, |Psi->  en orden 0,1,2,3
# |Phi+> = (|00>+|11>)/sqrt2, |Phi-> = (|00>-|11>)/sqrt2
# |Psi+> = (|01>+|10>)/sqrt2, |Psi-> = (|01>-|10>)/sqrt2

def bell_states():
    # devuelve 4 vectores en base computacional |00>,|01>,|10>,|11>
    s = 1/np.sqrt(2)
    return [
        np.array([s,0,0,s], dtype=complex),   # Phi+
        np.array([s,0,0,-s], dtype=complex),  # Phi-
        np.array([0,s,s,0], dtype=complex),   # Psi+
        np.array([0,s,-s,0], dtype=complex),  # Psi-
    ]

BELLS = bell_states()
PHI_PLUS = BELLS[0]

def rho_from_probs(p):
    # p = [p0,p1,p2,p3] sum=1
    p = np.array(p, dtype=float); p = p / p.sum()
    rho = np.zeros((4,4), dtype=complex)
    for pi, psi in zip(p, BELLS):
        rho += pi * np.outer(psi, psi.conj())
    return rho

def werner_probs(F):
    q = (1-F)/3.0
    return [F, q, q, q]

def kron(*mats):
    out = np.array([[1]], dtype=complex)
    for m in mats:
        out = np.kron(out, m)
    return out

# CNOT: control=primer qubit, target=segundo, en base |00>,|01>,|10>,|11>
# Ojo: nuestro orden es qA1,qB1,qA2,qB2 -> necesitamos reordenar para CNOT_A (qA1->qA2) y CNOT_B (qB1->qB2)
# Mejor: construimos U total por permutación. Usamos orden de qubits [A1,B1,A2,B2]
# CNOT_A actúa en qubits 0 y 2, CNOT_B en 1 y 3. Construimos por matrices 16x16 con lógica de bits.

def build_cnot_16(control, target):
    # qubits 0..3, bit 0 = más significativo (A1)
    U = np.zeros((16,16), dtype=complex)
    for inp in range(16):
        bits = [(inp >> (3-i)) & 1 for i in range(4)]  # [A1,B1,A2,B2]
        out_bits = bits.copy()
        if bits[control] == 1:
            out_bits[target] ^= 1
        out_idx = sum(b << (3-i) for i,b in enumerate(out_bits))
        U[out_idx, inp] = 1.0
    return U

CNOT_A = build_cnot_16(0,2)  # A1 -> A2
CNOT_B = build_cnot_16(1,3)  # B1 -> B2
U_ATFB = CNOT_B @ CNOT_A

def atfb_p1_bell_diagonal(p_primary, p_aux):
    rho_p = rho_from_probs(p_primary)
    rho_a = rho_from_probs(p_aux)
    # rho_in en orden [A1,B1,A2,B2] = kron(rho_p, rho_a) -> pero kron da [A1,B1] x [A2,B2] = [A1,B1,A2,B2] correcto
    rho_in = np.kron(rho_p, rho_a)
    rho_prime = U_ATFB @ rho_in @ U_ATFB.conj().T

    # Proyector aceptación: A2,B2 en 00 o 11. Qubits 2,3
    # P_acc = I_A1B1 ⊗ (|00><00| + |11><11|)_A2B2
    P = np.zeros((16,16), dtype=complex)
    for a1b1 in range(4):
        for a2b2 in [0,3]:  # 00=0, 11=3 en 2 bits
            idx = a1b1*4 + a2b2
            P[idx, idx] = 1.0

    rho_acc = P @ rho_prime @ P.conj().T

    # Traza parcial sobre A2,B2: quedarnos con A1,B1 (primeros 2 qubits)
    # rho_tilde[i,j] = sum_{k=0..3} rho_acc[i*4+k, j*4+k]
    rho_tilde = np.zeros((4,4), dtype=complex)
    for i in range(4):
        for j in range(4):
            s = 0j
            for k in range(4):
                s += rho_acc[i*4+k, j*4+k]
            rho_tilde[i,j] = s

    p_success = np.trace(rho_tilde).real
    if p_success <= 1e-12:
        return {"p_success": 0.0, "F_out": 0.0, "rho_out": rho_tilde, "F_in_primary": p_primary[0], "F_in_aux": p_aux[0]}

    rho_out = rho_tilde / p_success
    F_out = (PHI_PLUS.conj() @ rho_out @ PHI_PLUS).real
    F_in_p = p_primary[0]
    F_in_a = p_aux[0]
    return {
        "p_success": float(p_success),
        "F_out": float(F_out),
        "F_in_primary": float(F_in_p),
        "F_in_aux": float(F_in_a),
        "Delta_F": float(F_out - F_in_p),
        "F_tele_out": float((2*F_out+1)/3),
        "beneficial": bool(F_out > F_in_p),
        "rho_out": rho_out
    }

def binom_ci(k, n, z=1.96):
    p = k/n
    se = np.sqrt(p*(1-p)/n)
    return p, p - z*se, p + z*se, se

print("=== ATFB-P1 BELL-DIAGONAL VALIDATION ===")
print("\nCheck 1: Werner idéntico F=0.842 debe reproducir validación anterior")
print("Esperado: F_out=0.877039, p=0.811524, Delta=+0.035039")
r = atfb_p1_bell_diagonal(werner_probs(0.842), werner_probs(0.842))
print(f"F_out={r['F_out']:.6f} p={r['p_success']:.6f} Delta={r['Delta_F']:+.6f} Beneficial={r['beneficial']}")

print("\nCheck 2: Werner idéntico barrido")
for F in [0.5, 0.6, 0.7, 0.842, 0.9]:
    rr = atfb_p1_bell_diagonal(werner_probs(F), werner_probs(F))
    print(f"F_in={F:.3f} -> F_out={rr['F_out']:.4f} Delta={rr['Delta_F']:+.4f} p={rr['p_success']:.4f}")

print("\nCheck 3: ASIMÉTRICO - La prueba real")
print("Primario cansado, auxiliar fresco, y viceversa")
casos = [
    ("Prim 0.85 / Aux 0.75", werner_probs(0.85), werner_probs(0.75)),
    ("Prim 0.75 / Aux 0.85", werner_probs(0.75), werner_probs(0.85)),
    ("Prim 0.90 / Aux 0.60", werner_probs(0.90), werner_probs(0.60)),
    ("Prim 0.60 / Aux 0.90", werner_probs(0.60), werner_probs(0.90)),
    ("Prim 0.65 / Aux 0.55 - ambos bajos", werner_probs(0.65), werner_probs(0.55)),
    ("Prim 0.55 / Aux 0.95 - auxiliar casi perfecto", werner_probs(0.55), werner_probs(0.95)),
]
for nombre, pp, pa in casos:
    rr = atfb_p1_bell_diagonal(pp, pa)
    print(f"{nombre}: F_out={rr['F_out']:.4f} Delta={rr['Delta_F']:+.4f} p={rr['p_success']:.4f} Benef={rr['beneficial']}")

print("\nCheck 4: Bell-diagonal NO-Werner - errores sesgados")
print("Primario con error X dominante, Auxiliar con error Z dominante")
# p = [Phi+, Phi-, Psi+, Psi-] -> Phi- = error Z, Psi+ = error X, Psi- = error Y
p_prim = [0.80, 0.05, 0.13, 0.02]  # mucho X
p_aux  = [0.80, 0.13, 0.05, 0.02]  # mucho Z
rr = atfb_p1_bell_diagonal(p_prim, p_aux)
print(f"Sesgado X/Z: F_in_prim={rr['F_in_primary']:.3f} F_out={rr['F_out']:.4f} Delta={rr['Delta_F']:+.4f} p={rr['p_success']:.4f}")

print("\nCheck 5: Monte Carlo + Intervalo de Confianza Binomial")
# Usar caso Werner 0.842 para comparar con corrida anterior
np.random.seed(24052026)
N=10000
p_theo = atfb_p1_bell_diagonal(werner_probs(0.842), werner_probs(0.842))["p_success"]
accepts = (np.random.rand(N) < p_theo).sum()
phat, lo, hi, se = binom_ci(accepts, N)
print(f"N={N} Exitos={accepts} p_hat={phat:.4f} IC95%=[{lo:.4f}, {hi:.4f}] se={se:.4f} Teórico={p_theo:.4f} Dentro_IC={lo <= p_theo <= hi}")
