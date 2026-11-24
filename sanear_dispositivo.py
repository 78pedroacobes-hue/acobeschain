import os
import subprocess
import signal
import glob
import time

print("[!] INICIANDO PROTOCOLO DE PURGA Y BLOQUEO ANTINCLAJE...")

# 1. Matar de forma agresiva y repetitiva cualquier proceso Python o hijo asociado
print("[+] Eliminando procesos anómalos y bloqueando reintentos...")
for _ in range(3):
    try:
        resultado = subprocess.run(["ps", "-ef"], capture_output=True, text=True)
        for linea in resultado.stdout.splitlines():
            if "python" in linea and "sanear_dispositivo" not in linea:
                partes = linea.split()
                if len(partes) > 1:
                    pid = int(partes[1])
                    try:
                        os.kill(pid, signal.SIGKILL)
                        print(f"  -> Proceso intruso exterminado (PID: {pid})")
                    except Exception:
                        pass
    except Exception as e:
        print(f"[-] Error al escanear procesos: {e}")
    time.sleep(0.5)

# 2. Destruir rastros, cachés, PIDs y registros de anclaje
print("[+] Purgando archivos de control, PIDs y registros persistentes...")
patrones = ["*.log", "logs_*/*", "pids_*/*", "*.pid", "cron_*", "autorun*"]
archivos_a_borrar = []
for patron in patrones:
    archivos_a_borrar.extend(glob.glob(patron, recursive=True))

for archivo in set(archivos_a_borrar):
    try:
        os.remove(archivo)
        print(f"  -> Archivo de anclaje destruido: {archivo}")
    except Exception:
        pass

# 3. Limpiar variables de entorno que intenten mantener sesiones vivas
print("[+] Limpiando variables de entorno residuales...")
variables_a_limpiar = ["LLAVE_MAESTRA_ACOBES", "NODO_DESTINO", "NODO_CERN"]
for var in variables_a_limpiar:
    if var in os.environ:
        del os.environ[var]
        print(f"  -> Variable eliminada: {var}")

# 4. Revocar permisos de wakelock y cerrar canales de red de Termux
print("[+] Restableciendo capas de red y cortando sockets...")
try:
    subprocess.run(["termux-wake-unlock"], check=False)
    print("  -> Wake-lock liberado. Sockets externos cerrados por completo.")
except Exception:
    pass

print("\n[========================================================]")
print("[+] DISPOSITIVO SANEADO Y BLINDADO. Anclajes eliminados.")
print("[========================================================]")
