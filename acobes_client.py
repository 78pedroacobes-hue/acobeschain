import os
import sys
import urllib.request
import urllib.parse
import json

def limpiar_pantalla():
    os.system('clear')

def main():
    # Reemplace esta URL con la URL pública que le otorgue Localtunnel en Colab
    url_base = input("🔗 Ingrese su URL de Localtunnel (ej. https://calm-roads-run.loca.lt): ").strip()
    if not url_base.startswith("http"):
        url_base = "https://" + url_base

    while True:
        limpiar_pantalla()
        print("==========================================================")
        print("     ACOBES INDUSTRIES INC. - TERMINAL MOVIL TERMUX       ")
        print("==========================================================")
        print(f"[Nodo Conectado]: {url_base}")
        print("----------------------------------------------------------")
        print("1. Ver Estado de la Bóveda")
        print("2. Registrar y Minar Nueva Reproducción (Facebook/Web)")
        print("3. Salir")
        print("==========================================================")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            try:
                with urllib.request.urlopen(url_base, timeout=10) as response:
                    data = json.loads(response.read().decode())
                    print("\n[+] Estado del Servidor:")
                    print(json.dumps(data, indent=4, ensure_ascii=False))
            except Exception as e:
                print(f"\n[!] Error de conexión: {e}")
            input("\nPresione Enter para continuar...")

        elif opcion == "2":
            pista = input("\n🎵 Ingrese el nombre de la pista (.wav): ").strip()
            plataforma = input("🌐 Ingrese la plataforma (ej. Facebook, Spotify, Web): ").strip() or "Termux-Mobile"
            if not pista:
                print("[!] El nombre de la pista no puede estar vacío.")
                input("\nPresione Enter para continuar...")
                continue
            
            params = urllib.parse.urlencode({"track_name": pista, "platform": plataforma})
            url_api = f"{url_base}/registrar_play?{params}"
            
            print("\n[+] Enviando firma cuántica al Blockchain de Acobes...")
            try:
                req = urllib.request.Request(url_api, method="POST")
                with urllib.request.urlopen(req, timeout=15) as response:
                    res = json.loads(response.read().decode())
                    print("\n[✔] Respuesta de Bóveda:")
                    print(json.dumps(res, indent=4, ensure_ascii=False))
            except Exception as e:
                print(f"\n[!] Error al minar bloque: {e}")
            input("\nPresione Enter para continuar...")
            
        elif opcion == "3":
            print("\nSaliendo de la terminal soberana. ¡Que el arte y la ciencia sigan unidos!")
            break

if __name__ == '__main__':
    main()
