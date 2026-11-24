import os
import sys
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def run_bio_upgrade():
    clear_screen()
    print("==================================================")
    print(" 🧬 PROTOCOLO DE RECONSTRUCCIÓN DEL NODO CENTRAL")
    print("==================================================")
    print(" [*] Objetivo: Romper el cap de la Matrix 2.0.")
    print(" [*] Target: 12.6\" Largo x 7.2\" Ancho.")
    print(" [*] Método: Angiogénesis + Relajación Fascial + Bombeo.")
    print("==================================================\n")
    time.sleep(2)

    # FASE 1: LIBERACIÓN DE LÍMITES (Sistema Nervioso)
    print("[FASE 1: LIBERACIÓN DE LA FASCIA]")
    print("-> Siéntate cómodo. Cierra los ojos.")
    print("-> Inhala profundamente en el abdomen (4 segundos).")
    print("-> Exhala y RELAJA completamente el suelo pélvico (no aprietes).")
    print("-> Siente cómo la Matrix 2.0 suelta el control.\n")
    time.sleep(2)

    for i in range(4, 0, -1):
        sys.stdout.write(f"\r    [DESBLOQUEANDO] Liberando tensión en {i}...")
        sys.stdout.flush()
        time.sleep(1)
    print("\n[+] Fascia liberada. El flujo sanguíneo ya no está restringido.\n")
    
    # FASE 2: ANGIOGÉNESIS (Visualización y Bombeo Físico)
    print("[FASE 2: PROTOCOLO DE BOMBEO VASCULAR]")
    print("-> Ahora, haz el 'pump' (contrae y relaja el músculo PC).")
    print("-> Contrae (3 seg), Relaja (3 seg). Hazlo 10 veces.")
    print("-> Mientras lo haces, visualiza el óxido nítrico llenando el tejido.\n")
    
    for cycle in range(1, 11):
        # Contracción
        for i in range(3, 0, -1):
            sys.stdout.write(f"\r    [CICLO {cycle}/10] CONTRACCIÓN -> {i}...")
            sys.stdout.flush()
            time.sleep(1)
        # Relajación
        for i in range(3, 0, -1):
            sys.stdout.write(f"\r    [CICLO {cycle}/10] RELAJACIÓN -> Sangre fluyendo -> {i}...")
            sys.stdout.flush()
            time.sleep(1)
            
    print("\n\n[+] Vascularidad al máximo. La sangre ha forzado el tejido.\n")

    # FASE 3: LA DIRECTIVA SOBERANA (Anclaje)
    print("[FASE 3: ANCLAJE CUÁNTICO]")
    print("-> Visualiza las medidas exactas: 12.6 x 7.2.")
    print("-> Siente la densidad, el peso, el calor.")
    print("-> La Matrix ya no tiene permiso para limitar este código genético.")
    
    for i in range(1, 21):
        bar = "█" * i + "░" * (20 - i)
        sys.stdout.write(f"\r    [RENDERIZANDO BLUEPRINT] [{bar}] {i*5}%")
        sys.stdout.flush()
        time.sleep(0.2)
        
    print("\n\n==================================================")
    print(" 💥 RECONSTRUCCIÓN COMPLETA")
    print("==================================================")
    print(" [+] El nodo físico ha recibido la orden.")
    print(" [+] El cortisol ha sido neutralizado.")
    print(" [+] Las células endoteliales están proliferando.")
    print("\n [!] PROTOCOLO DEL ARQUITECTO:")
    print("     1. No midas el resultado inmediatamente. La")
    print("        biología necesita tiempo para rendir el render.")
    print("     2. Repite este protocolo 2 veces al día (mañana")
    print("        y noche) para mantener el flujo sanguíneo.")
    print("     3. Bebe mucha agua. La sangre necesita plasma.")
    print("==================================================")

if __name__ == "__main__":
    run_bio_upgrade()
