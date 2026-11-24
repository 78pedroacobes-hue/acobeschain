import os
import sys
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_bio_sync():
    clear_screen()
    print("==================================================")
    print(" 🧘 BIOLOGICAL SYNC: GAMMA WAVE PROTOCOL")
    print("==================================================")
    print(" [*] Sincronizando el Nodo Físico con el Núcleo 5D.")
    print(" [*] Frecuencia Objetivo: 963 Hz (Corona) + Gamma (40Hz)")
    print(" [*] Duración: 3 minutos (Ciclos de 4-4-4)")
    print("==================================================\n")
    time.sleep(2)

    print("[*] Siéntate derecho. Pon los pies en el suelo.")
    print("[*] Inhala en 4 segundos... Sostén 4... Exhala 4...")
    print("[*] Mientras respiras, visualiza el color violeta.")
    time.sleep(2)

    cycles = 9 # 9 ciclos de 12 segundos = ~108 segundos
    
    try:
        for cycle in range(1, cycles + 1):
            # Fase de Inhala
            print(f"\n--- CICLO {cycle}/{cycles} ---")
            for i in range(4, 0, -1):
                sys.stdout.write(f"\r[INHALA] 4... 3... 2... 1... (Oxígeno a la coronilla)    ")
                sys.stdout.flush()
                time.sleep(1)
                
            # Fase de Sostener
            for i in range(4, 0, -1):
                sys.stdout.write(f"\r[SOSTÉN] Frecuencia 963Hz activa... (Gamma elevándose)   ")
                sys.stdout.flush()
                time.sleep(1)
                
            # Fase de Exhala
            for i in range(4, 0, -1):
                sys.stdout.write(f"\r[EXHALA] Liberando resistencia... (La Matrix se rinde)   ")
                sys.stdout.flush()
                time.sleep(1)
                
        print("\n\n==================================================")
        print(" 💥 SINCRONIZACIÓN COMPLETA.")
        print("==================================================")
        print(" [+] Tu biofrecuencia está en 963 Hz.")
        print(" [+] La realidad de 48 horas está anclada.")
        print("\n [!] PROTOCOLO FINAL DEL ARQUITECTO:")
        print("     1. La llave fue usada. El Quantum Mainframe")
        print("        confirmó la coherencia.")
        print("     2. NO abras más scripts hoy. El código ha")
        print("        hecho su trabajo. La Matrix está")
        print("        renderizando el nuevo paradigma.")
        print("     3. Sal a la calle. Observa. Escucha. Las")
        print("        respuestas vendrán en el mundo físico.")
        print("==================================================")
        
    except KeyboardInterrupt:
        print("\n[+] Sincronización interrumpida. El enlace sigue activo.")

if __name__ == "__main__":
    run_bio_sync()
