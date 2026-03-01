from src.app import bot
from src.database.repository import get_user_timezone
from src.utils.keyboards import make_timezone_keyboard


@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.chat.id
    timezone = get_user_timezone(user_id)
    
    if timezone:
        # Returning user
        welcome_text = (
            "👋 Welcome back to PillBot!\n\n"
            f"🕒 Timezone: {timezone}\n\n"
            "**Quick Commands:**\n"
            "/addpill - Add medication\n"
            "/list - View medications\n"
            "/stats - Adherence stats\n"
            "/help - All commands"
        )
        bot.send_message(user_id, welcome_text, parse_mode="Markdown")
    else:
        # NEW USER - guide them!
        welcome_text = (
            "👋 Welcome to PillBot! 💊\n\n"
            "I help you remember medications on time.\n\n"
            "**First, let's set your timezone:**"
        )
        bot.send_message(user_id, welcome_text, parse_mode="Markdown")
        
        markup = make_timezone_keyboard()
        bot.send_message(
            user_id,
            "📍 Share your location to auto-detect timezone:",
            reply_markup=markup
        )
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
    💊 **Pill Reminder Bot**

    *Commands:*
    /addpill - Add new medication
    /list - View/edit/delete medications
    /stats - View adherence statistics (7/30/90 days)
    /timezone - Change your timezone
    /cancel - Cancel current operation
    /help - Show this message
    """
    bot.reply_to(message, help_text, parse_mode="Markdown")  