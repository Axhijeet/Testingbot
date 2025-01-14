import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging
import os
import json

# ---- Replace with your bot token ----
TOKEN = "7627790175:AAF7OmcCCxYxOwv5jl1dPEJDkCJb8AOMe2I"

# File to store recipient ID
RECIPIENT_FILE = "recipient.json"

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def load_recipient_id():
    """Loads the recipient ID from file or returns None."""
    if os.path.exists(RECIPIENT_FILE):
        with open(RECIPIENT_FILE, "r") as f:
            try:
                data = json.load(f)
                return data.get("recipient_id")
            except json.JSONDecodeError:
                return None
    return None

def save_recipient_id(recipient_id):
    """Saves the recipient ID to file."""
    with open(RECIPIENT_FILE, "w") as f:
        json.dump({"recipient_id": recipient_id}, f)

# Dictionary to store user message drafts
user_message_drafts = {}

# State enumeration
class BotState:
    IDLE = 0
    SETTING_RECIPIENT = 1
    ENTERING_MESSAGE = 2
    CONFIRMING_SEND = 3


def start(update, context):
    """Send a welcoming message and show main menu."""
    show_main_menu(update, context)


def show_main_menu(update, context):
    """Display the main menu options."""
    keyboard = [
        [InlineKeyboardButton("Set Recipient ID", callback_data='set_recipient')],
        [InlineKeyboardButton("Enter Message", callback_data='enter_message')],
        [InlineKeyboardButton("Send Message", callback_data='send_message')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text('Please select an action:', reply_markup=reply_markup)
    elif update.callback_query:
         query = update.callback_query
         query.edit_message_text('Please select an action:', reply_markup=reply_markup)

def set_recipient_id(update, context):
    """Prompt the user to enter a new recipient ID."""
    query = update.callback_query
    context.user_data['state'] = BotState.SETTING_RECIPIENT
    query.edit_message_text("Please enter the new recipient's User ID:")

def enter_message(update, context):
    """Prompt the user to enter the message they want to send."""
    query = update.callback_query
    context.user_data['state'] = BotState.ENTERING_MESSAGE
    query.edit_message_text("Please enter the message you want to send:")

def handle_message_input(update, context):
  """Handles the user's message based on the bot's current state."""
  user_id = update.message.chat.id

  if context.user_data.get('state') == BotState.SETTING_RECIPIENT:
      try:
          recipient_id = int(update.message.text)
          save_recipient_id(recipient_id)
          update.message.reply_text(f"Recipient ID set to {recipient_id}")
          context.user_data['state'] = BotState.IDLE
          show_main_menu(update, context)

      except ValueError:
          update.message.reply_text("Invalid User ID format. Please enter a valid numeric ID.")

  elif context.user_data.get('state') == BotState.ENTERING_MESSAGE:
      user_message_drafts[user_id] = update.message.text
      update.message.reply_text("Message saved!")
      context.user_data['state'] = BotState.IDLE
      show_main_menu(update, context)

  else:
      update.message.reply_text("Please use menu options to interact.")


def send_message(update, context):
    """Display a confirmation message with the current recipient and message."""
    query = update.callback_query
    user_id = update.effective_user.id
    recipient_id = load_recipient_id()
    message = user_message_drafts.get(user_id)

    if not recipient_id:
        query.answer(text="Please set a recipient ID first.", show_alert=True)
        return

    if not message:
        query.answer(text="Please enter a message first.", show_alert=True)
        return

    context.user_data['state'] = BotState.CONFIRMING_SEND

    keyboard = [
        [InlineKeyboardButton("Confirm Send", callback_data='confirm_send')],
        [InlineKeyboardButton("Edit Message", callback_data='edit_message')],
        [InlineKeyboardButton("Edit Recipient ID", callback_data='set_recipient')],
        [InlineKeyboardButton("Cancel", callback_data='cancel_send')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(
        f"Recipient ID: {recipient_id}\nMessage: {message}\n\nConfirm or Edit?",
        reply_markup=reply_markup
    )

def confirm_send(update, context):
  """Sends the message to the recipient."""
  query = update.callback_query
  user_id = update.effective_user.id
  recipient_id = load_recipient_id()
  message = user_message_drafts.get(user_id)

  try:
    context.bot.send_message(chat_id=recipient_id, text=f"Message from {update.effective_user.username} ({update.effective_user.id}): {message}")
    query.edit_message_text("Message sent!")
    user_message_drafts.pop(user_id, None)
    context.user_data['state'] = BotState.IDLE
  except Exception as e:
    query.edit_message_text(f"Failed to send message. Please check bot logs for errors: {e}")
    logging.error(f"Error sending message: {e}")


def edit_message(update, context):
   """Allows the user to edit the message."""
   query = update.callback_query
   context.user_data['state'] = BotState.ENTERING_MESSAGE
   query.edit_message_text("Please enter new message to send.")


def cancel_send(update, context):
  """Cancels the message and shows the main menu."""
  query = update.callback_query
  query.answer(text="Send cancelled.", show_alert=True)
  context.user_data['state'] = BotState.IDLE
  show_main_menu(update, context)

def button_handler(update, context):
  """Handles button callbacks."""
  query = update.callback_query
  query.answer()  # Acknowledge the callback

  if query.data == 'set_recipient':
    set_recipient_id(update, context)
  elif query.data == 'enter_message':
    enter_message(update, context)
  elif query.data == 'send_message':
    send_message(update, context)
  elif query.data == 'confirm_send':
    confirm_send(update, context)
  elif query.data == 'edit_message':
    edit_message(update, context)
  elif query.data == 'cancel_send':
    cancel_send(update, context)

def main():
    """Start the bot."""
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handler to handle /start command
    dispatcher.add_handler(CommandHandler("start", start))

    # Add handler for handling button presses
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    # Handle text messages (for ID and message input)
    dispatcher.add_handler(MessageHandler(Filters.text, handle_message_input))

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C
    updater.idle()

if __name__ == '__main__':
    main()
