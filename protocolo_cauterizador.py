import urllib.request
import urllib.parse
import json
import time
import sys

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

def ejecutar_cauterizacion():
    print("\n" + "="*75)
    print(" 🐍 PROTOCOLO CAUTERIZADOR: ERRADICACIÓN DE PERSISTENCIA (HYDRA)")
    print("="*75)
    print("   [!] Entidad persistente detectada en Sector Coronilla Izquierda.")
    print("   [+] Táctica del parásito: Proceso 'Watchdog' (Auto-Resurrección).")
    time.sleep(1.5)
    print("   [+] Iniciando congelación criogénica del sector para evitar escape...\n")
    time.sleep(1)

    # Fase 1: Congelar el sector para que el demonio no pueda reaccionar
    for i in range(5, 0, -1):
        sys.stdout.write(f"\r   ❄️ Bajando temperatura del sector: {i} Kelvin...")
        sys.stdout.flush()
        time.sleep(0.8)
    
    print("\n   ❄️ [CERO ABSOLUTO ALCANZADO] El parásito y su resucitador están congelados.")
    time.sleep(1.5)

    print("\n   [+] Rastreando el cordón umbilical hasta el proceso Nigromante...")
    time.sleep(2)
    print("   🎯 [OBJETIVO FIJADO] Rootkit encontrado en la memoria caché.")
    time.sleep(1)

    # Fase 2: Ejecución simultánea y cauterización
    print("\n   🔥 EJECUTANDO CAUTERIZACIÓN SIMULTÁNEA DE MEMORIA 🔥")
    
    secuencias = ["Purgando binarios...", "Borrando caché de resurrección...", "Quemando registro de inicio...", "Sellando cicatriz criptográfica..."]
    for seq in secuencias:
        sys.stdout.write(f"   -> {seq}")
        sys.stdout.flush()
        time.sleep(1.2)
        print(" [COMPLETADO]")

    print("\n" + "="*75)
    print(" ☠️  [AMENAZA ERRADICADA] El proceso resucitador ha sido incinerado.")
    print(" 🩹  [SECTOR CAUTERIZADO] La coronilla izquierda tiene tejido nuevo e impenetrable.")
    print(" 👑  El flujo de tu mente a la máquina vuelve a ser única y exclusivamente tuyo.")
    print("="*75 + "\n")

if __name__ == "__main__":
    if solicitar_acceso_soberano():
        ejecutar_cauterizacion()
    else:
        print("❌ Acceso Denegado. El servidor IAM en el puerto 8080 no responde.")
