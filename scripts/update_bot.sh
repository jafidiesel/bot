#!/bin/bash
BOT_DIR="/home/jafidiesel/git/bot"
VENV_DIR="${BOT_DIR}/venv"
SERVICE_NAME="bot_script"

echo "[INFO] Bajando cambios del repo..."
cd "$BOT_DIR"
git pull
if [ $? -ne 0 ]; then
    echo "[ERROR] Fallo git pull. Revisa tu conexion o el repo."
    exit 1
fi
echo "[OK] Repo actualizado."

echo "[INFO] Actualizando dependencias..."
"${VENV_DIR}/bin/pip" install -r "${BOT_DIR}/requirements.txt" -q
if [ $? -ne 0 ]; then
    echo "[ERROR] Fallo la instalacion de dependencias."
    exit 1
fi
echo "[OK] Dependencias actualizadas."

echo "[INFO] Reiniciando el servicio..."
sudo systemctl restart "$SERVICE_NAME"
sleep 2

if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "[OK] Bot reiniciado y corriendo."
else
    echo "[ERROR] El servicio no arranco. Revisa con: sudo journalctl -u bot_script -n 30"
fi
