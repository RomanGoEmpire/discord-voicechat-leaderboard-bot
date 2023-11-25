from discord import Color
import discord 


roles = [
    {"time": 1, "name": "Cloud Chaser", "color": Color.from_rgb(240, 248, 255)},
    {"time": 10, "name": "Sky Explorer", "color": Color.from_rgb(173, 216, 230)},
    {"time": 50, "name": "Star Gazer", "color": Color.from_rgb(255, 215, 0)},
    {"time": 100, "name": "Moon Walker", "color": Color.from_rgb(255, 250, 205)},
    {"time": 500, "name": "Astral Voyager", "color": Color.from_rgb(255, 255, 0)},
    {"time": 1000, "name": "Galactic Nomad", "color": Color.from_rgb(144, 238, 144)},
    {"time": 2000, "name": "Celestial Navigator", "color": Color.from_rgb(173, 216, 230)},
    {"time": 5000, "name": "Time Traveler", "color": Color.from_rgb(255, 99, 71)},
    {"time": 7500, "name": "Eternal Skyfarer", "color": Color.from_rgb(255, 215, 0)},
    {"time": 10000, "name": "Supernova Sage", "color": Color.from_rgb(178, 34, 34)},
]

def convert_to_readable_time(seconds):
    # display days, hours, minutes, seconds but start from the largest that is not 0
    days = seconds // (24 * 3600)
    seconds %= 24 * 3600
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    time_string = ""
    if days == 1:
        time_string += "1 day, "
    elif days > 1:
        time_string += f"{days} days, "

    if hours == 1:
        time_string += "1 hour, "
    elif hours > 1:
        time_string += f"{hours} hours, "

    if minutes == 1:
        time_string += "1 minute, "
    elif minutes > 1:
        time_string += f"{minutes} minutes, "

    if seconds == 1:
        time_string += "1 second"
    else:
        time_string += f"{seconds} seconds"
    return time_string


async def get_or_create_role(guild, role_name):
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        color = get_color_based_on_role(role_name)
        role = await guild.create_role(name=role_name, color=color, hoist=True)
    return role


def get_time_of_roles():
    return [role.get("time") for role in roles]

def get_roles_names():
    return [role.get("name") for role in roles]

def get_color_based_on_role(role_name):
    for role in roles:
        if role.get("name") == role_name:
            return role.get("color")
    raise ValueError(f"Role {role_name} not found in roles list.")


