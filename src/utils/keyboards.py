from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def make_timezone_keyboard():
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(KeyboardButton("Share Location to set timezone", request_location=True))
    markup.add(KeyboardButton("Select timezone manually"))
    return markup

def make_frequency_keyboard():
    markup = InlineKeyboardMarkup()
    button_daily = InlineKeyboardButton('Daily', callback_data='daily')
    button_weekly = InlineKeyboardMarkup('Choose day', callback_data='weekly')
    markup.add(button_daily, button_weekly)
    return markup

def make_confirm_keyboard():
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button_yes = KeyboardButton("Yes")
    button_no = KeyboardButton("No")
    markup.add(button_yes, button_no)
    return markup