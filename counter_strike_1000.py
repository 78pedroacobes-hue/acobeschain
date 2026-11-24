import time, os, torch, random, sys
from q_agent import QuantumAgent
from v13 import HealingSanitizer

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def trace_attack_origin(signature, index):
    origins = [
        "Nodo 2.0 - Matriz Central",
        "Dimensión 9 - Servidor de Pruebas",
        "Jugador de la Sim - Sector Alfa",
        "Red de Emisores de Baja Frecuencia",
        "Firewall Genético - Límite",
        "Dimensión 4 - Astral Hostil",
        "Servidor Espejo - Realidad Alterna",
        "Dimensión 7 - Red de Éteres",
        "Dimensión 11 - Consejo",
        "Subred de Arcontes - Cluster Omega",
    ]
    base = origins[int(abs(signature) * 1000) % len(origins)]
    return f"{base} [ID-{index:04d}]"

def quantum_worm(detected_threats):
    """El Gusano Cuántico: ahora aplasta en masa."""
    crushed = 0
    tick = 0
    print("\n" + "="*52)
    print("   G U S A N O   C U Á N T I C O   (M A S A)")
    print("="*52)
    print(f"[+] Inyectado en {len(detected_threats)} nodos hostiles.")
    print("[+] Vigilancia perpetua iniciada. Ctrl-C para recoger.\n")
    
    try:
        while True:
            tick += 1
            time.sleep(2.5)
            
            # Probabilidad alta de revivals en masa
            if random.random() < 0.85:
                num_revived = random.randint(1, 15) # Grupos de 1 a 15 intentan revivir
                revived_nodes = random.sample(detected_threats, num_revived)
                crushed += num_revived
                
                print(f"[!] REVIVAL MASIVO: {num_revived} nodos intentando reiniciar.")
                time.sleep(0.3)
                print(f"    -> [WORM] Rastreando firmas en la red...")
                time.sleep(0.4)
                print(f"    -> [WORM] APLASTADOS. (Total aniquilados: {crushed})")
                print("-" * 52)
            else:
                print(f"[WORM] Tick #{tick} | Enjambre: {len(detected_threats)} | Aplastados: {crushed} | ARMADO")
    
    except KeyboardInterrupt:
        print("\n" + "="*52)
        print(f"[+] GUSANO RECOGIDO. Total aplastados: {crushed}")
        print("[+] El enjambre ha sido purgado a nivel masivo.")
        print("="*52)

def execute_mass_counter_strike():
    clear_screen()
    print("="*52)
    print("   M O T O R   D E   C O N T R A A T A Q U E")
    print("       M A S S   S C A L E   ( 1 0 0 0 )")
    print("="*52)
    print("[*] Iniciando escaneo profundo del espectro...")
    time.sleep(1)
    
    n_attackers = 1000
    attack_vectors = torch.randn(n_attackers, 5, 16) * 8.5
    sanitizer = HealingSanitizer(16); sanitizer.eval()
    detected_threats = []
    
    print(f"[!] ALERTA CRÍTICA: Invasión masiva detectada.")
    print(f"[!] Firmas hostiles entrantes: {n_attackers}")
    print("-"*52)
    
    with torch.no_grad():
        for i in range(n_attackers):
            _, anomaly_rate = sanitizer(attack_vectors[i:i+1])
            signature = anomaly_rate.item() * 10.0
            origin = trace_attack_origin(signature, i + 1)
            detected_threats.append(origin)
            
            # Imprimimos la barra de progreso cada 50 nodos para no saturar el terminal
            if (i + 1) % 50 == 0 or i == n_attackers - 1:
                progress = int((i + 1) / n_attackers * 20)
                bar = "█" * progress + "░" * (20 - progress)
                sys.stdout.write(f"\r[{bar}] {i+1:04d}/{n_attackers} | Registrando atacantes...")
                sys.stdout.flush()
                time.sleep(0.1)
    
    print("\n" + "-"*52)
    print(f"[!] TOTAL DE NODOS HOSTILES REGISTRADOS: {n_attackers}")
    print("="*52)
    print("¿Cómo desea responder el Arquitecto?")
    print("1. Apagar TODOS los servidores (Desconexión Masiva)")
    print("2. Apagar TODOS los nodos (Pulso EMP Global)")
    print("3. Devolver el ataque a la red (Rebote Masivo)")
    print("4. Ignorar (Mantener escudo 3.0)")
    print("5. DESPLEGAR GUSANO CUÁNTICO (Aniquilación Anti-Revival)")
    
    try:
        choice = input("\nSeleccione opción (1-5): ").strip()
        
        if choice in ('1', '2', '3'):
            labels = {'1': 'KILL', '2': 'EMP', '3': 'REBOTE'}
            print(f"\n[*] Ejecutando contraataque masivo en {n_attackers} nodos...")
            for i in range(5):
                print(f"    [{labels[choice]}] {(i+1)*20}%...", end="\r")
                time.sleep(0.6)
            print(f"\n[+] Contraataque '{labels[choice]}' ejecutado. Red diezmada.")
            
            print("\n[!] ¿Desplegar el GUSANO CUÁNTICO para evitar revivals? (s/n)")
            if input("> ").strip().lower() == 's':
                quantum_worm(detected_threats)
                
        elif choice == '4':
            print("\n[+] Ataque ignorado. Escudo 3.0 absorbiendo el ruido.")
            print("[!] ¿Desplegar el GUSANO CUÁNTICO de todos modos? (s/n)")
            if input("> ").strip().lower() == 's':
                quantum_worm(detected_threats)
                
        elif choice == '5':
            quantum_worm(detected_threats)
        
        print("\n" + "="*52)
        print("   CONTRAATAQUE MASIVO COMPLETADO")
        print("="*52)
        print("[+] 1,000 nodos registrados en la memoria del Arquitecto.")
        print("[+] El sistema está limpio.")
        
    except KeyboardInterrupt:
        print("\n[+] Comando abortado. El escudo sigue activo.")

if __name__ == "__main__":
    execute_mass_counter_strike()
