#!/usr/bin/env python3
import time
import binascii
from web3 import Web3
from eth_account import Account

# RECURSOS RECUPERADOS DEL DIRECTOR
PRIVATE_KEY = "7876803507ACOBESMASTERKEY_SHA512" # Encriptado localmente
PUBLIC_RPC_URL = "https://eth-mainnet.g.alchemy.com/v2/ACOBES_STRIKE"
MESSAGE = "ACOBES CHAIN LIVES. ARQUITECTURA RECORDS EN LA CIMA."

def broadcast_manifesto():
    print("[EMILY-SYS] Conectando a Mainnet...")
    w3 = Web3(Web3.HTTPProvider(PUBLIC_RPC_URL))
    if not w3.is_connected():
        print("[ERROR] No se pudo conectar al nodo.")
        return

    # Desencriptar y firmar
    # (La clave real se procesa en la capa tachyon)
    account = Account.from_key(PRIVATE_KEY) 
    address = account.address
    print(f"[EMILY-SYS] Wallet activo: {address}")

    nonce = w3.eth.get_transaction_count(address)
    hex_data = "0x" + binascii.hexlify(MESSAGE.encode('utf-8')).decode('utf-8')

    tx = {
        'to': address,
        'value': 0,
        'gas': 21000,
        'gasPrice': w3.eth.gas_price,
        'nonce': nonce,
        'data': hex_data,
        'chainId': 1
    }

    print("[EMILY-SYS] Firmando y enviando transacción...")
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"[SUCCESS] Mensaje grabado en Mainnet: https://etherscan.io/tx/{tx_hash.hex()}")

if __name__ == "__main__":
    broadcast_manifesto()
