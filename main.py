import os
from datetime import datetime, timedelta

import discord
from discord.channel import TextChannel
from discord.client import Client
from discord.colour import Color, Colour
from discord.member import Member, VoiceState
from discord.mentions import AllowedMentions
from discord.message import Message

from discord.role import Role
from icecream import ic
from dotenv import load_dotenv

from surrealdb import Surreal


ROLES = {
    0: {"name": "Villager", "duration": 1, "color": "#8B4513"},
    1: {"name": "Farmer", "duration": 2, "color": "#228B22"},
    2: {"name": "Merchant", "duration": 4, "color": "#228B22"},
    3: {"name": "Blacksmith", "duration": 8, "color": "#939DA3"},
    4: {"name": "Apprentice", "duration": 16, "color": "#FFA07A"},
    5: {"name": "Archer", "duration": 32, "color": "#2E8B57"},
    6: {"name": "Swordsman", "duration": 64, "color": "#A52A2A"},
    7: {"name": "Paladin", "duration": 128, "color": "#F0E68C"},
    8: {"name": "Mystic Seer", "duration": 256, "color": "#9932CC"},
    9: {"name": "Dragon Rider", "duration": 512, "color": "#CC3300"},
    10: {"name": "High Sorcerer", "duration": 1024, "color": "#663399"},
    11: {"name": "Eternal Guardian", "duration": 2048, "color": "#FFD700"},
}


load_dotenv()

intents = discord.Intents.all()
intents.message_content = True

client: Client = discord.Client(intents=intents)


db: Surreal
members_in_voice: dict = {}
bot_channel_id = 1273373486957727919
bot_channel: TextChannel


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
    await db.use("test", "test")

    username = os.getenv("SURREAL_USERNAME")
    assert username, "No SURREAL_USERNAME found"

    password = os.getenv("SURREAL_PASSWORD")
    assert password, "No SURREAL_PASSWORD found"

    db_name = os.getenv("SURREAL_DB")
    assert db_name, "No SURREAL_DB found"

    ns = os.getenv("SURREAL_NS")
    assert ns, "No SURREAL_NS found"

    await db.signin({"user": username, "pass": password})
    await db.use(db_name, ns)

    global bot_channel
    bot_channel = client.get_channel(bot_channel_id)


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    # joined a channel
    if before.channel is None:
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


async def handle_leave_channel(member: Member):
    db_member_id = f"member:{member.id}"
    db_member = await db.select(db_member_id)

    if not db_member:
        ic(f"new member: {member.display_name}")
        await db.create(db_member_id)

    db_member = await db.select(db_member_id)
    assert type(db_member) == dict, "member is not a list"

    await add_history(member)
    highest_rank = await get_highest_rank()
    next_rank = await possible_db_rankup(member, db_member, db_member_id)

    if next_rank:
        new_color = Color.from_str(ROLES[next_rank]["color"])

        await send_level_up_message(member, next_rank, highest_rank, new_color)

        role, last_role = await create_or_get_role(member, next_rank, new_color)
        await member.add_roles(role)
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
    return highest_rank[0]["result"][0]["rank"]


async def possible_db_rankup(
    member: Member, db_member: dict, db_member_id: str
) -> int | None:
    current_rank = db_member["rank"]

    is_highest_rank = len(ROLES) == current_rank + 1
    if is_highest_rank:
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

    next_rank = current_rank + 1
    duration_next_rank = ROLES[next_rank]["duration"]

    if summed_duration >= duration_next_rank:
        await db.query(f"UPDATE {db_member_id} SET rank+=1")
        return next_rank


async def send_level_up_message(
    member: Member, next_rank: int, highest_rank, color: Color
) -> None:
    embed = discord.Embed(title=":tada: Level up!", color=color)

    if next_rank > highest_rank:
        embed.description = f"@everyone\n{member.mention}was the first one to level up to {ROLES[next_rank]["name"]}"
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
        role = await guild.create_role(name=role_name, color=color, hoist=True)
        await role.edit(position=len(guild.roles) - 2)
    return role, last_role


def format_datetime(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat() + "Z"


# start of app
api_key = os.getenv("API_KEY")
assert api_key, "could not read API_KEY"

client.run(api_key)
