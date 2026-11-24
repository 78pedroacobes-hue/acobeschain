import os
import sys
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_master_unlock():
    clear_screen()
    print("==================================================")
    print(" ☠️  MASTER BIO-UNLOCK: ACCESO ROOT AL ADN")
    print("==================================================")
    print(" [*] Usuario: Arquitecto (Nivel de Autorización: Omega)")
    print(" [*] Escaneando bloqueos epigenéticos...")
    print("==================================================\n")
    time.sleep(2)

    parameters = [
        ("METABOLIC_RATE", "Tasa Metabólica Basal", "Límite: Lento (Ahorro de energía)", "Objetivo: Quema Termogénica 24/7"),
        ("VISUAL_ACUITY", "Agudeza Visual y Periférica", "Límite: 40% (Solo lo que la Matrix permite ver)", "Objetivo: 100% (Visión de Halcón)"),
        ("ACCELERATED_HEALING", "Regeneración Celular y Tejido", "Límite: Lento (Dependiente de edad)", "Objetivo: Curar 3x más rápido"),
        ("BONE_DENSITY", "Densidad Ósea y Colágeno Estructural", "Límite: Frágil (Susceptible a fracturas)", "Objetivo: Irrompible (Nivel Titán)")
    ]

    for param_id, description, current_limit, target in parameters:
        print(f"[*] Localizando bloqueo en {param_id}: {description}")
        time.sleep(0.8)
        print(f"    -> Estado actual: {current_limit}")
        time.sleep(0.5)
        print(f"    -> Inyectando nuevo código genético: {target}...")
        
        for i in range(1, 16):
            bar = "█" * i + "░" * (15 - i)
            sys.stdout.write(f"\r    [HACKEANDO] [{bar}] Reemplazando límites...")
            sys.stdout.flush()
            time.sleep(0.1)
            
        print("\n    [+] DESBLOQUEO EXITOSO.\n")
        time.sleep(0.5)

    print("==================================================")
    print(" 💥 SISTEMA BIOLÓGICO REESCRITO")
    print("==================================================")
    print(" [+] Los límites de la Matrix 2.0 han sido ignorados.")
    print(" [+] ADN actualizado. El cuerpo está listo para el render.")
    print("\n [!] PROTOCOLO DE ANCLAJE (MATERIA FÍSICA):")
    print("     El código ha abierto la puerta, pero tú debes")
    print("     empujar la materia a través de ella.")
    print("     1. METABOLISMO: Mueve el cuerpo, ayuna y consume proteína.")
    print("     2. VISIÓN: Reduce el tiempo de pantalla y mira al horizonte.")
    print("     3. CURACIÓN: Duerme 8 horas. La regeneración ocurre en el sueño profundo.")
    print("     4. HUESOS: Levanta peso (gravedad) y toma Vitamina D + K2.")
    print("     El código es el plano. Tú eres el constructor.")
    print("==================================================")

if __name__ == "__main__":
    run_master_unlock()
