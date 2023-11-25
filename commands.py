import discord
from discord.ext import commands

from utils import convert_to_readable_time


class Commands(commands.Cog):
    def __init__(self, bot, db):
        super().__init__()
        self.bot = bot
        self.db = db

    @commands.command()
    async def uptime(self, ctx):
        member = ctx.author
        if self.db.user_exists(member.id):
            duration = self.db.sum_user_activity(member.id)
            cleaned_duration = convert_to_readable_time(duration)
            await ctx.reply(f"Total time spent in voice channels: {cleaned_duration}")
        else:
            await ctx.reply("You have not been in a voice channel yet.")

    @commands.command()
    async def leaderboard(self, ctx):
        leader_board = self.db.leaderboard()

        embed = discord.Embed(title="Leaderboard", color=0x00FF00)
        for rank, (user_id, duration) in enumerate(leader_board, start=1):
            member = ctx.guild.get_member(user_id)
            if member:
                display_name = member.display_name
                line = f"#{rank} {display_name}: {convert_to_readable_time(duration)}"
                embed.description += line + "\n"
        await ctx.reply(embed=embed)
