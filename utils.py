from discord import Color
import discord 


roles = [
    {"time": 1, "name": "Terra Novice", "color": Color.from_rgb(30, 195,  33)},
    {"time": 10, "name": "Lunar Adept", "color": Color.from_rgb(182, 208, 220)},
    {"time": 50, "name": "Stellar Guardian", "color": Color.from_rgb(18, 103, 130)},
    {"time": 100, "name": "Nebula Seeker", "color": Color.from_rgb(101, 4, 139)},
    {"time": 500, "name": "Galactic Explorer", "color": Color.from_rgb(255, 183, 3)},
    {"time": 1000, "name": "Celestial Voyager", "color": Color.from_rgb(253, 158, 2)},
    {"time": 2000, "name": "Intergalactic Wayfarer", "color": Color.from_rgb(251, 133, 0)},
    {"time": 5000, "name": "Cosmic Master", "color": Color.from_rgb(187, 62, 3)},
    {"time": 7500, "name": "Multiversal Luminary", "color": Color.from_rgb(174, 32, 18)},
    {"time": 10000, "name": "Galaxial Overlord", "color": Color.from_rgb(170, 0, 6)},
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





def get_time_of_roles():
    return [role.get("time") for role in roles]

def get_roles_names():
    return [role.get("name") for role in roles]

def get_color_based_on_role(role_name):
    for role in roles:
        if role.get("name") == role_name:
            return role.get("color")
    raise ValueError(f"Role {role_name} not found in roles list.")


def get_current_and_next_role(member, total_time):
    
    roles_names = get_roles_names()
    times = get_time_of_roles()
    roles_names.reverse()
    times.reverse()
    
    current_role = None
    next_role = None
    
    
    for role in member.roles:
        if role.name in roles_names:
            current_role = role
            break
    
    for i, time in enumerate(times):
        if total_time >= time:
            next_role = roles_names[i]
            break
    return current_role, next_role


    
        