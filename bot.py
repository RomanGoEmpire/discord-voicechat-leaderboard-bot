import datetime

import discord
from decouple import config
from discord import Color
from discord.ext import commands

from commands import Commands
from database import Database

time_based_roles = {
    1: "Cloud Chaser",
    10: "Sky Explorer",
    50: "Star Gazer",
    100: "Moon Walker",
    500: "Astral Voyager",
    1000: "Galactic Nomad",
    2000: "Celestial Navigator",
    5000: "Time Traveler",
    7500: "Eternal Skyfarer",
    10000: "Supernova Sage",
}

role_colors = {
    "Cloud Chaser": Color.from_rgb(240, 248, 255),  # Alice Blue
    "Sky Explorer": Color.from_rgb(173, 216, 230),  # Light Blue
    "Star Gazer": Color.from_rgb(255, 215, 0),  # Gold
    "Moon Walker": Color.from_rgb(255, 250, 205),  # LemonChiffon
    "Astral Voyager": Color.from_rgb(255, 255, 0),  # Yellow
    "Galactic Nomad": Color.from_rgb(144, 238, 144),  # LightGreen
    "Celestial Navigator": Color.from_rgb(173, 216, 230),  # Light Blue
    "Time Traveler": Color.from_rgb(255, 99, 71),  # Tomato
    "Eternal Skyfarer": Color.from_rgb(255, 215, 0),  # Gold
    "Supernova Sage": Color.from_rgb(178, 34, 34),  # Fire Brick
}


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.join_times = {}
        self.db = Database("discord.db")

    async def on_ready(self):
        await self.add_cog(Commands(self, self.db))
        print(f"Logged on as {bot.user}!")

    async def on_message(self, message):
        print(f"Message from {message.author}: {message.content}")
        await self.process_commands(message)

    async def on_voice_state_update(self, member, before, after):
        # If the member was connected to a voice channel before
        if before.channel is None and after.channel is not None:
            bot.join_times[member.id] = datetime.datetime.now()
            print(f"{member} has joined a voice channel.")

        elif before.channel is not None and after.channel is None:
            if member.id in bot.join_times:
                duration = datetime.datetime.now() - bot.join_times[member.id]
                duration = int(duration.total_seconds())

                await self.add_user_activity_to_database(member, duration)
                await self.update_role_based_on_time(member, duration)

    async def add_user_activity_to_database(self, member, duration):
        if not self.db.user_exists(member.id):
            print(f"Adding {member} to the database.")
            bot.db.insert_user(member.id, member.name)
            self.db.insert_user_activity(
                member.id,
                duration,
                datetime.datetime.now().strftime("%Y-%m-%d"),
                bot.join_times[member.id].strftime("%H:%M:%S"),
                datetime.datetime.now().strftime("%H:%M:%S"),
            )
            del bot.join_times[member.id]
            print(
                f"@{member.guild.display_name} has left a voice channel. They were in the channel for {duration} seconds."
            )

    async def update_role_based_on_time(self, member, duration):
        # duration = duration // 3600
        for time, role in time_based_roles.items():
            if duration >= time:
                role = await self.get_or_create_role(member.guild, role)
                await member.add_roles(role)
                print(f"@{member.display_name} has been given the {role} role.")
                break

    async def get_or_create_role(self, guild, role_name):
        role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            color = colors[role_name]
            role = await guild.create_role(name=role_name, color=color, hoist=True)
        return role


intents = discord.Intents.default()
intents.message_content = True

bot = Bot(command_prefix="!", intents=intents)

key = config("api_key")
bot.run(key)
