from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        print("⏰ Scheduler started")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        print("⏰ Scheduler stopped")