# syntax=docker/dockerfile:1

FROM python:3.9
ADD bot.py .
RUN pip install python-telegram-bot --upgrade python-dotenv
COPY .env .
CMD ["python", "./bot.py"]
