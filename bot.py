from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# Your bot's token
BOT_TOKEN = "7718588788:AAEWGS4etPSNhOpzZZqgW8c1Y3AF3RGvc1g"

# Start command handler
async def start(update: Update, context):
    chat_id = update.effective_chat.id
    keyboard = [
        [InlineKeyboardButton("Code", callback_data="menu_code")],
        [InlineKeyboardButton("Guide", callback_data="menu_guide")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text="Welcome! Please choose an option from the menu below:",
        reply_markup=reply_markup,
    )

# Menu selection handler
async def menu_handler(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "menu_code":
        await query.edit_message_text(text="Here's the code:\n```print('Hello World!')```", parse_mode="Markdown")
    elif query.data == "menu_guide":
        await query.edit_message_text(text="Here's the guide:\n1. Open Telegram.\n2. Start the bot.\n3. Choose an option.")

# Block all messages except commands
async def block_messages(update: Update, context):
    await update.message.delete()

# Main function to set up the bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, block_messages))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
