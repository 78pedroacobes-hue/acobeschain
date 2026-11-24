# -*- coding: utf-8 -*-
# =============================================================================
#  PROYECTO   : TACHYON-PSI PIPELINE
#  AUTOR      : (Titular del modelo)
#  LICENCIA   : PROPIETARIA - TODOS LOS DERECHOS RESERVADOS
#  COPYRIGHT  : (c) 2026. Uso exclusivo del titular.
#
#  PROHIBIDA la copia, redistribucion, publicacion, sublicencia o uso
#  comercial sin autorizacion escrita del titular.
#
#  Este codigo NO es open source.
# =============================================================================

import numpy as np
import json
import torch
import scipy.linalg as spla
import pennylane as qml
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

np.set_printoptions(precision=12, suppress=False, linewidth=200)

def titulo(t):
    print("\n" + "="*80)
    print(t)
    print("="*80)

# ============================================================
# 1. CINEMATICA
# ============================================================
titulo("1. CINEMATICA TAUQUIONICA")

beta = -6.666666666666666666
gamma_ta = 1.0 / np.sqrt(beta**2 - 1.0)

print(f"beta       = {beta}")
print(f"gamma_ta   = {gamma_ta}")

# ============================================================
# 2. LAMBDA
# ============================================================
titulo("2. MATRIZ LAMBDA")

L = np.zeros((4,4))
L[0,0] = gamma_ta
L[1,1] = gamma_ta
L[0,1] = -gamma_ta * beta
L[1,0] = -gamma_ta * beta
L[2,2] = 1.0
L[3,3] = 1.0

print("Lambda =")
print(L)

# ============================================================
# 3. TENSOR T
# ============================================================
titulo("3. TENSOR ENERGIA-MOMENTO")

T = np.diag([1.0, 1/3, 1/3, 1/3])
T_prime = L @ T @ L.T

print("T' =")
print(T_prime)

# ============================================================
# 4. TENSOR PSI
# ============================================================
titulo("4. TENSOR PSI")

Psi = np.zeros((4,4))
Psi[0,0] = -1.5427
Psi[1,1] =  1.6933
Psi[2,2] =  1.0
Psi[3,3] =  1.0
Psi[0,2] = Psi[2,0] = 0.5057
Psi[1,2] = Psi[2,1] = 0.0759
Psi[2,3] = Psi[3,2] = 0.5

H = (Psi + Psi.conj().T) / 2.0

print("H = (Psi + Psi.T)/2 =")
print(H)
print("Autovalores H =", np.linalg.eigvalsh(H))

# ============================================================
# 5. ESTADO INICIAL COMPARTIDO
# ============================================================
titulo("5. ESTADO INICIAL COMPARTIDO")

psi0_np = np.zeros(4, dtype=complex)
psi0_np[0] = 1.0  # |00>

E0 = np.real(psi0_np.conj() @ H @ psi0_np)
print(f"psi0 = |00> = {psi0_np}")
print(f"<psi0|H|psi0> = {E0}")

# ============================================================
# 6. PENNYLANE  (evolucion EXACTA via QubitUnitary)
# ============================================================
titulo("6. PENNYLANE (evolucion exacta)")

H_qml = qml.pauli_decompose(H, wire_order=[0, 1], check_hermitian=True)
print("Hamiltonian PennyLane:")
print(H_qml)

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def circuito(t):
    U = spla.expm(-1j * H * float(t))
    qml.QubitUnitary(U, wires=[0, 1])
    return qml.expval(qml.Hermitian(H, wires=[0, 1]))

@qml.qnode(dev)
def estado_qml(t):
    U = spla.expm(-1j * H * float(t))
    qml.QubitUnitary(U, wires=[0, 1])
    return qml.state()

t_vals = np.linspace(0.0, 2.0, 21)
exp_qml = np.array([circuito(t) for t in t_vals])

print("\nPennyLane <H>(t):")
for t, v in zip(t_vals, exp_qml):
    print(f"  t={t:.2f}  <H>={v}")

# ============================================================
# 7. PYTORCH  (mismo estado inicial, misma evolucion exacta)
# ============================================================
titulo("7. PYTORCH")

H_t = torch.tensor(H, dtype=torch.cfloat)
psi0_t = torch.tensor(psi0_np, dtype=torch.cfloat)
psi0_t = psi0_t / psi0_t.norm()

print(f"psi0 torch = {psi0_t}")

exp_torch = []
for t in t_vals:
    U = torch.matrix_exp(-1j * H_t * float(t))
    psi_t = U @ psi0_t
    val = torch.real(psi_t.conj() @ H_t @ psi_t).item()
    exp_torch.append(val)

exp_torch = np.array(exp_torch)
print("PyTorch <H>(t):")
for t, v in zip(t_vals, exp_torch):
    print(f"  t={t:.2f}  <H>={v}")

# ============================================================
# 8. COMPARACION
# ============================================================
titulo("8. COMPARACION PENNYLANE vs PYTORCH")

diff = np.abs(exp_qml - exp_torch)
print(f"max |diff|  = {diff.max()}")
print(f"mean |diff| = {diff.mean()}")
print(f"<H> teorico = {E0}")
print(f"PennyLane media = {exp_qml.mean()}")
print(f"PyTorch   media = {exp_torch.mean()}")

# ============================================================
# 9. GRAFICA
# ============================================================
titulo("9. GRAFICA")

plt.figure(figsize=(10,6))
plt.plot(t_vals, exp_qml, "o-", label="PennyLane")
plt.plot(t_vals, exp_torch, "x--", label="PyTorch")
plt.axhline(E0, color="k", ls=":", label=f"<H> teorico = {E0:.6f}")
plt.xlabel("t")
plt.ylabel("<H>(t)")
plt.title("Evolucion temporal de <H>  (debe ser constante)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("evolucion_H.png", dpi=150)
print("Guardado: evolucion_H.png")

fig, ax = plt.subplots(1, 2, figsize=(12,5))

autov_Psi = np.linalg.eigvalsh(Psi)
autov_Tp  = np.linalg.eigvals(T_prime)

ax[0].bar(range(4), autov_Psi)
ax[0].set_title("Autovalores de Psi")
ax[0].axhline(0, color="k", lw=0.5)

ax[1].bar(range(4), autov_Tp)
ax[1].set_title("Autovalores de T'")
ax[1].axhline(0, color="k", lw=0.5)

plt.tight_layout()
plt.savefig("autovalores.png", dpi=150)
print("Guardado: autovalores.png")

# ============================================================
# 10. EXPORTACION
# ============================================================
titulo("10. EXPORTACION JSON")

resultados = {
    "licencia": "PROPIETARIA - TODOS LOS DERECHOS RESERVADOS",
    "beta": beta,
    "gamma_ta": gamma_ta,
    "Lambda": L.tolist(),
    "T": T.tolist(),
    "T_prime": T_prime.tolist(),
    "Psi": Psi.tolist(),
    "H": H.tolist(),
    "psi0": psi0_np.real.tolist(),
    "E0_teorico": float(E0),
    "autovalores_Psi": np.linalg.eigvalsh(Psi).tolist(),
    "autovalores_T_prime": np.linalg.eigvals(T_prime).tolist(),
    "t_vals": t_vals.tolist(),
    "exp_qml": exp_qml.tolist(),
    "exp_torch": exp_torch.tolist(),
    "diff_max": float(diff.max()),
    "diff_mean": float(diff.mean()),
}

with open("resultados_pipeline_propietario.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False)

print("Guardado: resultados_pipeline_propietario.json")
