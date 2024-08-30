import os
from datetime import datetime


import discord
from discord.channel import TextChannel
from discord.client import Client
from discord.colour import Color
from discord.member import Member, VoiceState
from discord.message import Message
from discord.role import Role
from dotenv import load_dotenv
from icecream import ic
from surrealdb import Surreal

ROLES = {
    1: {"name": "Villager", "duration": 1, "color": "#8B4513"},
    2: {"name": "Farmer", "duration": 2, "color": "#228B22"},
    3: {"name": "Merchant", "duration": 4, "color": "#CD853F"},
    4: {"name": "Blacksmith", "duration": 8, "color": "#939DA3"},
    5: {"name": "Apprentice", "duration": 16, "color": "#FFA07A"},
    6: {"name": "Archer", "duration": 32, "color": "#2E8B57"},
    7: {"name": "Swordsman", "duration": 64, "color": "#A52A2A"},
    8: {"name": "Paladin", "duration": 128, "color": "#F0E68C"},
    9: {"name": "Mystic Seer", "duration": 256, "color": "#9932CC"},
    10: {"name": "Dragon Rider", "duration": 512, "color": "#CC3300"},
    11: {"name": "High Sorcerer", "duration": 1024, "color": "#663399"},
    12: {"name": "Eternal Guardian", "duration": 2048, "color": "#FFD700"},
}


load_dotenv()

intents = discord.Intents.all()
intents.message_content = True

client: Client = discord.Client(intents=intents)


db: Surreal
members_in_voice: dict = {}
bot_channel_id = os.getenv("BOT_CHANNEL_ID")

bot_channel = None


async def send_message_to_admin(message: str) -> None:
    admin_id = os.getenv("ADMIN_ID")
    assert admin_id and admin_id.isdigit(), "No admin id found"
    user = await client.fetch_user(int(admin_id))
    await user.send(message)


@client.event
async def on_ready():
    global db

    url = os.getenv("SURREAL_URL")
    assert url, "No SURREAL_URL found"

    db = Surreal(url)
    await db.connect()

    username = os.getenv("SURREAL_USERNAME")
    password = os.getenv("SURREAL_PASSWORD")
    namespace = os.getenv("SURREAL_NS")
    database = os.getenv("SURREAL_DB")

    assert username, "No SURREAL_USERNAME found"
    assert password, "No SURREAL_PASSWORD found"
    assert database, "No SURREAL_DB found"
    assert namespace, "No SURREAL_NS found"
    await db.signin({"user": username, "pass": password})
    await db.use(namespace, database)

    global bot_channel
    assert bot_channel_id
    assert bot_channel_id.isdigit()
    bot_channel = client.get_channel(int(bot_channel_id))
    ic("ready")


@client.event
async def on_message(message: Message):
    bot_is_author = message.author == client.user
    message_in_bot_channel = message.channel == bot_channel
    is_command = message.content.startswith("!")
    if bot_is_author or not message_in_bot_channel or not is_command:
        return
    if message.content.strip() == "!leaderboard":
        await send_leaderboard(message)


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    # joined a channel
    if before.channel is None or before.afk:
        # handle error case
        if members_in_voice.get(member.id):
            await send_message_to_admin(
                f"{member.id,member.display_name} joined channel without joining"
            )
        members_in_voice[member.id] = datetime.now()

    # leave channel
    if before.channel and after.channel is None or after.afk:
        if members_in_voice.get(member.id) is None:
            await send_message_to_admin(
                f"{member.id,member.display_name} left channel without joining"
            )
            return
        await handle_leave_channel(member)


async def send_leaderboard(message: Message) -> None:
    members = await db.query(
        """
        SELECT member.*, math::sum(duration) AS duration
        FROM history
        GROUP BY member.*;
        """
    )

    members = members[0]["result"]

    leaderboard = "**🚀 Leaderboard**\n"
    for i, m in enumerate(members):
        duration = formatted_duration(m["duration"])
        leaderboard += f"{i + 1}: {m["member"]["name"]} - {duration}"
    await bot_channel.send(leaderboard)


def formatted_duration(duration: int) -> str:
    # day, hour, minute
    durations = [86400, 3600, 60]

    total = [0, 0, 0, 0]
    time_strings = ["day", "hour", "minute", "second"]

    for i, o in enumerate(durations):
        while duration >= o:
            total[i] += 1
            duration -= o

    total[-1] = duration

    formatted = ""
    for i, t_string in enumerate(time_strings):
        if total[i] > 0:
            formatted += f"{total[i]} {t_string}"
            formatted += "s " if total[i] > 1 else " "
    return formatted


async def handle_leave_channel(member: Member):
    db_member_id = f"member:{member.id}"
    db_member = await db.select(db_member_id)

    if not db_member:
        await db.create(db_member_id, {"name": member.display_name})

    db_member = await db.select(db_member_id)
    assert isinstance(db_member, dict), "member is not a list"

    await add_history(member)
    highest_rank = await get_highest_rank()
    next_rank = await possible_db_rankup(member, db_member, db_member_id)

    if next_rank:
        new_color = Color.from_str(ROLES[next_rank]["color"])

        await send_level_up_message(member, next_rank, highest_rank, new_color)

        role, last_role = await create_or_get_role(member, next_rank, new_color)
        await member.add_roles(role)
        if last_role:
            await member.remove_roles(last_role)


async def add_history(member: Member) -> None:
    join_time = members_in_voice[member.id]
    leave_time = datetime.now()
    duration: int = round((leave_time - members_in_voice[member.id]).total_seconds())

    del members_in_voice[member.id]

    await db.create(
        "history",
        {
            "member": f"member:{member.id}",
            "join_time": format_datetime(join_time),
            "leave_time": format_datetime(leave_time),
            "duration": duration,
        },
    )


async def get_highest_rank() -> int:
    highest_rank = await db.query(
        """
        SELECT *
        FROM member
        ORDER BY rank DESC
        LIMIT 1
        """
    )

    return highest_rank[0]["result"][0].get("rank", 0)


async def possible_db_rankup(
    member: Member, db_member: dict, db_member_id: str
) -> int | None:
    current_rank = db_member["rank"]
    next_rank = current_rank + 1

    if len(ROLES) == next_rank:
        return

    summed_duration = await db.query(
        f"""
        SELECT member, math::sum(duration) AS summed_duration
        FROM history
        WHERE member = {db_member_id}
        GROUP BY member;
        """
    )
    summed_duration = summed_duration[0]["result"][0]["summed_duration"]

    duration_next_rank = ROLES[next_rank]["duration"] * 3600
    if summed_duration >= duration_next_rank:
        await db.query(f"UPDATE {db_member_id} SET rank+=1")
        return next_rank


async def send_level_up_message(
    member: Member, next_rank: int, highest_rank, color: Color
) -> None:
    embed = discord.Embed(title=":tada: Level up!", color=color)

    if next_rank > highest_rank:
        embed.description = f"@everyone\n{member.mention} is the first one to level up to {ROLES[next_rank]["name"]}!!!\nThis person spend more than {ROLES[next_rank]["duration"]} hours in Voice!"
    else:
        embed.description = f"{member.mention} leveled up to {ROLES[next_rank]["name"]}"

    embed.set_thumbnail(url=member.display_avatar.url)
    await bot_channel.send(embed=embed)


async def create_or_get_role(
    member: Member, new_rank: int, color: Color
) -> tuple[Role, Role]:
    guild = member.guild
    role_name = ROLES[new_rank]["name"]
    new_color = Color.from_str(ROLES[new_rank]["color"])
    role = discord.utils.get(guild.roles, name=role_name)
    last_role = discord.utils.get(guild.roles, name=ROLES[new_rank - 1]["name"])
    if not role:
        role = await guild.create_role(name=role_name, color=new_color, hoist=True)
    return role, last_role


def format_datetime(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat() + "Z"


# start of app
api_key = os.getenv("API_KEY")
assert api_key, "could not read API_KEY"

client.run(api_key)
