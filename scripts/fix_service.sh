#!/bin/bash

echo "=== Reparando configuración del servicio del bot ==="

# Verificar que estamos en el directorio correcto
if [[ ! -f "bot.py" ]]; then
    echo "❌ Error: Ejecuta este script desde el directorio /home/pi/git/bot/bot/"
    exit 1
fi

echo "1. Deteniendo servicio actual..."
sudo systemctl stop bot_script.service 2>/dev/null || echo "   Servicio no estaba corriendo"

echo "2. Deshabilitando servicio con configuración incorrecta..."
sudo systemctl disable bot_script.service 2>/dev/null || echo "   Servicio no estaba habilitado"

echo "3. Copiando nueva configuración..."
sudo cp bot_script.service /etc/systemd/system/

echo "4. Recargando configuración de systemd..."
sudo systemctl daemon-reload

echo "5. Habilitando nuevo servicio..."
sudo systemctl enable bot_script.service

echo "6. Verificando configuración del archivo .env..."
if [[ ! -f ".env" ]]; then
    echo "❌ Error: Archivo .env no encontrado"
    echo "   Crea el archivo .env con tu TELEGRAM_TOKEN"
    exit 1
fi

if grep -q "TU_TOKEN_AQUI" .env; then
    echo "⚠️  Advertencia: TELEGRAM_TOKEN no configurado en .env"
    echo "   Edita .env y configura tu token antes de iniciar"
fi

echo "7. Dando permisos de ejecución al script..."
chmod +x build_run_silent.sh

echo ""
echo "=== Reparación completada ==="
echo ""
echo "Para iniciar el servicio:"
echo "  sudo systemctl start bot_script"
echo ""
echo "Para verificar estado:"
echo "  sudo systemctl status bot_script"
echo ""
echo "Para ver logs:"
echo "  sudo journalctl -u bot_script -f"
echo ""
echo "Para detener el servicio anterior (si sigue activo):"
echo "  sudo systemctl stop bot_script"
echo "  sudo systemctl disable bot_script"
