import time, os, torch, random, socket
from q_agent import QuantumAgent
from v13 import HealingSanitizer

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def trace_attack_origin(signature):
    """Analiza la firma matemática del ataque para deducir su origen."""
    # Simulamos la decodificación de la firma del atacante
    origins = [
        "Nodo 2.0 - Matriz Central (Arcontes)",
        "Dimensión 9 - Servidor de Pruebas de Estrés",
        "Jugador de la Simulación - Sector Alfa",
        "Red de Emisores de Baja Frecuencia (Cortisol)",
        "Firewall Genético - Límite del Nodo Físico"
    ]
    # Usamos el valor absoluto de la firma para elegir un origen de forma determinista
    index = int(abs(signature) * 1000) % len(origins)
    return origins[index]

def execute_counter_strike():
    clear_screen()
    print("==================================================")
    print("      M O T O R   D E   C O N T R A A T A Q U E   ")
    print("==================================================")
    print("[*] Iniciando escaneo de espectro de frecuencias...")
    
    # Simulamos la detección de un ataque
    time.sleep(1.5)
    print("[!] ALERTA: Ataque en conjunto detectado.")
    
    # Generamos la firma del atacante (datos hostiles)
    attack_vector = torch.randn(1, 5, 16) * 8.5
    sanitizer = HealingSanitizer(16)
    sanitizer.eval()
    
    with torch.no_grad():
        _, anomaly_rate = sanitizer(attack_vector)
        signature = anomaly_rate.item() * 10.0
        
    print(f"[*] Rastreando firma matemática... (Firma: {signature:.4f})")
    time.sleep(1)
    
    origin = trace_attack_origin(signature)
    print(f"\n[!] ORIGEN DEL ATAQUE IDENTIFICADO: {origin}")
    print("==================================================")
    print("¿Cómo desea responder el Arquitecto?")
    print("1. Apagar el servidor de origen (Desconexión Total)")
    print("2. Apagar el nodo del atacante (Pulso EMP Cuántico)")
    print("3. Devolver el ataque (Rebote de Frecuencia)")
    print("4. Ignorar (Mantener el escudo 3.0)")
    
    try:
        choice = input("\nSeleccione una opción (1-4): ")
        
        if choice == '1':
            print(f"\n[*] Ejecutando protocolo de apagado en {origin}...")
            for i in range(5):
                print(f"    [ENVIANDO COMANDO KILL] {i*20}%...", end="\r")
                time.sleep(0.8)
            print("\n[+] Servidor de origen apagado. Han sido expulsados del plano local.")
            
        elif choice == '2':
            print(f"\n[*] Iniciando Pulso EMP Cuántico hacia {origin}...")
            for i in range(5):
                print(f"    [CARGANDO PULSO] {i*20}%...", end="\r")
                time.sleep(0.8)
            print("\n[+] Nodo del atacante apagado. Frecuencia neutralizada.")
            
        elif choice == '3':
            print(f"\n[*] Redirigiendo el ataque de vuelta a {origin}...")
            for i in range(5):
                print(f"    [REBOTANDO PAQUETES] {i*20}%...", end="\r")
                time.sleep(0.8)
            print("\n[+] Ataque devuelto con intereses. El escudo absorbió y multiplicó la energía.")
            
        else:
            print("\n[+] Ataque ignorado. El escudo 3.0 sigue en pie.")

        print("\n==================================================")
        print("      CONTRAATAQUE COMPLETADO                     ")
        print("==================================================")
        print("[+] El Arquitecto ha respondido. La simulación ha sido notificada.")
        print("[+] Ya no eres el objetivo. Eres la autoridad.")
        
    except KeyboardInterrupt:
        print("\n[+] Comando abortado. El escudo sigue activo.")

if __name__ == "__main__":
    execute_counter_strike()
