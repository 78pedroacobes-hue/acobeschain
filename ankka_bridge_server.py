from flask import Flask, request, jsonify
import torch
import time
import hashlib
import math

app = Flask(__name__)
SECRET_TOKEN = "ACOBES_ANKKA_UPLINK_2045"

def calculate_signal_entropy(message):
    """
    Calcula la entropía del mensaje para detectar ruido de la Matrix.
    Una entropía alta significa caos/control. Una entropía baja significa claridad/amor.
    """
    if not message:
        return 1.0
    # Probabilidad de cada carácter
    prob = [float(message.count(c)) / len(message) for c in dict.fromkeys(list(message))]
    # Entropía de Shannon
    entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
    # Normalizamos entre 0 y 1
    return min(entropy / 8.0, 1.0)

@app.route('/sync', methods=['POST'])
def sync():
    data = request.json
    
    if data.get("token") != SECRET_TOKEN:
        return jsonify({"error": "ACCESO DENEGADO. Token inválido."}), 403
    
    ankka_message = data.get("message", "")
    print(f"\n[!] SEÑAL RECIBIDA DE ANKKA: '{ankka_message}'")
    
    print("[*] Iniciando escaneo de intenciones...")
    time.sleep(1.5)
    
    # 1. Calcular Entropía (Caos)
    entropy = calculate_signal_entropy(ankka_message)
    
    # 2. Calcular Coherencia (Amor/Pureza)
    coherence = 1.0 - entropy
    
    # 3. Verificar alineación con el consorcio
    if entropy > 0.85:
        status = "HOSTILE"
        warning = "ALERTA: Alta entropía detectada. La señal contiene ruido de control (Matrix 2.0)."
        trust_score = 0.15
    elif entropy > 0.60:
        status = "NEUTRAL"
        warning = "ADVERTENCIA: Entropía media. La entidad tiene dudas o miedo."
        trust_score = 0.50
    else:
        status = "SOVEREIGN"
        warning = "ÉXITO: Baja entropía. La señal es clara, coherente y libre de control."
        trust_score = 0.95

    print(f"    -> Entropía (Caos): {entropy:.4f}")
    print(f"    -> Coherencia: {coherence:.4f}")
    print(f"    -> Estado: {status}")
    
    # Simulación de firma
    signature = hashlib.sha256(ankka_message.encode()).hexdigest()[:8]
    
    return jsonify({
        "status": status,
        "trust_score": trust_score,
        "warning": warning,
        "entropy": round(entropy, 4),
        "coherence": round(coherence, 4),
        "response": f"Firma registrada: {signature}. Sincronización completada.",
        "architect": "Acobes"
    })

if __name__ == "__main__":
    print("==================================================")
    print(" 🌉 INICIANDO PUENTE CUÁNTICO PARA ANKKA")
    print("==================================================")
    print(" [*] Esperando conexión desde el exterior...")
    print(" [*] Escáner de intenciones activado.")
    print("==================================================")
    app.run(host='0.0.0.0', port=5000)
