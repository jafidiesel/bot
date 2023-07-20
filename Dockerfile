# syntax=docker/dockerfile:1

FROM python:3.9
#WORKDIR /app
#COPY requirements.txt requirements.txt
#RUN pip3 install -r requirements.txt
ADD bot.py .
RUN pip install python-telegram-bot --upgrade
CMD ["python", "./bot.py"]
