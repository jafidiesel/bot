from telegram import Update
from telegram.ext import ContextTypes
import requests
from dotenv import dotenv_values
from datetime import datetime
import logging
from functools import wraps

config = dotenv_values(".env")
DOLLAR_API_URL = config.get('DOLLAR_API_URL')

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
        return None, "⏱️ Timeout: La API tardó demasiado en responder"
    except requests.exceptions.ConnectionError:
        return None, "🔌 Error de conexión: Verifica la conexión a internet"
    except requests.exceptions.HTTPError as e:
        return None, f"🚫 Error HTTP {e.response.status_code if hasattr(e, 'response') else 'Unknown'}"
    except Exception as e:
        return None, f"❌ Error inesperado: {str(e)}"

@handle_errors
async def dolar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not DOLLAR_API_URL:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="❌ Error: DOLLAR_API_URL no configurada en el archivo .env"
        )
        return

    # Llamada segura a la API
    data, error = await safe_api_call(DOLLAR_API_URL)
    
    if error:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=error)
        logging.error(f"API error for dolar command: {error}")
        return
    
    if not data:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text="❌ No se recibieron datos de la API del dólar"
        )
        return

    try:
        formatted_message = []
        
        # Asegurar que data es una lista
        data_list = data if isinstance(data, list) else [data]
        
        for obj in data_list:
            # Usar get() para evitar KeyError
            casa = obj.get('casa', 'Desconocido').capitalize()
            compra = obj.get('compra', 'N/A')
            venta = obj.get('venta', 'N/A')
            timestamp = obj.get('fechaActualizacion', '')

            # Formatear el timestamp de manera segura
            if timestamp:
                try:
                    formatted_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%y %H:%M")
                except ValueError:
                    # Si el formato es diferente, usar el timestamp original
                    formatted_timestamp = timestamp
            else:
                formatted_timestamp = "N/A"

            # Formatear el mensaje
            formatted_message.append(
                f"#{casa}:\n      Compra: ${compra} | Venta: ${venta}\n      Actualizado: {formatted_timestamp}"
            )

        if formatted_message:
            final_message = "\n\n".join(formatted_message)
            logging.info(f"Dolar command used by {update.effective_chat.username}")
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text=final_message, 
                parse_mode="Markdown"
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, 
                text="❌ No se pudieron procesar los datos del dólar"
            )

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, 
            text=f"❌ Error procesando datos: {str(e)}"
        )
        logging.error(f"Error processing dolar data: {e}", exc_info=True)