import datetime

import discord
from decouple import config
from discord.ext import commands

from database import Database
from utils import convert_to_readable_time

intents = discord.Intents.default()
intents.message_content = True

bot = Bot(command_prefix="!", intents=intents)
key = config("api_key")
bot.run(key)


bot.join_times = {}
bot.db = Database("discord.db")


@bot.event
async def on_ready():
    print(f"Logged on as {bot.user}!")


@bot.event
async def on_message(message):
    print(f"Message from {message.author}: {message.content}")
    await bot.process_commands(message)


@bot.event
async def on_voice_state_update(member, before, after):
    # If the member was connected to a voice channel before
    if before.channel is None and after.channel is not None:
        bot.join_times[member.id] = datetime.datetime.now()
        print(f"{member} has joined a voice channel.")

    elif before.channel is not None and after.channel is None:
        if member.id in bot.join_times:
            duration = datetime.datetime.now() - bot.join_times[member.id]
            duration = int(duration.total_seconds())

            if not bot.db.user_exists(member.id):
                print(f"Adding {member} to the database.")
                bot.db.insert_user(member.id, member.name)
            bot.db.insert_user_activity(
                member.id,
                duration,
                datetime.datetime.now().strftime("%Y-%m-%d"),
                bot.join_times[member.id].strftime("%H:%M:%S"),
                datetime.datetime.now().strftime("%H:%M:%S"),
            )
            del bot.join_times[member.id]
            print(
                f"@{member} has left a voice channel. They were in the channel for {duration} seconds."
            )


@bot.command()
async def uptime(ctx):
    member = ctx.author
    print(member, member.id)
    if bot.db.user_exists(member.id):
        duration = bot.db.sum_user_activity(member.id)
        cleaned_duration = convert_to_readable_time(duration)
        await ctx.reply(f"Total time spent in voice channels: {cleaned_duration}")
    else:
        await ctx.reply("You have not been in a voice channel yet.")


@bot.command()
async def leaderboard(ctx):
    leader_board = bot.db.get_leaderboard()

    embed = discord.Embed(title="Leaderboard", color=0x00FF00)
    for rank, (username, duration) in enumerate(leader_board, start=1):
        embed.add_field(
            name=f"#{rank} {username}",
            value=convert_to_readable_time(duration),
            inline=False,
        )
