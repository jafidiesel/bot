from telegram import Update
from telegram.ext import ContextTypes
import requests
import json
from dotenv import dotenv_values
import logging
from functools import wraps

config = dotenv_values(".env")
BITSO_URL = config.get('DOLLAR_BITSO_URL')

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

async def safe_api_call(url: str, timeout: int = 10):
    """Función utilitaria para llamadas seguras a APIs"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.Timeout:
        return None, "⏱️ Timeout: La API de Bitso tardó demasiado en responder"
    except requests.exceptions.ConnectionError:
        return None, "🔌 Error de conexión con Bitso: Verifica la conexión a internet"
    except requests.exceptions.HTTPError as e:
        return None, f"🚫 Error HTTP {e.response.status_code if hasattr(e, 'response') else 'Unknown'} en Bitso"
    except Exception as e:
        return None, f"❌ Error inesperado en Bitso: {str(e)}"

@handle_errors
async def bitso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not BITSO_URL:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="❌ Error: DOLLAR_BITSO_URL no configurada en el archivo .env"
        )
        return

    # Llamada segura a la API
    data, error = await safe_api_call(BITSO_URL)
    
    if error:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=error)
        logging.error(f"API error for bitso command: {error}")
        return
    
    if not data:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="❌ No se recibieron datos de la API de Bitso"
        )
        return

    try:
        formatted_message = []
        target_books = ['usd_ars', 'usdt_ars']
        
        # Verificar estructura de datos
        payload = data.get('payload', [])
        if not payload:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="❌ No hay datos disponibles en la respuesta de Bitso"
            )
            return

        for obj in payload:
            book = obj.get("book", "")
            if book in target_books:
                last = obj.get("last", "N/A")
                low = obj.get("low", "N/A")
                high = obj.get("high", "N/A")
                formatted_message.append(
                    f"#{book} -> _{last}_\n                 low: _{low}_ - high: _{high}_"
                )

        if formatted_message:
            final_message = "\n\n".join(formatted_message)
            logging.info(f"Bitso command used by {update.effective_chat.username}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=final_message, 
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="❌ No se encontraron datos para USD_ARS o USDT_ARS en Bitso"
            )

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=f"❌ Error procesando datos de Bitso: {str(e)}"
        )
        logging.error(f"Error processing bitso data: {e}", exc_info=True)