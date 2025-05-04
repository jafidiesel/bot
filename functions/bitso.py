from telegram import Update
from telegram.ext import ContextTypes
import requests
import json
from dotenv import dotenv_values
config = dotenv_values(".env")

BITSO_URL=config['DOLLAR_BITSO_URL']


async def bitso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Make the GET request
        response = requests.get(BITSO_URL)

        # Check if the request was successful (status code 200)
        formatted_message = []
        target_books = ['usd_ars', 'usdt_ars']

        if response.status_code == 200:
            # Parse and use the response data
            data = response.json()
            for obj in data.get('payload'):
                if obj.get("book") in target_books:
                    book = obj.get("book")
                    last = obj.get("last")
                    low = obj.get("low")
                    high = obj.get("high")
                    formatted_message.append(f"#{book} -> _{last}_\n                 low: _{low}_ - high: _{high}_")
        else:
            print(f"Request failed with status code {response.status_code}")
            formatted_message.append("Error: No se pudo obtener los datos de Bitso.")

    except requests.exceptions.RequestException as e:
        print("Request exception:", e)
        formatted_message.append("Error: Ocurrió un problema al realizar la solicitud.")

    # Send the formatted message
    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="\n\n".join(formatted_message), parse_mode="Markdown")