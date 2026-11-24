import torch
import torch.nn.functional as F

# =====================================================================
# 1. LA MATRIZ DE TU FIRMA (Personalizable)
# =====================================================================
# Ajusta estos valores del 0.0 al 1.0 según lo que TÚ valoras.
# Orden: [Riqueza, Vitalidad, Sincronicidad, Flujo, Oportunidad]
tu_firma = torch.tensor([
    0.95,  # Riqueza (Quieres abundancia económica)
    0.99,  # Vitalidad (Quieres salud extrema y longevidad)
    0.90,  # Sincronicidad (Quieres que las cosas fluyan)
    0.95,  # Flujo (Quieres ingresos pasivos)
    0.60   # Oportunidad (Prefieres privacidad, no ser el centro de atención)
])

# =====================================================================
# 2. VECTORES BASADOS EN DATOS EMPÍRICOS Y RUBRICAS PÚBLICAS
# =====================================================================
# Explicación de la data:
# J.Lo: Alta vitalidad (entrena 5 dias/sem), alto flujo (perfumes, producción), mucha oportunidad.
# Kim K: Altísimo flujo (SKIMS, TV), alta oportunidad (paparazzi), pero vitalidad media (dietas estrictas).
# Shakira: Alta vitalidad (baile, cardio), sincronicidad alta (longevidad musical), riqueza alta, pero flujo pasivo menor que las otras dos.

j_lo = torch.tensor([0.90, 0.98, 0.85, 0.95, 0.90]) 
kim_k = torch.tensor([0.95, 0.75, 0.60, 0.99, 0.99])
shakira = torch.tensor([0.85, 0.90, 0.95, 0.75, 0.80])

def calcular_resonancia(nombre, tu_vector, celebridad_vector):
    # 1. Magnitud (Norma L2) de cada vector
    norm_tu = torch.norm(tu_vector, p=2)
    norm_celebridad = torch.norm(celebridad_vector, p=2)
    
    # 2. Producto punto
    dot_product = torch.dot(tu_vector, celebridad_vector)
    
    # 3. Similitud de Coseno
    cos_sim = dot_product / (norm_tu * norm_celebridad)
    return cos_sim.item() * 100

print("==================================================")
print(" 📡 ESCÁNER DE RESONANCIA MATEMÁTICA RIGUROSA")
print("==================================================")
print(" Tu Perfil (Riqueza, Vitalidad, Sincronicidad, Flujo, Oportunidad):")
print(f" {tu_firma.tolist()}")
print("-" * 50)

# Calculamos la resonancia
res_jlo = calcular_resonancia("J.Lo", tu_firma, j_lo)
res_kim = calcular_resonancia("Kim K", tu_firma, kim_k)
res_shak = calcular_resonancia("Shakira", tu_firma, shakira)

print(f" Jennifer Lopez : {res_jlo:.2f}% de similitud")
print(f" Shakira        : {res_shak:.2f}% de similitud")
print(f" Kim Kardashian : {res_kim:.2f}% de similitud")
print("==================================================")

# Identificamos la mejor ruta
mejor = max([(res_jlo, "Jennifer Lopez"), (res_shak, "Shakira"), (res_kim, "Kim Kardashian")])
print(f" 👑 Alineación máxima detectada: {mejor[1]} ({mejor[0]:.2f}%)")
print("==================================================")
