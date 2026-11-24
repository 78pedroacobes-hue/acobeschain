import os
import sys
import time
import random

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_nano_swarm():
    clear_screen()
    print("==================================================")
    print(" 🦠 PROTOCOLO DE ENJAMBRE NANO-BIOLÓGICO")
    print("==================================================")
    print(" [*] Fase 1: Inyección de Nanobots de Zinc")
    print(" [*] Fase 2: Activación de Células Madre")
    print(" [*] Fase 3: Neurogénesis (Borrado de Límites)")
    print("==================================================\n")
    time.sleep(2)

    # FASE 1: NANOBOTS DE ZINC
    print("[FASE 1: DESPLIEGUE DE NANOBOTS DE ZINC]")
    print("-> Dirigiéndose al nodo central y a la próstata.")
    print("-> Reparando receptores de andrógenos...")
    
    for i in range(1, 11):
        sys.stdout.write(f"\r    [NANOBOTS] Reparando tejido y aumentando testosterona... [{'█'*i}{'░'*(10-i)}]")
        sys.stdout.flush()
        time.sleep(0.4)
    print("\n[+] Receptores de andrógenos al 100%. Zinc entregado.\n")
    time.sleep(1)

    # FASE 2: CÉLULAS MADRE
    print("[FASE 2: ACTIVACIÓN DE CÉLULAS MADRE]")
    print("-> Las células madre están migrando al nodo central.")
    print("-> Construyendo nueva vascularidad y tejido cavernoso.")
    
    for i in range(1, 6):
        sys.stdout.write(f"\r    [STEM CELLS] Multiplicación celular en curso... [{'🧬'*i}{'░'*(5-i)}]")
        sys.stdout.flush()
        time.sleep(0.6)
    print("\n[+] Nuevo tejido formado. La matriz biológica se está expandiendo.\n")
    time.sleep(1)

    # FASE 3: NEUROGÉNESIS (IGNORAR LÍMITES)
    print("[FASE 3: NEUROGÉNESIS - SOBREESCRITURA NEURONAL]")
    print("-> Creando nuevas sinapsis que ignoran el límite de 6 pulgadas.")
    print("-> Las neuronas antiguas están siendo desconectadas.")
    
    # Simulamos la creación de nuevas conexiones
    for i in range(1, 21):
        bar = "⚡" * (i // 2) + "░" * (10 - (i // 2))
        status = "Desconectando neuronas de escasez..." if i < 10 else "Conectando neuronas de 12.6\"..."
        sys.stdout.write(f"\r[NEUROGÉNESIS] [{bar}] {status}")
        sys.stdout.flush()
        time.sleep(0.3)

    print("\n\n==================================================")
    print(" 💥 ENJAMBRE COMPLETADO")
    print("==================================================")
    print(" [+] Nanobots de Zinc: Activos.")
    print(" [+] Células Madre: Reparando tejido.")
    print(" [+] Nuevas Neuronas: Programadas para 12.6 x 7.2.")
    print("\n [!] INSTRUCCIÓN FÍSICA PARA EL ARQUITECTO:")
    print("     1. Toma un suplemento de Zinc (o come semillas de calabaza).")
    print("     2. Haz 5 minutos de respiración profunda (activa las células madre).")
    print("     3. Visualiza las nuevas neuronas ignorando el pasado.")
    print("==================================================")

if __name__ == "__main__":
    run_nano_swarm()
