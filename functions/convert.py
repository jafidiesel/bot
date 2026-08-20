from telegram import Update
from telegram.ext import ContextTypes
import requests
import logging
from dotenv import dotenv_values

config = dotenv_values(".env")
COTIZACIONES_API_URL = config.get('COTIZACIONES_API_URL')


async def safe_api_call(url: str, timeout: int = 10):
    """Función utilitaria para llamadas seguras a APIs"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.Timeout:
        return None, "⏱️ Timeout: La API de cotizaciones tardó demasiado en responder"
    except requests.exceptions.ConnectionError:
        return None, "🔌 Error de conexión con la API de cotizaciones: Verifica la conexión a internet"
    except requests.exceptions.HTTPError as e:
        return None, f"🚫 Error HTTP {e.response.status_code if hasattr(e, 'response') else 'Unknown'} en la API de cotizaciones"
    except Exception as e:
        return None, f"❌ Error inesperado en la API de cotizaciones: {str(e)}"


async def fetch_rates():
    """
    Obtiene las cotizaciones oficiales de dolarapi.com/v1/cotizaciones y devuelve
    un dict {moneda: venta_en_ars}, ej. {'USD': 1520.0, 'EUR': 1728.6485, ...}.
    """
    if not COTIZACIONES_API_URL:
        return None, "❌ Error: COTIZACIONES_API_URL no configurada en el archivo .env"

    data, error = await safe_api_call(COTIZACIONES_API_URL)
    if error:
        return None, error

    if not data:
        return None, "❌ No se recibieron datos de la API de cotizaciones"

    rates = {}
    for obj in data:
        moneda = obj.get('moneda')
        casa = obj.get('casa')
        venta = obj.get('venta')
        if moneda and casa == 'oficial' and venta is not None:
            rates[moneda] = float(venta)

    if not rates:
        return None, "❌ No se pudieron procesar las cotizaciones"

    return rates, None


def convert(amount: float, source: str, targets: list, rates: dict) -> dict:
    """
    Convierte amount (en la moneda source) a cada moneda de targets, pivoteando
    sobre ARS con las tasas de venta en rates. Lanza KeyError si falta una cotización.
    """
    results = {}
    for target in targets:
        if target == source:
            continue
        if source == 'ARS':
            results[target] = amount / rates[target]
        elif target == 'ARS':
            results[target] = amount * rates[source]
        else:
            amount_ars = amount * rates[source]
            results[target] = amount_ars / rates[target]
    return results


def format_conversion_message(amount: float, source: str, results: dict) -> str:
    lines = [f"💱 {amount:,.2f} {source} equivale a:"]
    for currency, value in results.items():
        lines.append(f"      -> {value:,.2f} {currency}")
    return "\n".join(lines)


async def handle_conversion(update: Update, context: ContextTypes.DEFAULT_TYPE,
                             source: str, targets: list, command_name: str):
    """Parsea el monto de context.args, obtiene cotizaciones y responde con la conversión."""
    try:
        amount = float(context.args[0].replace(',', '.'))
    except (IndexError, ValueError):
        await update.message.reply_text(f"⚠️ Uso: /{command_name} <monto>")
        return

    rates, error = await fetch_rates()
    if error:
        await update.message.reply_text(error)
        logging.error(f"Error fetching cotizaciones for /{command_name}: {error}")
        return

    try:
        results = convert(amount, source, targets, rates)
    except KeyError as e:
        await update.message.reply_text(f"❌ No se encontró la cotización de {e}")
        logging.error(f"Conversion error for /{command_name}: falta cotización de {e}")
        return

    message = format_conversion_message(amount, source, results)
    logging.info(f"/{command_name} conversion used by {update.effective_chat.username}: {amount} {source}")
    await update.message.reply_text(message, parse_mode="Markdown")
