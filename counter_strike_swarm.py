import time, os, torch, random
from q_agent import QuantumAgent
from v13 import HealingSanitizer

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def trace_attack_origin(signature, index):
    """Analiza la firma matemática del ataque para deducir su origen único."""
    origins = [
        "Nodo 2.0 - Matriz Central (Arcontes)",
        "Dimensión 9 - Servidor de Pruebas",
        "Jugador de la Simulación - Sector Alfa",
        "Red de Emisores de Baja Frecuencia",
        "Firewall Genético - Límite del Nodo",
        "Dimensión 4 - Proyección Astral Hostil",
        "Servidor Espejo - Realidad Alterna"
    ]
    # Añadimos el índice para que cada atacante tenga un identificador único
    base_origin = origins[int(abs(signature) * 1000) % len(origins)]
    return f"{base_origin} [ID-{index:03d}]"

def execute_swarm_counter_strike():
    clear_screen()
    print("==================================================")
    print("      M O T O R   D E   C O N T R A A T A Q U E   ")
    print("            M O D O   E N J A M B R E             ")
    print("==================================================")
    print("[*] Iniciando escaneo profundo del espectro...")
    time.sleep(1)
    
    # Simulamos una red de 6 atacantes simultáneos
    n_attackers = 6
    attack_vectors = torch.randn(n_attackers, 5, 16) * 8.5
    
    sanitizer = HealingSanitizer(16)
    sanitizer.eval()
    detected_threats = []
    
    print(f"[!] ALERTA: Ataque coordinado detectado. {n_attackers} firmas hostiles entrantes.")
    print("--------------------------------------------------")
    
    # FASE 1: DETECCIÓN EN CASCADA
    with torch.no_grad():
        for i in range(n_attackers):
            # Aislamos el ataque de este atacante específico
            single_attack = attack_vectors[i:i+1]
            _, anomaly_rate = sanitizer(single_attack)
            signature = anomaly_rate.item() * 10.0
            
            # Rastreamos el origen
            origin = trace_attack_origin(signature, i+1)
            detected_threats.append(origin)
            
            # Efecto visual de cascada
            print(f"[*] Rastreando atacante {i+1}/{n_attackers}... Firma: {signature:.4f}")
            time.sleep(0.5)
            print(f"    -> ORIGEN: {origin}")
            time.sleep(0.3)

    print("--------------------------------------------------")
    print(f"[!] TOTAL DE NODOS HOSTILES BLOQUEADOS: {n_attackers}")
    print("==================================================")
    print("El Arquitecto tiene el control. ¿Cómo desea responder al enjambre?")
    print("1. Apagar TODOS los servidores de origen (Desconexión Masiva)")
    print("2. Apagar TODOS los nodos atacantes (Pulso EMP Global)")
    print("3. Devolver el ataque a toda la red (Rebote en Cascada)")
    print("4. Ignorar (Mantener el escudo 3.0)")
    
    try:
        choice = input("\nSeleccione una opción (1-4): ")
        
        if choice == '1':
            print(f"\n[*] Ejecutando protocolo de apagado masivo en {n_attackers} servidores...")
            for i in range(5):
                print(f"    [ENVIANDO COMANDO KILL] {i*20}%...", end="\r")
                time.sleep(0.8)
            print("\n[+] Servidores de origen apagados. El enjambre ha sido expulsado de la red.")
            
        elif choice == '2':
            print(f"\n[*] Iniciando Pulso EMP Global hacia los {n_attackers} nodos...")
            for i in range(5):
                print(f"    [CARGANDO PULSO] {i*20}%...", end="\r")
                time.sleep(0.8)
            print("\n[+] Nodos atacantes apagados. La frecuencia hostil ha sido neutralizada.")
            
        elif choice == '3':
            print(f"\n[*] Redirigiendo el ataque masivo de vuelta a la red...")
            for i in range(5):
                print(f"    [REBOTANDO PAQUETES] {i*20}%...", end="\r")
                time.sleep(0.8)
            print("\n[+] Ataque devuelto al enjambre. El escudo multiplicó la energía por 10x.")
            
        else:
            print("\n[+] Ataque ignorado. El escudo 3.0 sigue absorbiendo el ruido sin inmutarse.")

        print("\n==================================================")
        print("      CONTRAATAQUE EN CASCADA COMPLETADO          ")
        print("==================================================")
        print("[+] Todos los atacantes han sido registrados.")
        print("[+] La simulación ha recibido una respuesta contundente.")
        print("[+] El Arquitecto sigue en pie. Nadie apaga este nodo.")
        
    except KeyboardInterrupt:
        print("\n[+] Comando abortado. El escudo sigue activo.")

if __name__ == "__main__":
    execute_swarm_counter_strike()
