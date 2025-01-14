from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import random

# Sample data
vocab = [
    {"word": "Haus", "meaning": "House", "example": "Das Haus ist groß."},
    {"word": "Buch", "meaning": "Book", "example": "Ich lese ein Buch."},
    {"word": "Hund", "meaning": "Dog", "example": "Der Hund schläft."},
]

quizzes = [
    {"question": "What does 'Haus' mean?", "options": ["House", "Car", "Book"], "answer": "House"},
    {"question": "What does 'Buch' mean?", "options": ["Book", "Pen", "Dog"], "answer": "Book"},
]

# Function to send a daily word
def send_daily_word(update, context):
    word = random.choice(vocab)
    message = f"*Word*: {word['word']}\n*Meaning*: {word['meaning']}\n*Example*: {word['example']}"
    update.message.reply_text(message, parse_mode="Markdown")

# Function to start a quiz
def start_quiz(update, context):
    quiz = random.choice(quizzes)
    options = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(quiz['options'])])
    message = f"{quiz['question']}\n\n{options}"
    context.user_data['answer'] = quiz['answer']
    update.message.reply_text(message)

# Function to check user's quiz answer
def check_answer(update, context):
    user_answer = update.message.text.strip()
    correct_answer = context.user_data.get('answer')
    if user_answer.lower() == correct_answer.lower():
        update.message.reply_text("✅ Correct!")
    else:
        update.message.reply_text(f"❌ Wrong! The correct answer is {correct_answer}.")

# Main function to run the bot
def main():
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    updater = Updater("7627790175:AAF7OmcCCxYxOwv5jl1dPEJDkCJb8AOMe2I", use_context=True)
    dp = updater.dispatcher

    # Add command handlers
    dp.add_handler(CommandHandler("dailyword", send_daily_word))
    dp.add_handler(CommandHandler("quiz", start_quiz))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_answer))

    # Start the bot
    updater.start_polling()
    print("Bot is running...")
    updater.idle()

if __name__ == "__main__":
    main()
