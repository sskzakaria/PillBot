import os
import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):
    bot.reply_to(message, 'Hello! I am Pillbot 💊')

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
💊 **Pill Reminder Bot**

*Commands:*
/addpill - Add a medication reminder
/list - View your reminders
/delete - Remove a reminder
/help - Show this message 
"""
    bot.reply_to(message,help_text, parse_mode="Markdown") 


@bot.message_handler(commands=['addpill'])
def medication_handler(message):
    text= "What's the medication name?"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, dosage_handler)

def dosage_handler(message):
    medication = message.text
    text = "What's the dosage?"    
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, day_handler, medication)

def day_handler(message, medication):
    dosage = message.text
    text = "Which days are you taking this medication?"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, time_handler, medication, dosage)
   
def time_handler(message, medication, dosage):
    day = message.text
    text = "What time?"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")   
    bot.register_next_step_handler(sent_msg, fetch_medication_data, medication, dosage, day)

def fetch_medication_data(message, medication, dosage, day):
    time = message.text
    medication_data_message =(
        f'*Medication* {medication}\n'
        f'*Dosage* {dosage}\n'
        f'*Day* {day}\n'
        f'*Time* {time}\n'
)
    bot.send_message(message.chat.id,"Here's your Medication info ")
    bot.send_message(message.chat.id, medication_data_message, parse_mode="Markdown")


bot.infinity_polling()
