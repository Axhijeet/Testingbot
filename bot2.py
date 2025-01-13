import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from flask import Flask, jsonify
from threading import Thread
import asyncio

# Bot token and channel IDs
BOT_TOKEN = "7796769189:AAEsUfo32JREhiDTCodQuG9OAjS2LTeMIG4"
MAIN_CHANNEL_ID = -1002211085308
SECONDARY_CHANNEL_ID = -1002382553093

app = Flask(__name__)  # initialize flask app

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

log_messages = []  # initialize an empty list that will be used as a log


async def copy_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Copies messages starting with 'BUY' or 'SELL' to the secondary channel with hashtag replacement."""
    if update.channel_post:
        message = update.channel_post.text
        if message and (message.upper().startswith("BUY") or message.upper().startswith("SELL")):
            # Check if the message came from the main channel
            if update.effective_chat.id == MAIN_CHANNEL_ID:
                try:
                    # Replace the hashtag before sending
                    modified_message = message.replace("#TradeWithThePatienceOfAMonk", "#BrainyPips")
                    await context.bot.send_message(
                        chat_id=SECONDARY_CHANNEL_ID,
                        text=modified_message
                    )
                    log_message = f"Copied and modified message to secondary channel: {modified_message}"
                    log_messages.append(log_message)  # add log to the list
                    logging.info(log_message)

                except Exception as e:
                    log_message = f"Error copying message: {e}"
                    log_messages.append(log_message)  # add log to the list
                    logging.error(log_message)


@app.route("/", methods=['GET'])  # a default route to respond to keep alive method
def get_logs():
    return jsonify({"logs": log_messages})  # return all logs as json object


def run_bot():
    """Starts the bot and flask apps in separate threads."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    # Add a handler for all channel posts
    application.add_handler(MessageHandler(filters.ALL, copy_message))

    logging.info("Bot is running...")
    asyncio.run(application.run_polling())  # start the polling in a async way


if __name__ == '__main__':
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    app.run(host='0.0.0.0', port=10000, debug=False, use_reloader=False)
