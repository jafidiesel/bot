from telegram import Update
from telegram.ext import ContextTypes
import requests
from dotenv import dotenv_values
from datetime import datetime

config = dotenv_values(".env")
DOLLAR_API_URL=config['DOLLAR_API_URL']


async def dolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        data = requests.get(DOLLAR_API_URL).json()

        formatted_message = []
        for obj in data:
            type = obj.get('casa').capitalize()
            buy = obj.get('compra')
            sell = obj.get('venta')
            timestamp = obj.get('fechaActualizacion')

            # Formatear el timestamp
            formatted_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%y %H:%M")

            # Formatear el mensaje
            formatted_message.append(
                f"#{type}:\n      Compra: ${buy} | Venta: ${sell}\n      Actualizado: {formatted_timestamp}"
            )

    except requests.exceptions.RequestException as e:
        print("Request exception:", e)
        formatted_message = ["Error: Ocurrió un problema al realizar la solicitud."]

    # Enviar el mensaje formateado
    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="\n\n".join(formatted_message), parse_mode="Markdown")