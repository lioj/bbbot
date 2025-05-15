from telegram import Update
from telegram.ext import ContextTypes
from core.bybit_handler import BybitHandler
from config.settings import TELEGRAM_CHAT_ID, TELEGRAM_CHAT_ID
import asyncio
from datetime import datetime,timedelta

ALERTED_COINS = {}
ALERTED_COINS_UP = {}
PERCENT_THRESHOLD = -5  # %
PERCENT_THRESHOLD_UP = 5

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
        message_lines.append(f"• `{symbol}` — Цена: *{price}*, Кол-во: *{qty}*")

    message_text = "\n".join(message_lines)
    await update.message.reply_text(message_text, parse_mode='Markdown')


async def handle_test_order_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text("Укажи монету, например: /testorder buy BTCUSDT 2 2")
        return
    type = args[0].upper()
    symbol = args[1].upper()
    qty = "5"
    tp_percent = "1"
    if len(args) > 2:
        qty = args[2]
        if len(args) > 3:
            tp_percent = args[3]
    await update.message.reply_text(f"Запрос {type} {symbol} объемом {qty} и TP {tp_percent}% получен (ручной режим).")


async def signal_watcher(app, bb: BybitHandler):
    while True:
        bb.update_current_prices()
        now = datetime.now()

        for sym in list(ALERTED_COINS):
            if now - ALERTED_COINS[sym] > timedelta(hours=1):
                del ALERTED_COINS[sym]
            if now - ALERTED_COINS_UP[sym] > timedelta(hours=1):
                del ALERTED_COINS_UP[sym]

        for symbol, data in bb.coin2price.items():
            if symbol == "updated":
                continue

            last_price, day_change = data
            if day_change >= -3:
                continue  # только упавшие

            price_history = bb.coin2history.get(symbol, [])
            if len(price_history) < 10:
                continue  # нужно хотя бы 12 точки

            max_price = max(price_history)
            mean_price = sum(price_history) / len(price_history)
            down_change = (last_price - max_price) / max_price * 100
            down_change_from_mean = (last_price - mean_price) / mean_price * 100
            up_change = (last_price - max_price) / max_price * 100

            if symbol not in ALERTED_COINS\
                            and down_change <= PERCENT_THRESHOLD:
                ALERTED_COINS[symbol] = now  # сохраняем время

                await app.bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=(
                        f"📉 <b>{symbol}</b> упал сильнее после падения за день!\n"
                        f"📊 Падение: <b>{down_change:.2f}% , {down_change_from_mean}%</b>"
                    ),
                    parse_mode="HTML"
                )

            if symbol not in ALERTED_COINS_UP\
                    and up_change >= PERCENT_THRESHOLD_UP:
                ALERTED_COINS_UP[symbol] = now  # сохраняем время

                await app.bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=(
                        f"📉 <b>{symbol}</b> подрос после падения за день!\n"
                        f"📊 Рост: <b>{up_change:.2f}% </b>"
                    ),
                    parse_mode="HTML"
                )

        
        




        await asyncio.sleep(300)  # каждые 5 минут
