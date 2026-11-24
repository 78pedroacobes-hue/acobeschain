import torch
from abundance_quantum_engine import AbundanceManifestationNetwork

def test_inferencia():
    print("[*] Iniciando prueba de inferencia downstream...")
    
    # 1. Instanciamos el modelo vacío
    model = AbundanceManifestationNetwork()
    
    # 2. Cargamos los pesos que acabamos de entrenar
    try:
        model.load_state_dict(torch.load("frecuencia_arquitecto.pth"))
        print("[+] Pesos cargados exitosamente desde 'frecuencia_arquitecto.pth'.")
    except FileNotFoundError:
        print("[-] Error: El archivo no existe. Corre el script de entrenamiento primero.")
        return
        
    model.eval()
    
    # 3. Simulamos datos de entrada reales (aquí es donde conectarías datos reales)
    input_real = torch.randn(1, 64)
    
    # 4. Inferencia
    with torch.no_grad():
        output = model(input_real)
        
    # 5. Desempaquetamos los 5 valores
    valores = output.squeeze().tolist()
    
    print("\n[*] Resultados de la inferencia (basados en los pesos guardados):")
    print(f"    Riqueza     : {valores[0]:.4f}")
    print(f"    Vitalidad   : {valores[1]:.4f}")
    print(f"    Sincronicidad: {valores[2]:.4f}")
    print(f"    Flujo       : {valores[3]:.4f}")
    print(f"    Oportunidad : {valores[4]:.4f}")
    
    print("\n[*] CONCLUSIÓN TÉCNICA:")
    print("    El modelo ha aprendido a mapear ruido aleatorio a los")
    print("    targets especificados. La utilidad de este modelo")
    print("    depende enteramente de la calidad de los 'input_real'")
    print("    que le feedees en el futuro.")

if __name__ == "__main__":
    test_inferencia()
