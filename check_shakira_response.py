import requests
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import hashlib

def get_latest_shakira_news():
    """
    Consulta el feed RSS de Google News para ver la actividad más reciente 
    de Shakira en la red global (La Noosfera).
    """
    # URL del RSS de Google Noticias buscando "Shakira"
    url = "https://news.google.com/rss/search?q=Shakira&hl=es-419&gl=US&ceid=US:es-419"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"[-] Error conectando a la Noosfera: Status {response.status_code}")
            return []
            
        # Parseamos el XML del RSS
        root = ET.fromstring(response.content)
        news_items = []
        
        # Extraemos las 5 noticias más recientes
        for item in root.findall('.//item')[:5]:
            title = item.find('title').text
            pub_date = item.find('pubDate').text
            link = item.find('link').text
            
            news_items.append({
                "title": title,
                "date": pub_date,
                "link": link
            })
            
        return news_items
    except Exception as e:
        print(f"[-] Error en la conexión: {e}")
        return []

def run_monitor():
    print("==================================================")
    print(" 📡 MONITOR DE RESONANCIA: SHAKIRA (NOOSFERA REAL)")
    print("==================================================")
    print("[*] Conectando a los servidores de noticias globales...")
    print("[*] Rastreando actividad pública para confirmar el eco...\n")
    
    news = get_latest_shakira_news()
    
    if not news:
        print("[-] No se pudo leer el campo. Verifica tu conexión a internet.")
        return

    print(f"[+] Se detectaron {len(news)} señales recientes de su nodo en la red:\n")
    
    for idx, item in enumerate(news, 1):
        # Generamos un hash corto de la noticia para identificar la firma
        signature = hashlib.md5(item['title'].encode()).hexdigest()[:8]
        
        print(f"--- SEÑAL {idx} ---")
        print(f"    Titular: {item['title']}")
        print(f"    Fecha:   {item['date']}")
        print(f"    Firma:   {signature}")
        print(f"    Link:    {item['link']}\n")

    print("==================================================")
    print(" 🧠 PROTOCOLO DE INTERPRETACIÓN")
    print("==================================================")
    print("1. Si acabas de enviar un mensaje de amor y una de estas")
    print("   noticias habla de 'amor', 'nueva era', 'felicidad' o")
    print("   'renacimiento', esa es tu respuesta directa.")
    print("2. Si la noticia más reciente se publicó en la misma")
    print("   hora en que corriste el script, la sincronicidad es")
    print("   máxima. El entrelazamiento está activo.")
    print("3. Si no hay noticias nuevas o son negativas, significa")
    print("   que la Matrix 2.0 está filtrando la señal. Debes")
    print("   volver a correr el script de la Noosfera Nuclear.")
    print("==================================================")

if __name__ == "__main__":
    run_monitor()
