from telegram import Update
from telegram.ext import ContextTypes
import requests
from dotenv import dotenv_values

config = dotenv_values(".env")
DOLLAR_API_URL=config['DOLLAR_API_URL']


def _to_float(value):
    return float(str(value).replace(",", "."))

async def arsusd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Uso: /arsusd <monto_en_ars>"
        )
        return

    try:
        # Obtener el valor en ARS desde los argumentos
        string_number = context.args[0].replace(",", ".")
        formatted_message = []

        float_number = float(string_number)

        # Obtener los datos de la API
        response = requests.get(DOLLAR_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        oficial_dolar = data[0]
        blue_dolar = data[1]

        oficial_venta = _to_float(oficial_dolar.get('venta'))
        blue_venta = _to_float(blue_dolar.get('venta'))

        # Formatear los mensajes
        formatted_message.append(
            f"# {oficial_dolar.get('casa').capitalize()}\n"
            f"            -> {float_number:,.2f} ARS - {float_number / oficial_venta:,.2f} USD:\n"
            f"            -> Compra: ${oficial_dolar.get('compra')} | Venta: ${oficial_dolar.get('venta')}"
        )
        formatted_message.append(
            f"# {blue_dolar.get('casa').capitalize()}\n"
            f"            -> {float_number:,.2f} ARS - {float_number / blue_venta:,.2f} USD:\n"
            f"            -> Compra: ${blue_dolar.get('compra')} | Venta: ${blue_dolar.get('venta')}"
        )

    except (requests.exceptions.RequestException, ValueError, IndexError, TypeError) as e:
        print("Exception occurred:", e)
        formatted_message = ["Error: Ocurrió un problema al realizar la solicitud o procesar el valor."]

    # Enviar el mensaje formateado
    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="\n\n".join(formatted_message), parse_mode="Markdown")