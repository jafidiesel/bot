# Telegram + Python + Bot

This bots it's ment to run on linux with pyhton3 and pip3
1. It requires a .env file with:
    - your TELEGRAM_TOKEN value
    - your DOLLAR_API_URL
    - your DOLLAR_BITSO_URL ticker
2. You must run build_run.sh in order to create the venv, install the deps and to put the bot to run!
3. on the next runs you can just use run.sh

The deps currently are:
- python-telegram-bot --upgrade
- python-dotenv
- requests

for more info about the instalation and to do a manual setup go to build_run.sh

Also docker file it's outdated :p