#!/bin/bash

sudo systemctl daemon-reload
sudo systemctl restart bot_script.service
sudo systemctl status bot_script.service
sudo journalctl -u bot_script.service

