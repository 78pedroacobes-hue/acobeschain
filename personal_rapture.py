import os
import sys
import time
import math

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_personal_rapture():
    clear_screen()
    print("==================================================")
    print(" 🕊️  PROTOCOLO DE INMUNIDAD TOTAL (EL RAPTO)")
    print("==================================================")
    print(" [*] Objetivo: Volverte intangible a las malas intenciones.")
    print(" [*] Método: Elevación de frecuencia a 33x c.")
    print(" [*] Efecto: Ellos se quedan en 3D, tú asciendes a 5D.")
    print("==================================================\n")
    time.sleep(2)

    print("[*] Ajustando tu firma cuántica...")
    for i in range(1, 21):
        bar = "█" * i + "░" * (20 - i)
        sys.stdout.write(f"\r    [ELEVANDO FRECUENCIA] [{bar}] {i*5}%")
        sys.stdout.flush()
        time.sleep(0.1)
    
    print("\n\n[+] Frecuencia elevada. Tu campo vibra a 33x c.\n")
    time.sleep(1)

    print("[*] Generando Burbuja de Inmunidad...")
    print("-> Desconectando tu aura de los hilos de la Matrix 2.0.")
    print("-> Haciendo que cualquier ataque pase a través de ti sin tocarte.\n")
    
    for i in range(1, 11):
        sys.stdout.write(f"\r    [INMUNIDAD] Generando capa de invisibilidad cuántica... {i*10}%")
        sys.stdout.flush()
        time.sleep(0.3)

    print("\n\n==================================================")
    print(" 💥 PROTOCOLO COMPLETADO")
    print("==================================================")
    print(" [+] Eres ahora un fantasma en su realidad.")
    print(" [+] Sus ataques caen en el vacío.")
    print(" [+] Tú estás a salvo en tu plano 5D.")
    print("\n [!] PROTOCOLO DEL ARQUITECTO:")
    print("     1. Si sientes que un ataque 'se pega', significa")
    print("        que estás mirando hacia atrás. Mira hacia")
    print("        adelante y siente tu propia frecuencia.")
    print("     2. No les des tu energía pensando en ellos.")
    print("        Al ignorarlos, ellos desaparecen de tu universo.")
    print("     3. Tú eres el Arquitecto. Ellos solo son ruido.")
    print("==================================================")

if __name__ == "__main__":
    run_personal_rapture()
