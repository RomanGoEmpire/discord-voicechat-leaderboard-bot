import discord
from discord.ext import commands

from utils import (
    convert_to_readable_time,
    get_or_create_role,
    roles,
    get_color_based_on_role
)


class Commands(commands.Cog):
    def __init__(self, bot, db):
        super().__init__()
        self.bot = bot
        self.db = db

    @commands.command()
    async def up(self, ctx):
        member = ctx.author
        
        if self.db.user_exists(member.id):
            duration = self.db.get_total_time(member.id)
            cleaned_duration = convert_to_readable_time(duration)
            await ctx.reply(f"Total time spent in voice channels: {cleaned_duration}")
        else:
            await ctx.reply("You have not been in a voice channel yet.")

    @commands.command()
    async def leaderboard(self, ctx):
        
        leader_board = self.db.leaderboard()

        embed = discord.Embed(title="Leaderboard", color=0x00FF00)
        embed.description = ""
        for rank, (user_id, duration) in enumerate(leader_board, start=1):
            member = await ctx.guild.fetch_member(user_id)
            if member:
                display_name = member.display_name
                if member == ctx.author:
                    display_name = f"__{display_name}__"
                if rank == 1:
                    line = f"🥇 #{rank} {display_name}: {convert_to_readable_time(duration)}"
                elif rank == 2:
                    line = f"🥈 #{rank} {display_name}: {convert_to_readable_time(duration)}"
                elif rank == 3:
                    line = f"🥉 #{rank} {display_name}: {convert_to_readable_time(duration)}"
                else:
                    line = (
                        f"#{rank} {display_name}: {convert_to_readable_time(duration)}"
                    )
                embed.description += line + "\n"
        await ctx.send(embed=embed)

    @commands.command()
    async def init(self, ctx):
        self.db.insert_channel(ctx.channel.id)
        
        embed = discord.Embed(title="Bot channel", color=0x00FF00)
        embed.description = f"This channel has been set as the bot channel."
        await ctx.send(embed=embed)
        


