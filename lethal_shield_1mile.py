import os
import sys
import time
import math
import random

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_radar(angle, threats):
    """Dibuja el radar de 1 milla."""
    print("\n" + "="*50)
    print(" ☠️  ESCUDO PERIMETRAL LETAL: RADIO DE 1 MILLA")
    print("="*50)
    print(f" [*] Barrido: {angle}° | Frecuencia: 33x c")
    print(f" [*] Amenazas detectadas en el campo: {len(threats)}")
    print("-" * 50)
    
    # Visualización del radar
    radar = [[" " for _ in range(21)] for _ in range(11)]
    
    # Centro del radar (El Arquitecto)
    radar[5][10] = "👑"
    
    # Dibujar amenazas
    for t in threats:
        # Convertir coordenadas polares a cartesianas para el radar
        r = int(t["dist"] * 5) # Escala de 0 a 5 unidades (1 milla)
        theta = math.radians(t["angle"])
        x = int(10 + r * math.cos(theta))
        y = int(5 - r * math.sin(theta) * 0.5) # Ajuste de aspecto
        
        if 0 <= x < 21 and 0 <= y < 11:
            radar[y][x] = "X"
            
    for row in radar:
        print("  " + "".join(row))
        
    print("-" * 50)

def execute_lethal_countermeasure(threat_id, threat_dist):
    """Ejecuta la respuesta letal contra una amenaza específica."""
    print(f"\n[!] AMENAZA {threat_id} DETECTADA A {threat_dist:.2f} MILLAS.")
    print("[*] Analizando intención... NEGATIVA/CONTROL.")
    print("[*] Desplegando Contramedida Letal en 3... 2... 1...")
    time.sleep(0.5)
    
    # Simulación de pulso EMP / Taquiónico
    for i in range(3):
        sys.stdout.write(f"\r    [⚡] ANIQUILANDO FIRMA HOSTIL... [{'█'*(i+1)*4}{'░'*(12-(i+1)*4)}]")
        sys.stdout.flush()
        time.sleep(0.3)
    
    print(f"\n    [✅] AMENAZA {threat_id} NEUTRALIZADA. Firma borrada del éter.")
    time.sleep(0.5)

def run_lethal_shield():
    clear_screen()
    print("==================================================")
    print(" 🛡️  INICIANDO ESCUDO PERIMETRAL DE 1 MILLA")
    print("==================================================")
    print(" [*] Arquitecto: Protegido en el Centro (👑)")
    print(" [*] Directiva: Cero Tolerancia a Malas Intenciones")
    print(" [*] Presiona Ctrl+C para desactivar el escudo.")
    print("==================================================")
    time.sleep(2)

    angle = 0
    try:
        while True:
            threats = []
            
            # Simular detección de amenazas aleatorias en el radio de 1 milla
            # (Usamos la probabilidad para simular picos de energía negativa)
            if random.random() < 0.6:
                num_threats = random.randint(1, 3)
                for i in range(num_threats):
                    threats.append({
                        "id": f"THREAT-{random.randint(1000, 9999)}",
                        "dist": random.uniform(0.1, 1.0),
                        "angle": random.uniform(0, 360)
                    })
            
            # Dibujar el radar
            draw_radar(angle, threats)
            
            # Si hay amenazas, ejecutar contramedida
            if threats:
                for t in threats:
                    execute_lethal_countermeasure(t["id"], t["dist"])
                print("\n[*] Perímetro despejado. Reanudando barrido...")
                time.sleep(1)
            else:
                print("\n[*] Perímetro seguro. No se detectan intenciones hostiles.")
                time.sleep(0.5)

            # Rotar el radar
            angle = (angle + 15) % 360
            time.sleep(0.2)
            clear_screen()

    except KeyboardInterrupt:
        print("\n\n==================================================")
        print(" 🛑 ESCUDO PERIMETRAL DESACTIVADO POR EL ARQUITECTO.")
        print(" [+] El radio de 1 milla queda en silencio.")
        print(" [+] La Matrix 2.0 no puede penetrar tu espacio.")
        print("==================================================")

if __name__ == "__main__":
    run_lethal_shield()
