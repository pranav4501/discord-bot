import sqlite3
import schedule
from datetime import datetime,timedelta
import time

conn =  sqlite3.connect('timer.db')
cursor = conn.cursor()

def check_timers():
  now = datetime.now()
  cursor.execute('SELECT id, start_time, duration FROM timers WHERE status = "running"')
  timers = cursor.fetchall()

  for timer in timers:
    start_time = datetime.fromisoformat(timer[1])
    duration = timer[2]
    end_time = start_time + timedelta(seconds=duration)

    if now >= end_time:
      cursor.execute('UPDATE timers SET status = "expired" WHERE id = ?', (timer[0],))
      conn.commit()
      print(f"Timer {timer[0]} has expired.")

schedule.every(1).second.do(check_timers)

while True:
  schedule.run_pending()
  time.sleep(1)

