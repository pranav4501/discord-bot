import discord
import os
from openai import OpenAI

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
oAIClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
            response = oAIClient.chat.completions.create(model="gpt-4o-mini",
                                                       messages=chat_history)
            await channel.send(response.choices[0].message.content)


my_secret = os.environ['DISCORD_BOT_KEY']
client.run(my_secret)
