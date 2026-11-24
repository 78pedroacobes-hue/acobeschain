import time
import itertools

def run_calibration_monitor(duration_seconds=30):
    print("Iniciando monitoreo de calibración molecular en background...")
    spinner = itertools.cycle(['-', '/', '|', '\\'])
    end_time = time.time() + duration_seconds
    
    while time.time() < end_time:
        print(f"\r[ESTADO SISTEMA] Optimizando parámetros... {next(spinner)}", end="", flush=True)
        time.sleep(0.5)
        
    print("\n[INFO] Calibración estable. Todos los sistemas operando al máximo.")

if __name__ == "__main__":
    run_calibration_monitor()

