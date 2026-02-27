from src.app import bot

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
    /help - Show this message 
    /timezone - Add Users Timezone
    """
    bot.reply_to(message, help_text, parse_mode="Markdown")  