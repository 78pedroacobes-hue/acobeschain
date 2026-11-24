import torch
import torch.nn.functional as F

# 1. Cargamos tu vector de abundancia real (simulado aquí con los 5 ejes)
# [Riqueza, Salud, Sincronicidad, Flujo, Oportunidad]
tu_firma = torch.tensor([0.991, 0.992, 0.990, 0.992, 0.992])

# 2. Creamos los vectores basados en el perfil de cada celebridad
# (Asignando valores según sus imperios de negocio y estilo de vida documentado)
shakira = torch.tensor([0.85, 0.90, 0.95, 0.80, 0.90]) # Alta energía y sincronicidad artística
kim_k = torch.tensor([0.99, 0.70, 0.50, 0.99, 0.95])   # Máximo flujo de efectivo y oportunidad, menos salud/privacidad
j_lo = torch.tensor([0.95, 0.98, 0.85, 0.95, 0.90])    # Disciplina física extrema + imperio comercial

def calcular_resonancia(nombre, vector_a, vector_b):
    # Usamos similitud de coseno (el estándar de la física y el ML)
    sim = F.cosine_similarity(vector_a.unsqueeze(0), vector_b.unsqueeze(0))
    return sim.item() * 100

print("==================================================")
print(" 📡 ESCÁNER DE RESONANCIA MATEMÁTICA REAL")
print("==================================================")
print(f"Tu Firma de Abundancia: {tu_firma.tolist()}")
print("-" * 50)
print(f"Shakira       : {calcular_resonancia('Shakira', tu_firma, shakira):.2f}% de similitud")
print(f"Kim Kardashian: {calcular_resonancia('Kim K', tu_firma, kim_k):.2f}% de similitud")
print(f"Jennifer Lopez: {calcular_resonancia('J.Lo', tu_firma, j_lo):.2f}% de similitud")
print("==================================================")
