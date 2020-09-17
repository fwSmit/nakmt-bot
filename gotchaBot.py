#!/bin/python

import logging
# bot.py
import os
from datetime import datetime, timedelta, time

import discord
from discord import VoiceState, Member
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

formatter = logging.Formatter('[%(levelname)s] %(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger('gotcha')
logger.setLevel(logging.INFO)

fileHandler = logging.FileHandler('gotcha.log')
fileHandler.setLevel(logging.INFO)
fileHandler.setFormatter(formatter)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(formatter)

logger.addHandler(fileHandler)
logger.addHandler(consoleHandler)

start_time = time(13, 00)
end_time = time(2, 00)
check_every_seconds = 1


def isNowInTimePeriod(start: time, end: time, now: time):
    if start < end:
        return start <= now <= end
    else:  # Over midnight
        return now >= start or now <= end


class GotchaBot(discord.Client):
    names_by_id = dict()
    totalTimesNewMethod = dict()
    currentlyInAllowedChannel = set()

    botChannelId = 619951850031939594
    privateChannelId = 737309942628745230
    botOwnerId = 237631697150017537

    channelAllowList = ["Statafel (4x)", "Achterzaal", "Keuken", "Bar", "Dunste stukje van de Discord", "Gamen",
                        "Spelletjestafel", "Minecraft", "Twitch", "One-night-werewolf", "Eettafel"]

    helpMessage = "This is the Gotcha bot. It records how long you have been in a voice channel. You can talk to me " \
                  "with the following commands:\n!gotcha: Get current times. \n!allowedChannels or !allowed: Print " \
                  "the voice channels where your time gets recorded.\n!ghelp: Print this help message. "

    def get_allowed_channels(self):
        return "Allowed channels: {}".format(", ".join(self.channelAllowList))

    def get_gotcha_status(self):
        return_string = "Below you can see how long you have been in a voice channel.\n\n"

        for user_id_new, time_present_new in self.totalTimesNewMethod.items():
            name = self.names_by_id[user_id_new]
            seconds = time_present_new.seconds
            mark = "X" if seconds > 3600 else " "
            minutes = (seconds // 60) % 60
            hours = seconds // 3600
            seconds = seconds % 60

            return_string += "[{}] {} has a time of {}h:{}m:{}s\n".format(mark, name, hours, minutes, seconds)

        return return_string

    @tasks.loop(seconds=check_every_seconds)
    async def add_minute_to_people_in_allowed_channels(self):
        now = datetime.now()
        allowed_time_period = isNowInTimePeriod(start_time, end_time, now.time())

        # Known bug: saturday  0 -> 2 doesnt count
        if allowed_time_period and 0 <= now.weekday() < 5:
            for person_id in self.currentlyInAllowedChannel:
                if person_id in self.totalTimesNewMethod:
                    self.totalTimesNewMethod[person_id] += timedelta(seconds=check_every_seconds)
                else:
                    self.totalTimesNewMethod[person_id] = timedelta(0)

    @tasks.loop(hours=1)
    async def backup_and_reset(self):
        ids_to_names = {self.names_by_id[k] for k in self.currentlyInAllowedChannel}
        times_with_names = {self.names_by_id[k]: v.seconds for k, v in self.totalTimesNewMethod.items()}

        logger.info("Current active people: %s, Current times: %s", ids_to_names, times_with_names)
        now = datetime.now()

        gotcha_status_string = self.get_gotcha_status()
        yesterday = now - timedelta(days=1)
        p = self.get_channel(self.privateChannelId)
        await p.send("Here are the times from {}. Goodnight!".format(yesterday.strftime('%A %d-%m')))
        await p.send(gotcha_status_string)

        if now.hour == 3:
            if 0 < now.weekday() < 6:
                gotcha_status_string = self.get_gotcha_status()
                yesterday = now - timedelta(days=1)

                c = self.get_channel(self.botChannelId)
                await c.send("Here are the times from {}. Goodnight!".format(yesterday.strftime('%A %d-%m')))
                await c.send(gotcha_status_string)

                p = self.get_channel(self.privateChannelId)
                await p.send("Here are the times from {}. Goodnight!".format(yesterday.strftime('%A %d-%m')))
                await p.send(gotcha_status_string)

            self.totalTimesNewMethod.clear()

    async def on_ready(self):
        logger.info(f'{client.user.name} has connected to Discord!')
        logger.info('Guilds: {}'.format(self.guilds))
        self.backup_and_reset.start()
        self.add_minute_to_people_in_allowed_channels.start()

    def allowedChannel(self, c):
        return c and c.name in self.channelAllowList

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content == "!gotcha":
            await message.channel.send("Current status:\n" + self.get_gotcha_status())
        elif message.content in ["!allowedChannels", "!allowedchannels", "!allowed"]:
            await message.channel.send(self.get_allowed_channels())
        elif message.content == "!ghelp":
            await message.channel.send(self.helpMessage)
        elif not message.guild:
            # private message
            logger.info(
                "Received PM from {}, {}, message: {}".format(message.author.id, message.author.name, message.content)
            )
            if message.author.id == self.botOwnerId:
                await message.channel.send("Giving the times to you")
                await message.channel.send(self.get_gotcha_status())

    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        logger.info(
            "id: {}, Member: {}, Channel: {} -> {}".format(member.id, member.display_name, before.channel, after.channel)
        )

        self.names_by_id[member.id] = member.display_name

        if self.allowedChannel(after.channel):
            if member.id not in self.currentlyInAllowedChannel:
                self.currentlyInAllowedChannel.add(member.id)

        if not self.allowedChannel(after.channel):
            if member.id in self.currentlyInAllowedChannel:
                self.currentlyInAllowedChannel.remove(member.id)


client = GotchaBot()
client.run(TOKEN)
