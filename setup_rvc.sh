#!/bin/bash

# Actualizar e instalar dependencias del sistema
sudo apt update
sudo apt install -y python3-venv ffmpeg libsndfile1 libportaudio2 git

# Clonar repositorio oficial y entrar en la carpeta
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git
cd Retrieval-based-Voice-Conversion-WebUI

# Crear entorno virtual y activarlo
python3 -m venv .venv
source .venv/bin/activate

# Instalar requisitos de Python (versión para CPU/Linux)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Descargar modelos preentrenados necesarios
python tools/download_models.py

echo "Configuración completada. Activa el entorno con 'source .venv/bin/activate' para usar RVC."
