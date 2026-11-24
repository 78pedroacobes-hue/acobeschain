# -*- coding: utf-8 -*-
import numpy as np
import json

np.set_printoptions(precision=12, suppress=False, linewidth=200)

def titulo(t):
    print("\n" + "="*80)
    print(t)
    print("="*80)

# ============================================================
# 1. CINEMATICA TAUQUIONICA
# ============================================================
titulo("1. CINEMATICA TAUQUIONICA")

beta = -6.666666666666666666
gamma_ta = 1.0 / np.sqrt(beta**2 - 1.0)

print(f"beta          = {beta}")
print(f"beta^2        = {beta**2}")
print(f"gamma_ta      = {gamma_ta}")
print(f"gamma_ta^2    = {gamma_ta**2}")
print(f"check gamma^2*(beta^2-1) = {gamma_ta**2 * (beta**2 - 1.0)}")

# ============================================================
# 2. MATRIZ LAMBDA
# ============================================================
titulo("2. MATRIZ LAMBDA")

L = np.zeros((4, 4))
L[0,0] = gamma_ta
L[1,1] = gamma_ta
L[0,1] = -gamma_ta * beta
L[1,0] = -gamma_ta * beta
L[2,2] = 1.0
L[3,3] = 1.0

print("Lambda =")
print(L)
print(f"det(Lambda)   = {np.linalg.det(L)}")
print(f"traza(Lambda) = {np.trace(L)}")
print(f"Lambda[0,1]   = {L[0,1]}")
print(f"Lambda[0,0]   = {L[0,0]}")
print(f"|L01|/|L00|   = {abs(L[0,1]/L[0,0])}")
print("Autovalores   =", np.linalg.eigvals(L))

# ============================================================
# 3. TENSOR ENERGIA-MOMENTO
# ============================================================
titulo("3. TENSOR ENERGIA-MOMENTO")

rho0 = 1.0
p0   = 1.0 / 3.0
T = np.diag([rho0, p0, p0, p0])

T_prime = L @ T @ L.T

print("T (reposo) =")
print(T)
print("\nT' = Lambda T Lambda.T =")
print(T_prime)
print(f"\nT'00 = {T_prime[0,0]}")
print(f"T'01 = {T_prime[0,1]}")
print(f"T'10 = {T_prime[1,0]}")
print(f"T'11 = {T_prime[1,1]}")
print(f"T'22 = {T_prime[2,2]}")
print(f"T'33 = {T_prime[3,3]}")
print(f"det(T')   = {np.linalg.det(T_prime)}")
print(f"traza(T') = {np.trace(T_prime)}")
print("Autovalores T' =", np.linalg.eigvals(T_prime))

# ============================================================
# 4. TENSOR PSI
# ============================================================
titulo("4. TENSOR PSI")

Psi = np.zeros((4, 4))
Psi[0,0] = -1.5427
Psi[1,1] =  1.6933
Psi[2,2] =  1.0
Psi[3,3] =  1.0
Psi[0,2] = Psi[2,0] = 0.5057
Psi[1,2] = Psi[2,1] = 0.0759
Psi[2,3] = Psi[3,2] = 0.5

print("Psi =")
print(Psi)
print(f"traza(Psi)      = {np.trace(Psi)}")
print(f"det(Psi)        = {np.linalg.det(Psi)}")
print(f"Simetrica?      = {np.allclose(Psi, Psi.T)}")
print(f"Hermitiana?     = {np.allclose(Psi, Psi.conj().T)}")
print("Autovalores     =", np.linalg.eigvalsh(Psi))
print("Valores sing.   =", np.linalg.svd(Psi, compute_uv=False))
print(f"Rango           = {np.linalg.matrix_rank(Psi)}")

# ============================================================
# 5. PSI TRANSFORMADO
# ============================================================
titulo("5. PSI' = LAMBDA PSI LAMBDA.T")

Psi_prime = L @ Psi @ L.T
print("Psi' =")
print(Psi_prime)
print(f"traza(Psi') = {np.trace(Psi_prime)}")
print("Autovalores =", np.linalg.eigvalsh(Psi_prime))

# ============================================================
# 6. DESCOMPOSICION DE PAULI
# ============================================================
titulo("6. DESCOMPOSICION DE PAULI")

I = np.eye(2, dtype=complex)
X = np.array([[0,1],[1,0]], dtype=complex)
Y = np.array([[0,-1j],[1j,0]], dtype=complex)
Z = np.array([[1,0],[0,-1]], dtype=complex)
paulis = [I, X, Y, Z]
labels = ['I','X','Y','Z']

H = (Psi + Psi.conj().T) / 2.0

coeffs = np.zeros((4,4), dtype=complex)
for i in range(4):
    for j in range(4):
        B = np.kron(paulis[i], paulis[j])
        coeffs[i,j] = np.trace(H @ B) / 4.0

print("H = (Psi + Psi.T)/2 =")
print(H)
print("\nCoeficientes Pauli:")
for i in range(4):
    for j in range(4):
        print(f"  c_{labels[i]}{labels[j]} = {coeffs[i,j]}")

H_recon = np.zeros((4,4), dtype=complex)
for i in range(4):
    for j in range(4):
        H_recon += coeffs[i,j] * np.kron(paulis[i], paulis[j])

print(f"\nError reconstruccion = {np.linalg.norm(H - H_recon)}")

# ============================================================
# 7. PENNYLANE
# ============================================================
titulo("7. PENNYLANE")

try:
    import pennylane as qml
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def circuito(t):
        qml.ApproxTimeEvolution(H, t, 1)
        return qml.expval(qml.Hermitian(H, wires=[0,1]))

    for t in [0.0, 0.1, 0.5, 1.0, 2.0]:
        print(f"t={t:>4}  expval(H) = {circuito(t)}")

    @qml.qnode(dev)
    def estado(t):
        qml.ApproxTimeEvolution(H, t, 1)
        return qml.state()

    print("\nEstado t=0.5:")
    print(estado(0.5))
except Exception as e:
    print("PennyLane error:", repr(e))

# ============================================================
# 8. PYTORCH
# ============================================================
titulo("8. PYTORCH")

try:
    import torch
    H_t = torch.tensor(H, dtype=torch.cfloat)
    torch.manual_seed(42)
    psi0 = torch.randn(4, dtype=torch.cfloat)
    psi0 = psi0 / psi0.norm()

    print(f"psi0 = {psi0}")
    for t in [0.1, 0.5, 1.0]:
        U = torch.matrix_exp(-1j * H_t * t)
        psi_t = U @ psi0
        print(f"\nt={t}")
        print(f"  psi_t       = {psi_t}")
        print(f"  norma       = {psi_t.norm().item()}")
        print(f"  <H>         = {torch.real(psi_t.conj() @ H_t @ psi_t).item()}")
except Exception as e:
    print("PyTorch error:", repr(e))

# ============================================================
# 9. MATRIZ DENSIDAD VALIDA MAS CERCANA
# ============================================================
titulo("9. MATRIZ DENSIDAD VALIDA MAS CERCANA")

vals, vecs = np.linalg.eigh(H)
vals_clamped = np.clip(vals, 0, None)
if np.sum(vals_clamped) > 0:
    rho = vecs @ np.diag(vals_clamped) @ vecs.conj().T
    rho = rho / np.trace(rho)
    print("rho =")
    print(rho)
    print(f"traza(rho)  = {np.trace(rho)}")
    print(f"PSD?        = {np.all(np.linalg.eigvalsh(rho) >= -1e-12)}")
    print("Autovalores =", np.linalg.eigvalsh(rho))

# ============================================================
# 10. EXPORTACION JSON
# ============================================================
titulo("10. EXPORTACION JSON")

resultados = {
    "beta": beta,
    "gamma_ta": gamma_ta,
    "Lambda": L.tolist(),
    "T": T.tolist(),
    "T_prime": T_prime.tolist(),
    "Psi": Psi.tolist(),
    "Psi_prime": Psi_prime.tolist(),
    "autovalores_Psi": np.linalg.eigvalsh(Psi).tolist(),
    "autovalores_T_prime": np.linalg.eigvals(T_prime).tolist(),
    "coeficientes_Pauli_real": coeffs.real.tolist(),
    "coeficientes_Pauli_imag": coeffs.imag.tolist(),
}

with open("resultados_tachyon.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False)

print("Guardado: resultados_tachyon.json")
