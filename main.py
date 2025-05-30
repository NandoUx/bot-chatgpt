import telebot
import openai
import os

# Load token dari environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

# Handle /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hai! Aku adalah bot AI. Kirim pertanyaanmu sekarang!")

# Handle semua pesan
@bot.message_handler(func=lambda m: True)
def chat_ai(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}]
        )
        reply = response['choices'][0]['message']['content']
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

bot.polling()
