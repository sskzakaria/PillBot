import os 
from telebot import TeleBot
from src.handlers import(
    start, timezone, medication, reminders, stats , list
)
from src.app import bot

from src.database.schema import init_database

if __name__ == '__main__':
    #database setup
    init_database()

    #starting the bot
    try :
        print("Bot starting")
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("Stopping the bot")