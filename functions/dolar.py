from telegram import Update
from telegram.ext import ContextTypes
import requests
from dotenv import dotenv_values
from datetime import datetime

config = dotenv_values(".env")
DOLLAR_API_URL=config['DOLLAR_API_URL']


async def dolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    formatted_message = []
    try:
        response = requests.get(DOLLAR_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        for obj in data:
            rate_type = str(obj.get('casa', 'desconocido')).capitalize()
            buy = obj.get('compra')
            sell = obj.get('venta')
            timestamp = obj.get('fechaActualizacion')

            # Formatear el timestamp cuando exista y sea valido.
            formatted_timestamp = "N/A"
            if timestamp:
                formatted_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%y %H:%M")

            # Formatear el mensaje
            formatted_message.append(
                f"#{rate_type}:\n      Compra: ${buy} | Venta: ${sell}\n      Actualizado: {formatted_timestamp}"
            )

        if not formatted_message:
            formatted_message = ["Error: La API no devolvio datos de cotizaciones."]

    except (requests.exceptions.RequestException, ValueError, TypeError) as e:
        print("Request exception:", e)
        formatted_message = ["Error: Ocurrió un problema al realizar la solicitud."]

    # Enviar el mensaje formateado
    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="\n\n".join(formatted_message), parse_mode="Markdown")