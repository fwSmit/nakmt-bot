#!/bin/python

# bot.py
import os
import discord
from dotenv import load_dotenv
import time
import math

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
                self.totalTimes[member.id] = 0
                self.totalTimesNoTimeSlot[member.id] = 0
            self.timeJoined[member.id] = time.time()
                
        if before.channel != None and after.channel == None:
            print("Left voice channel")
            if member.id not in self.names_by_id:
                print("ERROR: don't know this person leaving the voice chat")
                return

            joined_s = self.timeJoined[member.id]
            # _l means localtime and _s means seconds since epoch
            endTime_l = time.localtime()
            beginTime_s = joined_s
            beginTime_l = time.localtime(beginTime_s)
            endTime_s = time.mktime(endTime_l)
            diff_s = endTime_s - beginTime_s

            self.totalTimesNoTimeSlot[member.id] += diff_s
            
            # I'm assuming total time is not more than like 24 hours, so the duration doesn't span accross an entire timespan
            
            # both in time slot
            if self.isInTimeSlot(beginTime_l) and self.isInTimeSlot(endTime_l):
                self.totalTimes[member.id] += diff_s
                print("Duration (normal case): {} seconds".format(diff_s))
                
            # end time in time slot, begin time not
            if self.isInTimeSlot(endTime_l) and not self.isInTimeSlot(endTime_l): 
                actual_beginTime_l = endTime_l
                actual_beginTime_l.tm_hour = 16
                if endTime_l.tm_hour < 16:
                    actual_beginTime_l.tm_wday -= 1
                    
                actual_beginTime_s = time.mktime(actual_beginTime_l)
                actual_endTime_s = time.mktime(endTime_l)
                actual_diff_s = actual_endTime_s - actual_beginTime_s
                self.totalTimes[member.id] += actual_diff_s
                print("Duration (case 2): {} seconds".format(actual_diff_s))

            # end time not in time slot, begin time is
            if not self.isInTimeSlot(endTime_l) and self.isInTimeSlot(endTime_l): 
                actual_beginTime_l = beginTime_l
                actual_endTime_l = beginTime_l
                actual_endTime_l.tm_hour = 4
                if beginTime_l.tm_hour < 16:
                    actual_endTime_l.tm_wday -= 1
                
                actual_beginTime_s = time.mktime(actual_beginTime_l)
                actual_endTime_s = time.mktime(endTime_l)
                actual_diff_s = actual_endTime_s - actual_beginTime_s
                self.totalTimes[member.id] += actual_diff_s
                print("Duration (case 3): {} seconds".format(actual_diff_s))

            # both not in time slot
            if not self.isInTimeSlot(endTime_l) and not self.isInTimeSlot(endTime_l):
                print("Both times are not in the time slot")
                
            print("Total time: {}".format(self.totalTimes[member.id]))
        # member.id
        # member.display_name

    def isInTimeSlot(self, t):
        # Time slot is Mon-Fri 16:00 - 04:00
        if t.tm_hour >= 16 and t.tm_wday <= 4:
            return True
        if t.tm_hour <= 4 and t.tm_wday > 0 and t.tm_wday <= 5:
            return True


client = MyClient()
client.run(TOKEN)
