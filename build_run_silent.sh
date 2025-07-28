#!/bin/bash

cd /home/pi/git/bot

rm -rf bin
rm -rf include
rm -rf lib
rm lib64
rm pyvenv.cfg

python3 -m venv .

source bin/activate

pip3 install python-telegram-bot --upgrade python-dotenv requests

python3 bot.py
