import socket
import hashlib
import time
import os
import sys
import secrets
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_multiverse_coordinates():
    """Calcula las coordenadas hacia Júpiter en 2045."""
    # Júpiter tarda 11.86 años en orbitar el Sol. 
    # Calculamos la posición exacta para el año 2045 en los Headwaters.
    current_year = datetime.now().year
    years_ahead = 2045 - current_year
    orbital_shift = (years_ahead % 11.86) * 360.0
    
    coord_hash = hashlib.sha256(f"JUPITER-2045-HEADWATERS-{orbital_shift}".encode()).hexdigest()
    return f"{coord_hash[:8]}-{coord_hash[8:12]}-{coord_hash[12:16]}-2045"

def open_portal():
    clear_screen()
    print("==================================================")
    print(" 🌌 PROTOCOLO DE PORTAL MULTIVERSAL: JÚPITER 2045")
    print("==================================================")
    print(" [*] Ubicación: Headwaters del Multiverso (Júpiter)")
    print(" [*] Año Objetivo: 2045")
    print(" [*] Seguridad: Protocolo de Tierra Quemada Activo")
    print("==================================================\n")
    time.sleep(1)

    # 1. Establecer coordenadas
    coords = generate_multiverse_coordinates()
    print(f"[*] Coordenadas de salto calculadas: {coords}")
    time.sleep(1)

    # 2. Generar una llave efímera (One-Time Pad)
    ephemeral_key = secrets.token_hex(16)
    print(f"[*] Llave Efímera generada: {ephemeral_key[:8]}... (Solo válida para este salto)")

    # 3. Abrir un Socket (Puerto Local 2045 para simular el portal)
    # Usamos localhost porque el "puente" se crea en tu propia máquina
    print("\n[*] Abriendo túnel cuántico (Puerto 2045)...")
    time.sleep(1)
    
    try:
        # Creamos el socket del servidor (el portal)
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Lo atamos al puerto 2045
        server_socket.bind(('127.0.0.1', 2045))
        server_socket.listen(1)
        
        print("[+] Portal ABIERTO. Esperando conexión desde Júpiter...")
        print("[*] Tienes 3 segundos para autenticarte antes de que se cierre por seguridad.")
        
        # Hacemos una petición local para simular el handshake (conexión)
        time.sleep(1)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('127.0.0.1', 2045))
        
        # Aceptar la conexión
        conn, addr = server_socket.accept()
        
        # 4. Intercambiar la llave (Handshake)
        print("\n[*] Conexión establecida desde el Nodo Futuro.")
        print("[*] Transmitiendo llave efímera...")
        
        # Enviamos la llave al "futuro"
        conn.send(ephemeral_key.encode())
        
        # Recibimos la confirmación
        auth_response = conn.recv(1024).decode()
        print(f"[+] Respuesta recibida: {auth_response}")
        time.sleep(0.5)
        
        # 5. EL CIERRE INMEDIATO (Tierra Quemada)
        print("\n[!] INICIANDO PROTOCOLO DE CIERRE DE EMERGENCIA.")
        print("[!] Destruyendo puentes de red...")
        
        conn.close()
        client_socket.close()
        server_socket.close()
        
        # 6. Destruir la llave de la memoria (Zero out)
        ephemeral_key = "0" * 32
        
        # 7. Firma de clausura
        closure_hash = hashlib.sha256(f"CERRADO-{coords}-{time.time()}".encode()).hexdigest()
        
        print(f"\n[+] PORTAL SELLADO. Rastro encriptado con hash: {closure_hash[:16]}")
        print("[+] Nadie más puede cruzar. La puerta está cerrada desde ambos lados.")
        
    except Exception as e:
        print(f"\n[-] Falla de contención espacial: {e}")
        print("[*] El portal colapsó antes de tiempo. Intenta de nuevo.")

    print("\n==================================================")
    print(" ✅ SESIÓN TERMINADA. CONEXIÓN A JÚPITER 2045 EXITOSA.")
    print("==================================================")

if __name__ == "__main__":
    open_portal()
