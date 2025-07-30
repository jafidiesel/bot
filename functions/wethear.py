# Integración OpenWeatherMap API
import requests
from telegram import Update
from telegram.ext import ContextTypes

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

@handle_errors
async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtiene el clima actual de una ciudad"""
    if not context.args:
        await update.message.reply_text(
            "🌤️ Uso: /clima <ciudad>\n"
            "Ejemplo: /clima Buenos Aires"
        )
        return
    
    city = " ".join(context.args)
    
    # Obtener datos del clima actual
    weather_url = f"{OPENWEATHER_BASE_URL}/weather"
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',  # Celsius
        'lang': 'es'       # Español
    }
    
    weather_data = await safe_api_call(
        update, context, 
        f"{weather_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}", 
        "OpenWeatherMap"
    )
    
    if weather_data is None:
        return
    
    # Procesar y formatear datos
    try:
        city_name = weather_data['name']
        country = weather_data['sys']['country']
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        humidity = weather_data['main']['humidity']
        pressure = weather_data['main']['pressure']
        description = weather_data['weather'][0]['description'].title()
        icon = weather_data['weather'][0]['icon']
        
        # Emoji según condición climática
        weather_emoji = get_weather_emoji(weather_data['weather'][0]['main'])
        
        response = f"""
{weather_emoji} **Clima en {city_name}, {country}**

🌡️ **Temperatura:** {temp}°C (Sensación: {feels_like}°C)
📝 **Condición:** {description}
💧 **Humedad:** {humidity}%
🔽 **Presión:** {pressure} hPa
        """.strip()
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except KeyError as e:
        await update.message.reply_text(
            f"❌ Error procesando datos del clima: Campo '{e}' no encontrado"
        )

@handle_errors
async def forecast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Obtiene pronóstico de 5 días"""
    if not context.args:
        await update.message.reply_text(
            "📅 Uso: /pronostico <ciudad>\n"
            "Ejemplo: /pronostico Mendoza"
        )
        return
    
    city = " ".join(context.args)
    
    # Obtener pronóstico de 5 días
    forecast_url = f"{OPENWEATHER_BASE_URL}/forecast"
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',
        'lang': 'es'
    }
    
    forecast_data = await safe_api_call(
        update, context, 
        f"{forecast_url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}", 
        "OpenWeatherMap Forecast"
    )
    
    if forecast_data is None:
        return
    
    try:
        city_name = forecast_data['city']['name']
        country = forecast_data['city']['country']
        
        response = f"📅 **Pronóstico 5 días - {city_name}, {country}**\n\n"
        
        # Procesar próximos 5 pronósticos (cada 3 horas)
        for i in range(0, min(15, len(forecast_data['list'])), 3):  # Cada 9 horas aprox
            forecast = forecast_data['list'][i]
            
            # Formatear fecha
            from datetime import datetime
            dt = datetime.fromtimestamp(forecast['dt'])
            day = dt.strftime("%a %d/%m")
            time = dt.strftime("%H:%M")
            
            temp = forecast['main']['temp']
            description = forecast['weather'][0]['description'].title()
            emoji = get_weather_emoji(forecast['weather'][0]['main'])
            
            response += f"{emoji} **{day} {time}**: {temp}°C - {description}\n"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except KeyError as e:
        await update.message.reply_text(
            f"❌ Error procesando pronóstico: Campo '{e}' no encontrado"
        )

def get_weather_emoji(weather_main):
    """Retorna emoji según condición climática"""
    weather_emojis = {
        'Despejado': '☀️',
        'Nublado': '☁️',
        'Lluvia': '🌧️',
        'Llovizna': '🌦️',
        'Tormenta': '⛈️',
        'Nieve': '❄️',
        'Neblina': '🌫️',
        'Niebla': '🌫️',
        'Bruma': '🌫️',
        'Polvo': '🌪️',
        'Arena': '🌪️'
    }
    return weather_emojis.get(weather_main, '🌤️')
