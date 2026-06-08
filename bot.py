from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
from dotenv import dotenv_values
import logging
import traceback
import requests
import os
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
from functions.euro import euro
from functions.temp import temp
from functions.usdars import usdars
from functions.eurars import eurars
from functions.arsusd import arsusd
from functions.arseur import arseur
from functions.test import test
from functions.scrape import scrape
from functions.status import status, set_bot_start_time

# Try to import transcription feature (optional - may fail on some systems)
TRANSCRIBE_AVAILABLE = False
try:
    from functions.transcribe import transcribe_voice
    TRANSCRIBE_AVAILABLE = True
    logging.info("Transcription feature loaded successfully")
except ImportError as e:
    logging.warning(f"Transcription feature not available: {e}")
except Exception as e:
    logging.warning(f"Could not load transcription (Vosk issue): {e}")

import functions.weather as weather
from functions.metrics import track_resources

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
    
    # Lista de usuarios autorizados
    authorized_users = [71870097]
    if user_id not in authorized_users:
        await update.message.reply_text("❌ No autorizado para usar este comando")
        return
    
    current_debug = context.bot_data.get('debug_mode', False)
    context.bot_data['debug_mode'] = not current_debug
    
    status = "activado" if context.bot_data['debug_mode'] else "desactivado"
    await update.message.reply_text(f"🐛 Modo debug {status}")
    logging.info(f"Debug mode {status} by user {user_id}")

async def get_my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando temporal para obtener el user ID"""
    await update.message.reply_text(f"Tu user ID es: {update.effective_user.id}")

@handle_errors
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler para transcribir mensajes de voz usando Vosk"""
    
    if not TRANSCRIBE_AVAILABLE:
        await update.message.reply_text(
            "❌ Transcripción no disponible\n\n"
            "La función de transcripción está deshabilitada en este bot.\n"
            "Esto puede deberse a:\n"
            "- Vosk no está instalado\n"
            "- El modelo de Spanish no está descargado\n"
            "- Problema de compatibilidad en tu sistema"
        )
        logging.warning(f"Transcription requested but not available for user {update.effective_user.id}")
        return
    
    try:
        # Send processing message
        processing_msg = await update.message.reply_text("🎤 Transcribiendo...")
        
        # Get voice file from Telegram
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        
        # Create temporary directory if it doesn't exist
        temp_dir = "temp_audio"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Download audio file
        audio_file_path = os.path.join(temp_dir, f"voice_{voice.file_id}.ogg")
        await file.download_to_drive(audio_file_path)
        
        try:
            # Transcribe audio
            transcribed_text, stats = transcribe_voice(audio_file_path)

            stats_line = (
                f"ffmpeg {stats['ffmpeg_s']}s | api {stats['api_s']}s | "
                f"total {stats['total_s']}s | cpu {stats['cpu_s']}s | mem {stats['mem_mb']}MB"
            )
            await processing_msg.edit_text(f"🎤 Transcripción:\n\n{transcribed_text}\n\n`{stats_line}`", parse_mode='Markdown')

            logging.info(f"Voice message transcribed successfully for user {update.effective_user.id}")
        
        finally:
            # Delete audio file to save memory
            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)
                logging.info(f"Deleted temporary audio file: {audio_file_path}")
    
    except FileNotFoundError as e:
        await update.message.reply_text(f"❌ Dependencia faltante:\n{str(e)}")
        logging.error(f"Missing dependency: {e}")
    
    except ValueError as e:
        await update.message.reply_text(f"❌ Error en el audio:\n{str(e)}")
        logging.error(f"Audio processing error: {e}")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Error al transcribir:\n{str(e)}")
        logging.error(f"Transcription handler error: {e}", exc_info=True)


if __name__ == '__main__':
    application = ApplicationBuilder().token(config['TELEGRAM_TOKEN']).build()
    
    # Initialize bot start time
    set_bot_start_time()
    
    def cmd(command, func):
        application.add_handler(CommandHandler(command, track_resources(func)))

    cmd('start',    start)
    cmd('bitso',    bitso)
    cmd('dolar',    dolar)
    cmd('euro',     euro)
    cmd('temp',     temp)
    cmd('usdars',   usdars)
    cmd('eurars',   eurars)
    cmd('arsusd',   arsusd)
    cmd('arseur',   arseur)
    cmd('test',     test)
    cmd('scrape',   scrape)
    cmd('clima',    weather.weather_command)
    cmd('debug',    debug_command)
    cmd('myid',     get_my_id)
    cmd('status',   status)
    
    # Handler para transcribir mensajes de voz
    voice_handler = MessageHandler(filters.VOICE, handle_voice_message)
    application.add_handler(voice_handler)
    
    logging.info("Bot iniciado correctamente")
    application.run_polling()
