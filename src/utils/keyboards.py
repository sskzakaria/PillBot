# src/utils/keyboards.py

from telebot.types import (
    KeyboardButton, 
    ReplyKeyboardMarkup, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardRemove
)

def make_timezone_keyboard():
    '''Create keyboard for timezone selection'''
    markup = ReplyKeyboardMarkup(
        row_width=1, 
        resize_keyboard=True, 
        one_time_keyboard=True
    )
    markup.add(KeyboardButton("📍 Share Location", request_location=True))
    return markup


def make_frequency_keyboard():
    '''Create keyboard for frequency selection'''
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton('📅 Daily', callback_data='freq_daily'),
        InlineKeyboardButton('📆 Weekly', callback_data='freq_weekly')
    )
    return markup


def make_times_per_day_keyboard():
    '''Create keyboard for selecting how many times per day'''
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton('Once', callback_data='times_1'),
        InlineKeyboardButton('Twice', callback_data='times_2')
    )
    markup.add(
        InlineKeyboardButton('3 times', callback_data='times_3'),
        InlineKeyboardButton('4 times', callback_data='times_4')
    )
    return markup


def make_day_selector(selected_days: set) -> InlineKeyboardMarkup:
    '''Create multi-select day picker with checkmarks'''
    markup = InlineKeyboardMarkup(row_width=3)
    
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Create buttons with checkmarks
    buttons = []
    for day in days:
        if day in selected_days:
            text = f"{day} ✅"
        else:
            text = f"{day} ⬜"
        
        buttons.append(
            InlineKeyboardButton(text, callback_data=f"day_{day}")
        )
    
    # Add buttons in rows of 3
    for i in range(0, len(buttons), 3):
        if i + 2 < len(buttons):
            markup.row(buttons[i], buttons[i + 1], buttons[i + 2])
        elif i + 1 < len(buttons):
            markup.row(buttons[i], buttons[i + 1])
        else:
            markup.row(buttons[i])
    
    # Quick select buttons
    markup.row(
        InlineKeyboardButton("📅 Weekdays", callback_data="day_weekdays"),
        InlineKeyboardButton("📅 Weekend", callback_data="day_weekend")
    )
    
    # Control buttons
    markup.row(
        InlineKeyboardButton("✅ Done", callback_data="day_done"),
        InlineKeyboardButton("🔄 Clear", callback_data="day_clear")
    )
    
    return markup


def make_confirm_keyboard():
    '''Create keyboard for yes/no confirmation'''
    markup = ReplyKeyboardMarkup(
        one_time_keyboard=True, 
        resize_keyboard=True,
        row_width=2
    )
    markup.add(KeyboardButton("✅ Yes"), KeyboardButton("❌ No"))
    return markup


def make_edit_keyboard(medication_id: int):
    '''Create keyboard for editing medication'''
    markup = InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        InlineKeyboardButton("✏️ Name", callback_data=f"edit_name_{medication_id}"),
        InlineKeyboardButton("✏️ Dosage", callback_data=f"edit_dosage_{medication_id}")
    )
    markup.add(
        InlineKeyboardButton("✏️ Times", callback_data=f"edit_times_{medication_id}"),
        InlineKeyboardButton("✏️ Days", callback_data=f"edit_days_{medication_id}")
    )
    markup.add(
        InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{medication_id}")
    )
    markup.add(
        InlineKeyboardButton("« Back to List", callback_data="back_to_list")
    )
    
    return markup


def make_medication_list_keyboard(medications: list):
    '''Create keyboard for medication list with view/edit buttons'''
    markup = InlineKeyboardMarkup(row_width=1)
    
    for med in medications:
        # Create button text with emoji based on frequency
        if med['frequency'] == 'daily':
            emoji = "📅"
        else:
            emoji = "📆"
        
        button_text = f"{emoji} {med['name']} - {med['dosage']}"
        
        markup.add(
            InlineKeyboardButton(
                button_text,
                callback_data=f"view_{med['id']}"
            )
        )
    
    # Add medication button
    markup.add(
        InlineKeyboardButton(
            "➕ Add New Medication",
            callback_data="add_new_med"
        )
    )
    
    return markup


def make_delete_confirm_keyboard(medication_id: int):
    '''Create keyboard for delete confirmation'''
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(" Yes, Delete", callback_data=f"confirm_delete_{medication_id}"),
        InlineKeyboardButton(" Cancel", callback_data=f"view_{medication_id}")
    )
    return markup


def make_stats_period_keyboard():
    '''Create keyboard for stats time period selection'''
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("7 Days", callback_data="stats_7"),
        InlineKeyboardButton("30 Days", callback_data="stats_30"),
        InlineKeyboardButton("90 Days", callback_data="stats_90")
    )
    return markup