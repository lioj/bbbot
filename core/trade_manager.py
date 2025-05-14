from telegram import Update
from telegram.ext import ContextTypes
from core.bybit_handler import BybitHandler
from config.settings import TELEGRAM_CHAT_ID, TELEGRAM_CHAT_ID
import asyncio
from datetime import datetime,timedelta

ALERTED_COINS = {}
PERCENT_THRESHOLD = -5  # %

async def handle_buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Укажи монету, например: /buy BTCUSDT")
        return
    symbol = args[0].upper()
    await update.message.reply_text(f"Запрос на покупку {symbol} получен (ручной режим).")

async def handle_sell_order_recomendations_command(update: Update, context: ContextTypes.DEFAULT_TYPE, bb_handler: BybitHandler):
    chat_id = update.effective_chat.id
    if chat_id != TELEGRAM_CHAT_ID:
        return

    recommendations = bb_handler.get_sell_order_recomendations()

    if not recommendations:
        await update.message.reply_text("🔍 Нет рекомендаций для продажи в данный момент.")
        return

    message_lines = ["📉 *Рекомендации по продаже:*"]
    for symbol, price, qty in recommendations:
        message_lines.append(f"• `{symbol}` — Цена: *{price:.4f}*, Кол-во: *{qty}*")

    message_text = "\n".join(message_lines)
    await update.message.reply_text(message_text, parse_mode='Markdown')


async def signal_watcher(app, bb: BybitHandler):
    while True:
        bb.update_current_prices()
        now = datetime.now()

        for sym in list(ALERTED_COINS):
            if now - ALERTED_COINS[sym] > timedelta(hours=1):
                del ALERTED_COINS[sym]

        for symbol, data in bb.coin2price.items():
            if symbol == "updated":
                continue

            last_price, day_change = data
            if day_change >= 0:
                continue  # только упавшие

            if symbol in ALERTED_COINS:
                continue

            price_history = bb.coin2history.get(symbol, [])
            if len(price_history) < 2:
                continue  # нужно хотя бы 2 точки

            max_price = max(price_history)
            change = (last_price - max_price) / max_price * 100

            if change <= PERCENT_THRESHOLD:
                ALERTED_COINS[symbol] = now  # сохраняем время

                await app.bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=(
                        f"📈 <b>{symbol}</b> упал сильнее после падения за день!\n"
                        f"📉 Максимум за час: <code>{max_price:.6f}</code>\n"
                        f"🚀 Сейчас: <code>{last_price:.6f}</code>\n"
                        f"📊 Падение: <b>{change:.2f}%</b>"
                    ),
                    parse_mode="HTML"
                )




        await asyncio.sleep(300)  # каждые 5 минут
