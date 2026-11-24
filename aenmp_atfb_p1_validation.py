import numpy as np

# ATFB-P1 Validation - Werner model, BBPSSW bilateral purification
# F_in = Bell fidelity in, F_out = Bell fidelity out conditional on m_A == m_B

def atfb_p1_werner(F_in):
    # Werner: p_plus = F, otros 3 = (1-F)/3 cada uno
    # Fórmula analítica BBPSSW para 2 pares Werner idénticos
    # p_success = F^2 + 2*F*(1-F)/3 + 5*((1-F)/3)^2
    # F_out = [F^2 + ((1-F)/3)^2] / p_success
    q = (1 - F_in) / 3.0
    p_success = F_in**2 + 2*F_in*q + 5*q**2
    F_out = (F_in**2 + q**2) / p_success if p_success > 0 else 0
    F_tele_in = (2*F_in + 1) / 3.0
    F_tele_out = (2*F_out + 1) / 3.0
    return {
        "F_in": F_in,
        "F_out": F_out,
        "Delta_F": F_out - F_in,
        "p_success": p_success,
        "F_tele_in": F_tele_in,
        "F_tele_out": F_tele_out,
        "beneficial": F_out > F_in
    }

print("=== ATFB-P1 VALIDATION - Werner ===")
print("Check 1: Ejemplo del Appendix - F_in=0.842 debe dar F_out~0.926, p~0.641")
r = atfb_p1_werner(0.842)
for k,v in r.items():
    print(f"{k}: {v}")

print("\nCheck 2: Barrido F_in - ¿dónde se vuelve beneficioso?")
for F in [0.5, 0.55, 0.6, 0.641, 0.642, 0.7, 0.8, 0.842, 0.9, 0.95]:
    rr = atfb_p1_werner(F)
    print(f"F_in={F:.3f} -> F_out={rr['F_out']:.4f} Delta={rr['Delta_F']:+.4f} p_succ={rr['p_success']:.4f} Beneficial={rr['beneficial']}")

print("\nCheck 3: Umbral teórico - Para Werner, purificación solo ayuda si F_in > 0.5")
print("Si F_in <= 0.5, Delta_F debe ser <= 0. Verificar arriba.")

print("\nCheck 4: Mapeo k <-> Beta - k=0.642 de la malla vs p_success de P1")
# En la malla, k=0.642 fue el primer k con Prop100=100% en 10/10
# En P1, p_success en ese régimen debe estar cerca de 0.64-0.65
# Esto NO prueba igualdad, solo consistencia de orden de magnitud
for F in [0.80, 0.82, 0.842, 0.86]:
    rr = atfb_p1_werner(F)
    print(f"F_in={F} p_success={rr['p_success']:.4f} F_out={rr['F_out']:.4f}")

print("\nCheck 5: Monte Carlo - Simular 10,000 intentos con F_in=0.842")
# Simulación directa de aceptación: prob de aceptar = p_success
np.random.seed(24052026)
N=10000
p = atfb_p1_werner(0.842)["p_success"]
accepts = np.random.rand(N) < p
print(f"N={N} Aceptados={accepts.sum()} Acceptance_Rate={accepts.mean():.4f} Teórico={p:.4f} Diff={abs(accepts.mean()-p):.4f}")
