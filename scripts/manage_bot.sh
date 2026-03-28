#!/bin/bash

# ============================================================

# manage_bot.sh — Gestión del Bot de Telegram en Raspberry Pi

# Uso: ./manage_bot.sh [install|start|stop|restart|status|logs|uninstall]

# ============================================================

SERVICE_NAME=“bot_script”
SERVICE_FILE=”/etc/systemd/system/${SERVICE_NAME}.service”
BOT_DIR=”/home/jafidiesel/git/bot”
VENV_DIR=”${BOT_DIR}/venv”
PYTHON=”${VENV_DIR}/bin/python3”

RED=’\033[0;31m’
GREEN=’\033[0;32m’
YELLOW=’\033[1;33m’
NC=’\033[0m’

print_ok()   { echo -e “${GREEN}[OK]${NC} $1”; }
print_err()  { echo -e “${RED}[ERROR]${NC} $1”; }
print_info() { echo -e “${YELLOW}[INFO]${NC} $1”; }

check_root() {
if [ “$EUID” -ne 0 ]; then
print_err “Este comando requiere permisos de root. Usá: sudo ./manage_bot.sh $1”
exit 1
fi
}

check_bot_dir() {
if [ ! -d “$BOT_DIR” ]; then
print_err “No se encontró el directorio del bot en: $BOT_DIR”
print_info “Verificá que el repo esté clonado en $BOT_DIR”
exit 1
fi
}

check_env_file() {
if [ ! -f “${BOT_DIR}/.env” ]; then
print_err “No existe el archivo .env en $BOT_DIR”
print_info “Copiá .env.example a .env y completá tus tokens:”
print_info “  cp ${BOT_DIR}/.env.example ${BOT_DIR}/.env”
print_info “  nano ${BOT_DIR}/.env”
exit 1
fi
}

cmd_install() {
check_root “install”
check_bot_dir
check_env_file

```
print_info "Creando entorno virtual en $VENV_DIR ..."
python3 -m venv "$VENV_DIR"
if [ $? -ne 0 ]; then
    print_err "Falló la creación del venv. ¿Está instalado python3-venv?"
    print_info "Intentá: sudo apt install python3-venv"
    exit 1
fi
print_ok "Entorno virtual creado."

print_info "Instalando dependencias..."
"${VENV_DIR}/bin/pip" install --upgrade pip -q
"${VENV_DIR}/bin/pip" install -r "${BOT_DIR}/requirements.txt" -q
if [ $? -ne 0 ]; then
    print_err "Falló la instalación de dependencias."
    exit 1
fi
print_ok "Dependencias instaladas."

print_info "Registrando servicio systemd..."
cat > "$SERVICE_FILE" << EOF
```

[Unit]
Description=Bot de Telegram - Python
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=jafidiesel
Group=jafidiesel
WorkingDirectory=${BOT_DIR}
ExecStart=${PYTHON} ${BOT_DIR}/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

```
systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

sleep 2
if systemctl is-active --quiet "$SERVICE_NAME"; then
    print_ok "Servicio instalado y corriendo correctamente."
    print_info "El bot va a iniciarse automáticamente con cada reboot."
    print_info "Para ver los logs: sudo ./manage_bot.sh logs"
else
    print_err "El servicio no arrancó correctamente."
    print_info "Revisá los logs con: sudo ./manage_bot.sh logs"
fi
```

}

cmd_start() {
check_root “start”
print_info “Iniciando el bot…”
systemctl start “$SERVICE_NAME”
sleep 1
if systemctl is-active –quiet “$SERVICE_NAME”; then
print_ok “Bot iniciado.”
else
print_err “No se pudo iniciar. Revisá: sudo ./manage_bot.sh logs”
fi
}

cmd_stop() {
check_root “stop”
print_info “Deteniendo el bot…”
systemctl stop “$SERVICE_NAME”
print_ok “Bot detenido.”
}

cmd_restart() {
check_root “restart”
print_info “Reiniciando el bot…”
systemctl restart “$SERVICE_NAME”
sleep 1
if systemctl is-active –quiet “$SERVICE_NAME”; then
print_ok “Bot reiniciado correctamente.”
else
print_err “No se pudo reiniciar. Revisá: sudo ./manage_bot.sh logs”
fi
}

cmd_status() {
echo “”
systemctl status “$SERVICE_NAME” –no-pager
echo “”
}

cmd_logs() {
print_info “Mostrando últimas 50 líneas de log (Ctrl+C para salir)…”
echo “”
journalctl -u “$SERVICE_NAME” -n 50 -f
}

cmd_uninstall() {
check_root “uninstall”
print_info “Desinstalando el servicio…”
systemctl stop “$SERVICE_NAME” 2>/dev/null
systemctl disable “$SERVICE_NAME” 2>/dev/null
rm -f “$SERVICE_FILE”
systemctl daemon-reload
print_ok “Servicio desinstalado. El venv y el código no fueron tocados.”
}

case “$1” in
install)   cmd_install ;;
start)     cmd_start ;;
stop)      cmd_stop ;;
restart)   cmd_restart ;;
status)    cmd_status ;;
logs)      cmd_logs ;;
uninstall) cmd_uninstall ;;
*)
echo “”
echo “Uso: $0 {install|start|stop|restart|status|logs|uninstall}”
echo “”
echo “  install    — Crea el venv, instala deps y registra el servicio”
echo “  start      — Inicia el bot”
echo “  stop       — Detiene el bot”
echo “  restart    — Reinicia el bot”
echo “  status     — Muestra el estado del servicio”
echo “  logs       — Muestra los logs en tiempo real”
echo “  uninstall  — Elimina el servicio de systemd”
echo “”
exit 1
;;
esac