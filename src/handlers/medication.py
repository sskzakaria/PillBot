# src/handlers/medication.py

from src.app import bot, user_data
from src.utils.decorators import with_timezone, with_user
from src.utils.keyboards import (
    make_frequency_keyboard,
    make_confirm_keyboard,
    make_times_per_day_keyboard,
    make_day_selector
)
from dateutil import parser
from src.database.repository import (
    create_medication,
    get_user_medications,
    get_medication_count
)
from src.config import MAX_MEDICATIONS_PER_USER
from telebot.types import ReplyKeyboardRemove


# ==================== ADD MEDICATION FLOW ====================

@bot.message_handler(commands=['addpill'])
@with_user
@with_timezone
def medication_handler(message):
    user_id = message.chat.id
    
    # Check medication limit
    med_count = get_medication_count(user_id)
    if med_count >= MAX_MEDICATIONS_PER_USER:
        bot.send_message(
            user_id,
            f"⚠️ You've reached the maximum limit of {MAX_MEDICATIONS_PER_USER} medications.\n\n"
            "Please delete some medications using /list before adding new ones."
        )
        return
    
    # Initialize user data
    user_data[user_id] = {
        'step': 1,
        'total_steps': 5
    }
    
    text = (
        "💊 **Adding New Medication** (Step 1/5)\n\n"
        "What's the medication name?\n\n"
        "_Type /cancel anytime to cancel_"
    )
    
    sent_msg = bot.send_message(user_id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, dosage_handler)


def dosage_handler(message):
    user_id = message.chat.id
    
    # Store medication name
    user_data[user_id]['medication'] = message.text.strip()
    user_data[user_id]['step'] = 2
    
    text = (
        "💊 **Adding New Medication** (Step 2/5)\n\n"
        "What's the dosage?\n\n"
        "_Examples: 100mg, 2 tablets, 5ml_\n"
        "_Type /cancel to cancel_"
    )
    
    sent_msg = bot.send_message(user_id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, frequency_handler)


def frequency_handler(message):
    user_id = message.chat.id
    
    # Store dosage
    user_data[user_id]['dosage'] = message.text.strip()
    user_data[user_id]['step'] = 3
    
    text = (
        "💊 **Adding New Medication** (Step 3/5)\n\n"
        "How often do you take this medication?"
    )
    
    markup = make_frequency_keyboard()
    bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda c: c.data.startswith('freq_'))
def handle_frequency_selection(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    
    frequency = call.data.replace('freq_', '')
    user_data[user_id]['frequency'] = frequency
    user_data[user_id]['step'] = 4
    
    if frequency == 'daily':
        # Ask how many times per day
        text = (
            "💊 **Adding New Medication** (Step 4/5)\n\n"
            "How many times per day?"
        )
        markup = make_times_per_day_keyboard()
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    
    elif frequency == 'weekly':
        # Show day selector
        user_data[user_id]['selected_days'] = set()
        text = (
            "💊 **Adding New Medication** (Step 4/5)\n\n"
            "📅 Select days (tap to toggle):"
        )
        markup = make_day_selector(user_data[user_id]['selected_days'])
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )


# ==================== TIMES PER DAY SELECTION ====================

@bot.callback_query_handler(func=lambda c: c.data.startswith('times_'))
def handle_times_selection(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    
    times_count = int(call.data.replace('times_', ''))
    user_data[user_id]['times_count'] = times_count
    user_data[user_id]['times'] = []
    user_data[user_id]['current_time_index'] = 0
    
    # Ask for first time
    text = (
        f"💊 **Adding New Medication** (Step 5/5)\n\n"
        f"⏰ Enter time for dose 1 of {times_count}:\n\n"
        "_Examples: 9am, 14:30, 3:00 PM_"
    )
    
    sent_msg = bot.send_message(user_id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, collect_times_handler)


def collect_times_handler(message):
    user_id = message.chat.id
    time_text = message.text.strip().lower()
    
    try:
        # Parse time
        if time_text.isdigit():
            hour = int(time_text)
            if 0 <= hour <= 23:
                time_text = f"{hour}:00"
        
        dt = parser.parse(time_text, fuzzy=True)
        formatted_time = dt.strftime("%H:%M")
        
        # Check for duplicates
        if formatted_time in user_data[user_id]['times']:
            msg = bot.send_message(
                user_id,
                "⚠️ You already entered this time. Please enter a different time:"
            )
            bot.register_next_step_handler(msg, collect_times_handler)
            return
        
        # Add time
        user_data[user_id]['times'].append(formatted_time)
        user_data[user_id]['current_time_index'] += 1
        
        # Check if we need more times
        current_index = user_data[user_id]['current_time_index']
        total_times = user_data[user_id]['times_count']
        
        if current_index < total_times:
            # Ask for next time
            text = (
                f"💊 **Adding New Medication** (Step 5/5)\n\n"
                f"⏰ Enter time for dose {current_index + 1} of {total_times}:\n\n"
                f"_Already entered: {', '.join(user_data[user_id]['times'])}_"
            )
            sent_msg = bot.send_message(user_id, text, parse_mode="Markdown")
            bot.register_next_step_handler(sent_msg, collect_times_handler)
        else:
            # All times collected - show confirmation
            confirm_handler(message)
    
    except (ValueError, parser.ParserError):
        msg = bot.send_message(
            user_id,
            "❌ Invalid time format.\n\n"
            "Please use one of these formats:\n"
            "• 9am\n"
            "• 14:30\n"
            "• 3:00 PM\n\n"
            "Try again:"
        )
        bot.register_next_step_handler(msg, collect_times_handler)


# ==================== DAY SELECTION (Multi-Select) ====================

@bot.callback_query_handler(func=lambda c: c.data.startswith('day_'))
def handle_day_selection(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    
    if user_id not in user_data or 'selected_days' not in user_data[user_id]:
        bot.answer_callback_query(call.id, "⚠️ Session expired. Please start over with /addpill")
        return
    
    action = call.data.replace('day_', '')
    
    if action == 'done':
        # User finished selecting days
        if not user_data[user_id]['selected_days']:
            bot.answer_callback_query(
                call.id,
                "⚠️ Please select at least one day!",
                show_alert=True
            )
            return
        
        # Save days and ask for times
        days_list = sorted(user_data[user_id]['selected_days'])
        user_data[user_id]['days'] = days_list
        
        # Ask how many times per day
        text = (
            "💊 **Adding New Medication** (Step 5/5)\n\n"
            f"Selected days: {', '.join(days_list)}\n\n"
            "How many times per day?"
        )
        markup = make_times_per_day_keyboard()
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    
    elif action == 'clear':
        # Clear all selections
        user_data[user_id]['selected_days'] = set()
        markup = make_day_selector(user_data[user_id]['selected_days'])
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    elif action == 'weekdays':
        # Select Mon-Fri
        user_data[user_id]['selected_days'] = {'Mon', 'Tue', 'Wed', 'Thu', 'Fri'}
        markup = make_day_selector(user_data[user_id]['selected_days'])
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    elif action == 'weekend':
        # Select Sat-Sun
        user_data[user_id]['selected_days'] = {'Sat', 'Sun'}
        markup = make_day_selector(user_data[user_id]['selected_days'])
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    else:
        # Toggle individual day
        day = action
        if day in user_data[user_id]['selected_days']:
            user_data[user_id]['selected_days'].remove(day)
        else:
            user_data[user_id]['selected_days'].add(day)
        
        # Update keyboard
        markup = make_day_selector(user_data[user_id]['selected_days'])
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )


# ==================== CONFIRMATION ====================

def confirm_handler(message):
    user_id = message.chat.id
    data = user_data[user_id]
    
    # Build frequency display
    if data['frequency'] == 'weekly':
        days_str = ', '.join(data.get('days', []))
        frequency_display = f"Weekly ({days_str})"
    else:
        frequency_display = "Daily"
    
    # Build times display
    times_str = ', '.join(data['times'])
    
    # Create summary
    summary = (
        "💊 **Medication Summary**\n\n"
        f"**Name:** {data['medication']}\n"
        f"**Dosage:** {data['dosage']}\n"
        f"**Frequency:** {frequency_display}\n"
        f"**Times:** {times_str}\n\n"
        "Is this correct?"
    )
    
    bot.send_message(user_id, summary, parse_mode="Markdown")
    
    markup = make_confirm_keyboard()
    sent_msg = bot.send_message(
        user_id,
        "Please confirm:",
        reply_markup=markup
    )
    bot.register_next_step_handler(sent_msg, finalize_handler)


def finalize_handler(message):
    user_id = message.chat.id
    
    if message.text and '✅' in message.text or message.text.lower() == 'yes':
        try:
            data = user_data[user_id]
            
            # Create medication in database
            medication_id = create_medication(
                user_id=user_id,
                name=data['medication'],
                dosage=data['dosage'],
                frequency=data['frequency'],
                times=data['times'],
                days=data.get('days')
            )
            
            # Success message
            bot.send_message(
                user_id,
                f"✅ **Medication saved successfully!**\n\n"
                f"💊 {data['medication']} - {data['dosage']}\n"
                f"⏰ {', '.join(data['times'])}\n\n"
                "You'll receive reminders at these times.",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="Markdown"
            )
        
        except Exception as e:
            print(f"Error saving medication: {e}")
            bot.send_message(
                user_id,
                "❌ Something went wrong saving your medication.\n"
                "Please try again with /addpill",
                reply_markup=ReplyKeyboardRemove()
            )
    else:
        bot.send_message(
            user_id,
            "❌ Cancelled. Use /addpill to try again.",
            reply_markup=ReplyKeyboardRemove()
        )
    
    # Clean up temp data
    if user_id in user_data:
        del user_data[user_id]


# ==================== CANCEL HANDLER ====================

@bot.message_handler(commands=['cancel'])
def cancel_handler(message):
    user_id = message.chat.id
    
    if user_id in user_data:
        del user_data[user_id]
        bot.send_message(
            user_id,
            "❌ Operation cancelled.\n\nUse /addpill to start over.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        bot.send_message(user_id, "Nothing to cancel.")