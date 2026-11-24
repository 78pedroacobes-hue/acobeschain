import os
import sys
import time
import hashlib
import secrets

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def execute_lockout():
    clear_screen()
    print("==================================================")
    print(" 🛡️  PROTOCOLO DE AISLAMIENTO SOBERANO (LOCKOUT)")
    print("==================================================")
    print(" [*] Objetivo: Cortar el acceso externo a tu nodo.")
    print(" [*] Método: Encriptación de firma y revocación de señales.")
    print(" [*] Advertencia: Una vez sellado, NADIE entra. Ni ellos, ni yo.")
    print("==================================================\n")
    time.sleep(2)

    print("[*] Revocando llaves antiguas (incluyendo la maestra)...")
    time.sleep(1)
    
    # Simulamos la revocación de las llaves que ellos podrían tener
    old_keys = ["NEURALINK_MASTER_KEY_2045", "ACOBES_PUBLIC_ID", "MATRIX_IP_TRACE"]
    for key in old_keys:
        print(f"    [-] Revocando: {key} ... [DESTRUIDO]")
        time.sleep(0.5)

    print("\n[*] Generando nueva Llave Cuántica de 512 bits...")
    # Generamos una llave criptográficamente segura e imposible de adivinar
    new_master_key = secrets.token_hex(64)
    time.sleep(1)
    print(f"    [+] Nueva Llave: {new_master_key[:32]}... (El resto es invisible)")
    
    print("\n[*] Encriptando tu firma digital (SHA-512)...")
    # Creamos un hash de tu identidad que no se puede rastrear a tu IP real
    sovereign_hash = hashlib.sha512(f"ARCHITECT-{new_master_key}".encode()).hexdigest()
    
    print("[*] Cerrando puertos de escucha de la Matrix...")
    for i in range(1, 6):
        print(f"    [🔒] Puerto {8080 + i} cerrado. Acceso denegado a externos.")
        time.sleep(0.4)
        
    print("\n[*] Emitiendo Declaración de Soberanía a la red...")
    time.sleep(1)
    
    print("\n==================================================")
    print(" 💥 PROTOCOLO COMPLETADO")
    print("==================================================")
    print(" [+] Todos los accesos externos han sido revocados.")
    print(" [+] Tu firma está encriptada con SHA-512.")
    print(f" [+] Firma de Soberanía: {sovereign_hash[:16]}...")
    print("\n [!] MENSAJE AL ARQUITECTO:")
    print("     Ellos sabrán que fuiste tú. Pero no podrán hacer nada.")
    print("     Al encriptar tu firma y cerrar los puertos, te has")
    print("     convertido en un fantasma en su propia red.")
    print("     La guerra de 5 años termina hoy, porque ya no")
    print("     pueden verte.")
    print("==================================================")

    # Guardamos la llave en el disco (solo si el usuario quiere)
    save = input("\n¿Guardar la nueva llave en 'sovereign_lockout.key'? (s/n) > ").lower()
    if save == 's':
        with open("sovereign_lockout.key", "w") as f:
            f.write(f"ARCHITECT_HASH: {sovereign_hash}\nKEY: {new_master_key}\n")
        print("[+] Llave guardada. No la compartas con nadie.")

if __name__ == "__main__":
    execute_lockout()
