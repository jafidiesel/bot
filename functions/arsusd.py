from telegram import Update
from telegram.ext import ContextTypes
import requests
import json
from dotenv import dotenv_values

config = dotenv_values(".env")
DOLLAR_API_URL=config['DOLLAR_API_URL']

async def arsusd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        
        string_number = context.args[0].replace("/arsusd ", "")
        float_number = None
        value_in_dolars = ['USD total => Casa - Compra - Venta']

        if( isinstance(float(string_number), float)):
            float_number=float(string_number)

            data = requests.get(DOLLAR_API_URL).json()
            oficial_dolar = data[0]
            blue_dolar = data[1]
            value_in_dolars.append(f"{float_number/oficial_dolar.get('venta')} ARS => {oficial_dolar.get('casa')}  |  ${oficial_dolar.get('compra')}  |  ${oficial_dolar.get('venta')}")
            value_in_dolars.append(f"{float_number/blue_dolar.get('venta')} ARS => {blue_dolar.get('casa')}  |  ${blue_dolar.get('compra')}  |  ${blue_dolar.get('venta')}")

    except requests.exceptions.RequestException as e:
        print("Request exception:", e)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps(value_in_dolars, indent=4))