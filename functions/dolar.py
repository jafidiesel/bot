from telegram import Update
from telegram.ext import ContextTypes
import requests
import json
from dotenv import dotenv_values

config = dotenv_values(".env")
DOLLAR_API_URL=config['DOLLAR_API_URL']


async def dolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dolar_prices = [' Casa - Compra - Venta - Timestamp']
    try:
        data = requests.get(DOLLAR_API_URL).json()
        print(data)

        for obj in data:
            type = obj.get('casa')
            buy = obj.get('compra')
            sell = obj.get('venta')
            timestamp = obj.get('fechaActualizacion')
            dolar_prices.append(f"<{type}>  |  ${buy}  |  ${sell}  |  {timestamp}")

    except requests.exceptions.RequestException as e:
        print("Request exception:", e)

    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps(dolar_prices, indent=4))