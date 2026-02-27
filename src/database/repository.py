# src/database/repository.py

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict
from src.database.schema import DB_PATH



def create_or_update_user(user_id: int, timezone: str) -> None:
    """Save or update user timezone"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (user_id, timezone, last_active)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(user_id) DO UPDATE SET
            timezone = excluded.timezone,
            last_active = CURRENT_TIMESTAMP
    ''', (user_id, timezone))
    conn.commit()
    conn.close()


def get_user_timezone(user_id: int) -> Optional[str]:
    """Get user's timezone, returns None if user doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT timezone FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


def user_exists(user_id: int) -> bool:
    """Check if user exists in database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result is not None



def create_medication(
    user_id: int,
    name: str,
    dosage: str,
    frequency: str,
    times: List[str],
    days: Optional[List[str]] = None
) -> int:
    """Create new medication, returns medication ID"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    times_json = json.dumps(times)
    days_json = json.dumps(days) if days else None
    
    c.execute('''
        INSERT INTO medications
        (user_id, name, dosage, frequency, times, days, active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
    ''', (user_id, name, dosage, frequency, times_json, days_json))
    
    medication_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return medication_id


def get_user_medications(user_id: int, active_only: bool = True) -> List[Dict]:
    """Get all medications for a user"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    if active_only:
        c.execute('''
            SELECT id, name, dosage, frequency, times, days, active
            FROM medications
            WHERE user_id = ? AND active = 1
            ORDER BY created_at DESC
        ''', (user_id,))
    else:
        c.execute('''
            SELECT id, name, dosage, frequency, times, days, active
            FROM medications
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
    
    rows = c.fetchall()
    conn.close()
    
    medications = []
    for row in rows:
        med = dict(row)
        med['times'] = json.loads(med['times'])
        med['days'] = json.loads(med['days']) if med['days'] else None
        medications.append(med)
    
    return medications


def get_medication_by_id(medication_id: int) -> Optional[Dict]:
    """Get single medication by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT id, user_id, name, dosage, frequency, times, days, active
        FROM medications
        WHERE id = ?
    ''', (medication_id,))
    
    row = c.fetchone()
    conn.close()
    
    if not row:
        return None
    
    med = dict(row)
    med['times'] = json.loads(med['times'])
    med['days'] = json.loads(med['days']) if med['days'] else None
    
    return med


def update_medication(
    medication_id: int,
    name: Optional[str] = None,
    dosage: Optional[str] = None,
    times: Optional[List[str]] = None,
    days: Optional[List[str]] = None
) -> None:
    """Update medication fields"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    updates = []
    params = []
    
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    
    if dosage is not None:
        updates.append("dosage = ?")
        params.append(dosage)
    
    if times is not None:
        updates.append("times = ?")
        params.append(json.dumps(times))
    
    if days is not None:
        updates.append("days = ?")
        params.append(json.dumps(days))
    
    if not updates:
        conn.close()
        return
    
    params.append(medication_id)
    query = f"UPDATE medications SET {', '.join(updates)} WHERE id = ?"
    
    c.execute(query, params)
    conn.commit()
    conn.close()


def deactivate_medication(medication_id: int) -> None:
    """Soft delete - set active to False"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('UPDATE medications SET active = 0 WHERE id = ?', (medication_id,))
    
    conn.commit()
    conn.close()


def get_medication_count(user_id: int) -> int:
    """Get count of active medications for user"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT COUNT(*) FROM medications 
        WHERE user_id = ? AND active = 1
    ''', (user_id,))
    
    result = c.fetchone()
    conn.close()
    
    return result[0] if result else 0



def get_all_users_with_meds():
    """
    Get all users who have active medications.
    Returns list of tuples: [(user_id, timezone), ...]
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT DISTINCT u.user_id, u.timezone
        FROM users u
        JOIN medications m ON u.user_id = m.user_id
        WHERE m.active = 1
        AND u.notifications_enabled = 1
    ''')
    
    results = c.fetchall()
    conn.close()
    
    return results


def log_reminder_sent(medication_id: int, user_id: int) -> int:
    """Log when we send a reminder"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO reminder_logs (medication_id, user_id)
        VALUES (?, ?)
    ''', (medication_id, user_id))
    
    log_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return log_id


def mark_reminder_acknowledged(log_id: int):
    """Mark when user clicks 'Taken' button"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        UPDATE reminder_logs 
        SET acknowledged = 1 
        WHERE id = ?
    ''', (log_id,))
    
    conn.commit()
    conn.close()



def get_user_stats(user_id: int, days: int = 7) -> Dict:
    """Get user statistics for last N days"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT 
            COUNT(*) as total_reminders,
            SUM(acknowledged) as taken_count
        FROM reminder_logs
        WHERE user_id = ?
        AND sent_at >= datetime('now', '-' || ? || ' days')
    ''', (user_id, days))
    
    result = c.fetchone()
    conn.close()
    
    total, taken = result
    taken = taken or 0
    
    return {
        'total_reminders': total,
        'taken_count': taken,
        'missed_count': total - taken,
        'adherence_rate': (taken / total * 100) if total > 0 else 0
    }