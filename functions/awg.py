from telegram import Update
from telegram.ext import ContextTypes
import requests
from dotenv import dotenv_values
import logging
from functools import wraps

config = dotenv_values(".env")
AWG_API_URL = config.get('AWG_API_URL')


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
        return None, "⏱️ Timeout: La API del florín tardó demasiado en responder"
    except requests.exceptions.ConnectionError:
        return None, "🔌 Error de conexión con la API del florín: Verifica la conexión a internet"
    except requests.exceptions.HTTPError as e:
        return None, f"🚫 Error HTTP {e.response.status_code if hasattr(e, 'response') else 'Unknown'} en la API del florín"
    except Exception as e:
        return None, f"❌ Error inesperado en la API del florín: {str(e)}"


@handle_errors
async def awg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not AWG_API_URL:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Error: AWG_API_URL no configurada en el archivo .env"
        )
        return

    amount = 1.0
    if context.args:
        try:
            amount = float(context.args[0].replace(',', '.'))
        except ValueError:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="⚠️ Uso: /awg [monto]"
            )
            return

    data, error = await safe_api_call(AWG_API_URL)

    if error:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=error)
        logging.error(f"API error for awg command: {error}")
        return

    if not data or data.get('result') != 'success':
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ No se recibieron datos válidos de la API del florín"
        )
        return

    rates = data.get('rates', {})
    usd = rates.get('USD')
    ars = rates.get('ARS')
    eur = rates.get('EUR')

    if usd is None or ars is None or eur is None:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ La API no devolvió las cotizaciones esperadas (USD/ARS/EUR)"
        )
        return

    last_update = data.get('time_last_update_utc', 'N/A')

    message = (
        "#Florín (AWG)\n"
        f"      -> {amount:,.2f} AWG = {amount * usd:,.4f} USD\n"
        f"      -> {amount:,.2f} AWG = {amount * ars:,.2f} ARS\n"
        f"      -> {amount:,.2f} AWG = {amount * eur:,.4f} EUR\n\n"
        f"🕐 Last update: {last_update}"
    )

    logging.info(f"Awg command used by {update.effective_chat.username}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message,
        parse_mode="Markdown"
    )
