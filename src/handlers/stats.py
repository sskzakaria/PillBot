from src.app import bot
from src.database.repository import get_user_stats, get_medication_count
from src.utils.keyboards import make_stats_period_keyboard

@bot.message_handler(commands=['stats'])
def show_stats(message):
    user_id = message.chat.id
    
    # Check if user has medications
    med_count = get_medication_count(user_id)
    if med_count == 0:
        bot.send_message(
            user_id,
            "📊 No statistics available yet.\n\n"
            "Add medications with /addpill to start tracking adherence."
        )
        return
    
    # Get 7-day stats by default
    show_stats_for_period(message, days=7)


def show_stats_for_period(message, days=7):
    user_id = message.chat.id
    
    stats = get_user_stats(user_id, days=days)
    
    adherence = stats['adherence_rate']
    
    # Choose emoji and message based on adherence
    if adherence >= 90:
        emoji = "🎉"
        status = "Excellent!"
        color = "🟢"
    elif adherence >= 75:
        emoji = "👍"
        status = "Good job!"
        color = "🟡"
    elif adherence >= 50:
        emoji = "💪"
        status = "Keep it up!"
        color = "🟠"
    else:
        emoji = "📈"
        status = "Room for improvement"
        color = "🔴"
    
    text = (
        f"{emoji} **Your Medication Adherence ({days} days)**\n\n"
        f"{color} **Adherence Rate: {adherence:.1f}%**\n\n"
        f"✅ Taken: {stats['taken_count']}\n"
        f"❌ Missed: {stats['missed_count']}\n"
        f"📋 Total Reminders: {stats['total_reminders']}\n\n"
        f"_{status}_"
    )
    
    markup = make_stats_period_keyboard()
    bot.send_message(
        user_id,
        text,
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('stats_'))
def handle_stats_period(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    
    days = int(call.data.replace('stats_', ''))
    
    stats = get_user_stats(user_id, days=days)
    adherence = stats['adherence_rate']
    
    # Choose emoji and message
    if adherence >= 90:
        emoji = "🎉"
        status = "Excellent!"
        color = "🟢"
    elif adherence >= 75:
        emoji = "👍"
        status = "Good job!"
        color = "🟡"
    elif adherence >= 50:
        emoji = "💪"
        status = "Keep it up!"
        color = "🟠"
    else:
        emoji = "📈"
        status = "Room for improvement"
        color = "🔴"
    
    text = (
        f"{emoji} **Your Medication Adherence ({days} days)**\n\n"
        f"{color} **Adherence Rate: {adherence:.1f}%**\n\n"
        f"✅ Taken: {stats['taken_count']}\n"
        f"❌ Missed: {stats['missed_count']}\n"
        f"📋 Total Reminders: {stats['total_reminders']}\n\n"
        f"_{status}_"
    )
    
    markup = make_stats_period_keyboard()
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )