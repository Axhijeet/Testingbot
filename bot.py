from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import asyncio
import logging

# Your bot's token
BOT_TOKEN = "7718588788:AAEWGS4etPSNhOpzZZqgW8c1Y3AF3RGvc1g"

# Your channel ID (replace with the correct channel ID)
CHANNEL_ID = -100754041005  # Use your actual channel ID

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to send the menu to the channel
async def send_menu(context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Code", callback_data="menu_code")],
        [InlineKeyboardButton("Guide", callback_data="menu_guide")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Post the message with the menu
    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="Welcome! Please choose an option from the menu below:",
        reply_markup=reply_markup,
    )

# Function to handle the button interaction
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Check if the user is an admin or a normal user
    user = query.from_user
    is_admin = False

    try:
        # Get the list of admins
        admins = await context.bot.get_chat_administrators(CHANNEL_ID)

        # Check if the user is an admin
        is_admin = any(admin.user.id == user.id for admin in admins)

    except Exception as e:
        logger.error(f"Failed to check admin status: {e}")

    if is_admin:
        await query.edit_message_text(
            text=f"Hello Admin {user.first_name}, you've clicked the menu button!\n\nChoose an option.",
        )
    else:
        if query.data == "menu_code":
            await query.edit_message_text(
                text="Here's the code:\n```print('Hello World!')```",
                parse_mode="Markdown",
            )
        elif query.data == "menu_guide":
            await query.edit_message_text(
                text="Here's the guide:\n1. Open Telegram.\n2. Interact with the bot.\n3. Choose an option."
            )

# Function to block any text messages
async def block_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()

# Main function to set up the bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Periodically post the menu every 30 seconds
    async def periodic_post():
        while True:
            await send_menu(application)
            await asyncio.sleep(30)  # Post every 30 seconds

    # Schedule the periodic menu posting
    application.job_queue.run_once(periodic_post, when=0)

    # Add handler for menu button clicks
    application.add_handler(CallbackQueryHandler(menu_handler))

    # Block text messages from users
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, block_messages))

    # Add the error handler
    application.add_error_handler(lambda update, context: logger.error(f"Error occurred: {context.error}"))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
