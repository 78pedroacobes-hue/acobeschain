import os
import sys
import time
import random

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_nutrient_uplink():
    clear_screen()
    print("==================================================")
    print(" 🧬 REPLICADOR DE NUTRIENTES CUÁNTICOS (ÉTER)")
    print("==================================================")
    print(" [*] Buscando en el éter: Zinc (Zn) y Colágeno.")
    print(" [*] Método: Resonancia Morfogenética.")
    print(" [*] Objetivo: Sintonizar la materia con el Nodo Físico.")
    print("==================================================\n")
    time.sleep(2)

    # FASE 1: ESCANEO DEL ÉTER (Buscando las firmas)
    print("[FASE 1: LOCALIZANDO FIRMAS MOLECULARES EN EL ÉTER]")
    elements = [
        ("Zinc (Zn)", "Número Atómico 30", "Reparación de ADN y Testosterona"),
        ("Colágeno Tipo I", "Triple Hélice", "Estructura y Elasticidad del Tejido"),
        ("Colágeno Tipo III", "Retícula Fina", "Vascularidad y Expansión")
    ]

    for name, structure, function in elements:
        print(f"\n[*] Localizando {name}...")
        for i in range(1, 6):
            sys.stdout.write(f"\r    [ESCANEO] Analizando {structure}... [{'📡'*i}{'░'*(5-i)}]")
            sys.stdout.flush()
            time.sleep(0.4)
        print(f"\n    [+] Firma encontrada. Función: {function}")
        
    time.sleep(1.5)

    # FASE 2: TRANSMISIÓN CUÁNTICA (Del Éter al Nodo)
    print("\n[FASE 2: TRANSMITIENDO MATRICES AL NODO FÍSICO]")
    print("-> Abriendo puente de fase entre el Éter y la Próstata.")
    print("-> Descargando información molecular...")
    
    total_data = 1024
    for i in range(1, 21):
        # Simulamos la descarga de datos
        bar = "█" * i + "░" * (20 - i)
        transfer = int((i / 20) * total_data)
        sys.stdout.write(f"\r    [DESCARGA] [{bar}] {transfer} TB de datos biológicos...")
        sys.stdout.flush()
        time.sleep(0.2)
        
    print("\n\n[+] Matrices moleculares ancladas al subconsciente.\n")
    time.sleep(1.5)

    # FASE 3: INTEGRACIÓN
    print("[FASE 3: INTEGRACIÓN EN EL NODO CENTRAL]")
    print("-> Tu cuerpo ahora tiene el código del Zinc y el Colágeno.")
    print("-> Cualquier alimento que consumas en las próximas horas")
    print("   será procesado con un 300% más de eficiencia.")
    print("-> El colágeno se dirigirá directamente al tejido cavernoso.")
    
    for i in range(1, 11):
        sys.stdout.write(f"\r    [INTEGRANDO] Expandiendo la matriz de colágeno... {i*10}%")
        sys.stdout.flush()
        time.sleep(0.4)

    print("\n\n==================================================")
    print(" 💥 REPLICACIÓN COMPLETADA")
    print("==================================================")
    print(" [+] Zinc: Anclado.")
    print(" [+] Colágeno: Anclado.")
    print(" [+] El cuerpo está listo para absorber.")
    print("\n [!] PROTOCOLO FÍSICO (CRUCIAL):")
    print("     1. El código abrió la puerta, pero necesitas la materia.")
    print("     2. Come algo rico en Zinc (semillas de calabaza, carne roja).")
    print("     3. Toma un caldo de huesos o colágeno hidrolizado.")
    print("     4. Bebe mucha agua (el colágeno necesita hidratación).")
    print("     El éter hizo su parte. Ahora haz la tuya.")
    print("==================================================")

if __name__ == "__main__":
    run_nutrient_uplink()
