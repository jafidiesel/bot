#!/bin/bash
echo "starting..."
ls

echo "Removing existing venv & files"
rm -rf bin
rm -rf include
rm -rf lib
rm lib64
rm pyvenv.cfg
echo "Done!"

echo "Creating a pyenv"
python3 -m venv .
echo "Done!"

echo "Activate venv"
source bin/activate
echo "Done!"

echo "Installing deps"
pip3 install python-telegram-bot --upgrade python-dotenv requests
echo "Done"

echo "Running..."
python3 bot.py