from telegram.ext import CommandHandler, MessageHandler, ContextTypes, filters 
from telegram import Update
from bot.webapp import show_chart
from core.trade_manager import handle_buy_command, handle_test_order_command, handle_sell_order_recomendations_command
from config.settings import TELEGRAM_CHAT_ID
from functools import partial
from core.bybit_handler import BybitHandler

async def start(update, context):
    chat_id = update.effective_chat.id
    if chat_id != TELEGRAM_CHAT_ID:
        return
    await update.message.reply_text("Привет! Я твой помощник по торговле.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != TELEGRAM_CHAT_ID:
        return
    text = update.message.text.strip()
    print('!', chat_id, text)


def setup_handlers(app, bb_handler: BybitHandler):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("buy", handle_buy_command))
    app.add_handler(CommandHandler("testorder", handle_test_order_command))
    app.add_handler(CommandHandler("sellrecomends", partial(handle_sell_order_recomendations_command, bb_handler=bb_handler)))
    app.add_handler(CommandHandler("chart", show_chart))
