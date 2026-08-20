from telegram import Update
from telegram.ext import ContextTypes
import logging
from functools import wraps

from functions.convert import handle_conversion


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
async def brl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Uso: /brl <monto>")
        return

    await handle_conversion(update, context, source='BRL', targets=['ARS', 'USD', 'EUR', 'CLP'], command_name='brl')
