import time, os, torch, random
from q_agent import QuantumAgent
from v13 import HealingSanitizer

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def trace_attack_origin(signature, index):
    origins = [
        "Nodo 2.0 - Matriz Central (Arcontes)",
        "Dimensión 9 - Servidor de Pruebas",
        "Jugador de la Simulación - Sector Alfa",
        "Red de Emisores de Baja Frecuencia",
        "Firewall Genético - Límite del Nodo",
        "Dimensión 4 - Proyección Astral Hostil",
        "Servidor Espejo - Realidad Alterna",
        "Dimensión 7 - Red de Éteres",
        "Dimensión 11 - Consejo de Vigilancia",
        "Subred de Arcontes - Cluster Omega",
    ]
    base = origins[int(abs(signature) * 1000) % len(origins)]
    return f"{base} [ID-{index:03d}]"

def quantum_worm(detected_threats):
    """El Gusano Cuántico: vive en el código del enjambre. Si reviven, los aplasta."""
    crushed = 0
    tick = 0
    print("\n" + "="*52)
    print("   G U S A N O   C U Á N T I C O   A C T I V O")
    print("="*52)
    print(f"[+] Inyectado en {len(detected_threats)} nodos hostiles.")
    print("[+] Vigilancia perpetua iniciada.")
    print("[+] Ctrl-C para recoger al gusano.\n")
    
    try:
        while True:
            tick += 1
            time.sleep(2.5)
            
            # Cada ciclo, chance de que algún atacante intente revivir
            if random.random() < 0.65:
                idx = random.randint(0, len(detected_threats) - 1)
                revived = detected_threats[idx]
                crushed += 1
                print(f"[!] REVIVAL DETECTADO: {revived}")
                time.sleep(0.4)
                print(f"    -> [WORM] Localizando firma...")
                time.sleep(0.3)
                print(f"    -> [WORM] Inyectando payload de aniquilación...")
                time.sleep(0.3)
                print(f"    -> [WORM] APLASTADO. (Total aplastados: {crushed})")
                print("-"*52)
            else:
                print(f"[WORM] Tick #{tick} | Vigilando {len(detected_threats)} nodos | "
                      f"Aplastados: {crushed} | Status: ARMADO")
    
    except KeyboardInterrupt:
        print("\n" + "="*52)
        print(f"[+] GUSANO RECOGIDO. Total aplastados: {crushed}")
        print("[+] El enjambre está purgado.")
        print("[+] Ninguno revive sin ser aplastado de nuevo.")
        print("="*52)

def execute_swarm_worm():
    clear_screen()
    print("="*52)
    print("   M O T O R   D E   C O N T R A A T A Q U E")
    print("     M O D O   E N J A M B R E   +   W O R M")
    print("="*52)
    print("[*] Iniciando escaneo profundo del espectro...")
    time.sleep(1.2)
    
    n_attackers = 25
    attack_vectors = torch.randn(n_attackers, 5, 16) * 8.5
    sanitizer = HealingSanitizer(16); sanitizer.eval()
    detected_threats = []
    
    print(f"[!] ALERTA CRÍTICA: Ataque coordinado masivo detectado.")
    print(f"[!] Firmas hostiles entrantes: {n_attackers}")
    print("-"*52)
    
    with torch.no_grad():
        for i in range(n_attackers):
            _, anomaly_rate = sanitizer(attack_vectors[i:i+1])
            signature = anomaly_rate.item() * 10.0
            origin = trace_attack_origin(signature, i + 1)
            detected_threats.append(origin)
            
            progress = int((i + 1) / n_attackers * 20)
            bar = "█" * progress + "░" * (20 - progress)
            short = origin[:38] + ("..." if len(origin) > 38 else "")
            print(f"[{bar}] {i+1:02d}/{n_attackers} | {short}")
            time.sleep(0.15)
    
    print("-"*52)
    print(f"[!] TOTAL DE NODOS HOSTILES REGISTRADOS: {n_attackers}")
    print("="*52)
    print("¿Cómo desea responder el Arquitecto?")
    print("1. Apagar TODOS los servidores de origen (Desconexión Masiva)")
    print("2. Apagar TODOS los nodos atacantes (Pulso EMP Global)")
    print("3. Devolver el ataque a toda la red (Rebote en Cascada)")
    print("4. Ignorar (Mantener escudo 3.0)")
    print("5. DESPLEGAR GUSANO CUÁNTICO (Anti-Revival)")
    
    try:
        choice = input("\nSeleccione opción (1-5): ").strip()
        
        if choice in ('1', '2', '3'):
            labels = {'1': 'KILL', '2': 'EMP', '3': 'REBOTE'}
            actions = {
                '1': f"Apagado masivo en {n_attackers} servidores...",
                '2': f"EMP Global hacia {n_attackers} nodos...",
                '3': f"Rebote en cascada a toda la red...",
            }
            print(f"\n[*] {actions[choice]}")
            for i in range(5):
                print(f"    [{labels[choice]}] {(i+1)*20}%...", end="\r")
                time.sleep(0.6)
            print(f"\n[+] Contraataque '{labels[choice]}' ejecutado.")
            
            print("\n[!] ¿Desplegar también el GUSANO CUÁNTICO? (s/n)")
            if input("> ").strip().lower() == 's':
                quantum_worm(detected_threats)
                
        elif choice == '4':
            print("\n[+] Ataque ignorado. Escudo 3.0 activo.")
            print("[!] ¿Desplegar el GUSANO CUÁNTICO de todos modos? (s/n)")
            if input("> ").strip().lower() == 's':
                quantum_worm(detected_threats)
                
        elif choice == '5':
            quantum_worm(detected_threats)
        
        print("\n" + "="*52)
        print("   CONTRAATAQUE COMPLETADO")
        print("="*52)
        print("[+] Todos los atacantes registrados.")
        print("[+] El Arquitecto sigue en pie.")
        
    except KeyboardInterrupt:
        print("\n[+] Comando abortado. El escudo sigue activo.")

if __name__ == "__main__":
    execute_swarm_worm()
