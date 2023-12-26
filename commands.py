import discord
from discord.ext import commands
from discord import Color
from utils import *


class Commands(commands.Cog):
    def __init__(self, bot, db):
        super().__init__()
        self.bot = bot
        self.db = db

    @commands.command(aliases=["info", "command", "commands"])
    async def help(self, ctx):
        if not self.is_bot_channel(ctx):
            embed = discord.Embed(title=" Not a Bot Channel", color=Color.red())
            embed.description = "This channel is not a bot channel.\n\n"
            embed.add_field(
                name="List of bot channels",
                value="\n".join([f"<#{c}>" for c in self.db.get_channel()]),
            )
            embed.add_field(
                name="How to add a bot channel?",
                value="Type `!add` in the channel you want to add.",
                inline=False,
            )
            embed.add_field(
                name="How to remove a bot channel?",
                value="Type `!remove` in the channel you want to remove.",
                inline=False,
            )
            await ctx.send(embed=embed, delete_after=60)
            return

        embed = discord.Embed(title=":information_source: Info", color=Color.blue())
        embed.add_field(
            name="!up",
            value="Shows how much time you have spent in voice channels.",
            inline=False,
        )
        embed.add_field(
            name="!leaderboard",
            value="Shows the leaderboard of the server.",
            inline=False,
        )
        embed.add_field(
            name="!times",
            value="Shows the time needed to unlock the a role.",
            inline=False,
        )
        embed.add_field(
            name="!add",
            value="Adds the current channel as a bot channel.",
            inline=False,
        )
        embed.add_field(
            name="!remove",
            value="Removes the current channel as a bot channel.",
            inline=False,
        )
        embed.add_field(name="!help", value="Shows this message.", inline=False)
        await ctx.send(embed=embed)

    @commands.command(aliases=["uptime"])
    async def up(self, ctx):
        member = ctx.author

        if not self.is_bot_channel(ctx):
            return

        if self.db.user_exists(member.id):
            duration = self.db.get_total_time(member.id)
            cleaned_duration = convert_to_readable_time(duration)

            # get current role
            current_role, next_role = get_current_and_next_role(member, duration)
            color = color_based_on_role(next_role)

            embed = discord.Embed(title=":stopwatch: Total time", color=color)
            embed.description = (
                f"You have spent **{cleaned_duration}** in voice channels."
            )
            embed.add_field(name="Current Role", value=current_role)
            embed.set_footer(
                text="You can see the leaderboard with the !leaderboard command."
            )
            embed.set_thumbnail(url=member.display_avatar.url)
            await ctx.reply(embed=embed)

        else:
            embed = discord.Embed(title=":stopwatch: Total time", color=Color.red())
            embed.description = f"You have not spent any time in voice channels yet."
            embed.set_footer(
                text="You can see the leaderboard with the !leaderboard command."
            )
            await ctx.reply(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        if not self.is_bot_channel(ctx):
            return

        leader_board = self.db.leaderboard()

        embed = discord.Embed(title=":trophy: Leaderboard", color=Color.gold())
        embed.description = (
            "The leaderboard shows the total time spent in voice channels.\n\n"
        )

        top_3 = ""
        others = ""
        for rank, (user_id, duration) in enumerate(leader_board, start=1):
            member = await ctx.guild.fetch_member(user_id)
            if member:
                display_name = member.display_name
                role, _ = get_current_and_next_role(member, duration)
                if member == ctx.author:
                    display_name = f"**__{display_name}__**({role})"
                match rank:
                    case 1:
                        line = f"🥇{display_name}: {convert_to_readable_time(duration)}"
                    case 2:
                        line = f"🥈{display_name}: {convert_to_readable_time(duration)}"
                    case 3:
                        line = f"🥉{display_name}: {convert_to_readable_time(duration)}"
                    case _:
                        line = f"**#{rank}** {display_name}: {convert_to_readable_time(duration)}"
                        others += line + "\n"
                        continue
                top_3 += line + "\n"

        embed.add_field(name="Top 3", value=top_3, inline=False)
        embed.add_field(name="Others", value=others, inline=False)
        await ctx.reply(embed=embed)

    @commands.command()
    async def times(self, ctx):
        if not self.is_bot_channel(ctx):
            return

        # get the highest role
        highest_role = ctx.author.roles[1].name
        roles = get_roles_names()
        time = get_time_of_roles()

        embed = discord.Embed(title=":alarm_clock: Times", color=Color.blue())
        embed.description = (
            "The Timeboard shows the time needed to unlock the next role.\n\n"
        )

        # go through all roles and add them to the embed. Stop when the highest role is found
        is_highest_role = False
        for role in roles:
            if is_highest_role:
                break
            if role == highest_role:
                is_highest_role = True
                embed.add_field(
                    name=f"**{role}**",
                    value=f"**{convert_to_readable_time(time[roles.index(role)])}**",
                    inline=False,
                )

        await ctx.send(embed=embed)

        # get all

    @commands.command()
    async def add(self, ctx):
        await self.verify_admin(ctx)

        if ctx.channel.id in self.db.get_channel():
            embed = discord.Embed(title="Error", color=Color.red())
            embed.description = f"This channel is already a bot channel."
            await ctx.send(embed=embed)
            return
        self.db.insert_channel(ctx.channel.id)

        embed = discord.Embed(title="Added bot channel", color=Color.green())
        embed.description = f"This channel is now a bot channel."
        embed.set_footer(
            text="You can remove it again with the !remove_channel command."
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=["delete"])
    async def remove(self, ctx):
        await self.verify_admin(ctx)
        if ctx.channel.id not in self.db.get_channel():
            embed = discord.Embed(title="Error", color=Color.red())
            embed.description = f"This channel is not a bot channel."
            await ctx.send(embed=embed)
            return
        self.db.delete_channel(ctx.channel.id)

        embed = discord.Embed(title="Removed bot channel", color=Color.green())
        embed.description = f"This channel is no longer a bot channel."
        embed.set_footer(text="You can add it again with the !add_channel command.")
        await ctx.send(embed=embed)

    @commands.command(aliases=["channels"])
    async def channel(self, ctx):
        channels = self.db.get_channel()
        if len(channels) == 0:
            embed = discord.Embed(title="Error", color=Color.red())
            embed.description = f"There are no bot channels."
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title="Bot channels", color=Color.blue())
        embed.description = f"Here is a list of all bot channels."
        embed.add_field(name="Channels", value="\n".join([f"<#{c}>" for c in channels]))
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(title="Error", color=Color.red())
            embed.description = f"Command not found. Use `!help` to see all commands."
            await ctx.reply(embed=embed)

    def is_bot_channel(self, ctx):
        return ctx.channel.id in self.bot.db.get_channel()

    async def verify_admin(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            embed = discord.Embed(title="Error", color=Color.red())
            embed.description = f"You need to be an administrator to use this command."
            await ctx.send(embed=embed)
            return False
        return True
