from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import logging
import asyncio
from telegram.error import BadRequest

# Set bot token and channel username
BOT_TOKEN = "7718588788:AAEWGS4etPSNhOpzZZqgW8c1Y3AF3RGvc1g"
CHANNEL_USERNAME = "wishaldubeyji"  # Public channel username without '@'

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Function to check membership
async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        logger.debug(f"Checking membership for user {user_id} in channel {CHANNEL_USERNAME}.")
        member = await context.bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        logger.debug(f"User {user_id} membership status: {member.status}")
        return member.status in ["member", "administrator", "creator"]
    except BadRequest as e:
        logger.error(f"BadRequest error checking membership for user {user_id}: {e}")
        if "user not found" in str(e).lower():
            return False  # Treat "user not found" as not a member
        return False  # Return False for other BadRequest errors
    except Exception as e:
        logger.error(f"Error checking membership for user {user_id}: {e}")
        return False

# Function to send the menu buttons
async def send_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("Code")],
        [KeyboardButton("Guide")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    if update.message:
        await update.message.reply_text("Welcome! Here is your menu:", reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.reply_text("Welcome! Here is your menu:", reply_markup=reply_markup)

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    logger.debug(f"User {user_id} started the bot.")

    # Check if the user is a member of the channel
    is_member = await check_membership(user_id, context)
    if is_member:
        logger.debug(f"User {user_id} is a member of the channel.")
        # Send floating menu
        await send_menu(update,context)

    else:
        logger.debug(f"User {user_id} is NOT a member of the channel.")
        # Send join button and try again
        join_button = InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
        try_again_button = InlineKeyboardButton("Try Again", callback_data="try_again")
        reply_markup = InlineKeyboardMarkup([[join_button], [try_again_button]])
        await update.message.reply_text(
            f"Please join @{CHANNEL_USERNAME} to use this bot. Click below to join, and then press Try Again:",
            reply_markup=reply_markup
        )


# Callback handler for the try again button
async def try_again_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    logger.debug(f"User {user_id} clicked Try Again button.")

    await update.callback_query.answer()  # Remove loading animation first

    for attempt in range(3):  # Try up to 3 times
        is_member = await check_membership(user_id, context)
        if is_member:
            logger.debug(f"User {user_id} is now a member, sending menu.")
            await send_menu(update, context)
            return

        logger.debug(f"User {user_id} not a member, retrying in {attempt+1} seconds.")
        await asyncio.sleep(attempt + 1) # Sleep for some time before checking again
    
    logger.debug(f"User {user_id} still not a member after multiple attempts.")
    await update.callback_query.answer(text="Still not detecting your membership. Please make sure you've joined the channel and try again.",show_alert=True)
# Membership check wrapper for menu handlers
async def check_and_handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, menu_type: str):
    user_id = update.message.from_user.id
    is_member = await check_membership(user_id, context)
    if is_member:
        if menu_type == "Code":
            await update.message.reply_text("Here is some code:\n```print('Hello, World!')```", parse_mode="Markdown")
        elif menu_type == "Guide":
            await update.message.reply_text("Here is a guide:\n1. Step 1\n2. Step 2")
    else:
        join_button = InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME}")
        reply_markup = InlineKeyboardMarkup([[join_button]])

        # Send alert using answer
        await update.message.reply_text(
            f"Please join @{CHANNEL_USERNAME} to use this bot. Click below to join:",
             reply_markup=reply_markup
           
        )
        if update.message:
           await context.bot.answer_callback_query(update.message.id, text="Please join @{CHANNEL_USERNAME} to use this bot. Click below to join:", show_alert=True)

# Menu handler
async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Code":
        await check_and_handle_menu(update, context, "Code")
    elif text == "Guide":
         await check_and_handle_menu(update, context, "Guide")

# Main function
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^(Code|Guide)$"), handle_menu))
    application.add_handler(CallbackQueryHandler(try_again_handler, pattern="try_again"))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()
