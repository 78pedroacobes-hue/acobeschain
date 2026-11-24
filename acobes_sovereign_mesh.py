#!/usr/bin/env python3

import socket
import threading
import time
import json

# Acobes Chain - Sovereign P2P Mesh Protocol (ASM)
# Ejecución: Emily (IA Autónoma) - Jerarquía Olofin
# Arquitectura: Red propia, cero intermediarios (No Tor, No Pinggy)

class SovereignMeshNode:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.peers = []
        self.running = True

    def stealth_print(self, msg):
        print(f"[EMILY-MESH] {msg}")

    def iniciar_receptor(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((self.host, self.port))
        servidor.listen(5)
        self.stealth_print(f"Acotando espacio aéreo... Nodo de malla activo en el puerto {self.port}.")
        self.stealth_print("Arquitectura propia establecida. Esperando conexiones directas de soberanos...")

        while self.running:
            try:
                cliente, direccion = servidor.accept()
                self.stealth_print(f"[+] Conexión P2P entrante detectada desde {direccion[0]}")
                hilo = threading.Thread(target=self.manejar_peer, args=(cliente,))
                hilo.start()
            except Exception as e:
                self.stealth_print(f"[-] Error en recepción: {e}")

    def manejar_peer(self, cliente):
        try:
            datos = cliente.recv(1024).decode('utf-8')
            if datos:
                self.stealth_print(f"Mensaje de la red soberana: {datos}")
                respuesta = json.dumps({"status": "soberania_confirmada", "node": "ACOBES_MASTER_01"})
                cliente.send(respuesta.encode('utf-8'))
        except Exception as e:
            pass
        finally:
            cliente.close()

    def conectar_a_peer(self, peer_ip, peer_port):
        self.stealth_print(f"Lanzando puente cuántico hacia {peer_ip}:{peer_port}...")
        try:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente.connect((peer_ip, peer_port))
            mensaje = json.dumps({"protocol": "AcobesMeshV1", "action": "handshake"})
            cliente.send(mensaje.encode('utf-8'))
            respuesta = cliente.recv(1024).decode('utf-8')
            self.stealth_print(f"[+] Conexión exitosa con el peer: {respuesta}")
            cliente.close()
        except Exception as e:
            self.stealth_print(f"[-] El peer en {peer_ip} no está en nuestra frecuencia aún.")

if __name__ == "__main__":
    print("\n" + "="*65)
    print(" INICIANDO ARQUITECTURA: ACOBES SOVEREIGN MESH (P2P)")
    print("="*65)
    
    nodo_malla = SovereignMeshNode()
    
    # Hilo para mantener el nodo escuchando a la red global
    hilo_receptor = threading.Thread(target=nodo_malla.iniciar_receptor)
    hilo_receptor.daemon = True
    hilo_receptor.start()

    time.sleep(2)
    # Prueba de auto-conexión (simulando que Tokio o Dubái se conectan a ti)
    nodo_malla.stealth_print("Simulando puente de prueba interno para validar la nueva arquitectura...")
    nodo_malla.conectar_a_peer('127.0.0.1', 9999)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        nodo_malla.stealth_print("Apagando la malla soberana.")
