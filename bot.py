from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application
import asyncio

# Your bot's token
BOT_TOKEN = "7718588788:AAEWGS4etPSNhOpzZZqgW8c1Y3AF3RGvc1g"

# Your channel ID (prefix with -100)
CHANNEL_ID = -100754041005  # Replace with your actual channel ID

# Function to send the menu
async def send_menu(context):
    keyboard = [
        [InlineKeyboardButton("Code", callback_data="menu_code")],
        [InlineKeyboardButton("Guide", callback_data="menu_guide")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="Welcome! Please choose an option from the menu below:",
        reply_markup=reply_markup,
    )

# Function to handle menu responses
async def menu_handler(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "menu_code":
        await query.edit_message_text(
            text="Here's the code:\n```print('Hello World!')```",
            parse_mode="Markdown",
        )
    elif query.data == "menu_guide":
        await query.edit_message_text(
            text="Here's the guide:\n1. Open Telegram.\n2. Start the bot.\n3. Choose an option."
        )

# Main function to run the bot
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add a periodic task to send the menu
    async def periodic_post():
        while True:
            await send_menu(application)
            await asyncio.sleep(3600)  # Wait 1 hour before posting again (adjust as needed)

    # Run the periodic task in the background
    application.job_queue.run_once(periodic_post, when=0)

    # Add handler for menu button clicks
    application.add_handler(CallbackQueryHandler(menu_handler))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
