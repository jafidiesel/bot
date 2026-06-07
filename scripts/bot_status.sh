#!/bin/bash

# Bot Status Script - Shows systemctl status and last 20 log lines

BOT_DIR="/home/jafidiesel/git/bot"
SERVICE_NAME="bot_script"

echo "========================================"
echo "     BOT STATUS & LOG MONITOR"
echo "========================================\n"

# Check if service is running
echo "[System Status]"
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo "Service Status: RUNNING"
    UPTIME=$(systemctl status "$SERVICE_NAME" | grep "since" | awk '{print $NF, $(NF-1), $(NF-2), $(NF-3)}')
    echo "Since: $UPTIME"
else
    echo "Service Status: STOPPED"
fi

echo "\n[Service Details]"
systemctl status "$SERVICE_NAME" --no-pager | grep -E "Main PID|Memory|CPU" | sed 's/^/  /'

echo "\n[Process Check]"
PID=$(pgrep -f "python.*bot.py")
if [ -n "$PID" ]; then
    echo "Bot Process: Found (PID: $PID)"
else
    echo "Bot Process: Not found"
fi

echo "\n========================================"
echo "     LAST 20 LOG LINES"
echo "========================================\n"

# Display last 20 lines from bot log file
if [ -f "${BOT_DIR}/bot.log" ]; then
    echo "[From bot.log file]"
    tail -20 "${BOT_DIR}/bot.log" | sed 's/^/  /'
else
    echo "[From systemd journal]"
    sudo journalctl -u "$SERVICE_NAME" -n 20 --no-pager | sed 's/^/  /'
fi

echo "\n========================================"
echo "[Quick Commands]"
echo "  View live logs:     sudo journalctl -u $SERVICE_NAME -f"
echo "  Restart service:    sudo systemctl restart $SERVICE_NAME"
echo "  Stop service:       sudo systemctl stop $SERVICE_NAME"
echo "  Start service:      sudo systemctl start $SERVICE_NAME"
echo "========================================\n"
