async def show_chart(update, context):
    await update.message.reply_text(
        "Открыть график: [chart link]",
        disable_web_page_preview=False
    )
