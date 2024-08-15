import sqlite3
from datetime import datetime

conn = sqlite3.connect('timer.db')
cursor =  conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS timers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT,
    duration INTEGER, -- duration in seconds
    status TEXT
)
''')
conn.commit()

def add_timer(duration):
  start_time = datetime.now()
  status = 'running'
  cursor.execute('''
  INSERT INTO timers (start_time, duration, status) 
  VALUES (?, ?, ?)''', (start_time, duration, status))
  conn.commit()

add_timer(10)
conn.close()
