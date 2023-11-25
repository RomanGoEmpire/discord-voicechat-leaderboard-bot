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


async def setup(bot, db):
    await bot.add_cog(Commands(bot, db))
