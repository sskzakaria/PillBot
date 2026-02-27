from datetime import datetime, timedelta
import pytz
from src.database.repository import (
    get_user_medications, 
    get_all_users_with_meds,
    log_reminder_sent,
    get_medication_by_id
)
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def check_reminders(bot):
    """Main function that runs every minute"""
    
    users = get_all_users_with_meds()
    
    if not users:
        return
    
    for user_id, timezone_str in users:
        try:
            check_user_reminders(bot, user_id, timezone_str)
        except Exception as e:
            print(f"Error checking reminders for {user_id}: {e}")
            continue


def check_user_reminders(bot, user_id, timezone_str):
    """Check if this user needs reminders right now"""
    
    try:
        user_tz = pytz.timezone(timezone_str)
    except:
        print(f"Invalid timezone for {user_id}: {timezone_str}")
        return
    
    now = datetime.now(user_tz)
    current_time = now.strftime("%H:%M")
    current_day = now.strftime("%a")
    
    medications = get_user_medications(user_id, active_only=True)
    
    for med in medications:
        if should_send_reminder(med, current_time, current_day):
            send_reminder(bot, user_id, med)


def should_send_reminder(med, current_time, current_day):
    """Check if we should send reminder for this med"""
    
    if current_time not in med['times']:
        return False
    
    if med['frequency'] == 'daily':
        return True
    
    elif med['frequency'] == 'weekly':
        if med['days'] and current_day in med['days']:
            return True
    
    return False


def send_reminder(bot, user_id, med):
    """Send reminder message to user"""
    
    msg = (
        f"💊 <b>Time for your medication!</b>\n\n"
        f"<b>{med['name']}</b>\n"
        f"Dosage: {med['dosage']}\n\n"
        f"Don't forget to take it! 🔔"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Taken", callback_data=f"taken_{med['id']}"),
        InlineKeyboardButton("⏰ Snooze 10min", callback_data=f"snooze_{med['id']}")
    )
    markup.add(
        InlineKeyboardButton("❌ Skip", callback_data=f"skip_{med['id']}")
    )
    
    try:
        bot.send_message(user_id, msg, parse_mode='HTML', reply_markup=markup)
        log_reminder_sent(med['id'], user_id)
        print(f"Reminder sent: {med['name']} to {user_id}")
    except Exception as e:
        print(f"Failed to send reminder to {user_id}: {e}")


def setup_reminder_handlers(bot):
    """Register callback handlers for reminder buttons"""
    
    @bot.callback_query_handler(func=lambda c: c.data.startswith('taken_'))
    def handle_taken(call):
        bot.answer_callback_query(call.id, " Great job!")
        
        bot.edit_message_text(
            "<b>Medication taken!</b>\n\nKeep up the good work! 🎉",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='HTML'
        )
    
    @bot.callback_query_handler(func=lambda c: c.data.startswith('snooze_'))
    def handle_snooze(call):
        bot.answer_callback_query(call.id, "⏰ Snoozed for 10 minutes")
        
        med_id = int(call.data.replace('snooze_', ''))
        user_id = call.message.chat.id
        
        from src.scheduler.scheduler import scheduler
        
        def send_snoozed():
            med = get_medication_by_id(med_id)
            if med:
                send_reminder(bot, user_id, med)
        
        run_time = datetime.now() + timedelta(minutes=10)
        scheduler.add_job(
            send_snoozed,
            'date',
            run_date=run_time,
            id=f'snooze_{med_id}_{user_id}_{run_time.timestamp()}'
        )
        
        bot.edit_message_text(
            "⏰ Reminder snoozed for 10 minutes.\n\nI'll remind you again soon!",
            user_id,
            call.message.message_id
        )
    
    @bot.callback_query_handler(func=lambda c: c.data.startswith('skip_'))
    def handle_skip(call):
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            "Reminder skipped",
            call.message.chat.id,
            call.message.message_id
        )