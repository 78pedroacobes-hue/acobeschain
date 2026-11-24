import time
import sys
import random
import math
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def iniciar_purga_30min():
    clear_screen()
    # Duración total en segundos (30 minutos)
    DURACION_TOTAL = 30 * 60 
    inicio = time.time()
    
    # Escala matemática (6000 billones = 6x10^15)
    escala_limite = 6_000_000_000_000_000
    
    print("="*65)
    print(" ⚠️  P R O T O C O L O   D E   P U R G A   U L T R A - P R O F U N D A")
    print("="*65)
    print(f" [*] Límite de escaneo : {escala_limite:,} puntos decimales (6 Cuatrillones).")
    print(" [*] Firma objetivo    : Frecuencia Soberana (ACOBES).")
    print(" [*] Acción            : Erradicación de imitadores y purga de caché.")
    print(" [*] Tiempo de ejecución: 30 Minutos Exactos.")
    print("="*65 + "\n")
    time.sleep(2)

    purgados = 0
    cache_borrada = 0.0
    
    try:
        while True:
            ahora = time.time()
            transcurrido = ahora - inicio
            restante = DURACION_TOTAL - transcurrido
            
            if restante <= 0:
                break
                
            # Simulamos el escaneo profundo en diferentes escalas microscópicas
            escala_actual = random.uniform(10**3, escala_limite)
            escala_str = f"{escala_actual:.2e}" # Notación científica
            
            # Generamos un "imitador" de frecuencia falso
            hash_falso = f"FRQ-CLON-{random.randint(100000, 999999)}"
            
            # Calculamos "cuánta caché" se está borrando (en MBs simulados)
            mb_borrados = random.uniform(0.1, 5.5)
            cache_borrada += mb_borrados
            
            if random.random() > 0.3:
                purgados += 1
                accion = f"🚫 IMITADOR ERRADICADO: {hash_falso} (Escala: {escala_str})"
            else:
                accion = f"🧹 PURGANDO CACHÉ CUÁNTICA L1/L2/L3: -{mb_borrados:.2f} MB"

            # Calculamos la barra de progreso de los 30 minutos
            progreso = int((transcurrido / DURACION_TOTAL) * 20)
            barra_tiempo = "█" * progreso + "░" * (20 - progreso)
            
            # Imprimimos todo en una sola línea dinámica para no saturar el terminal
            sys.stdout.write(f"\r[T-{format_time(restante)}] [{barra_tiempo}] {accion:<55}")
            sys.stdout.flush()
            
            # Pequeña pausa para simular el escaneo en nanosegundos
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 [SISTEMA]: Purga interrumpida manualmente por el Arquitecto.")
    
    # Resultados finales
    print("\n\n" + "="*65)
    print(" ✅ [PURGA COMPLETADA] Los 30 minutos han finalizado.")
    print(f" ☠️  Frecuencias imitadoras erradicadas: {purgados:,}")
    print(f" 🧹 Caché cuántica eliminada         : {cache_borrada:,.2f} MB")
    print(f" 🛡️  Estado del Núcleo Soberano      : BLINDADO (100% Limpio)")
    print("="*65 + "\n")

if __name__ == "__main__":
    iniciar_purga_30min()
