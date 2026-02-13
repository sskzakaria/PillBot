import os
import telebot 
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv
from dateutil import parser
from timezonefinder import TimezoneFinder
import pytz


load_dotenv()
user_data = {}
BOT_TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, 'Hello! I am Pillbot 💊')

@bot.message_handler(commands=['timezone'])
def send_welcome(message):
    location_button = KeyboardButton("Share Location to set timezone", request_location=True)
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(location_button)
    markup.add(KeyboardButton("Select timezone manually"))
    bot.send_message(message.chat.id, "Please share your location to set your time zone.", reply_markup=markup)

@bot.message_handler(content_types=['location'])
def handle_location(message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
    bot.send_message(message.chat.id, f"Time zone set to {timezone_str}", reply_markup=ReplyKeyboardRemove())

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
💊 **Pill Reminder Bot**

*Commands:*
/addpill - Add a medication reminder
/list - View your reminders
/delete - Remove a reminder
/help - Show this message 
/timezone - Add Users Timezone
"""
    bot.reply_to(message, help_text, parse_mode="Markdown") 

@bot.message_handler(commands=['addpill'])
def medication_handler(message):
    text = "What's the medication name?"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    user_data[message.chat.id] = {}  
    bot.register_next_step_handler(sent_msg, dosage_handler)

def dosage_handler(message):
    user_data[message.chat.id]['medication'] = message.text  # Store medication name
    text = "What's the dosage?"    
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, frequency_handler)

def frequency_handler(message):
    user_data[message.chat.id]['dosage'] = message.text  # Store dosage
    markup = InlineKeyboardMarkup()
    button_daily = InlineKeyboardButton('Daily', callback_data='daily')
    button_weekly = InlineKeyboardButton('Choose day', callback_data='weekly')
    markup.add(button_daily, button_weekly)

@bot.callback_query_handler(func=lambda call: call.data in ['daily', 'weekly'])
def handle_frequency_selection(call):
    bot.answer_callback_query(call.id)
    user_data[call.message.chat.id]['frequency'] = call.data  # Store frequency 
    if call.data == 'daily':
        bot.send_message(call.message.chat.id, "What time do you want to take this medication?")
        bot.register_next_step_handler(call.message, time_handler)
    if call.data == 'weekly':
        bot.send_message(call.message.chat.id, "On which day of the week would you like to take this medication?")
        bot.register_next_step_handler(call.message, day_handler)

def day_handler(message):
    day = message.text.strip().capitalize()
    valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    if day not in valid_days:
        msg = bot.send_message(message.chat.id, "Invalid day. Please type a day like `Monday`.")
        bot.register_next_step_handler(msg, day_handler)
        return
    user_data[message.chat.id]['day'] = day  # Store day
    bot.send_message(message.chat.id, "What time do you want to take this medication?")
    bot.register_next_step_handler(message, time_handler)


def time_handler(message):
    time = message.text.strip().lower()
    try:
        if time.isdigit():
            hour = int(time)
            if 0 <= hour <= 23:
                time = f"{hour}:00"
        
        dt = parser.parse(time, fuzzy=True)
        user_data[message.chat.id]['time'] = dt.time()
        confirm_handler(message)
    
    except (ValueError, parser.ParserError):
        msg = bot.send_message(
            message.chat.id, 
            " Invalid time format. Please try again (e.g., 9am, 14:30, 3:00 PM):"
        )
        bot.register_next_step_handler(msg, time_handler)

def confirm_handler(message):
    data = user_data[message.chat.id]

    if data['frequency'] == 'weekly':
        frequency_display = f"Weekly on {data.get('day', 'N/A')}"
    else:
        frequency_display = "Daily"
    
    medication_data_message = (
        f"Medication: {data['medication']}\n"
        f"Dosage: {data['dosage']}\n"
        f"Frequency: {frequency_display}\n" 
        f"Time: {data['time']}\n\n"
        "Is this correct?"
    )

    bot.send_message(message.chat.id, "Here's your Medication info:")
    bot.send_message(message.chat.id, medication_data_message, parse_mode="Markdown")
    
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button_yes = KeyboardButton("Yes")
    button_no = KeyboardButton("No")
    markup.add(button_yes, button_no)

    sent_msg= bot.send_message(message.chat.id, "Please confirm:", reply_markup=markup)
    bot.register_next_step_handler(sent_msg, finalize_handler)

def finalize_handler(message):
    if message.text.lower() == 'yes':
        bot.send_message(message.chat.id, "Your medication schedule has been saved!")
    else:
        bot.send_message(message.chat.id, "Cancelled. Use /addpill to try again.")

    if message.chat.id in user_data:
        del user_data[message.chat.id]
        
bot.infinity_polling()
