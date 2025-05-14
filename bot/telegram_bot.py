from telegram.ext import ApplicationBuilder
from bot.handlers import setup_handlers
from config.settings import TELEGRAM_BOT_TOKEN
from core.bybit_handler import BybitHandler
from core.trade_manager import signal_watcher
from functools import partial

async def start_background_tasks(app, bb: BybitHandler):
    app.create_task(signal_watcher(app, bb))

def run_bot():
    bb_handler = BybitHandler()
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN)\
        .post_init(partial(start_background_tasks, bb=bb_handler))\
        .build()
    setup_handlers(app, bb_handler)
    print("Бот запущен...")
    app.run_polling()
