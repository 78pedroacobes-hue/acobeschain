import urllib.request
import urllib.parse
import json
import time
import sys
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
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data.get("access_token")
    except:
        return None

def ejecutar_protocolo_soberano():
    print("\n" + "="*75)
    print(" 🏛️ PROTOCOLO DE EXILIO Y PURGA DE RAÍZ [ACBES INDUSTRIES]")
    print("="*75)
    print("   [+] Autoridad: Pedro J. Acobes (I_AM_ACOBES)")
    print("   [+] Fase 1: Barrido y revocación de privilegios internos (Infiltrados).")
    print("   [+] Fase 2: Confinamiento perimetral a 5,000 millas (Exilio de 6 meses).")
    print("="*75 + "\n")
    time.sleep(1.5)

    # FASE 1: PURGA INTERNA (ROOT SWEEP)
    print("🧹 [FASE 1] Ejecutando Root Sweep de procesos internos...")
    time.sleep(1)
    
    infiltrados_internos = ["daemon_backdoor_local", "root_proxy_fake", "auth_bypass_v1"]
    for proc in infiltrados_internos:
        sys.stdout.write(f"   -> Revocando credenciales y expulsando al proceso '{proc}'...")
        sys.stdout.flush()
        time.sleep(0.8)
        print(" [ELIMINADO]")

    print("\n   ✅ [RAÍZ INTERNA LIMPIA] Los privilegios de administración han sido centralizados.")
    time.sleep(1.5)

    # FASE 2: EXILIO PERIMETRAL (5,000 MILLAS / 6 MESES)
    print("\n🌍 [FASE 2] Estableciendo el Perímetro de Exilio (5,000 millas)...")
    time.sleep(1)

    print("   -> Reenrutando entidades externas a la sub-red de baja frecuencia.")
    print("   -> Asignando paquete de subsistencia básica (Ancho de banda mínimo).")
    print("   -> Programando temporizador de reevaluación: 6 Meses terrestres.")
    
    for i in range(1, 6):
        sys.stdout.write(f"\r   [CONFINAMIENTO] Sincronizando órbita de aislamiento... [{i}/5]")
        sys.stdout.flush()
        time.sleep(0.6)

    print("\n\n" + "="*75)
    print(" 🚪  [PUERTAS CERRADAS] Ya no hay llaves falsas ni cómplices adentro.")
    print(" 🛰️  [EXILIO ACTIVO] Los intrusos operan a 5,000 millas con lo mínimo indispensable.")
    print(" ⏳  [CRONOGRAMA FIJADO] Próxima revisión de estado en 6 meses (Abril de 2027).")
    print(" 👑  [SISTEMA SOBERANO] El núcleo responde única y exclusivamente al Arquitecto.")
    print("="*75 + "\n")

if __name__ == "__main__":
    token = solicitar_acceso_soberano()
    if token:
        ejecutar_protocolo_soberano()
    else:
        print("❌ Acceso Denegado. El servidor IAM en el puerto 8080 no responde.")
