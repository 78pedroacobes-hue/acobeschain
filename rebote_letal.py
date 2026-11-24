import time
import sys
import random
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def iniciar_rebote_letal():
    clear_screen()
    print("="*70)
    print(" ☠️  P R O T O C O L O   D E   R E B O T E   L E T A L")
    print("="*70)
    print(" [*] Modo              : Contraofensiva Asimétrica")
    print(" [*] Amplificación     : 1000x (Devolución de daño)")
    print(" [*] Objetivo          : Servidores y Nodos hostiles")
    print(" [*] Advertencia       : No detener hasta que el enjambre caiga.")
    print("="*70 + "\n")
    time.sleep(2)

    nodos_caidos = 0
    servidores_caidos = 0
    dano_total = 0.0

    try:
        while True:
            # Simulamos que detectamos un ataque entrante
            ataque_entrante = random.uniform(10.0, 500.0)
            
            # Generamos el objetivo (IP o Nodo de la Matrix)
            ip_hostil = f"{random.randint(11,199)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            tipo_objetivo = random.choice(["NODO", "SERVIDOR", "CLUSTER"])
            
            # El rebote multiplica el ataque x1000
            dano_rebotado = ataque_entrante * 1000
            dano_total += dano_rebotado

            # Simulamos el impacto en el sistema enemigo
            if tipo_objetivo == "SERVIDOR":
                servidores_caidos += 1
                estado = "🔥 SERVIDOR COLAPSADO (Cero Respuesta)"
            elif tipo_objetivo == "CLUSTER":
                nodos_caidos += random.randint(5, 20)
                estado = "☠️ CLÚSTER DESTRUIDO (Fallo en Cascada)"
            else:
                nodos_caidos += 1
                estado = "💀 NODO TUMBADO (Kernel Panic)"

            # Formateamos la línea de ataque
            sys.stdout.write(f"\r[REBOBOTE] IP: {ip_hostil:<15} | Daño: {dano_rebotado:,.0f} MW | {estado:<35} | "
                             f"Servidores: {servidores_caidos} | Nodos: {nodos_caidos}")
            sys.stdout.flush()
            
            # Velocidad de los disparos (muy rápido, parece una ametralladora)
            time.sleep(0.05)
            
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print(" 🛑 [SISTEMA]: Alto al fuego solicitado por el Arquitecto.")
        print(f" 📊 REPORTE DE DAÑO:")
        print(f"    -> Servidores Apagados : {servidores_caidos:,}")
        print(f"    -> Nodos Aniquilados   : {nodos_caidos:,}")
        print(f"    -> Daño Total Devuelto : {dano_total:,.2f} Megavatios (MW)")
        print("="*70)
        print(" El enjambre hostil ha sido neutralizado. La red está a salvo.\n")

if __name__ == "__main__":
    iniciar_rebote_letal()
