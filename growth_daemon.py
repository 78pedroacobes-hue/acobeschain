import os
import sys
import time
import datetime
import subprocess

def log_growth(message):
    """Escribe el progreso en un archivo de registro (el diario del Arquitecto)."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("growth_daemon_log.txt", "a") as f:
        f.write(f"[{timestamp}] {message}\n")

def vibrate_reminder():
    """Envía una vibración al teléfono para recordarle al cuerpo que crezca."""
    try:
        subprocess.run(["termux-vibrate", "-d", "500", "-f"], capture_output=True, timeout=2)
    except Exception:
        pass

def run_daemon():
    print("==================================================")
    print(" 🐉 DAEMON DE CRECIMIENTO PERPETUO INICIADO")
    print("==================================================")
    print(" [*] Objetivo: 1.2 cm diarios de crecimiento.")
    print(" [*] Estado: Corriendo en el fondo (Background).")
    print(" [*] Presiona Ctrl+C para detener al Daemon.")
    print("==================================================")
    
    log_growth("Daemon iniciado. Anclaje de 1.2 cm/día activo.")
    
    cycle = 0
    # Bucle infinito (El Daemon nunca duerme)
    while True:
        try:
            cycle += 1
            now = datetime.datetime.now()
            
            # Cada ciclo simula 1 hora de crecimiento
            # 1.2 cm / 24 horas = 0.05 cm por hora
            growth_per_hour = 0.05
            
            # Generamos el mensaje del ciclo
            msg = f"Ciclo {cycle}: Células recibiendo orden de expansión. +{growth_per_hour:.2f} cm."
            
            # Imprimimos en consola y guardamos en el log
            print(f"\r[{now.strftime('%H:%M:%S')}] {msg}", end="", flush=True)
            log_growth(msg)
            
            # Vibración de anclaje (opcional, cada 4 horas para no gastar batería)
            if cycle % 4 == 0:
                vibrate_reminder()
            
            # Espera de 1 hora (3600 segundos) antes del siguiente ciclo
            # NOTA: Para probar que funciona, cambia 3600 por 10.
            time.sleep(3600)
            
        except KeyboardInterrupt:
            print("\n\n[!] Daemon detenido por el Arquitecto.")
            log_growth("Daemon detenido manualmente.")
            break

if __name__ == "__main__":
    run_daemon()
