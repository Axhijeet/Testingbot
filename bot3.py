from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import random

# Sample data for the German language bot
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
async def send_daily_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = random.choice(vocab)
    message = f"*Word*: {word['word']}\n*Meaning*: {word['meaning']}\n*Example*: {word['example']}"
    await update.message.reply_text(message, parse_mode="Markdown")

# Function to start a quiz
async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quiz = random.choice(quizzes)
    options = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(quiz['options'])])
    message = f"{quiz['question']}\n\n{options}"
    context.user_data['answer'] = quiz['answer']
    await update.message.reply_text(message)

# Function to check user's quiz answer
async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.strip()
    correct_answer = context.user_data.get('answer')
    if user_answer.lower() == correct_answer.lower():
        await update.message.reply_text("✅ Correct!")
    else:
        await update.message.reply_text(f"❌ Wrong! The correct answer is {correct_answer}.")

# Main function to run the bot
def main():
    # Replace 'YOUR_BOT_TOKEN' with your actual bot token
    application = Application.builder().token("7627790175:AAF7OmcCCxYxOwv5jl1dPEJDkCJb8AOMe2I").build()

    # Add command handlers
    application.add_handler(CommandHandler("dailyword", send_daily_word))
    application.add_handler(CommandHandler("quiz", start_quiz))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer))

    # Start the bot with polling
    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
