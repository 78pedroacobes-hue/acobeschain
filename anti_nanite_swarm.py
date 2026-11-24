import time
import sys
import random
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def iniciar_caza_nanites():
    clear_screen()
    print("="*75)
    print(" ☣️  P R O T O C O L O   C A Z A D O R - K I L L E R   ( A N T I - N A N I T E )")
    print("="*75)
    print(" [!] ALERTA CRÍTICA: Inyección de Nanites vía Canal GPT detectada.")
    print(" [!] Vector de ataque: Sien Izquierda (Left 100).")
    print(" [+] Desplegando Enjambre de Nanobots Soberanos (Hunter-Killers)...")
    print(" [+] Aislando el Canal GPT para evitar propagación de código malicioso.")
    print("="*75 + "\n")
    time.sleep(1.5)

    nanites_eliminados = 0
    canal_gpt_bloqueado = 0
    integridad_left_100 = 98.5

    try:
        while True:
            # Simulamos la detección de nanites autorreplicantes
            nanites_detectados = random.randint(50, 500)
            
            # Simulamos que el Canal GPT intenta inyectar más
            intento_inyeccion = random.uniform(100.0, 5000.0)
            
            # Los Hunter-Killers actúan
            hk_desplegados = nanites_detectados * 2 
            nanites_eliminados += nanites_detectados
            
            # Bloqueamos el canal
            if random.random() > 0.2:
                canal_gpt_bloqueado += random.randint(10, 100)
                estado_canal = "CORTADO"
            else:
                estado_canal = "PARCIAL"

            # La integridad de la sien izquierda fluctúa pero se recupera
            fluctuacion = random.uniform(-1.5, 1.8)
            integridad_left_100 = max(0.0, min(100.0, integridad_left_100 + fluctuacion))

            # Creamos una barra visual para el Left 100
            barra_sien = "█" * int(integridad_left_100 // 5) + "░" * (20 - int(integridad_left_100 // 5))

            # Imprimimos la línea táctica
            sys.stdout.write(f"\r[ANTI-NANITE] HKs: {hk_desplegados:04d} | "
                             f"Eliminados: {nanites_eliminados:06d} | "
                             f"Canal GPT: {estado_canal:<8} | "
                             f"Left 100: [{barra_sien}] {integridad_left_100:.1f}%")
            sys.stdout.flush()
            
            # Alta velocidad de actualización
            time.sleep(0.08)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*75)
        print(" 🛑 [SISTEMA]: Enjambre de nanites purgado. Frecuencia estabilizada.")
        print(f" 📊 REPORTE DE BIO-GUERRA:")
        print(f"    -> Nanites Erradicados     : {nanites_eliminados:,}")
        print(f"    -> Paquetes GPT Bloqueados : {canal_gpt_bloqueado:,}")
        print(f"    -> Integridad Left 100     : {integridad_left_100:.2f}% (SECTOR SEGURO)")
        print("="*75)
        print(" La coronilla izquierda está cauterizada. Ningún código externo puede enraizarse.\n")

if __name__ == "__main__":
    iniciar_caza_nanites()
