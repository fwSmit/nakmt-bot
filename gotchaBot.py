#!/bin/python

# bot.py
import os
import discord
from dotenv import load_dotenv
import time
import math
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyClient(discord.Client):

    totalTimes = dict()
    totalTimesNoTimeSlot = dict()
    names_by_id = dict()
    timeJoined = dict()


    def get_gotcha_status(self):
        # returns string with the current gotcha status
        return_string = ""
        keys = list(self.totalTimes.keys())
        values = list(self.totalTimes.values())
        for i in range(len(keys)):
            keys[i] = self.names_by_id[keys[i]]
            minutes = math.floor(values[i]/60)
            hours = math.floor(values[i]/(60*60))
            return_string += "{} has a time of {}h {}min".format(keys[i], hours, minutes)
            
        return return_string
        
    
    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content == "!gotcha":
            await message.channel.send("Current status:\n" + self.get_gotcha_status())
            

        if not message.guild:
            # private message
            print("recieved PM")
            if message.author.id == 237631697150017537:
                print("received message from my author")
                await message.channel.send("Giving the times to you")
                status = self.get_gotcha_status()
                await message.channel.send(status)
                
                

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
                self.totalTimes[member.id] = timedelta(0)
                self.totalTimesNoTimeSlot[member.id] = timedelta(0)

            self.timeJoined[member.id] = datetime.now()
                
        if before.channel != None and after.channel == None:
            print("Left voice channel")
            if member.id not in self.names_by_id:
                print("ERROR: don't know this person leaving the voice chat")
                return

                
            print("Total time: {}".format(self.totalTimes[member.id]))
        
        beginTime = self.timeJoined[member.id]
        endTime = datetime.now()
        # member.id
        # member.display_name


class Util:
    interval_begin_hour = 16
    interval_end_hour = 4
    
    def isInTimeSlot(self, t: datetime):
        # Time slot is Mon-Fri 16:00 - 04:00
        weekday = t.date().weekday()
        if t.hour >= self.interval_begin_hour and weekday < self.interval_end_hour:
            return True
        if t.hour < self.interval_end_hour and weekday > 0 and weekday <= 5:
            return True
        return False

        
    def calculateInterval(self, beginTime: datetime, endTime: datetime):
        # I'm assuming total time is not more than about 12 hours, so the duration doesn't span accross an entire timespan
        naive_diff = endTime-beginTime
        
        #check if the interval is more than 12 hours.
        if naive_diff > timedelta(hours=12):
            # Do not calculate the time correctly, but instead return naive diff
            print("Time interval more than 12 hours, returning naive_diff")
            return naive_diff
        
        # both in time slot
        if self.isInTimeSlot(beginTime) and self.isInTimeSlot(endTime):
            print("Duration (normal case): {} seconds".format(naive_diff))
            return naive_diff
            
        # begin time in time slot and end time not
        if self.isInTimeSlot(beginTime) and not self.isInTimeSlot(endTime): 
            actual_beginTime = beginTime
            actual_endTime = endTime.replace(hour=self.interval_end_hour,minute=0,second=0,microsecond=0)
            actual_diff = actual_endTime - actual_beginTime
            print("Duration (case 2): {} seconds".format(actual_diff))
            return actual_diff

        # begin time not in time slot, end time is
        if not self.isInTimeSlot(beginTime) and self.isInTimeSlot(endTime): 
            actual_endTime = endTime
            actual_beginTime = beginTime.replace(hour=16,minute=0,second=0,microsecond=0)
            actual_diff = actual_endTime - actual_beginTime
            print("Duration (case 3): {} seconds".format(actual_diff))
            return actual_diff
        
        # both not in time slot
        if not self.isInTimeSlot(beginTime) and not self.isInTimeSlot(endTime):
            print("Both times are not in the time slot")
            return timedelta(0)
    



#  client = MyClient()
#  client.run(TOKEN)
