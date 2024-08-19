import sqlite3
from datetime import datetime, timedelta



def add_timer(duration, channel_id):
    conn = sqlite3.connect('timer.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS timers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        end_time TEXT,
        duration INTEGER, -- duration in seconds
        status TEXT,
        channel_id TEXT
    )
    ''')
    conn.commit()

    end_time = datetime.now() + timedelta(seconds=duration)
    status = 'running'

    cursor.execute('''
    INSERT INTO timers (end_time, duration, status, channel_id) 
    VALUES (?, ?, ?, ?)''', (end_time.isoformat(), duration, status, channel_id))

    conn.commit()
    conn.close()
