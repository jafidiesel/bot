from telegram import Update
from telegram.ext import ContextTypes
import requests
from dotenv import dotenv_values
from datetime import datetime
import logging
from functools import wraps

config = dotenv_values(".env")
OPENWEATHER_API_KEY = config.get('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = config.get('OPENWEATHER_BASE_URL')

WEATHER_EMOJIS = {
    'Clear':         '☀️',
    'Clouds':        '☁️',
    'Rain':          '🌧️',
    'Drizzle':       '🌦️',
    'Thunderstorm':  '⛈️',
    'Snow':          '❄️',
    'Mist':          '🌫️',
    'Fog':           '🌫️',
    'Haze':          '🌫️',
    'Dust':          '🌪️',
    'Sand':          '🌪️',
    'Smoke':         '🌫️',
    'Ash':           '🌋',
    'Squall':        '💨',
    'Tornado':       '🌪️',
}


def handle_errors(func):
    @wraps(func)
    async def wrapper(update, context):
        try:
            return await func(update, context)
        except Exception as e:
            error_msg = f"❌ Error en {func.__name__}: {str(e)}"
            try:
                await update.message.reply_text(error_msg)
            except Exception:
                pass
            logging.error(f"Error in {func.__name__}: {e}", exc_info=True)
    return wrapper


def safe_api_call(url: str, params: dict, timeout: int = 10):
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.Timeout:
        return None, "⏱️ Timeout: La API tardó demasiado en responder"
    except requests.exceptions.ConnectionError:
        return None, "🔌 Error de conexión: Verifica la conexión a internet"
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if hasattr(e, 'response') else 'Unknown'
        if status == 404:
            return None, "❌ Ciudad no encontrada"
        if status == 401:
            return None, "🔑 API key inválida o no configurada"
        return None, f"🚫 Error HTTP {status}"
    except Exception as e:
        return None, f"❌ Error inesperado: {str(e)}"


def get_weather_emoji(weather_main: str) -> str:
    return WEATHER_EMOJIS.get(weather_main, '🌤️')


@handle_errors
async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not OPENWEATHER_API_KEY:
        await update.message.reply_text("❌ OPENWEATHER_API_KEY no configurada en .env")
        return

    if not context.args:
        await update.message.reply_text(
            "🌤️ Uso: /clima <ciudad>\n"
            "Ejemplo: /clima Buenos Aires"
        )
        return

    city = " ".join(context.args)
    params = {'q': city, 'appid': OPENWEATHER_API_KEY, 'units': 'metric', 'lang': 'es'}

    current, error = safe_api_call(f"{OPENWEATHER_BASE_URL}/weather", params)
    if error:
        await update.message.reply_text(error)
        return

    forecast, forecast_error = safe_api_call(f"{OPENWEATHER_BASE_URL}/forecast", params)

    try:
        emoji = get_weather_emoji(current['weather'][0]['main'])
        city_name = current['name']
        country = current['sys']['country']

        response = (
            f"{emoji} *Clima en {city_name}, {country}*\n\n"
            f"🌡️ *Temperatura:* {current['main']['temp']}°C (Sensación: {current['main']['feels_like']}°C)\n"
            f"📝 *Condición:* {current['weather'][0]['description'].title()}\n"
            f"💧 *Humedad:* {current['main']['humidity']}%\n"
            f"🔽 *Presión:* {current['main']['pressure']} hPa\n"
            f"💨 *Viento:* {current['wind']['speed']} m/s\n"
        )

        if forecast and not forecast_error:
            response += "\n📅 *Próximas horas:*\n"
            for item in forecast['list'][::3][:5]:
                dt = datetime.fromtimestamp(item['dt'])
                fe = get_weather_emoji(item['weather'][0]['main'])
                response += (
                    f"{fe} *{dt.strftime('%a %d/%m %H:%M')}*: "
                    f"{item['main']['temp']}°C - {item['weather'][0]['description'].title()}\n"
                )
        else:
            response += f"\n_{forecast_error}_"

        await update.message.reply_text(response, parse_mode='Markdown')
        logging.info(f"Weather command: {city_name} by {update.effective_user.id}")

    except KeyError as e:
        await update.message.reply_text(f"❌ Error procesando datos del clima: campo '{e}' no encontrado")
