import sqlite3
import json
from datetime import datetime
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / 'data' / 'bot.db'

def init_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Users table - stores per-user settings
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            timezone TEXT NOT NULL,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notifications_enabled BOOLEAN DEFAULT 1
        )
    ''')

    # Medications table - one-to-many with users
    c.execute('''
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            dosage TEXT,
            frequency TEXT NOT NULL,
            times TEXT NOT NULL,
            days TEXT,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
                ON DELETE CASCADE
        )
    ''')

    # Reminder logs - track what was sent
    c.execute('''
        CREATE TABLE IF NOT EXISTS reminder_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medication_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            acknowledged BOOLEAN DEFAULT 0,
            FOREIGN KEY (medication_id) REFERENCES medications (id)
                ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
                ON DELETE CASCADE
        )
    ''')
        
    # Indexes
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_user_active 
        ON medications(user_id, active)
    ''')

    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_reminder_sent 
        ON reminder_logs(sent_at)
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database setup at {DB_PATH}")

if __name__=='__main__':
    init_database()