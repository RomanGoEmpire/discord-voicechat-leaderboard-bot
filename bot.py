import datetime

import discord
from decouple import config
from discord.ext import commands

from commands import Commands
from database import Database
from utils import *

import os
import logging


def open_or_create_database():
    if not os.path.isfile("discord.db"):
        logging.info("Database not found. Creating new database.")
        db = Database("discord.db")
        db.create_user_table()
        db.create_user_activity_table()
        db.create_channel_table()
        db.close()
    else:
        logging.info("Database found.")
    db = Database("discord.db")
    return db


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.join_times = {}
        self.db = open_or_create_database()

    async def on_ready(self):
        await self.add_cog(Commands(self, self.db))
        logging.info(f"Ready: {self.user.name}(Bot) is ready.")

    async def on_message(self, message):
        message.content = message.content.lower()
        if message.author.bot:
            return
        logging.info(
            f"{message.author.name} ({message.channel.name}): {message.content}"
        )
        await self.process_commands(message)

    async def on_voice_state_update(self, member, before, after):
        # If member joins a voice channel
        if before.channel is None and after.channel is not None:
            self.join_times[member.id] = datetime.datetime.now()
            logging.info(f"Join: {member.display_name} has joined a voice channel.")
        # If member leaves a voice channel
        elif before.channel is not None and after.channel is None:
            if member.id in self.join_times:
                # calculate duration
                duration = datetime.datetime.now() - self.join_times[member.id]
                duration = int(duration.total_seconds())
                # add time to database
                self.add_user_activity_to_database(member, duration)
                logging.info(
                    f"Leave: {member.display_name} has left a voice channel after {convert_to_readable_time(duration)}"
                )
                # get total time and update role if necessary
                total_duration = self.db.get_total_time(member.id)
                await self.update_role_based_on_time(member, total_duration)
            else:
                logging.warning(
                    f"Leave: {member.display_name} has left a voice channel without joining one."
                )

    async def update_role_based_on_time(self, member, total_time):
        # convert to hours because that's what the roles are based on
        # total_time = total_time / 3600

        current_role, next_role = get_current_and_next_role(member, total_time)
        # if the roles are the same, do nothing
        if current_role and current_role.name == next_role:
            return
        logging.info(f"Lvl up: {member.display_name} has leveled up to {next_role}")
        # remove the current role
        if current_role:
            await member.remove_roles(current_role)
        # add the next role
        if next_role:
            role = await self.get_or_create_role(member, next_role)
            await member.add_roles(role)

        # send a message to the first Bot channel
        channel = self.db.get_channel()
        # get color based on role
        color = color_based_on_role(next_role)
        embed = discord.Embed(title=":tada: Level up!", color=color)
        embed.description = f"{member.mention} has leveled up to {next_role}"
        embed.set_thumbnail(url=member.display_avatar.url)
        if channel and len(channel) > 0:
            channel = member.guild.get_channel(channel[0])
            await channel.send(embed=embed)
        else:
            logging.warning("No bot channel found.")

    def add_user_activity_to_database(self, member, duration):
        if not self.db.user_exists(member.id):
            logging.info(f"New user {member.display_name} added to database.")
            bot.db.insert_user(member.id, member.name)
        self.db.insert_user_activity(
            member.id,
            duration,
            datetime.datetime.now().strftime("%Y-%m-%d"),
            self.join_times[member.id].strftime("%H:%M:%S"),
            datetime.datetime.now().strftime("%H:%M:%S"),
        )
        del self.join_times[member.id]

    def check_if_bot_channel(self, id):
        return self.db.get_channel() == id

    async def get_or_create_role(self, member, role_name):
        guild = member.guild
        role = discord.utils.get(guild.roles, name=role_name)
        # if the role doesn't exist, create it
        if not role:
            color = color_based_on_role(role_name)
            role = await guild.create_role(name=role_name, color=color, hoist=True)
            # move the role to the top
            await role.edit(position=len(guild.roles) - 2)

            # get time that was needed to unlock the role
            time = get_time_of_roles()[get_roles_names().index(role_name)]
            logging.info(f"Role: {role_name} created.")
            message = f"@everyone"
            embed = discord.Embed(title=":rocket: New role unlocked!", color=color)
            embed.description = f"{member.mention} is the first **{role_name}**!\n\nThis role was unlocked after being in voice channels for **{time} hours**."
            embed.set_thumbnail(url=member.display_avatar.url)
            channel = self.db.get_channel()
            if channel and len(channel) > 0:
                channel = member.guild.get_channel(channel[0])
                await channel.send(message, embed=embed)

            else:
                logging.warning("No bot channel found.")
        return role


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

intents = discord.Intents.default()
intents.message_content = True

bot = Bot(command_prefix="!", intents=intents, help_command=None)

key = config("api_key")
bot.run(key)
