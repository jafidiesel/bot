from telegram import Update
from telegram.ext import ContextTypes
import subprocess

async def temp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    temperature_result = "Error: No se pudo obtener la temperatura en este entorno."
    try:
        # Works on Raspberry Pi systems where vcgencmd is available.
        temperature_result = subprocess.check_output(["vcgencmd", "measure_temp"], text=True).strip()

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("Failed to execute the command. Ensure this is a Raspberry Pi.")
        print("Subprocess error:", e)

    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=temperature_result)