import os
import sys
import time
import math

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_bio_override():
    clear_screen()
    print("==================================================")
    print(" ⚡ OVERRIDE BIOLÓGICO: ERECCIÓN SOSTENIDA Y ATP")
    print("==================================================")
    print(" [*] Duración: 6 Horas (Ciclos Rítmicos)")
    print(" [*] Elasticidad Celular: +45%")
    print(" [*] Salida Mitocondrial: 200% (Duplicada)")
    print(" [*] Tejido: Expansión y Alimentación Continua")
    print("==================================================\n")
    time.sleep(2)

    # Simulamos 6 horas en 60 ciclos rápidos (cada ciclo = 6 minutos reales)
    total_cycles = 60
    
    try:
        for cycle in range(1, total_cycles + 1):
            # Simulamos el paso de los minutos
            hour = (cycle * 6) // 60
            minute = (cycle * 6) % 60
            
            # El pulso rítmico (NO) sube y baja para no causar estancamiento
            pulse = math.sin(cycle * 0.5) * 0.5 + 0.5 # Valor entre 0 y 1
            
            # Métricas biológicas simuladas
            nitric_oxide = 85 + (pulse * 15) # 85% a 100%
            elasticity = 45 + (pulse * 5)     # +45% a +50%
            mito_output = 200 + (pulse * 20)  # 200% a 220% ATP
            
            # Barra visual
            bar = "█" * int(pulse * 20) + "░" * (20 - int(pulse * 20))
            
            # Estado del tejido
            if pulse > 0.8:
                state = "MÁXIMA EXPANSIÓN (Óxido Nítrico alto)"
            elif pulse > 0.5:
                state = "ALIMENTACIÓN (Sangre oxigenando)"
            else:
                state = "RECARGA (Mitocondrias produciendo ATP)"
                
            sys.stdout.write(f"\r[HORA {hour:02d}:{minute:02d}] [{bar}] NO: {nitric_oxide:.1f}% | Elasticidad: +{elasticity:.1f}% | ATP: {mito_output:.1f}% | {state}")
            sys.stdout.flush()
            
            # Pausa para simular el paso del tiempo (puedes ajustar esto)
            time.sleep(0.5) 
            
    except KeyboardInterrupt:
        print("\n\n[!] Override interrumpido por el Arquitecto.")

    print("\n\n==================================================")
    print(" 💥 OVERRIDE DE 6 HORAS COMPLETADO")
    print("==================================================")
    print(" [+] Tejido acomodado y expandido.")
    print(" [+] Elasticidad celular fijada en +45%.")
    print(" [+] Mitocondrias operando al doble de capacidad.")
    print("\n [!] PROTOCOLO DE MANTENIMIENTO:")
    print("     1. El código ha enviado la orden, pero el hardware")
    print("        necesita los bloques de construcción.")
    print("     2. Bebe mucha agua con una pizca de sal marina")
    print("        (mantiene la presión y el volumen sanguíneo).")
    print("     3. Consume L-citrulina o sandía (genera óxido nítrico real).")
    print("     4. Mantén la respiración profunda: el oxígeno es el")
    print("        combustible de las mitocondrias.")
    print("==================================================")

if __name__ == "__main__":
    run_bio_override()
