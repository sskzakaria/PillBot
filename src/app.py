from telebot import TeleBot
from src.config import BOT_TOKEN
import time

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables.")

bot = TeleBot(BOT_TOKEN)

user_data = {}
USER_DATA_TTL = 1800  # 30 minutes

def set_user_data(user_id, data):
    user_data[user_id] = {**data, '_created_at': time.time()}

def get_user_data(user_id):
    data = user_data.get(user_id)
    if not data:
        return None
    if time.time() - data.get('_created_at', 0) > USER_DATA_TTL:
        del user_data[user_id]
        return None
    return data

def clear_user_data(user_id):
    user_data.pop(user_id, None)