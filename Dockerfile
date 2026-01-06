# syntax=docker/dockerfile:1

FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos necesarios
COPY bot.py ./
COPY functions ./functions
COPY requirements.txt ./
COPY .env ./

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Comando para ejecutar el bot
CMD ["python", "bot.py"]