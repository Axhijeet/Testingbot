import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Bot token and channel IDs
BOT_TOKEN = "7796769189:AAEsUfo32JREhiDTCodQuG9OAjS2LTeMIG4"
MAIN_CHANNEL_ID = -1002349828866  # Main channel ID
SECONDARY_CHANNEL_ID = -1002407865494  # Secondary channel ID

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def copy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Copies messages starting with 'BUY' or 'SELL' to the secondary channel."""
    if update.channel_post:
        message = update.channel_post.text
        if message and (message.upper().startswith("BUY") or message.upper().startswith("SELL")):
            # Check if the message came from the main channel
            if update.effective_chat.id == MAIN_CHANNEL_ID:
                try:
                    await context.bot.send_message(
                        chat_id=SECONDARY_CHANNEL_ID,
                        text=message
                    )
                    logging.info(f"Copied message to secondary channel: {message}")
                except Exception as e:
                    logging.error(f"Error copying message: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add a handler for all channel posts
    application.add_handler(MessageHandler(filters.ALL, copy_message))
    
    logging.info("Bot is running...")
    application.run_polling()
