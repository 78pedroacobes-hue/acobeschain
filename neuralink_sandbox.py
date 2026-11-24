import os
import sys
import time
import random
import hashlib

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class NeuralinkSandboxClient:
    def __init__(self, master_key: str):
        self.master_key = master_key
        self.connected = False
        
    def authenticate(self):
        print("[*] Conectando al Neuralink Sandbox API (Local)...")
        time.sleep(1)
        print("[*] Enviando Master Key...")
        
        # Simulamos la verificación del servidor
        # Si la llave tiene más de 10 caracteres, la consideramos válida (en el sandbox)
        if len(self.master_key) > 10:
            print("[+] AUTH OK. Neuralink Sandbox Access Granted.")
            self.connected = True
            return True
        else:
            print("[-] AUTH FAILED. Key too short.")
            return False
            
    def stream_brainwaves(self, seconds=5):
        if not self.connected:
            print("[-] Not connected.")
            return
            
        print(f"\n[*] Abriendo stream de datos EEG (Simulado) durante {seconds} segundos...")
        print("    (Capturando actividad neuronal de 1024 electrodos)")
        
        # Simulamos una lectura de ondas cerebrales
        # Alpha (8-13 Hz), Beta (13-30 Hz), Gamma (30-100 Hz)
        for i in range(seconds):
            alpha = random.uniform(0.5, 1.0)
            beta = random.uniform(0.3, 0.8)
            gamma = random.uniform(0.1, 0.9) # Gamma alta = alta cognición
            
            # Generamos una barra visual
            bar = "█" * int(gamma * 20)
            
            sys.stdout.write(f"\r[EEG LIVE] Alpha: {alpha:.2f} | Beta: {beta:.2f} | Gamma: {bar} {gamma:.2f}")
            sys.stdout.flush()
            time.sleep(1)
            
        print("\n\n[+] Stream completado. Patrón neuronal registrado.")

def run_sandbox():
    clear_screen()
    print("==================================================")
    print(" 🧠 NEURALINK SANDBOX: MASTER KEY PROTOCOL")
    print("==================================================")
    print(" [*] Entorno: Sandbox Local (Seguro, sin hardware real)")
    print(" [*] Objetivo: Probar la llave de acceso del Arquitecto")
    print("==================================================\n")
    
    # Le pedimos al usuario que ingrese su "llave"
    # (En un entorno real, esto sería un token OAuth, aquí es simulado)
    key = input("Ingresa tu Master Key de Neuralink (o presiona Enter para usar una de prueba) > ")
    if not key.strip():
        key = "ACOBES_NEURALINK_MASTER_KEY_2045"
        
    client = NeuralinkSandboxClient(key)
    
    if client.authenticate():
        client.stream_brainwaves(seconds=5)
        
    print("\n==================================================")
    print(" 📊 RESULTADO DE LA PRUEBA")
    print("==================================================")
    print(" [+] La llave funciona en el Sandbox.")
    print(" [+] Tu capacidad de procesamiento BCI es real.")
    print(" [!] Recuerda: Este es un entorno seguro.")
    print("     No estamos hackeando hardware médico real.")
    print("     Estamos entrenando tu mente para interactuar")
    print("     con interfaces cerebro-computadora.")
    print("==================================================")

if __name__ == "__main__":
    run_sandbox()
