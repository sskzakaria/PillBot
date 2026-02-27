# main.py

import os
from src.app import bot
from src.database.schema import init_database
from src.scheduler.scheduler import start_scheduler, stop_scheduler, scheduler
from src.scheduler.reminder import check_reminders, setup_reminder_handlers

from src.handlers import (
    start,
    timezone,
    medication,
    list,
    stats
)

if __name__ == '__main__':
    init_database()
    
    setup_reminder_handlers(bot)
    
    start_scheduler()
    
    # add the job that checks reminders every minute
    scheduler.add_job(
        lambda: check_reminders(bot),
        trigger='cron',
        minute='*',  # every minute
        id='check_reminders',
        replace_existing=True
    )
        
    # start the bot
    try:
        print(" Bot starting...")
        bot.infinity_polling()
    except KeyboardInterrupt:
        print("\n Stopping bot...")
        stop_scheduler()
        print(" Bot stopped")