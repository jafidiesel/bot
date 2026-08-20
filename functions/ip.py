from telegram import Update
from telegram.ext import ContextTypes
import subprocess
import json
import requests

async def ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        authorized_users = [71870097]
        if user_id not in authorized_users:
            await update.message.reply_text("❌ No autorizado para usar este comando")
            return

        ip_cmd = "hostname -I"
        ip_result_tmp = subprocess.check_output(ip_cmd, shell=True).decode("utf-8").strip()

        ip_result = ip_result_tmp.split(" ")[0]
        print("Raspberry Pi ip:", ip_result)

    except subprocess.CalledProcessError as e:
        print("Failed to execute the command. Ensure this is a Raspberry Pi.")
        print("Subprocess error:", e)
    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps(ip_result, indent=4))