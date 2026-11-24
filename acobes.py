#!/usr/bin/env python3

import json
import hashlib
import time

class ReadOnlyChainBridge:
    def __init__(self, rpc_node_url):
        self.rpc_url = rpc_node_url
        # Token interno para asegurar modo solo lectura
        self.read_only_token = hashlib.sha256(b"ACOBES_READ_ONLY_V1").hexdigest()

    def _validate_read_only(self, payload):
        forbidden_keywords = ["sendTransaction", "personal_sign", "eth_send", "unlockAccount", "write", "modify", "deploy"]
        payload_str = json.dumps(payload).lower()
        for keyword in forbidden_keywords:
            if keyword in payload_str:
                raise PermissionError("Bloqueo de Seguridad: Intento de escritura detectado.")
        return True

    def _rpc_call(self, method, params):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": int(time.time())
        }
        self._validate_read_only(payload)
        # Aquí se haría la petición HTTP real al nodo.
        # Simulación para este ejemplo:
        return {"jsonrpc": "2.0", "id": payload["id"], "result": "0x0"}

    def get_balance(self, address):
        return self._rpc_call("eth_getBalance", [address, "latest"])

    def get_transaction_count(self, address):
        return self._rpc_call("eth_getTransactionCount", [address, "latest"])

if __name__ == "__main__":
    # Apunta al nodo local levantado por Emily
    bridge = ReadOnlyChainBridge("http://127.0.0.1:8545")
    try:
        result = bridge.get_balance("0x0000000000000000000000000000000000000000")
        print("Lectura segura completada. Resultado:", result)
    except PermissionError as e:
        print("ALERTA:", e)

