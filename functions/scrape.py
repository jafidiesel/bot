from telegram import Update
from telegram.ext import ContextTypes
import requests
import logging
import traceback
from readability import Document
from lxml.html import fromstring
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme in ('http', 'https'), result.netloc])
    except:
        return False


async def scrape(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) == 0:
        await update.message.reply_text(
            "📋 Uso: /scrape <url>\n\nEjemplo:\n/scrape https://example.com"
        )
        return

    url = context.args[0]

    if not is_valid_url(url):
        await update.message.reply_text("❌ URL inválida. Asegúrate de incluir http:// o https://")
        return

    await update.message.reply_text("🔄 Obteniendo página...")

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type and 'application/xhtml' not in content_type:
            await update.message.reply_text(
                "❌ La URL no parece ser una página HTML.\n"
                f"Tipo de contenido: {content_type}"
            )
            return

        doc = Document(response.text)
        title = doc.title() or "Sin título"
        summary_html = doc.summary()
        
        if summary_html:
            root = fromstring(summary_html)
            text_content = root.text_content()
        else:
            text_content = ""

        if not text_content or len(text_content.strip()) < 50:
            await update.message.reply_text(
                "⚠️ No se pudo extraer contenido legible de esta página."
            )
            return

        text_content = ' '.join(text_content.split())

        max_length = 4000
        if len(text_content) > max_length:
            text_content = text_content[:max_length] + "\n\n... (contenido truncado)"

        message = f"📄 *{title}*\n\n{text_content}"

        await update.message.reply_text(message, parse_mode='Markdown')

    except requests.exceptions.Timeout:
        await update.message.reply_text("⏱️ Timeout: La página tardó demasiado en responder.")
    except requests.exceptions.ConnectionError:
        await update.message.reply_text("🔌 Error de conexión. Verifica la URL o tu conexión a internet.")
    except requests.exceptions.HTTPError as e:
        await update.message.reply_text(f"🚫 Error HTTP {e.response.status_code}")
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Scrape error for {url}: {e}\n{tb}")
        
        debug_mode = context.bot_data.get('debug_mode', False)
        error_msg = f"❌ Error al procesar la página:\n"
        error_msg += f"URL: {url}\n"
        error_msg += f"Error: {type(e).__name__}: {str(e)}"
        
        if debug_mode:
            error_msg += f"\n\n```\n{tb}\n```"
        
        await update.message.reply_text(error_msg, parse_mode='Markdown' if debug_mode else None)
