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