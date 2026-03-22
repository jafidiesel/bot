from telegram import Update
from telegram.ext import ContextTypes
import requests
from dotenv import dotenv_values
config = dotenv_values(".env")

BITSO_URL=config['DOLLAR_BITSO_URL']


async def bitso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    formatted_message = []
    try:
        # Make the GET request
        response = requests.get(BITSO_URL, timeout=10)
        response.raise_for_status()

        target_books = ['usd_ars', 'usdt_ars']
        data = response.json()
        payload = data.get('payload', [])

        # Parse and use the response data
        for obj in payload:
            if obj.get("book") in target_books:
                book = obj.get("book")
                last = obj.get("last")
                low = obj.get("low")
                high = obj.get("high")
                formatted_message.append(f"#{book} -> _{last}_\n                 low: _{low}_ - high: _{high}_")

        if not formatted_message:
            formatted_message = ["Error: No se encontraron datos para los pares esperados en Bitso."]

    except (requests.exceptions.RequestException, ValueError, TypeError) as e:
        print("Request exception:", e)
        formatted_message = ["Error: Ocurrió un problema al realizar la solicitud."]

    # Send the formatted message
    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="\n\n".join(formatted_message), parse_mode="Markdown")