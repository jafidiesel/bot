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

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Make the GET request
        response = requests.get(api_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse and use the response data
            data = response.json()
            usd_ars = data['payload'][21]
            del usd_ars['volume']
            del usd_ars['vwap']
            del usd_ars['change_24']
            del usd_ars['rolling_average_change']

            usdt_ars = data['payload'][82]
            del usdt_ars['volume']
            del usdt_ars['vwap']
            del usdt_ars['change_24']
            del usdt_ars['rolling_average_change']
        else:
            print(f"Request failed with status code {response.status_code}")

    except requests.exceptions.RequestException as e:
        print("Request exception:", e)
    print(update.effective_chat.username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps([usd_ars,usdt_ars], indent=4))

if __name__ == '__main__':
    application = ApplicationBuilder().token(config['TELEGRAM_TOKEN']).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    test_handler = CommandHandler('test', test)
    application.add_handler(test_handler)
    
    application.run_polling()
