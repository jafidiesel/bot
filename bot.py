import logging
import requests
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import dotenv_values
config = dotenv_values(".env")

api_url ="https://bitso.com/api/v3/ticker"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def bitso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Make the GET request
        response = requests.get(api_url)

        # Check if the request was successful (status code 200)
        matching_objects = []
        target_books = ['usd_ars', 'usdt_ars']

        if response.status_code == 200:
            # Parse and use the response data
            data = response.json()
            for obj in data.get('payload'):
                if obj.get("book") in target_books:
                    del obj["volume"]
                    del obj["vwap"]
                    del obj["change_24"]
                    del obj["rolling_average_change"]
                    matching_objects.append(obj)
        else:
            print(f"Request failed with status code {response.status_code}")

    except requests.exceptions.RequestException as e:
        print("Request exception:", e)
    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps(matching_objects, indent=4))

async def dolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        URL = 'https://dolarapi.com/v1/dolares'

        data = requests.get(URL).json()
        dolar_prices = [' Casa - Compra - Venta - Timestamp']

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


if __name__ == '__main__':
    application = ApplicationBuilder().token(config['TELEGRAM_TOKEN']).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    bitso_handler = CommandHandler('bitso', bitso)
    application.add_handler(bitso_handler)

    dolar_handler = CommandHandler('dolar', dolar)
    application.add_handler(dolar_handler)
    
    application.run_polling()
