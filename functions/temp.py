from telegram import Update
from telegram.ext import ContextTypes
import subprocess
import json
import requests

async def temp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Read CPU temperature using subprocess
        temperature_cmd = "vcgencmd measure_temp"
        temperature_result = subprocess.check_output(temperature_cmd, shell=True).decode("utf-8").strip()

        print("Raspberry Pi CPU Temperature (millidegrees):", temperature_result)

    except requests.exceptions.RequestException as e:
        print("Command only valid for Raspberry Pi")
        print("Request exception:", e)
    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps(temperature_result, indent=4))