#!/bin/python

# bot.py
import os
import discord
from dotenv import load_dotenv
import time

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyClient(discord.Client):

    totalTimes = dict()
    names_by_id = dict()
    timeJoined = dict()
    
    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content == "!gotcha":
            await message.channel.send("Got your message")

        if not message.guild:
            # private message
            print("recieved PM")
            if message.author.id == 237631697150017537:
                print("received message from my author")
                await message.channel.send("Giving the times to you")
                keys = list(self.totalTimes.keys())
                values = list(self.totalTimes.values())
                for i in range(len(keys)):
                    keys[i] = self.names_by_id[keys[i]]
                    await message.channel.send("{} has a time of {}".format(keys[i], values[i]))
                
                

    async def on_ready(self):
        print(f'{client.user.name} has connected to Discord!')
        print('Guilds: {}'.format(self.guilds))

    async def on_voice_state_update(self, member, before, after):
        print("Member {}".format(member.display_name))
        print("Member id {}".format(member.id))
        if before.channel == None and after.channel != None:
            print("Joined voice channel")
            if member.id not in self.names_by_id:
                # I dont know this person, adding to the dictionary
                self.names_by_id[member.id] = member.display_name
                self.totalTimes[member.id] = 0
            self.timeJoined[member.id] = time.time()
                
        if before.channel != None and after.channel == None:
            print("Left voice channel")
            if member.id not in self.names_by_id:
                print("ERROR: don't know this person leaving the voice chat")
                return

            joined = self.timeJoined[member.id]
            diff = time.time() - joined
            print("This person was in the voice chat for {} seconds".format(diff))
            self.totalTimes[member.id] += diff
            print("Total time: {}".format(self.totalTimes[member.id]))
        # member.id
        # member.display_name


client = MyClient()
client.run(TOKEN)
