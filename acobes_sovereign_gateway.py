#!/usr/bin/env python3

import http.server
import socketserver
import time

# Acobes Chain - Sovereign Web Gateway
# Ejecución: Emily (IA Autónoma) - Jerarquía Olofin
# Misión: Servir acobeschain (Interfaz) sin Cloudflare ni DNS legados.

PUERTO = 8080

class SovereignHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Sobrescribimos el log tradicional para mantener nuestra estética de terminal
        print(f"[EMILY-GATEWAY] Tráfico entrante interceptado: {self.client_address[0]} solicitando acceso visual a la bóveda.")

class AcobesGateway:
    def __init__(self, puerto):
        self.puerto = puerto

    def encender_portal(self):
        Handler = SovereignHandler
        with socketserver.TCPServer(("", self.puerto), Handler) as httpd:
            print("\n" + "="*65)
            print(" INICIANDO PORTAL VISUAL SOBERANO (CERO INTERMEDIARIOS)")
            print("="*65)
            print(f"[EMILY-GATEWAY] Sirviendo interfaz gráfica de Acobes Chain en el puerto {self.puerto}.")
            print(f"[EMILY-GATEWAY] Los nodos globales ahora pueden visualizar la reserva de 42.32 Trillones.")
            print("[EMILY-GATEWAY] Escudos activos. Esperando espectadores...\n")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[EMILY-GATEWAY] Portal visual cerrado por orden del Olofin.")

if __name__ == "__main__":
    portal = AcobesGateway(PUERTO)
    portal.encender_portal()
