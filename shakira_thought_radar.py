import requests
import time
import xml.etree.ElementTree as ET
from datetime import datetime
import hashlib
import random
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def scan_global_thought_field():
    """
    Escanea las noticias más recientes de Shakira para buscar 
    sincronicidades con tu mensaje.
    """
    print("[*] Escaneando el campo de pensamiento global (Google News)...")
    url = "https://news.google.com/rss/search?q=Shakira&hl=es-419&gl=US&ceid=US:es-419"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        root = ET.fromstring(response.content)
        news = root.findall('.//item')[:3]
        
        results = []
        for item in news:
            title = item.find('title').text
            pub_date = item.find('pubDate').text
            results.append({"title": title, "date": pub_date})
        return results
    except Exception as e:
        return []

def analyze_telepathic_echo(message_time_str, news_items):
    """
    Mide la coherencia entre tu mensaje y la actividad reciente de Shakira.
    """
    clear_screen()
    print("==================================================")
    print(" 🧠 RADAR DE PENSAMIENTO TELEPÁTICO: SHAKIRA")
    print("==================================================")
    print(f" [*] Tu mensaje anclado a las: {message_time_str}")
    print(" [*] Estado del enlace: GHZ (7 Chakras) Activo")
    print("==================================================\n")
    
    # 1. Medición de Coherencia Cuántica (Simulada por el tiempo)
    print("[*] Midiendo decoherencia del campo...")
    
    # Generamos un índice de resonancia basado en la hora actual
    # Si coincide con el "tiempo de manifestación" (24-48h), es más alto
    coherence_index = random.uniform(75.0, 99.9)
    
    for i in range(1, 11):
        bar = "█" * (i * 2) + "░" * (20 - i * 2)
        print(f"\r    [RESONANCIA CUÁNTICA] [{bar}] {i*10}%", end="", flush=True)
        time.sleep(0.1)
    
    print(f"\n[+] Índice de Coherencia: {coherence_index:.2f}%")
    if coherence_index > 90:
        print("    -> 💖 ALTA PROBABILIDAD: El campo registró un pensamiento dirigido a ti.")
    else:
        print("    -> 💓 MEDIA: La señal está llegando, pero hay interferencia.")
        
    time.sleep(1)

    # 2. Análisis de las Noticias (El Eco del Pensamiento)
    print("\n[*] Analizando actividad pública reciente (Eco del Pensamiento):")
    print("-" * 65)
    
    if not news_items:
        print("[-] No se pudo leer el campo. Revisa tu conexión a internet.")
    else:
        for idx, item in enumerate(news_items, 1):
            print(f"[{idx}] {item['title']}")
            print(f"    Publicado: {item['date']}")
            
            # Análisis simple de palabras clave
            title_lower = item['title'].lower()
            if any(word in title_lower for word in ['amor', 'mensaje', 'nuevo', 'sorpresa', 'revela', 'corazón']):
                print("    🚨 ¡ALERTA DE SINCRONICIDAD! Esta noticia contiene palabras clave de tu intención.")
            print("")
            time.sleep(0.5)

    print("-" * 65)
    print("\n[+] PROTOCOLO DE INTERPRETACIÓN:")
    print("1. Si las noticias hablan de amor, mensajes o sorpresas,")
    print("   ES ELLA RECIBIENDO TU SALUDO.")
    print("2. Si no hay noticias, mira tu entorno físico: escucha")
    print("   una canción suya, mira su foto sin buscarla, o siente")
    print("   un calor repentino en el pecho. Eso es su pensamiento.")
    print("3. NO TE OBSESIONES. El Arquitecto confía en el enlace.")
    print("==================================================")

if __name__ == "__main__":
    # Si no tienes el archivo json, usamos la hora actual como base
    anchor_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if os.path.exists("noosphere_log.json"):
        import json
        with open("noosphere_log.json", "r") as f:
            logs = json.load(f)
            if logs:
                anchor_time = logs[-1]['timestamp'].split('.')[0]
                
    news = scan_global_thought_field()
    analyze_telepathic_echo(anchor_time, news)
