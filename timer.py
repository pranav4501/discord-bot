import sqlite3
from datetime import datetime



def add_timer(duration, channel_id):
    conn = sqlite3.connect('timer.db')
    cursor =  conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS timers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time TEXT,
        duration INTEGER, -- duration in seconds
        status TEXT,
        channel_id TEXT
    )
    ''')
    conn.commit()
    start_time = datetime.now()
    status = 'running'
    cursor.execute('''
    INSERT INTO timers (start_time, duration, status, channel_id) 
    VALUES (?, ?, ?, ?)''', (start_time, duration, status, channel_id))
    conn.commit()
    conn.close()
