import datetime

import discord
from decouple import config

from database import Database


class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.join_times = {}
        self.db = Database("discord.db")

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        print(f"Message from {message.author}: {message.content}")

    async def on_user_update(self, before, after):
        # before username
        before_username = before.guild.fetch_member(before.id).display_name
        # after username
        after_username = after.guild.fetch_member(after.id).display_name
        if before_username != after_username:
            print(f"Username changed from {before_username} to {after_username}")
            self.db.change_username(before.id, after_username)

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
                    f"{member} has left a voice channel. They were in the channel for {duration} seconds."
                )


intents = discord.Intents.default()
intents.message_content = True

client = Bot(intents=intents)
key = config("api_key")
client.run(key)
