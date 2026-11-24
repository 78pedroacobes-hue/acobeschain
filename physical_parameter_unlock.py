import os
import sys
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_parameter_unlock():
    clear_screen()
    print("==================================================")
    print(" 🔓 SISTEMA DE DESBLOQUEO DE PARÁMETROS (ROOT)")
    print("==================================================")
    print(" [*] Usuario: Arquitecto (Root Access Granted)")
    print(" [*] Escaneando bloqueos en la matriz física...")
    print("==================================================\n")
    time.sleep(2)

    # Los parámetros bloqueados por la Matrix 2.0
    parameters = [
        ("ANDROGEN_RECEPTORS", "Sensibilidad a la testosterona", "Límite actual: 60%", "Objetivo: 100%"),
        ("IGF-1_HORMONE", "Factor de crecimiento (Tejido)", "Límite actual: 40%", "Objetivo: 95%"),
        ("NEUROPLASTICITY", "Reescritura de límites mentales", "Límite actual: 30%", "Objetivo: 100%"),
        ("MITOCHONDRIA_OUTPUT", "Energía celular y ATP", "Límite actual: 50%", "Objetivo: 100%"),
        ("TELOMERASE_ENZYME", "Protección de los telómeros (Longevidad)", "Límite actual: 20%", "Objetivo: 80%")
    ]

    for param_id, description, current_limit, target in parameters:
        print(f"[*] Analizando {param_id}: {description}...")
        time.sleep(0.5)
        print(f"    -> Detectado {current_limit}. Buscando el código de bloqueo...")
        time.sleep(0.5)
        
        # Simulación del desbloqueo
        for i in range(1, 11):
            sys.stdout.write(f"\r    [HACKEANDO] [{ '█'*i }{ '░'*(10-i) }] Sobrescribiendo parámetros...")
            sys.stdout.flush()
            time.sleep(0.2)
            
        print(f"\n    [+] DESBLOQUEADO. Nuevo límite establecido: {target}\n")
        time.sleep(0.5)

    print("==================================================")
    print(" 💥 ACCESO ROOT COMPLETADO")
    print("==================================================")
    print(" [+] Todos los parámetros biológicos han sido liberados.")
    print(" [+] Tu epigenética ahora está receptiva al cambio.")
    print("\n [!] PROTOCOLO DE ANCLAJE FÍSICO (CRUCIAL):")
    print("     El software ya desbloqueó las puertas, pero el")
    print("     hardware necesita materia para ejecutar el código.")
    print("     Para mantener estos parámetros al 100%, debes:")
    print("     1. ZINC y MAGNESIO: Para los receptores de andrógenos.")
    print("     2. PROTEÍNA y SUEÑO: Para el IGF-1 y la mitocondria.")
    print("     3. AYUNO: Para activar la autofagia y la neuroplasticidad.")
    print("     4. SOL: Para la testosterona y la longevidad.")
    print("     La Matrix 2.0 no puede volver a bloquearlos si")
    print("     cumples con estas 4 reglas.")
    print("==================================================")

if __name__ == "__main__":
    run_parameter_unlock()
