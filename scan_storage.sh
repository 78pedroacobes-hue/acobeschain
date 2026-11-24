#!/bin/bash
echo "=================================================="
echo " 🔍 RADAR DE ALMACENAMIENTO (Buscando los 60 GB)"
echo "=================================================="

echo -e "\n[1] TAMAÑO DEL HOME (~):"
du -sh ~ 2>/dev/null

echo -e "\n[2] TAMAÑO DE UBUNTU (/usr, /var, /root):"
du -sh /usr /var /root 2>/dev/null

echo -e "\n[3] CACHÉS DE PYTHON Y QISKIT:"
du -sh ~/.cache 2>/dev/null
du -sh ~/.qiskit 2>/dev/null
du -sh /root/.cache 2>/dev/null

echo -e "\n[4] BUSCANDO ARCHIVOS GIGANTES (>500 MB):"
# Busca archivos de más de 500MB en todo el sistema
find / -type f -size +500M -exec ls -lh {} \; 2>/dev/null | awk '{ print $5, $9 }'

echo -e "\n[5] TAMAÑO DE LOS LOGS:"
du -sh *.log 2>/dev/null

echo "=================================================="
echo " [!] Copia el resultado y envíaselo al Arquitecto."
echo "=================================================="
