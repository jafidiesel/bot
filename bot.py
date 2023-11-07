import logging
import requests
import json
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import dotenv_values
config = dotenv_values(".env")

BITSO_URL=config['DOLLAR_BITSO_URL']
DOLLAR_API_URL=config['DOLLAR_API_URL']

#logging.basicConfig(
#    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#    level=logging.INFO
#)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def bitso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Make the GET request
        response = requests.get(BITSO_URL)

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
        data = requests.get(DOLLAR_API_URL).json()
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

async def temp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Read CPU temperature using subprocess
        temperature_cmd = "vcgencmd measure_temp"
        temperature_result = subprocess.check_output(temperature_cmd, shell=True).decode("utf-8").strip()

        print("Raspberry Pi CPU Temperature (millidegrees):", temperature_result)

    except requests.exceptions.RequestException as e:
        print("Request exception:", e)
    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps(temperature_cmd, indent=4))

async def usdars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        
        string_number = context.args[0].replace("/usdars ", "")
        float_number = None
        value_in_dolars = ['ARS total => Casa - Compra - Venta']

        if( isinstance(float(string_number), float)):
            float_number=float(string_number)

            data = requests.get(DOLLAR_API_URL).json()
            oficial_dolar = data[0]
            blue_dolar = data[1]
            value_in_dolars.append(f"{float_number*oficial_dolar.get('venta')} ARS => {oficial_dolar.get('casa')}  |  ${oficial_dolar.get('compra')}  |  ${oficial_dolar.get('venta')}")
            value_in_dolars.append(f"{float_number*blue_dolar.get('venta')} ARS => {blue_dolar.get('casa')}  |  ${blue_dolar.get('compra')}  |  ${blue_dolar.get('venta')}")

    except requests.exceptions.RequestException as e:
        print("Request exception:", e)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps(value_in_dolars, indent=4))

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

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="http://jafibravin.com/cv")

if __name__ == '__main__':
    application = ApplicationBuilder().token(config['TELEGRAM_TOKEN']).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    bitso_handler = CommandHandler('bitso', bitso)
    application.add_handler(bitso_handler)

    dolar_handler = CommandHandler('dolar', dolar)
    application.add_handler(dolar_handler)

    temp_handler = CommandHandler('temp', temp)
    application.add_handler(temp_handler)

    usdars_handler = CommandHandler('usdars', usdars)
    application.add_handler(usdars_handler)

    arsusd_handler = CommandHandler('arsusd', arsusd)
    application.add_handler(arsusd_handler)

    test_handler = CommandHandler('test', test)
    application.add_handler(test_handler)
    
    application.run_polling()
