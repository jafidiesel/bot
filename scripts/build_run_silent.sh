#!/bin/bash

# Definir la ruta del proyecto
PROJECT_DIR="/home/pi/git/bot"

# Cambiar al directorio del proyecto
cd "$PROJECT_DIR"

# Limpiar instalación anterior del virtual environment
rm -rf bin
rm -rf include
rm -rf lib
rm -f lib64
rm -f pyvenv.cfg

# Crear nuevo virtual environment
python3 -m venv .

# Activar virtual environment
source bin/activate

# Actualizar pip
pip3 install --upgrade pip

# Instalar dependencias desde requirements.txt
pip3 install -r requirements.txt

# Ejecutar el bot
python3 bot.py
