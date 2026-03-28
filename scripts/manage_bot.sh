#!/bin/bash

# manage_bot.sh - Gestion del Bot de Telegram en Raspberry Pi

# Uso: ./manage_bot.sh [install|start|stop|restart|status|logs|uninstall]

SERVICE_NAME=“bot_script”
SERVICE_FILE=”/etc/systemd/system/${SERVICE_NAME}.service”
BOT_DIR=”/home/jafidiesel/git/bot”
VENV_DIR=”${BOT_DIR}/venv”
PYTHON=”${VENV_DIR}/bin/python3”

print_ok()   { echo “[OK] $1”; }
print_err()  { echo “[ERROR] $1”; }
print_info() { echo “[INFO] $1”; }

check_root() {
if [ “$EUID” -ne 0 ]; then
print_err “Requiere root. Usa: sudo ./manage_bot.sh $1”
exit 1
fi
}

check_bot_dir() {
if [ ! -d “$BOT_DIR” ]; then
print_err “No se encontro el directorio: $BOT_DIR”
exit 1
fi
}

check_env_file() {
if [ ! -f “${BOT_DIR}/.env” ]; then
print_err “No existe .env en $BOT_DIR”
print_info “Copia .env.example a .env y completa tus tokens”
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
    print_err "Fallo la creacion del venv."
    print_info "Intenta: sudo apt install python3-venv"
    exit 1
fi
print_ok "Entorno virtual creado."

print_info "Instalando dependencias..."
"${VENV_DIR}/bin/pip" install --upgrade pip -q
"${VENV_DIR}/bin/pip" install -r "${BOT_DIR}/requirements.txt" -q
if [ $? -ne 0 ]; then
    print_err "Fallo la instalacion de dependencias."
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
    print_ok "Servicio instalado y corriendo."
    print_info "El bot se iniciara automaticamente en cada reboot."
else
    print_err "El servicio no arranco correctamente."
    print_info "Revisa los logs con: sudo ./manage_bot.sh logs"
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
print_err “No se pudo iniciar. Revisa: sudo ./manage_bot.sh logs”
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
print_err “No se pudo reiniciar. Revisa: sudo ./manage_bot.sh logs”
fi
}

cmd_status() {
echo “”
systemctl status “$SERVICE_NAME” –no-pager
echo “”
}

cmd_logs() {
print_info “Mostrando ultimas 50 lineas de log (Ctrl+C para salir)…”
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
print_ok “Servicio desinstalado. El venv y el codigo no fueron tocados.”
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
echo “  install    - Crea el venv, instala deps y registra el servicio”
echo “  start      - Inicia el bot”
echo “  stop       - Detiene el bot”
echo “  restart    - Reinicia el bot”
echo “  status     - Muestra el estado del servicio”
echo “  logs       - Muestra los logs en tiempo real”
echo “  uninstall  - Elimina el servicio de systemd”
echo “”
exit 1
;;
esac