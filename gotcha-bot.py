#!/bin/python

# bot.py
import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyClient(discord.Client):

    async def on_message(self, message):
        if message.author == client.user:
            return

        if not message.guild:
            # private message
            print("recieved PM")

    async def on_ready(self):
        print(f'{client.user.name} has connected to Discord!')


client = MyClient()
client.run(TOKEN)
