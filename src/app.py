from telebot import TeleBot
from src.config import BOT_TOKEN

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables.")

bot = TeleBot(BOT_TOKEN)
user_data = {}