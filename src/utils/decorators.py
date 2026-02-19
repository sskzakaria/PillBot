from functools import wraps
from database.repository import ensure_user_exists
from database.repository import get_user_timezone
from keyboards import make_timezone_keyboard
from src.app import bot

def with_user(func):
    """Decorator to automatically add the user to the database."""
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        user_id = message.chat.id
        ensure_user_exists(user_id)
        return func(message, *args, **kwargs)
    return wrapper


def with_timezone(func):
    """Decorator to automatically add the users timezone to the database."""
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        user_id = message.chat.id
        timezone= get_user_timezone
        if not timezone:
            markup = make_timezone_keyboard()
            bot.send_message(
                user_id,
                " You need to set your timezone before using this command.",
                reply_markup=markup
            )
            return  
        return func(message, *args, **kwargs)
    return wrapper