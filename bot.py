import datetime

import discord
from decouple import config
from discord.ext import commands

from database import Database
from utils import convert_to_readable_time


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.join_times = {}
        self.db = Database("discord.db")

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    @commands.Cog.listener()
    async def on_message(self, message):
        print(f"Message from {message.author}: {message.content}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # If the member was connected to a voice channel before
        if before.channel is None and after.channel is not None:
            self.join_times[member.id] = datetime.datetime.now()
            print(f"{member} has joined a voice channel.")

        elif before.channel is not None and after.channel is None:
            if member.id in self.join_times:
                duration = datetime.datetime.now() - self.join_times[member.id]
                duration = int(duration.total_seconds())

                if not self.db.user_exists(member.id):
                    print(f"Adding {member} to the database.")
                    self.db.insert_user(member.id, member.name)
                self.db.insert_user_activity(
                    member.id,
                    duration,
                    datetime.datetime.now().strftime("%Y-%m-%d"),
                    self.join_times[member.id].strftime("%H:%M:%S"),
                    datetime.datetime.now().strftime("%H:%M:%S"),
                )
                del self.join_times[member.id]
                print(
                    f"@{member} has left a voice channel. They were in the channel for {duration} seconds."
                )

    @commands.command()
    async def uptime(self, ctx):
        member = ctx.author
        print(member, member.id)
        if self.db.user_exists(member.id):
            duration = self.db.sum_user_activity(member.id)
            cleaned_duration = convert_to_readable_time(duration)
            await ctx.reply(f"Total time spent in voice channels: {cleaned_duration}")
        else:
            await ctx.reply("You have not been in a voice channel yet.")

    @commands.command()
    async def leaderboard(self, ctx):
        leader_board = self.db.get_leaderboard()

        embed = discord.Embed(title="Leaderboard", color=0x00FF00)
        for rank, (username, duration) in enumerate(leader_board, start=1):
            embed.add_field(
                name=f"#{rank} {username}",
                value=convert_to_readable_time(duration),
                inline=False,
            )


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
key = config("api_key")
client.run(key)
