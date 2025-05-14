from telegram import Update
from telegram.ext import ContextTypes
from core.bybit_handler import BybitHandler
from config.settings import TELEGRAM_CHAT_ID

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

