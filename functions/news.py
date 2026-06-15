import html
import logging
import requests
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

RSS_SOURCES = [
    {'name': 'Pimoroni', 'url': 'https://blog.pimoroni.com/rss/', 'emoji': '🔧'},
]

PAGE_SIZE = 5


def _parse_feed(source: dict) -> list[dict]:
    try:
        resp = requests.get(source['url'], timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        items = []
        for item in root.findall('.//item'):
            title = item.findtext('title', '').strip()
            link = item.findtext('link', '').strip()
            pub_date = item.findtext('pubDate', '')
            try:
                date_str = parsedate_to_datetime(pub_date).strftime('%d %b %Y')
            except Exception:
                date_str = ''
            items.append({
                'title': title,
                'link': link,
                'date': date_str,
                'source': source['name'],
                'emoji': source['emoji'],
            })
        return items
    except Exception as e:
        logging.error(f"Error fetching {source['name']} RSS: {e}")
        return []


def _fetch_all() -> list[dict]:
    items = []
    for source in RSS_SOURCES:
        items.extend(_parse_feed(source))
    return items


def _format_item(item: dict) -> str:
    title = html.escape(item['title'])
    meta = html.escape(f"{item['source']} · {item['date']}")
    return f"{item['emoji']} <b>{title}</b>\n{item['link']}\n<i>{meta}</i>"


def _more_button(offset: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Ver 5 +", callback_data=f"news_page:{offset}")
    ]])


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = _fetch_all()
    if not items:
        await update.message.reply_text("❌ No se pudieron obtener noticias.")
        return

    for item in items[:PAGE_SIZE]:
        await update.message.reply_text(_format_item(item), parse_mode='HTML')

    if len(items) > PAGE_SIZE:
        await update.message.reply_text(
            "📰 <b>Pimoroni Blog</b>",
            parse_mode='HTML',
            reply_markup=_more_button(PAGE_SIZE),
        )


async def news_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    offset = int(query.data.split(':')[1])
    items = _fetch_all()

    if not items or offset >= len(items):
        await query.edit_message_text("No hay más noticias.")
        return

    await query.delete_message()

    chat_id = query.message.chat_id
    page = items[offset:offset + PAGE_SIZE]

    for item in page:
        await context.bot.send_message(
            chat_id=chat_id,
            text=_format_item(item),
            parse_mode='HTML',
        )

    next_offset = offset + PAGE_SIZE
    if next_offset < len(items):
        await context.bot.send_message(
            chat_id=chat_id,
            text="📰 <b>Pimoroni Blog</b>",
            parse_mode='HTML',
            reply_markup=_more_button(next_offset),
        )
