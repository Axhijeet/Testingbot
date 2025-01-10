from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import logging

# Your bot's token and channel username
BOT_TOKEN = "7718588788:AAEWGS4etPSNhOpzZZqgW8c1Y3AF3RGvc1g"  # Your bot token
CHANNEL_USERNAME = "@channelwishal"  # Your channel's username

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Function to check if the user is a member of the channel
async def is_member_of_channel(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Check if the user is a member of the channel
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"Error checking membership: {e}")
        return False

# Function to send the floating menu
async def send_floating_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("Code")],
        [KeyboardButton("Guide")]
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_text(
        "Welcome! Please choose an option below:",
        reply_markup=reply_markup
    )

# Command to start the bot and check channel membership
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Check if the user is a member of the channel
    if await is_member_of_channel(user_id, context):
        await send_floating_menu(update, context)
    else:
        # If not a member, prompt the user to join
        join_button = InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
        reply_markup = InlineKeyboardMarkup([[join_button]])

        await update.message.reply_text(
            f"Please join the channel {CHANNEL_USERNAME} to use the bot. Click below to join:",
            reply_markup=reply_markup
        )

# Function to handle the button interactions (Code/Guide)
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message

    if query.text == "Code":
        await query.reply_text("Here's the code:\n```print('Hello World!')```", parse_mode="Markdown")
    elif query.text == "Guide":
        await query.reply_text("Here's the guide:\n1. Open Telegram.\n2. Interact with the bot.\n3. Choose an option.")

# Main function to set up the bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add the /start command handler
    application.add_handler(CommandHandler("start", start))

    # Add the menu button handler
    application.add_handler(MessageHandler(filters.Regex('^(Code|Guide)$'), menu_handler))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
