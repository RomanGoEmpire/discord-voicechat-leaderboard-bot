import os
import discord
import colorlog
import logging
import logging.handlers
from typing import override
from dotenv import load_dotenv
from discord.ext import commands


logger = logging.getLogger("discord")
logger.name = "leaderboard_bot"


class Bot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.join_times = {}
        self.db = None

    @override
    async def on_ready(self):
        logger.info(f"{self.user} is ready")
        await self.load_extension("cogs.base")
        try:
            synced = await self.tree.sync()
        except Exception as e:
            logger.error(f"Error syncing tree: {e}")

    @override
    async def on_message(self, message):
        if message.author.bot:
            return
        logger.info(f"{message.author} sent a message: {message.content}")
        message.content = message.content.lower()
        await self.process_commands(message)

    @override
    async def on_member_leave(self, member):
        logger.info(f"{member} left the server")


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True


help_command = commands.DefaultHelpCommand()
help_command.no_category = "Commands"
help_command.command_attrs["ping"] = "Pong!"

bot = Bot(command_prefix="/", intents=intents, help_command=help_command)

key = os.getenv("API_KEY")


# ! Use this in development
bot.run(key)


# ! Use this in production

# handler = logging.handlers.RotatingFileHandler(
#     filename="discord.log",
#     encoding="utf-8",
#     maxBytes=32 * 1024 * 1024,  # 32 MiB
#     backupCount=5,  # Rotate through 5 files
# )
# dt_fmt = "%Y-%m-%d %H:%M:%S"
# formatter = logging.Formatter(
#     "[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{"
# )
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# bot.run(key, log_handler=None)
