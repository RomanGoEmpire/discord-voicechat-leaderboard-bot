import discord
import discord.ext.commands as commands
from discord import app_commands, Interaction, Color


class Leaderboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Get the bot's ping")
    async def ping(self, ctx: Interaction):
        ping = self.bot.latency * 1000
        await ctx.response.send_message(f"Ping is {ping:.2f}ms")

    @app_commands.command(name="leaderboard", description="Get the leaderboard")
    async def leaderboard(self, ctx: Interaction):
        await ctx.response.send_message("Leaderboard")

    @app_commands.command(
        name="hoursneeded",
        description="Get the amount of hours needed to reach a certain level",
    )
    async def times(self, ctx: Interaction):
        await ctx.response.send_message("Times")

    @app_commands.command(name="stats", description="Get a user's stats")
    @app_commands.describe(member="The member to get the stats for")
    async def stats(self, ctx: Interaction, member: discord.Member = None):
        if not member:
            member = ctx.user.name
        await ctx.response.send_message(f"Stats for {member}")

    @app_commands.command(name="up", description="Get the bot's uptime")
    async def up(self, ctx: Interaction):
        await ctx.response.send_message("Uptime")


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
