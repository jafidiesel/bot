from telegram import Update
from telegram.ext import ContextTypes
import logging
from functools import wraps

def handle_errors(func):
    """Decorator para manejar errores y enviarlos al usuario"""
    @wraps(func)
    async def wrapper(update, context):
        try:
            return await func(update, context)
        except Exception as e:
            error_msg = f"❌ Error en {func.__name__}: {str(e)}"
            try:
                await update.message.reply_text(error_msg)
            except:
                pass
            logging.error(f"Error in {func.__name__}: {e}", exc_info=True)
    return wrapper

@handle_errors
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text="¡Hola! 👋 Soy tu bot de información financiera.\n\n"
             "Comandos disponibles:\n"
             "🔹 /usd - Precio del dólar\n"
             "🔹 /usd [monto] - Convertir USD a ARS/EUR/BRL/CLP\n"
             "🔹 /eur - Precio del euro\n"
             "🔹 /eur [monto] - Convertir EUR a ARS/USD/BRL/CLP\n"
             "🔹 /ars [monto] - Convertir ARS a USD/EUR/BRL/CLP\n"
             "🔹 /clp [monto] - Convertir CLP a ARS/USD/EUR/BRL\n"
             "🔹 /brl [monto] - Convertir BRL a ARS/USD/EUR/CLP\n"
             "🔹 /awg [monto] - Precio del florín (AWG) en USD/ARS/EUR\n"
             "🔹 /bitso - Datos de Bitso\n"
             "🔹 /temp - Temperatura\n"
             "🔹 /test - Comando de prueba\n"
             "🔹 /status - Estado del bot y sistema 📊\n"
             "🔹 /clima - Información del clima\n"
             "🔹 /pronostico - Pronóstico del clima\n\n"
             "📝 Características adicionales:\n"
             "🎤 Envía un audio de voz para transcribir (español)"
    )
