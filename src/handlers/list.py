from src.app import bot, user_data
from src.database.repository import (
    get_user_medications,
    get_medication_by_id,
    deactivate_medication,
    update_medication
)
from src.utils.keyboards import (
    make_medication_list_keyboard,
    make_edit_keyboard,
    make_delete_confirm_keyboard,
    make_day_selector
)
from telebot.types import ReplyKeyboardRemove
from dateutil import parser


def _show_medication(user_id, med_id):
    """Re-fetch and display a medication with its edit keyboard."""
    med = get_medication_by_id(med_id)
    if not med:
        bot.send_message(user_id, "⚠️ Medication not found.")
        return

    times_str = ', '.join(med['times'])
    if med['frequency'] == 'weekly' and med['days']:
        freq_display = f"Weekly ({', '.join(med['days'])})"
    else:
        freq_display = med['frequency'].capitalize()

    text = (
        f"💊 **{med['name']}**\n\n"
        f"**Dosage:** {med['dosage']}\n"
        f"**Frequency:** {freq_display}\n"
        f"**Times:** {times_str}\n\n"
        "What would you like to do?"
    )

    markup = make_edit_keyboard(med_id, frequency=med['frequency'])
    bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")

def _send_medication_list(chat_id):
    medications = get_user_medications(chat_id)
    if not medications:
        bot.send_message(chat_id, "📋 You don't have any medications yet.\n\nAdd your first medication with /addpill")
        return
    text = f"💊 **Your Medications** ({len(medications)})\n\nTap a medication to view details:"
    markup = make_medication_list_keyboard(medications)
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['list'])
def list_medications(message):
    user_id = message.chat.id
    
    medications = get_user_medications(user_id)
    
    if not medications:
        text = (
            "📋 You don't have any medications yet.\n\n"
            "Add your first medication with /addpill"
        )
        bot.send_message(user_id, text)
        return
    
    text = f"💊 **Your Medications** ({len(medications)})\n\n"
    text += "Tap a medication to view details:"
    
    markup = make_medication_list_keyboard(medications)
    bot.send_message(user_id, text, reply_markup=markup, parse_mode="Markdown")



@bot.callback_query_handler(func=lambda c: c.data.startswith('view_'))
def view_medication(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    
    med_id = int(call.data.replace('view_', ''))
    med = get_medication_by_id(med_id)
    
    if not med:
        bot.answer_callback_query(call.id, " Medication not found")
        return
    
    # Build display
    times_str = ', '.join(med['times'])
    
    if med['frequency'] == 'weekly' and med['days']:
        days_str = ', '.join(med['days'])
        freq_display = f"Weekly ({days_str})"
    else:
        freq_display = med['frequency'].capitalize()
    
    text = (
        f"💊 **{med['name']}**\n\n"
        f"**Dosage:** {med['dosage']}\n"
        f"**Frequency:** {freq_display}\n"
        f"**Times:** {times_str}\n\n"
        "What would you like to do?"
    )
    markup = make_edit_keyboard(med_id, frequency=med['frequency'])     
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )



@bot.callback_query_handler(func=lambda c: c.data.startswith('delete_'))
def confirm_delete(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    
    med_id = int(call.data.replace('delete_', ''))
    med = get_medication_by_id(med_id)
    
    if not med:
        bot.answer_callback_query(call.id, " Medication not found")
        return
    
    text = (
        f" **Delete Medication?**\n\n"
        f" {med['name']} - {med['dosage']}\n\n"
        "This action cannot be undone."
    )
    
    markup = make_delete_confirm_keyboard(med_id)
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('confirm_delete_'))
def execute_delete(call):
    bot.answer_callback_query(call.id, "Deleted!")
    user_id = call.message.chat.id
    med_id = int(call.data.replace('confirm_delete_', ''))
    deactivate_medication(med_id)
    bot.edit_message_text("✅ Medication deleted successfully.", call.message.chat.id, call.message.message_id)
    _send_medication_list(user_id)


@bot.callback_query_handler(func=lambda c: c.data == 'back_to_list')
def back_to_list(call):
    bot.answer_callback_query(call.id)
    
    medications = get_user_medications(call.message.chat.id)
    
    if not medications:
        bot.edit_message_text(
            "📋 No medications found.",
            call.message.chat.id,
            call.message.message_id
        )
        return
    
    text = f"💊 **Your Medications** ({len(medications)})\n\n"
    text += "Tap a medication to view details:"
    
    markup = make_medication_list_keyboard(medications)
    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )


# ==================== ADD NEW FROM LIST ====================

@bot.callback_query_handler(func=lambda c: c.data == 'add_new_med')
def add_new_from_list(call):
    bot.answer_callback_query(call.id)
    from src.handlers.medication import _start_add_medication
    _start_add_medication(call.message.chat.id)



@bot.callback_query_handler(func=lambda c: c.data.startswith('edit_name_'))
def edit_name(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    med_id = int(call.data.replace('edit_name_', ''))
    
    # Store editing state
    user_data[user_id] = {
        'editing': True,
        'edit_field': 'name',
        'medication_id': med_id
    }
    
    sent_msg = bot.send_message(
        user_id,
        "✏️ Enter new medication name:\n\n_Type /cancel to cancel_",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent_msg, process_edit_name)


def process_edit_name(message):
    user_id = message.chat.id
    
    if user_id not in user_data:
        bot.send_message(user_id, " Session expired. Please try again.")
        return
    
    med_id = user_data[user_id]['medication_id']
    new_name = message.text.strip()
    
    # Update in database
    update_medication(med_id, name=new_name)
    
    bot.send_message(user_id, f" Name updated to: {new_name}")
    
    # Clean up
    del user_data[user_id]
    
    # Show updated medication
    med = get_medication_by_id(med_id)
    times_str = ', '.join(med['times'])
    
    if med['frequency'] == 'weekly' and med['days']:
        days_str = ', '.join(med['days'])
        freq_display = f"Weekly ({days_str})"
    else:
        freq_display = med['frequency'].capitalize()
    
    text = (
        f"💊 **{med['name']}**\n\n"
        f"**Dosage:** {med['dosage']}\n"
        f"**Frequency:** {freq_display}\n"
        f"**Times:** {times_str}\n\n"
        "What would you like to do?"
    )
    
    markup = make_edit_keyboard(med_id)
    bot.send_message(
        user_id,
        text,
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('edit_dosage_'))
def edit_dosage(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    med_id = int(call.data.replace('edit_dosage_', ''))
    
    user_data[user_id] = {
        'editing': True,
        'edit_field': 'dosage',
        'medication_id': med_id
    }
    
    sent_msg = bot.send_message(
        user_id,
        "✏️ Enter new dosage:\n\n_Examples: 100mg, 2 tablets_\n_Type /cancel to cancel_",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(sent_msg, process_edit_dosage)


def process_edit_dosage(message):
    user_id = message.chat.id
    
    if user_id not in user_data:
        bot.send_message(user_id, " Session expired. Please try again.")
        return
    
    med_id = user_data[user_id]['medication_id']
    new_dosage = message.text.strip()
    
    # Update in database
    update_medication(med_id, dosage=new_dosage)
    
    bot.send_message(user_id, f" Dosage updated to: {new_dosage}")
    
    # Clean up
    del user_data[user_id]
    
    _show_medication(user_id, med_id)

@bot.callback_query_handler(func=lambda c: c.data.startswith('edit_times_'))
def edit_times(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    med_id = int(call.data.replace('edit_times_', ''))

    med = get_medication_by_id(med_id)
    existing_times_count = len(med['times']) if med and med.get('times') else 1

    user_data[user_id] = {
        'editing': True,
        'edit_field': 'times',
        'medication_id': med_id,
        'times': [],
        'current_time_index': 0,
        'times_count': existing_times_count
    }

    sent_msg = bot.send_message(
        user_id,
        f"⏰ Enter time for dose 1 of {existing_times_count}:\n\n"
        "_Examples: 9am, 14:30, 3:00 PM_\n"
        "_Type /cancel to cancel_",
        parse_mode="Markdown"
    )
    from src.handlers.medication import collect_times_handler
    bot.register_next_step_handler(sent_msg, collect_times_handler) 

def process_edit_times(message):
    user_id = message.chat.id
    
    if user_id not in user_data:
        bot.send_message(user_id, " Session expired. Please try again.")
        return
    
    med_id = user_data[user_id]['medication_id']
    new_name = message.text.strip()
    
    # Update in database
    update_medication(med_id, times=new_name)
    
    bot.send_message(user_id, f" Name updated to: {new_name}")
    
    # Clean up
    del user_data[user_id]
    
    _show_medication(user_id, med_id)


# ==================== EDIT DAYS ====================

@bot.callback_query_handler(func=lambda c: c.data.startswith('edit_days_'))
def edit_days(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    med_id = int(call.data.replace('edit_days_', ''))

    med = get_medication_by_id(med_id)
    current_days = set(med['days']) if med and med.get('days') else set()

    user_data[user_id] = {
        'editing': True,
        'edit_field': 'days',
        'medication_id': med_id,
        'selected_days': current_days
    }

    markup = make_day_selector(current_days)
    bot.send_message(
        user_id,
        "✏️ **Edit Days**\n\nTap to toggle, then press Done:",
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda c: c.data.startswith('day_') and
                             user_data.get(c.message.chat.id, {}).get('edit_field') == 'days')
def handle_edit_day_selection(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id

    if user_id not in user_data or 'selected_days' not in user_data[user_id]:
        bot.answer_callback_query(call.id, "⚠️ Session expired. Please try again.")
        return

    action = call.data.replace('day_', '')

    if action == 'done':
        if not user_data[user_id]['selected_days']:
            bot.answer_callback_query(call.id, "⚠️ Select at least one day!", show_alert=True)
            return

        med_id = user_data[user_id]['medication_id']
        days_list = sorted(user_data[user_id]['selected_days'])

        update_medication(med_id, days=days_list)
        del user_data[user_id]

        bot.edit_message_text(
            f"✅ Days updated to: {', '.join(days_list)}",
            call.message.chat.id,
            call.message.message_id
        )
        _show_medication(user_id, med_id)

    elif action == 'clear':
        user_data[user_id]['selected_days'] = set()
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=make_day_selector(user_data[user_id]['selected_days'])
        )

    elif action == 'weekdays':
        user_data[user_id]['selected_days'] = {'Mon', 'Tue', 'Wed', 'Thu', 'Fri'}
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=make_day_selector(user_data[user_id]['selected_days'])
        )

    elif action == 'weekend':
        user_data[user_id]['selected_days'] = {'Sat', 'Sun'}
        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=make_day_selector(user_data[user_id]['selected_days'])
        )

    else:
        day = action
        if day in user_data[user_id]['selected_days']:
            user_data[user_id]['selected_days'].remove(day)
        else:
            user_data[user_id]['selected_days'].add(day)

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=make_day_selector(user_data[user_id]['selected_days'])
        )