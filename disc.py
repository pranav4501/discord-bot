import discord
import os
import psycopg2
from psycopg2 import sql
from openai import OpenAI
import json
from timer import add_timer


channel_id = 0

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT")
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    channel_id BIGINT NOT NULL,
    message_author VARCHAR(100),
    message_content TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
""")

conn.commit()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
oAIClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from datetime import datetime

def get_current_time():
    # Get the current time
    now = datetime.now()

    # Format the time as a string
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    return current_time + " UTC"

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time",
            "parameters": {
                },
            },
           
    },
    {
        "type":"function",
        "function":{
            "name": "add_timer",
            "description": "Add a timer",
            "parameters":{
                "type":"object",
                "properties":{
                    "duration":{
                        "type":"integer",
                        "description":"The duation of timer in seconds."
                    }
                },
                "required": ["duration"]
            }
        }
    }
]
def gen_tool_call_response(response,channel_id):
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    print(function_name)
    if function_name == "get_current_time":
        time = get_current_time()
        function_call_result_message = {
            "role": "tool",
            "content": json.dumps({
                "time": time
            }),
            "tool_call_id": response.choices[0].message.tool_calls[0].id
        }
    else:
        args = json.loads(tool_call.function.arguments)['duration']
        duration = int(args)
        print("set timer for "+ str(duration)+ " seconds and channel id - " +str(channel_id))
        add_timer(duration,channel_id)
        function_call_result_message = {
            "role" : "tool",
            "content": json.dumps({
                "message": "Timer added successfully for duration"+ str(duration) + " seconds."
            }),
            "tool_call_id": response.choices[0].message.tool_calls[0].id
        }
                                    
    return function_call_result_message

async def get_chat_history(channel_id, limit=10):
    cursor.execute(
        sql.SQL("SELECT message_author, message_content FROM chat_history WHERE channel_id = %s ORDER BY timestamp DESC LIMIT %s"),
        [channel_id, limit]
    )
    rows = cursor.fetchall()
    chat_history = [{"role": "user" if row[0] != 'assistant' else "assistant", "content": row[1]} for row in rows]
    chat_history.reverse()  # Ensure messages are in chronological order
    return chat_history
    

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:
        channel = message.channel
        channel_id = channel.id
        
        async with channel.typing():
            cursor.execute(
                sql.SQL("INSERT INTO chat_history (channel_id, message_author, message_content) VALUES (%s, %s, %s)"),
                [message.channel.id, message.author.name, message.content]
            )
            conn.commit()

            chat_history = await get_chat_history(channel.id)
            chat_history.insert(0, {"role": "system", "content": "You are a helpful assistant."})

            
            response = oAIClient.chat.completions.create(model="gpt-4o-mini", messages=chat_history, tools = tools)

            
            if response.choices[0].finish_reason=="tool_calls":
                chat_history.append(response.choices[0].message)
                chat_history.append(gen_tool_call_response(response,channel_id))
                response = oAIClient.chat.completions.create(model="gpt-4o-mini", messages=chat_history, tools = tools)

            cursor.execute(
                sql.SQL("INSERT INTO chat_history (channel_id, message_author, message_content) VALUES (%s, %s, %s)"),
                [channel.id, 'assistant', response.choices[0].message.content]
            )
            conn.commit()
            await channel.send(response.choices[0].message.content)


my_secret = os.environ['DISCORD_BOT_KEY']
client.run(my_secret)
