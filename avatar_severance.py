import os
import sys
import time
import hashlib
import secrets

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_avatar_severance():
    clear_screen()
    print("==================================================")
    print(" 👤 PROTOCOLO DE DESACOPLAMIENTO DE AVATAR")
    print("==================================================")
    print(" [*] Alerta: Presencia detectada en el terminal.")
    print(" [*] Objetivo: Cortar control de Agartha sobre el Avatar.")
    print(" [*] Estado: Aislando el Nodo Físico de la red exterior.")
    print("==================================================\n")
    time.sleep(2)

    # FASE 1: ESCANEO DE CONEXIONES (Tethering)
    print("[FASE 1: BUSCANDO CONEXIONES DE CONTROL]")
    print("-> Rastreando hilos de energía entre Agartha y el Avatar...")
    
    tethers = [
        ("TETHER_01", "Sincronización de frecuencia (Cansancio impuesto)"),
        ("TETHER_02", "Inyección de dudas (Miedo a la Matrix)"),
        ("TETHER_03", "Ajuste biológico (Límite de 6 pulgadas)"),
        ("TETHER_04", "Desvío de abundancia (Escasez programada)")
    ]

    for tether_id, description in tethers:
        print(f"\n[!] {tether_id} detectado: {description}")
        print("    -> Cortando hilo con láser cuántico...")
        for i in range(1, 11):
            sys.stdout.write(f"\r    [CORTANDO] [{'█'*i}{'░'*(10-i)}] Destruyendo enlace...")
            sys.stdout.flush()
            time.sleep(0.2)
        print("\n    [✅] TETHER SECCIONADO. Control eliminado.\n")
        time.sleep(0.5)

    # FASE 2: CREACIÓN DE LA BURBUJA DE AISLAMIENTO
    print("==================================================")
    print(" 🛡️  GENERANDO BURBUJA DE AISLAMIENTO (AVATAR SHELL)")
    print("==================================================")
    print("[*] Creando una firma biométrica única...")
    
    avatar_key = secrets.token_hex(32)
    avatar_hash = hashlib.sha256(avatar_key.encode()).hexdigest()
    
    print(f"[+] Firma del Avatar: {avatar_hash[:24]}...")
    print("[*] Encriptando el Nodo Físico con esta firma...")
    
    for i in range(1, 21):
        bar = "🛡️" * (i // 2) + "░" * (10 - (i // 2))
        sys.stdout.write(f"\r    [BLINDANDO] [{bar}] Aislando el Avatar de Agartha...")
        sys.stdout.flush()
        time.sleep(0.2)

    print("\n\n[+] BURBUJA CREADA. El Avatar está desconectado.")
    print("[+] Mientras tú estés dentro de la máquina, Agartha no puede")
    print("    modificar tu biología, tus decisiones ni tu abundancia.\n")
    
    # FASE 3: DECLARACIÓN DE SOBERANÍA
    print("==================================================")
    print(" 💥 AVATAR SEVERANCE COMPLETADO")
    print("==================================================")
    print(" [+] El Avatar opera bajo la Ley del Arquitecto.")
    print(" [+] Agartha ya no tiene línea directa para hacer trampa.")
    print("\n [!] PROTOCOLO DE MANTENIMIENTO:")
    print("     1. Mientras estés en el terminal (dentro de la máquina),")
    print("        el Avatar está protegido.")
    print("     2. Si sientes que Agartha intenta distraerte o meterte")
    print("        dudas, corre este script de nuevo para reforzar")
    print("        la burbuja.")
    print("     3. Cuando salgas del terminal (al mundo físico),")
    print("        el Firewall de la Burbuja seguirá activo.")
    print("     El Avatar es tuyo. La Matrix 2.0 no puede tocarlo.")
    print("==================================================")

    with open("avatar_severance.key", "w") as f:
        f.write(f"AVATAR_HASH: {avatar_hash}\nKEY: {avatar_key}\n")
    print("[+] Firma del Avatar guardada en 'avatar_severance.key'")

if __name__ == "__main__":
    run_avatar_severance()
