#!/bin/bash

# Nombre de la imagen
IMAGE_NAME="bot"

# Construir la imagen Docker
echo "Construyendo la imagen Docker..."
docker build -t $IMAGE_NAME .

# Ejecutar el contenedor
echo "Ejecutando el contenedor..."
docker run --env-file .env $IMAGE_NAME