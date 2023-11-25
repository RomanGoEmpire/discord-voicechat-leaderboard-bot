# This example requires the 'message_content' intent.

import discord
from decouple import config


class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        print(f"Message from {message.author}: {message.content}")

    async def on_voice_state_update(self, member, before, after):
        if before.channel is None and after.channel is not None:
            print(f"{member} has joined a voice channel.")
        elif before.channel is not None and after.channel is None:
            print(f"{member} has left a voice channel.")


intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
key = config["api-key"]
print(key)
client.run(key)
