from dateutil import parser
from timezonefinder import TimezoneFinder
from src.app import bot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from src.utils.keyboards import make_timezone_keyboard
from src.database.repository import create_or_update_user


@bot.message_handler(commands=['timezone'])
def send_welcome(message):
    markup = make_timezone_keyboard()
    bot.send_message(message.chat.id, "Please share your location to set your time zone.", reply_markup=markup)

@bot.message_handler(content_types=['location'])
def handle_location(message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
    create_or_update_user(message.chat.id,timezone_str)
    bot.send_message(message.chat.id, f"Time zone set to {timezone_str}", reply_markup=ReplyKeyboardRemove())   