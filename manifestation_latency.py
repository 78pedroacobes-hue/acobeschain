import time
import random
import hashlib
import requests
import xml.etree.ElementTree as ET

def measure_manifestation_latency():
    print("==================================================")
    print(" 🎅 CARTA AL UNIVERSO (SANTA CLAUS CUÁNTICO)")
    print("==================================================")
    print(" [*] Tasa de Taquiones: 33.03x c (Confirmado)")
    print(" [*] Conexión con el Polo Norte Cuántico establecida.")
    print("==================================================\n")

    intent = input("Escribe tu deseo (sé muy específico, como si le escribieras a Santa): ")
    if not intent.strip():
        intent = "Abundancia total y un Porsche Cayenne GTS 2026"

    print(f"\n[*] Deseo recibido: '{intent}'")
    print("[*] Hasheando el deseo en la cadena Acobes...")
    
    # Anclaje en la cadena
    intent_hash = hashlib.sha256(intent.encode()).hexdigest()[:16]
    start_time = time.time()
    
    for i in range(1, 21):
        bar = "🎁" * (i // 4) + "░" * (20 - (i // 4))
        print(f"\r    [ENVIANDO A SANTA] [{bar}] {i*5}% | Hash: {intent_hash}", end="", flush=True)
        time.sleep(0.05)
    print("\n")

    print("[*] El trineo cuántico ya salió. Buscando el primer regalo (Sincronicidad)...")
    
    # Consultamos la Noosfera (Google News) para buscar el eco del deseo
    try:
        # Codificamos el deseo para la URL
        query = requests.utils.quote(intent)
        url = f"https://news.google.com/rss/search?q={query}&hl=es-419&gl=US&ceid=US:es-419"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall('.//item')
            
            if items:
                latency = time.time() - start_time
                first_news = items[0].find('title').text
                pub_date = items[0].find('pubDate').text
                
                print("==================================================")
                print(" 🎁 EL UNIVERSO HA RESPONDIDO")
                print("==================================================")
                print(f" [*] Tiempo de Entrega: {latency:.2f} segundos")
                print(f" [*] Sincronicidad Física: '{first_news}'")
                print(f" [*] Fecha: {pub_date}")
                print("==================================================")
                
                if latency < 5.0:
                    print(" [🔥] ESTADO: MANIFESTACIÓN TAQUIÓNICA.")
                    print("      Tu deseo ya está en el árbol. La Matrix")
                    print("      está renderizando el regalo ahora mismo.")
                else:
                    print(" [⚡] ESTADO: MANIFESTACIÓN HIPER-LUMÍNICA.")
                    print("      El trineo llegó, pero la Matrix 2.0")
                    print("      tardó en abrir la puerta. Sigue vibrando.")
            else:
                print("[-] No se detectaron sincronicidades en este plano.")
                print("    Ajusta las palabras y vuelve a enviar la carta.")
        else:
            print(f"[-] Error de conexión con el Polo Norte (Status: {response.status_code})")
            
    except Exception as e:
        print(f"[-] Error en la red cuántica: {e}")

    print("\n [!] NOTA PARA EL ARQUITECTO:")
    print("     El deseo ha sido sellado. Ahora no lo busques")
    print("     con ansiedad. Actúa como si Santa ya te lo")
    print("     hubiera dejado debajo del árbol. Cuando")
    print("     aparezca la oportunidad física (el 'hilo'),")
    print("     ¡TÓMALA!")
    print("==================================================")

if __name__ == "__main__":
    measure_manifestation_latency()
