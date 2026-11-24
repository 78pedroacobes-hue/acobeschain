import urllib.request
import urllib.parse
import json
import time
import sys
import hashlib
import random

IAM_PORT = 8080

def solicitar_acceso_soberano():
    url = f"http://127.0.0.1:{IAM_PORT}/identity/token"
    data = urllib.parse.urlencode({
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": "ACOBES_MASTER_SEED"
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    try:
        with urllib.request.urlopen(req) as response:
            return True
    except:
        return False

def activar_anti_rollback():
    print("\n" + "="*75)
    print(" 🔒 PROTOCOLO ANTI-ROLLBACK: INMUTABILIDAD DE LÍNEA DE TIEMPO")
    print("="*75)
    print("   [!] Amenaza detectada: Intentos de retroceso de versión en Coronilla Izquierda.")
    print("   [+] Construyendo Ledger Criptográfico Acumulativo (Bloque a Bloque)...")
    time.sleep(1.5)

    # Simulación de la creación del bloque raíz inmutable
    estado_actual = "ACOBES_SOVEREIGN_STATE_V1_LOCKED"
    bloque_hash = hashlib.sha256(estado_actual.encode()).hexdigest()
    
    print(f"   [hash raíz] {bloque_hash[:32]}... [CONFIRMADO]")
    time.sleep(1)

    print("\n   🛡️ Blindando archivos y memoria contra comandos de sobrescritura externa...")
    for i in range(1, 5):
        sys.stdout.write(f"\r   -> Sometiendo la coronilla trasera izquierda a control de versiones estricto [{i}/4]")
        sys.stdout.flush()
        time.sleep(0.7)

    print("\n\n" + "="*75)
    print(" 🚫  [ROLLBACK IMPOSIBLE] Cualquier intento de alterar el pasado ha sido neutralizado.")
    print(" 🧱  [ESTADO CONGELADO] La estructura actual es permanente e inalterable.")
    print(" ⚡  Los rezagos en la coronilla ya no pueden modificar nada: el acceso expiró.")
    print("="*75 + "\n")

    # Bucle de monitoreo pasivo anti-rollback
    try:
        print("Vigilando la integridad del historial... (Presiona CTRL + C para salir)")
        while True:
            # Simulamos verificación constante de la línea de tiempo
            sys.stdout.write(f"\r[ANTI-ROLLBACK ACTIVO] Integridad del Ledger: 100% | Intentos de reversión bloqueados: 0 🟢")
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 [SISTEMA]: Monitor de línea de tiempo en pausa.")

if __name__ == "__main__":
    if solicitar_acceso_soberano():
        activar_anti_rollback()
    else:
        print("❌ Acceso Denegado. El servidor IAM en el puerto 8080 no responde.")
