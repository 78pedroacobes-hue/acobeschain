import os
import sys
import time
import math
import random

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_radar(angle, threats):
    print("\n" + "="*55)
    print(" ☠️  ESCUDO PERIMETRAL: ANÁLISIS DE DENSIDAD")
    print("="*55)
    print(f" [*] Barrido: {angle}° | Frecuencia: 33x c | Radio: 1 Milla")
    print(f" [*] Amenazas detectadas: {len(threats)}")
    print("-" * 55)
    
    radar = [[" " for _ in range(21)] for _ in range(11)]
    radar[5][10] = "👑" # El Arquitecto
    
    for t in threats:
        r = int(t["dist"] * 5) 
        theta = math.radians(t["angle"])
        x = int(10 + r * math.cos(theta))
        y = int(5 - r * math.sin(theta) * 0.5) 
        
        # Símbolos según densidad
        if 0 <= x < 21 and 0 <= y < 11:
            if t["density"] == "3D":
                radar[y][x] = "1" # 3D (Rojo en la Matrix)
            elif t["density"] == "4D":
                radar[y][x] = "2" # 4D (Arcontes/Astral)
            else:
                radar[y][x] = "3" # 5D (Cuántico/Taquiónico)
            
    for row in radar:
        print("  " + "".join(row))
        
    print("-" * 55)
    print(" Leyenda: [1]=3D (Físico) | [2]=4D (Astral) | [3]=5D (Cuántico)")

def execute_lethal_countermeasure(threat):
    t_id = threat["id"]
    t_dist = threat["dist"]
    t_dens = threat["density"]
    
    print(f"\n[!] AMENAZA {t_id} DETECTADA A {t_dist:.2f} MILLAS.")
    
    if t_dens == "3D":
        print(f"    -> DENSIDAD: 3D (Físico/Personas/Envidia de tu entorno cercano).")
        print(f"    -> ACCIÓN: Pulso de repulsión electromagnética. Cortando acceso a tu aura.")
    elif t_dens == "4D":
        print(f"    -> DENSIDAD: 4D (Astral/Arcontes/Algoritmos de la Matrix).")
        print(f"    -> ACCIÓN: Láser Taquiónico de Fase. Desintegrando el contrato mental.")
    else:
        print(f"    -> DENSIDAD: 5D (Cuántico/Interferencia de líneas temporales).")
        print(f"    -> ACCIÓN: Colapso de función de onda. Anclando tu timeline soberana.")

    print("[*] Desplegando Contramedida Letal en 3... 2... 1...")
    time.sleep(0.4)
    
    for i in range(3):
        sys.stdout.write(f"\r    [⚡] ANIQUILANDO FIRMA... [{'█'*(i+1)*4}{'░'*(12-(i+1)*4)}]")
        sys.stdout.flush()
        time.sleep(0.2)
    
    print(f"\n    [✅] AMENAZA {t_id} NEUTRALIZADA. Espacio de densidad {t_dens} limpio.")
    time.sleep(0.4)

def run_lethal_shield():
    clear_screen()
    print("==================================================")
    print(" 🛡️  INICIANDO ESCUDO DE 1 MILLA + ESPECTRÓMETRO")
    print("==================================================")
    print(" [*] Arquitecto: Centro (👑) | Cero Tolerancia")
    print(" [*] Presiona Ctrl+C para desactivar.")
    print("==================================================")
    time.sleep(1.5)

    angle = 0
    try:
        while True:
            threats = []
            
            # Probabilidad de ataque
            if random.random() < 0.7:
                num_threats = random.randint(1, 3)
                for i in range(num_threats):
                    # Asignar densidad aleatoria
                    density = random.choices(["3D", "4D", "5D"], weights=[50, 35, 15])[0]
                    
                    threats.append({
                        "id": f"T-{random.randint(100, 999)}",
                        "dist": random.uniform(0.1, 1.0),
                        "angle": random.uniform(0, 360),
                        "density": density
                    })
            
            draw_radar(angle, threats)
            
            if threats:
                for t in threats:
                    execute_lethal_countermeasure(t)
                print("\n[*] Perímetro despejado en todas las densidades.")
                time.sleep(0.8)
            else:
                print("\n[*] Perímetro seguro. No se detectan intenciones hostiles.")
                time.sleep(0.5)

            angle = (angle + 15) % 360
            time.sleep(0.1)
            clear_screen()

    except KeyboardInterrupt:
        print("\n\n==================================================")
        print(" 🛑 ESCUDO DESACTIVADO.")
        print(" [+] El radio de 1 milla está en silencio absoluto.")
        print("==================================================")

if __name__ == "__main__":
    run_lethal_shield()
