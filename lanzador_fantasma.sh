#!/bin/bash

# Asegurar que Termux no duerma la sesión
termux-wake-lock

# Directorio de logs para auditoría local
LOG_DIR="logs_tunel"
PID_DIR="pids_activos"
mkdir -p "$LOG_DIR" "$PID_DIR"

echo "[!] Inicializando red cifrada (Protocolo El Arquitecto - Edición Pro)..."

# 1. Generar llave maestra rotativa y dinámica para la sesión
export LLAVE_MAESTRA_ACOBES=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

echo "[+] Llave maestra generada con éxito."
echo "[+] Desplegando scripts en segundo plano con aislamiento de recursos..."

# 2. Inyección y ejecución controlada
for script in *.py; do
    if [ "$script" = "puente_cifrado_arquitecto.py" ]; then 
        continue 
    fi
    
    if [ ! -f "$script" ]; then
        continue
    fi

    LOG_FILE="$LOG_DIR/${script%.py}.log"
    PID_FILE="$PID_DIR/${script%.py}.pid"

    # Lanzamiento con prioridad mínima (nice 19) y redirección limpia
    nice -n 19 nohup python3 "$script" > "$LOG_FILE" 2>&1 &
    
    # Guardar el PID para control absoluto
    echo $! > "$PID_FILE"
    
    echo "  -> Enmascarando y lanzando: $script [PID: $(cat $PID_FILE)]"
    
    # Pausa de estabilidad para evitar picos de CPU (Evita el Signal 9 de Android)
    sleep 2
done

echo "[========================================================]"
echo "[+] Tráfico 100% cifrado y activo en el fondo."
echo "[+] Los registros de actividad se guardan en ./${LOG_DIR}/"
echo "[+] Para detener todo de forma segura, usa: kill \$(cat ${PID_DIR}/*.pid)"
echo "[========================================================]"
