#!/bin/python

# bot.py
import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
import math
from datetime import datetime, timedelta
import asyncio
import time

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyClient(discord.Client):

    totalTimes = dict()
    totalTimesNoTimeSlot = dict()
    names_by_id = dict()
    timeJoined = dict()
    enoughTime = [dict() for n in range(5)]
    #  requiredTime = timedelta(hours=1)
    requiredTime = timedelta(seconds=10)
    channelAllowList = ["Statafel (4x)", "Achterzaal", "Keuken", "Bar", "Dunste stukje van de soos"]


    def get_gotcha_status(self):
        # returns string with the current gotcha status
        return_string = "Below you can see how long you have been in a voice channel in total today. This only gets updated when you leave a voice channel.\n"
        keys = list(self.totalTimes.keys())
        values = list(self.totalTimes.values())
        for i in range(len(keys)):
            name = self.names_by_id[keys[i]]
            minutes = math.floor(values[i].seconds/60) % 60
            hours = math.floor(values[i].seconds/(60*60))
            return_string += "{} has a time of {}h {}min\n".format(name, hours, minutes)
            
        return return_string
        
    def get_signoff_status(self):
        return_string = ""
        for i in range(len(self.enoughTime)):
            return_string += "Day: " + str(datetime.now().weekday) + "\n"
            for key in self.enoughTime[i]:
                name = self.names_by_id[key]
                signed_off = self.enoughTime[i][key]
                return_string += "{} has signed of status {}".format(name, signed_off)
            
        if len(return_string) == 0:
            return "Niemand is lang genoeg aanwezig geweest."
    
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
                signed_off = self.get_signoff_status()
                await message.channel.send(status)
                await message.channel.send(signed_off)
                
                
    @tasks.loop(hours=1)
    async def myloop(self):
        hour = time.localtime().tm_hour
        self.backup()
        if hour == 6:
            # check who has had enough time in the discord
            currDay = datetime.now().weekday()
            currDay -= 1
            for key in self.totalTimes:
                t = self.totalTimes[key]
                if t > self.requiredTime:
                    print("{} has enough time")
                    self.enoughTime[currDay][key] = 1

            for key in self.totalTimes:
                self.totalTimes[key] = timedelta(0)
                    
    def backup(self):
        currMonth = datetime.now().month
        currDay = datetime.now().day
        currHour = datetime.now().hour
        currMin = datetime.now().minute
        with open ('backup_{}_{}_{}_{}'.format(currMonth, currDay, currHour, currMin)+".txt", 'w') as f:
            f.write("total times:\n")
            for key in self.totalTimes:
                f.write("{} - {} - {}\n".format(key, self.totalTimes[key], self.names_by_id[key]))
            

    async def on_ready(self):
        print(f'{client.user.name} has connected to Discord!')
        print('Guilds: {}'.format(self.guilds))
        self.myloop.start()

    async def on_voice_state_update(self, member, before, after):
        print("Member {}".format(member.display_name))
        print("Member id {}".format(member.id))
        if before.channel == None and after.channel != None:
            print("Joined voice channel {}".format(after.channel.name))
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

            u = Util()
            beginTime = self.timeJoined[member.id]
            del self.timeJoined[member.id]
            endTime = datetime.now()
            diff = u.calculateInterval(beginTime, endTime)
            self.totalTimes[member.id] += diff
            print("Total time: {}".format(self.totalTimes[member.id]))
            #  if self.totalTimes[member.id] > timedelta(hours=1):
            if self.totalTimes[member.id] > timedelta(minutes=1):
                print("This person has enough time")
                day = endTime.date().day
                #  if endTime.hour <
                
                
        
        # member.id
        # member.display_name


class Util:
    interval_begin_hour = 16
    interval_end_hour = 2
    maxInterval = 10
    
    def isInTimeSlot(self, t: datetime):
        # Time slot is Mon-Fri 16:00 - 02:00
        weekday = t.date().weekday()
        if t.hour >= self.interval_begin_hour and weekday >= 0 and weekday < 5:
            return True
        if t.hour < self.interval_end_hour and weekday > 0 and weekday <= 5:
            return True
        return False

        
    def calculateInterval(self, beginTime: datetime, endTime: datetime):
        # I'm assuming total time is not more than about 12 hours, so the duration doesn't span accross an entire timespan
        naive_diff = endTime-beginTime
        
        #check if the interval is more than 12 hours.
        if naive_diff > timedelta(hours=self.maxInterval):
            # Do not calculate the time correctly, but instead return naive diff
            print("Time interval more than {} hours, returning naive_diff".format(self.maxInterval))
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
    

client = MyClient()
client.run(TOKEN)
