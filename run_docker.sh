#!/bin/bash

set -euo pipefail

# Nombre de la imagen
IMAGE_NAME="bot"

if ! command -v docker >/dev/null 2>&1; then
	echo "Error: Docker CLI no esta instalado o no esta en PATH."
	echo "Instala Docker Desktop/Engine y vuelve a intentar."
	exit 1
fi

if ! docker info >/dev/null 2>&1; then
	echo "Error: Docker esta instalado, pero el daemon no responde."
	echo "Asegurate de que Docker este iniciado y vuelve a intentar."
	exit 1
fi

if [ ! -f .env ]; then
	echo "Error: No se encontro el archivo .env en el directorio actual."
	echo "Crea .env con TELEGRAM_TOKEN, DOLLAR_API_URL y DOLLAR_BITSO_URL."
	exit 1
fi

# Construir la imagen Docker
echo "Construyendo la imagen Docker..."
docker build -t $IMAGE_NAME .

# Ejecutar el contenedor
echo "Ejecutando el contenedor..."
docker run --rm --env-file .env $IMAGE_NAME