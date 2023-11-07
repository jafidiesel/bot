#!/bin/bash
echo "starting..."
ls

echo "Activate venv"
source bin/activate
echo "Done!"

echo "Running..."
python3 bot.py