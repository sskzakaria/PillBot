from timezonefinder import TimezoneFinder
from src.app import bot
from telebot.types import ReplyKeyboardRemove
from src.utils.keyboards import make_timezone_keyboard
from src.database.repository import create_or_update_user, get_user_timezone

tf = TimezoneFinder()


@bot.message_handler(commands=['timezone'])
def send_welcome(message):
    user_id = message.chat.id
    current_tz = get_user_timezone(user_id)
    markup = make_timezone_keyboard()

    if current_tz:
        text = f"🕒 Current timezone: **{current_tz}**\n\nShare your location to update it:"
    else:
        text = "📍 Share your location to set your timezone:"

    bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")


@bot.message_handler(content_types=['location'])
def handle_location(message):
    latitude = message.location.latitude
    longitude = message.location.longitude

    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)

    if not timezone_str:
        bot.send_message(
            message.chat.id,
            "⚠️ Couldn't detect timezone from that location. Please try again."
        )
        return

    create_or_update_user(message.chat.id, timezone_str)
    bot.send_message(
        message.chat.id,
        f"✅ Timezone set to {timezone_str}",
        reply_markup=ReplyKeyboardRemove()
    )