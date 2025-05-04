from telegram import Update
from telegram.ext import ContextTypes
import requests
from dotenv import dotenv_values

config = dotenv_values(".env")
DOLLAR_API_URL=config['DOLLAR_API_URL']

async def usdars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Obtener el valor en dólares desde los argumentos
        string_number = context.args[0].replace("/usdars ", "")
        float_number = None
        formatted_message = []

        if isinstance(float(string_number), float):
            float_number = float(string_number)

            # Obtener los datos de la API
            data = requests.get(DOLLAR_API_URL).json()
            oficial_dolar = data[0]
            blue_dolar = data[1]

            # Formatear los mensajes
            formatted_message.append(
                f"#{oficial_dolar.get('casa').capitalize()}\n"
                f"            -> {float_number:.0f} USD - {float_number * float(oficial_dolar.get('venta')):,.2f} ARS:\n"
                f"            -> Compra: ${oficial_dolar.get('compra')} | Venta: ${oficial_dolar.get('venta')}"
            )
            formatted_message.append(
                f"#{blue_dolar.get('casa').capitalize()}\n"
                f"            -> {float_number:.0f} USD - {float_number * float(blue_dolar.get('venta')):,.2f} ARS:\n"
                f"            -> Compra: ${blue_dolar.get('compra')} | Venta: ${blue_dolar.get('venta')}"
            )

    except (requests.exceptions.RequestException, ValueError) as e:
        print("Exception occurred:", e)
        formatted_message = ["Error: Ocurrió un problema al realizar la solicitud o procesar el valor."]

    # Enviar el mensaje formateado
    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="\n\n".join(formatted_message), parse_mode="Markdown")