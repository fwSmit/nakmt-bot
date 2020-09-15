#!/bin/python
# bot.py
import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN2')

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
            if message.author.id not in self.conversations:
                print("I don't know this person. Making new conversation")
                self.conversations[message.author.id] = Conversation()
                await self.conversations[message.author.id].start(message.channel)
            else:
                await self.conversations[message.author.id].talk(message)
            

    async def on_ready(self):
        print(f'{client.user.name} has connected to Discord!')


class Conversation:
    testing = False
    progress = 0
    questions = [
            "Hello there. You need to answer a few questions to show you know me well. Use the information you've gathered well. \nFirst question: What is my name?",
            "Second question: At which activity am I always present?",
            "Third question: What is my favorite aquarium decoration?",
            "Fourth question: What kind of water do I like to stay in?"
    ]
    answers = [
            ["Bob", "bob de vis"],
            ["ALV", "algemene ledenvergadering"],
            ["De aardenwerken vis", "Aardenwerken vis", "Aardewerken vis", "De aardewerken vis"],
            ["Formaline"]
    ]

    def validateAnswer(self, content):
        for a in self.answers[self.progress]:
            l_answer = str.lower(a)
            l_content = str.lower(content)
            if l_content.find(l_answer) == 0:
                return True
        
        return False
    
    async def say(self, string, channel):
        if self.testing:
            print(string)
        else:
            await channel.send(string)
    
    async def start(self, channel):
        await self.say(self.questions[0], channel)

    async def talk(self, message):
        # await message.channel.send("Received message: {}".format(message.content))
        if self.progress > len(self.answers)-1:
            await self.say("There are no more questions", message.channel)
            return
        
        if self.validateAnswer(message.content):
            await self.say("That's correct!", message.channel)
            self.progress = self.progress + 1
            if self.progress > len(self.questions) - 1:
                await self.say("You have gotten all questions correct! Send the message 'Sterk water' to Jayce to show that you have completed the scavenger hunt.", message.channel)
            else:
                question = self.questions[self.progress]
                await self.say(question, message.channel)
                await self.say("Progress: {}".format(self.progress), message.channel)
        else:
            await self.say("That's not the right answer", message.channel)
            #  await self.say("The right answer is {}".format(self.answers[self.progress]), message.channel)
        # receive message


client = MyClient()
client.run(TOKEN)
