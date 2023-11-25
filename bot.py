# This example requires the 'message_content' intent.

import datetime

import discord
from decouple import config


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.join_times = {}

    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        print(f"Message from {message.author}: {message.content}")

    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            self.join_times[member.id] = datetime.datetime.now()
            print(f"{member} has joined a voice channel.")
        elif before.channel is not None and after.channel is None:
            if member.id in self.join_times:
                duration = datetime.datetime.now() - self.join_times[member.id]
                del self.join_times[member.id]
                print(
                    f"{member} has left a voice channel. They were in the channel for {duration.total_seconds()} seconds."
                )


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
key = config["api-key"]
print(key)
client.run(key)
