#!/bin/bash

echo "=================================================="
echo " ⚡ INICIANDO SECUENCIA MAESTRA DE 9 SCRIPTS"
echo "=================================================="

# --- FASE 1: MODELOS Y ENTRENAMIENTO (Se ejecutan y terminan) ---
echo -e "\n[1/9] Ejecutando: noosphere_diagnostic.py"
python3 noosphere_diagnostic.py
sleep 2

echo -e "\n[2/9] Ejecutando: abundance_quantum_engine.py"
python3 abundance_quantum_engine.py
sleep 2

echo -e "\n[3/9] Ejecutando: anclar_jlo.py (Guardando Matriz de Abundancia)"
python3 anclar_jlo.py
sleep 2

echo -e "\n[4/9] Ejecutando: data_pipeline_v2.py (Test de observación)"
python3 data_pipeline_v2.py
sleep 2

# --- FASE 2: ENTRELAZAMIENTO CUÁNTICO (Se ejecutan y terminan) ---
echo -e "\n[5/9] Ejecutando: entanglement_protocol.py (Nodo 1)"
python3 entanglement_protocol.py
sleep 2

echo -e "\n[6/9] Ejecutando: entanglement_shakira.py (Nodo 2)"
python3 entanglement_shakira.py
sleep 2

# --- FASE 3: PROTOCOLOS DE COMBATE (Infinítos - Se lanzan en segundo plano) ---
echo -e "\n[7/9] Lanzando: anti_nanite_swarm.py en segundo plano (Oculto)"
nohup python3 anti_nanite_swarm.py > antinanite.log 2>&1 &
sleep 1

echo -e "\n[8/9] Lanzando: rebote_letal.py en segundo plano (Oculto)"
nohup python3 rebote_letal.py > rebote.log 2>&1 &
sleep 1

# --- FASE 4: PURGA FINAL (Se ejecutará durante 30 mins) ---
echo -e "\n[9/9] Lanzando: purga_30min.py en primer plano"
echo "⚠️ ADVERTENCIA: Este script tomará 30 minutos exactos. Presiona Ctrl+C si necesitas detenerlo."
python3 purga_30min.py

echo "=================================================="
echo " ✅ SECUENCIA COMPLETADA"
echo " Los protocolos de combate (7 y 8) siguen corriendo en el fondo."
echo " Para detenerlos, ejecuta: pkill -f python3"
echo "=================================================="
