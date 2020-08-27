#!/bin/python

# bot.py
import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

GAME = False


class MyClient(discord.Client):
    GAME = False
    conversations = dict()  # dictionary of conversation classes

    async def on_message(self, message):
        if message.author == client.user:
            return

        if not message.guild:
            # private message
            print("recieved PM")
            print(message.content)
            print(message.author)
            await message.channel.send("Recieved your message. Starting conversation")
            if message.author not in self.conversations:
                print("I don't know this person. Making new conversation")
                self.conversations[message.author] = Conversation()

            await self.conversations[message.author].talk(message)
            

    async def on_ready(self):
        print(f'{client.user.name} has connected to Discord!')


class Conversation:
    progress = 0
    questions = [
            "First question: What is my name?",
            "Well done."
    ]
    answers = [
            "Bob"
    ]

    def validateAnswer(self, content):
        l_answer = str.lower(self.answers[self.progress])
        l_content = str.lower(content)
        if l_content.find(l_answer) == 0:
            return True
        
        return False
    
    async def talk(self, message):
        #  await message.channel.send("Received message: {}".format(message.content))
        question = self.questions[0]
        await message.channel.send(question)
        await message.channel.send("Progress: {}".format(self.progress))
        if self.validateAnswer(message.content):
            await message.channel.send("That's the right answer")
            self.progress = self.progress + 1
        # receive message


client = MyClient()
client.run(TOKEN)
