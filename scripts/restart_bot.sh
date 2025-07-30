#!/bin/bash
sudo rm -f /etc/systemd/bot_script.service
sudo cp /home/pi/git/bot/telegram-bot.service /etc/systemd

sudo systemctl daemon-reload
sudo systemctl restart bot_script.service
sudo systemctl status bot_script.service
sudo journalctl -u bot_script.service

