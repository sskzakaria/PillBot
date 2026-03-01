from src.app import bot
from src.database.repository import get_user_stats, get_medication_count
from src.utils.keyboards import make_stats_period_keyboard


def _build_stats_text(stats, days):
    adherence = stats['adherence_rate']
    if adherence >= 90:
        emoji, status, color = "🎉", "Excellent!", "🟢"
    elif adherence >= 75:
        emoji, status, color = "👍", "Good job!", "🟡"
    elif adherence >= 50:
        emoji, status, color = "💪", "Keep it up!", "🟠"
    else:
        emoji, status, color = "📈", "Room for improvement", "🔴"

    return (
        f"{emoji} **Your Medication Adherence ({days} days)**\n\n"
        f"{color} **Adherence Rate: {adherence:.1f}%**\n\n"
        f"✅ Taken: {stats['taken_count']}\n"
        f"❌ Missed: {stats['missed_count']}\n"
        f"📋 Total Reminders: {stats['total_reminders']}\n\n"
        f"_{status}_"
    )


def _send_stats(chat_id, days):
    stats = get_user_stats(chat_id, days=days)
    text = _build_stats_text(stats, days)
    markup = make_stats_period_keyboard()
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")


@bot.message_handler(commands=['stats'])
def show_stats(message):
    user_id = message.chat.id
    med_count = get_medication_count(user_id)
    if med_count == 0:
        bot.send_message(
            user_id,
            "📊 No statistics available yet.\n\n"
            "Add medications with /addpill to start tracking adherence."
        )
        return
    _send_stats(user_id, days=7)


@bot.callback_query_handler(func=lambda c: c.data.startswith('stats_'))
def handle_stats_period(call):
    bot.answer_callback_query(call.id)
    days = int(call.data.replace('stats_', ''))
    stats = get_user_stats(call.message.chat.id, days=days)
    text = _build_stats_text(stats, days)
    markup = make_stats_period_keyboard()
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )