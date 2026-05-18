from telegram import Update
from telegram.ext import ContextTypes
import requests
from dotenv import dotenv_values

config = dotenv_values(".env")
EURO_API_URL = config.get('EURO_API_URL')


async def eurars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Obtener el valor en euros desde los argumentos
        string_number = context.args[0].replace("/eurars ", "")
        float_number = float(string_number)
        formatted_message = []

        if not EURO_API_URL:
            raise ValueError("EURO_API_URL no configurada")

        # Obtener los datos de la API
        data = requests.get(EURO_API_URL).json()
        euro_data = data[0] if isinstance(data, list) else data

        # Formatear el mensaje
        formatted_message.append(
            f"#{euro_data.get('casa', 'Euro').capitalize()}\n"
            f"            -> {float_number:.0f} EUR - {float_number * float(euro_data.get('venta')):,.2f} ARS:\n"
            f"            -> Compra: ${euro_data.get('compra')} | Venta: ${euro_data.get('venta')}"
        )

    except (IndexError, TypeError, requests.exceptions.RequestException, ValueError) as e:
        print("Exception occurred:", e)
        formatted_message = ["Error: Ocurrió un problema al realizar la solicitud o procesar el valor."]

    # Enviar el mensaje formateado
    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="\n\n".join(formatted_message), parse_mode="Markdown")
