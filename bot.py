from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
from telegram.ext import ContextTypes
from dotenv import dotenv_values
import logging
import traceback
import requests
from functools import wraps

config = dotenv_values(".env")

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

from functions.start import start
from functions.bitso import bitso
from functions.dolar import dolar
from functions.temp import temp
from functions.usdars import usdars
from functions.arsusd import arsusd
from functions.test import test

def handle_errors(func):
    """Decorator para manejar errores y enviarlos al usuario"""
    @wraps(func)
    async def wrapper(update, context):
        try:
            return await func(update, context)
        except Exception as e:
            error_msg = f"❌ Error en {func.__name__}:\n```\n{str(e)}\n```"
            
            # Si está en modo debug, incluir traceback
            if context.bot_data.get('debug_mode', False):
                tb = traceback.format_exc()
                error_msg += f"\n\nTraceback:\n```\n{tb[:1000]}...\n```" if len(tb) > 1000 else f"\n\nTraceback:\n```\n{tb}\n```"
            
            try:
                await update.message.reply_text(error_msg, parse_mode='Markdown')
            except:
                # Fallback si falla el markdown
                await update.message.reply_text(f"❌ Error en {func.__name__}: {str(e)}")
            
            logging.error(f"Error in {func.__name__}: {e}", exc_info=True)
    
    return wrapper

async def safe_api_call(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                       url: str, description: str = "API"):
    """Función utilitaria para llamadas seguras a APIs"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.Timeout:
        await update.message.reply_text(
            f"⏱️ Timeout en {description}\nLa API tardó demasiado en responder"
        )
        logging.warning(f"Timeout en {description}: {url}")
        return None
    
    except requests.exceptions.ConnectionError:
        await update.message.reply_text(
            f"🔌 Error de conexión con {description}\nVerifica la conexión a internet"
        )
        logging.error(f"Connection error en {description}: {url}")
        return None
    
    except requests.exceptions.HTTPError as e:
        error_text = e.response.text[:200] if hasattr(e, 'response') and e.response else str(e)
        await update.message.reply_text(
            f"🚫 Error HTTP {e.response.status_code if hasattr(e, 'response') else 'Unknown'} en {description}\n{error_text}"
        )
        logging.error(f"HTTP error en {description}: {e}")
        return None
    
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error inesperado en {description}:\n```\n{str(e)}\n```",
            parse_mode='Markdown'
        )
        logging.error(f"Unexpected error en {description}: {e}")
        return None

@handle_errors
async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para activar/desactivar modo debug"""
    user_id = update.effective_user.id
    
    # Lista de usuarios autorizados (CAMBIAR POR TU USER ID REAL)
    authorized_users = [123456789]  # ⚠️ CAMBIAR ESTE NÚMERO
    if user_id not in authorized_users:
        await update.message.reply_text("❌ No autorizado para usar este comando")
        return
    
    current_debug = context.bot_data.get('debug_mode', False)
    context.bot_data['debug_mode'] = not current_debug
    
    status = "activado" if context.bot_data['debug_mode'] else "desactivado"
    await update.message.reply_text(f"🐛 Modo debug {status}")
    logging.info(f"Debug mode {status} by user {user_id}")

@handle_errors
async def start_enhanced(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Función start mejorada con manejo de errores"""
    await update.message.reply_text(
        '¡Hola! 👋\n\n'
        '🔹 /dolar - Precio del dólar\n'
        '🔹 /bitso - Datos de Bitso\n'
        '🔹 /temp - Temperatura\n'
        '🔹 /usdars - USD a ARS\n'
        '🔹 /arsusd - ARS a USD\n'
        '🔹 /test - Comando de prueba\n'
        '🔹 /debug - Activar/desactivar modo debug\n'
        '🔹 /myid - Obtener tu ID de usuario'
    )

async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando temporal para obtener el user ID"""
    await update.message.reply_text(f"Tu user ID es: {update.effective_user.id}")

@handle_errors
async def dolar_enhanced(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Función dólar mejorada con manejo de errores"""
    DOLLAR_API_URL = config.get('DOLLAR_API_URL')
    
    if not DOLLAR_API_URL:
        await update.message.reply_text("❌ Error: DOLLAR_API_URL no configurada en .env")
        return
    
    # Usar safe_api_call para obtener datos del dólar
    dollar_data = await safe_api_call(update, context, DOLLAR_API_URL, "API del Dólar")
    if dollar_data is None:
        return
    
    try:
        formatted_message = []
        
        # Verificar si la respuesta es una lista o un objeto
        data_list = dollar_data if isinstance(dollar_data, list) else [dollar_data]
        
        for obj in data_list:
            # Usar get() para evitar KeyError
            casa = obj.get('casa', 'Desconocido').capitalize()
            compra = obj.get('compra', 'N/A')
            venta = obj.get('venta', 'N/A')
            timestamp = obj.get('fechaActualizacion', '')

            if timestamp:
                try:
                    from datetime import datetime
                    formatted_timestamp = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%d/%m/%y %H:%M")
                except:
                    formatted_timestamp = timestamp
            else:
                formatted_timestamp = "N/A"

            formatted_message.append(
                f"#{casa}:\n      Compra: ${compra} | Venta: ${venta}\n      Actualizado: {formatted_timestamp}"
            )
        
        if formatted_message:
            await update.message.reply_text("\n\n".join(formatted_message), parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No se pudieron procesar los datos del dólar")
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Error procesando datos del dólar:\n```\n{str(e)}\n```",
            parse_mode='Markdown'
        )
        logging.error(f"Error processing dollar data: {e}", exc_info=True)


if __name__ == '__main__':
    application = ApplicationBuilder().token(config['TELEGRAM_TOKEN']).build()
    
    # Handlers originales (con funciones del directorio functions/)
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    bitso_handler = CommandHandler('bitso', bitso)
    application.add_handler(bitso_handler)

    dolar_handler = CommandHandler('dolar', dolar)
    application.add_handler(dolar_handler)

    temp_handler = CommandHandler('temp', temp)
    application.add_handler(temp_handler)

    usdars_handler = CommandHandler('usdars', usdars)
    application.add_handler(usdars_handler)

    arsusd_handler = CommandHandler('arsusd', arsusd)
    application.add_handler(arsusd_handler)

    test_handler = CommandHandler('test', test)
    application.add_handler(test_handler)
    
    # Nuevos handlers con manejo de errores
    application.add_handler(CommandHandler("debug", debug_command))
    application.add_handler(CommandHandler("myid", get_my_id))
    application.add_handler(CommandHandler("start_enhanced", start_enhanced))
    application.add_handler(CommandHandler("dolar_enhanced", dolar_enhanced))
    
    logging.info("Bot iniciado correctamente")
    application.run_polling()
