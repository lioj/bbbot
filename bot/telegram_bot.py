from telegram.ext import ApplicationBuilder
from bot.handlers import setup_handlers
from config.settings import TELEGRAM_BOT_TOKEN
from core.bybit_handler import BybitHandler

def run_bot():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    bb_handler = BybitHandler()
    setup_handlers(app, bb_handler)
    print("Бот запущен...")
    app.run_polling()
