import sqlite3
import schedule
from datetime import datetime, timedelta
from openai import OpenAI
import discord
import time
import os
import asyncio


oAIClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Setup Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

async def send_expired_timer_message(channel_id):
  print(int(channel_id))
  channel = client.get_channel(int(channel_id))
  print(channel)
  chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
  messages = [msg async for msg in channel.history(limit=10)]
  for msg in reversed(messages):
      role = "assistant" if msg.author == client.user else "user"
      chat_history.append({"role": role, "content": msg.content})
  chat_history.append({"role": "assistant","content": "timer has expired"})
  print(chat_history)
  response = oAIClient.chat.completions.create(model="gpt-4o-mini", messages=chat_history)  
  print(response.choices[0].message.content)
  await channel.send(response.choices[0].message.content)  


def check_timers():
    conn = sqlite3.connect('timer.db')
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute('SELECT id, end_time, channel_id FROM timers WHERE status = "running"')
    timers = cursor.fetchall()

    for timer in timers:
        end_time = datetime.fromisoformat(timer[1])
        channel_id = timer[2]

        if now >= end_time:
            cursor.execute('UPDATE timers SET status = "expired" WHERE id = ?', (timer[0],))
            conn.commit()
            print(f"Timer {timer[0]} has expired.")
            asyncio.run_coroutine_threadsafe(send_expired_timer_message(channel_id), client.loop)
    conn.close()


def schedule_check_timers():
  schedule.every(1).second.do(check_timers)
  while True:
      schedule.run_pending()
      time.sleep(1)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, schedule_check_timers)

client.run(os.getenv("DISCORD_BOT_KEY"))
