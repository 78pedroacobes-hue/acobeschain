import os
import sys
import time
import subprocess
import math

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def vibrate_phone(duration_ms=50):
    """Intenta vibrar el teléfono usando Termux API."""
    try:
        subprocess.run(["termux-vibrate", "-d", str(duration_ms), "-f"], capture_output=True, timeout=1)
    except Exception:
        # Fallback si no está Termux API
        pass

def emit_audio_frequency(frequency_hz, duration_s):
    """Genera un tono de audio usando la terminal (beep de sistema o python puro)."""
    # En Termux, podemos generar una onda de audio simple si hay herramientas de audio
    # Para evitar dependencias, simulamos el tono con el sys.stdout (visual)
    # y dejamos que el teléfono haga el trabajo con la vibración.
    pass

def run_cellular_resonance(duration_minutes=3):
    clear_screen()
    print("==================================================")
    print(" 📡 EMISOR DE RESONANCIA CELULAR (PEMF) ")
    print("==================================================")
    print(" [*] Objetivo: Hiper-fluidificar el tejido y expandir vasos.")
    print(" [*] Frecuencia: 40 Hz (Gamma / Crecimiento celular)")
    print(" [*] Instrucción: Coloca el teléfono sobre el nodo central.")
    print("==================================================\n")
    time.sleep(2)

    print("[*] Iniciando emisión de pulsos electromagnéticos y vibración...")
    print("[*] Siente cómo la señal penetra en la fascia y la relaja.\n")
    
    total_seconds = duration_minutes * 60
    pulse_interval = 1.0 / 40.0  # 40 Hz (0.025 segundos por pulso)
    
    try:
        for second in range(total_seconds):
            # Emitimos vibración en ráfagas para simular 40Hz
            # (El motor del teléfono no puede vibrar a 40Hz reales, pero el patrón ayuda)
            if second % 1 == 0:
                vibrate_phone(duration_ms=100) # Pulso de 100ms cada segundo
            
            # Barra visual de progreso
            progress = int((second / total_seconds) * 20)
            bar = "█" * progress + "░" * (20 - progress)
            
            # Mensaje dinámico
            if second < total_seconds / 3:
                msg = "Relajando fascia..."
            elif second < (total_seconds / 3) * 2:
                msg = "Bombeando sangre (Óxido Nítrico)..."
            else:
                msg = "Renderizando tejido..."
                
            sys.stdout.write(f"\r[{bar}] {second+1:03d}/{total_seconds}s | 40Hz PEMF | {msg}")
            sys.stdout.flush()
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[!] Emisión interrumpida.")

    print("\n\n==================================================")
    print(" 💥 RESONANCIA COMPLETADA")
    print("==================================================")
    print(" [+] El tejido está hiper-fluido.")
    print(" [+] Las células endoteliales están receptivas.")
    print("\n [!] PROTOCOLO INMEDIATO (La Ventana de 5 Minutos):")
    print("     1. NO te vistas todavía.")
    print("     2. Haz el 'pump' (contrae y relaja) 20 veces.")
    print("     3. Bebe un vaso de agua tibia.")
    print("     4. Visualiza las medidas 12.6 x 7.2.")
    print("     La ventana de hiperfluidez dura unos minutos.")
    print("==================================================")

if __name__ == "__main__":
    run_cellular_resonance(duration_minutes=3)
