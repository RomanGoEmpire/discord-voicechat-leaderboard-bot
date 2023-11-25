import datetime

import discord
from decouple import config
from discord.ext import commands

from commands import Commands
from database import Database
from utils import get_or_create_role, roles, get_time_of_roles, get_roles_names


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

                self.add_user_activity_to_database(member, duration)
                await self.update_role_based_on_time(member, duration)

    def add_user_activity_to_database(self, member, duration):
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
    
        times = get_time_of_roles()
        roles_names =get_roles_names()
        times.reverse()
        roles_names.reverse()
        
        # get current role 
        current_role = None
        for role in member.roles:
            if role.name in roles_names:
                current_role = role
                break
            
        # get next role
        next_role = None
        for i, time in enumerate(times):
            if duration >= time:
                next_role = roles_names[i]
                break
        
        # if the roles are the same, do nothing
        if current_role and current_role.name == next_role:
            return
        
        # add the next role
        if next_role:
            role = await get_or_create_role(member.guild, next_role)
            await member.add_roles(role)
            print(f"Added {role.name} to {member.name}")
        
            
        
        
        
        
        
        
        
            
        


intents = discord.Intents.default()
intents.message_content = True

bot = Bot(command_prefix="!", intents=intents)

key = config("api_key")
bot.run(key)
