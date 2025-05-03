import logging
import requests
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from dotenv import dotenv_values
config = dotenv_values(".env")


#logging.basicConfig(
#    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#    level=logging.INFO
#)

from functions.start import start
from functions.bitso import bitso
from functions.dolar import dolar
from functions.temp import temp
from functions.usdars import usdars
from functions.arsusd import arsusd
from functions.test import test


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
