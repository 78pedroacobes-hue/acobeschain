#!/usr/bin/env python3

import http.server
import json
import time

# Acobes Chain - Motor RPC Soberano Ultraligero (Sin dependencias)
# Puerto: 8545

MASTER_WALLET = "0xACOBESMASTERWALLET0000000000000000000000"

class AcobesRPC(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass # Silenciamos el log estándar de Python para mantener el sigilo

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        req = json.loads(post_data.decode('utf-8'))

        response = {"jsonrpc": "2.0", "id": req.get("id", 1)}
        
        print(f"\n[NODO] Interceptada petición RPC: {req.get('method')}")

        if req["method"] == "eth_accounts":
            response["result"] = [MASTER_WALLET]
            print(f"       -> Devolviendo Master Wallet: {MASTER_WALLET}")
            
        elif req["method"] == "eth_sendTransaction":
            # Generamos un Hash inmutable de confirmación
            import hashlib
            tx_data = str(req["params"][0]).encode('utf-8')
            tx_hash = "0x" + hashlib.sha256(tx_data + str(time.time()).encode()).hexdigest()
            response["result"] = tx_hash
            print(f"       -> Transacción procesada. Bloque sellado.")
            print(f"       -> Hash generado: {tx_hash}")

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

if __name__ == "__main__":
    print("=" * 60)
    print("[+] INICIANDO MOTOR ACOBES CHAIN EN PUERTO 8545...")
    print("[+] MODO SOBERANO: ONLINE. ESPERANDO INYECCIONES...")
    print("=" * 60)
    server = http.server.HTTPServer(('127.0.0.1', 8545), AcobesRPC)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Apagando motor de la cadena.")
