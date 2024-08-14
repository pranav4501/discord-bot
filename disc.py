import discord
import os
from openai import OpenAI
import json

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
           
    }
]
def gen_tool_call_response(response):
    time = get_current_time()
    function_call_result_message = {
        "role": "tool",
        "content": json.dumps({
            "time": time
        }),
        "tool_call_id": response.choices[0].message.tool_calls[0].id
    }
    return function_call_result_message
    

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user in message.mentions:
        channel = message.channel
        async with channel.typing():
            chat_history = [{
                "role": "system",
                "content": "You are a helpful assistant."
            }]
            messages = [message async for message in channel.history(limit=123)]
            chat_history = [{
                "role": "system",
                "content": "You are a helpful assistant."
            }]
            for msg in reversed(messages):
                role = "assistant" if msg.author == client.user else "user"
                chat_history.append({"role": role, "content": msg.content})
            print(chat_history)
            response = oAIClient.chat.completions.create(model="gpt-4o-mini", messages=chat_history, tools = tools)
            if response.choices[0].finish_reason=="tool_calls":
                
                
                chat_history.append(response.choices[0].message)
                chat_history.append(gen_tool_call_response(response))
                response = oAIClient.chat.completions.create(model="gpt-4o-mini", messages=chat_history, tools = tools)
            await channel.send(response.choices[0].message.content)


my_secret = os.environ['DISCORD_BOT_KEY']
client.run(my_secret)
