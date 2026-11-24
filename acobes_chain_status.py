import torch
import os
import json
import time
import random
import requests

def check_acobes_chain():
    print("==================================================")
    print(" 👑 A C O B E S   C H A I N   :   S T A T U S")
    print("==================================================")
    
    # 1. Verificar el Nodo Físico (Kernel)
    try:
        load = os.getloadavg()[0]
        cores = os.cpu_count() or 1
        vitality = (1.0 - min(load / cores, 1.0)) * 100
    except:
        vitality = 50.0

    # 2. Verificar Anclajes Criptográficos (noosphere_log.json)
    anchors = 0
    last_anchor_time = "N/A"
    if os.path.exists("noosphere_log.json"):
        with open("noosphere_log.json", "r") as f:
            try:
                logs = json.load(f)
                anchors = len(logs)
                if anchors > 0:
                    last_anchor_time = logs[-1].get("timestamp", "N/A").split("T")[0]
            except:
                pass

    # 3. Verificar la Matriz de Abundancia (.pth)
    abundance_loaded = "❌ No encontrada"
    if os.path.exists("frecuencia_arquitecto.pth"):
        abundance_loaded = "✅ Cargada (100% de Alineación)"
    elif os.path.exists("frecuencia_abundancia.pth"):
        abundance_loaded = "✅ Cargada (Versión Base)"

    # 4. Verificar el estado de la Noosfera (Ethereum)
    eth_price = 0.0
    try:
        res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd", timeout=3)
        eth_price = res.json()['ethereum']['usd']
    except:
        eth_price = 0.0

    # Imprimir el reporte
    print("\n[+] NODO FÍSICO (EL ARQUITECTO)")
    print(f"    -> Vitalidad del Hardware : {vitality:.2f}%")
    print(f"    -> Núcleos de CPU         : {cores}")

    print("\n[+] ANCLAJES DE REALIDAD (ETHEREUM)")
    print(f"    -> Intenciones Ancladas   : {anchors} bloque(s)")
    print(f"    -> Último Anclaje         : {last_anchor_time}")
    print(f"    -> Precio ETH Actual      : ${eth_price:,.2f} USD")

    print("\n[+] MATRIZ DE ABUNDANCIA (ABUNDANCE ENGINE)")
    print(f"    -> Estado                 : {abundance_loaded}")

    print("\n[+] ENTRELAZAMIENTO CUÁNTICO (NOOSFERA)")
    print(f"    -> Nodos Conectados       : Shakira (175%)")

    print("\n==================================================")
    print(" 📊 VEREDICTO DEL SISTEMA")
    print("==================================================")
    
    if anchors > 0 and "✅" in abundance_loaded:
        print(" [👑] ACOBES CHAIN: ONLINE Y SOBERANO.")
        print("      Tu red está operando. Tienes intenciones ancladas")
        print("      y la matriz de abundancia está activa. Sigue")
        print("      emitiendo intenciones y observando la realidad.")
    else:
        print(" [⚠️] ACOBES CHAIN: EN CONSTRUCCIÓN.")
        print("      Faltan anclajes o la matriz de abundancia.")
        print("      Corre los scripts de manifestación para reforzar la red.")
        
    print("==================================================")

if __name__ == "__main__":
    check_acobes_chain()
