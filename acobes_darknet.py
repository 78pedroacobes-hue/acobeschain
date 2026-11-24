#!/usr/bin/env python3

import os
import time
import subprocess

# Acobes Chain - Arquitectura Tor (Capa Oscura)
# Ejecución: Emily (IA Autónoma)

TORRC_PATH = "/etc/tor/torrc"
HS_DIR = "/var/lib/tor/acobes_chain"
HOSTNAME_FILE = f"{HS_DIR}/hostname"

def stealth_print(msg):
    print(f"[EMILY-SYS] {msg}")
    time.sleep(0.4)

def deploy_darknet():
    stealth_print("1) Instalando motor Tor en la matriz local...")
    subprocess.run(["apt", "update"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["apt", "install", "-y", "tor"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    stealth_print("2) Forjando configuración del Servicio Oculto...")
    # Limpiamos configuraciones previas si existen y añadimos el bloque nuevo
    torrc_config = f"\nHiddenServiceDir {HS_DIR}/\nHiddenServicePort 80 127.0.0.1:8545\n"
    with open(TORRC_PATH, "a") as f:
        f.write(torrc_config)
        
    stealth_print("3) Encendiendo el motor de enrutamiento cebolla (Tor)...")
    os.makedirs(HS_DIR, exist_ok=True)
    os.chmod(HS_DIR, 0o700) # Tor exige seguridad estricta en su directorio
    
    # Lanzamos tor en segundo plano
    subprocess.Popen(["tor"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    stealth_print("4) Tejiendo la ruta criptográfica a través de los nodos globales...")
    stealth_print("   (Esto puede tomar unos 10-20 segundos mientras forja la llave permanente)")
    
    for _ in range(40):
        if os.path.exists(HOSTNAME_FILE):
            with open(HOSTNAME_FILE, "r") as f:
                onion_url = f.read().strip()
            print("\n" + "="*65)
            stealth_print("¡ENLACE SOBERANO ESTABLECIDO!")
            stealth_print(f"DIRECCIÓN INMUTABLE: {onion_url}")
            stealth_print("ESTADO: Fuera de la matriz. Cero intermediarios.")
            print("="*65 + "\n")
            return
        time.sleep(1)
        
    stealth_print("[-] La red está tardando en sincronizar. Dale unos segundos más y revisa el archivo de hostname manualmente.")

if __name__ == "__main__":
    print("\n" + "="*65)
    stealth_print("INICIANDO PROTOCOLO DARKNET: ACOBES CHAIN")
    print("="*65)
    deploy_darknet()
