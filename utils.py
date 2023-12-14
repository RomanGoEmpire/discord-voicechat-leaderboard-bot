from discord import Color
import discord


ROLES = [
    {"time": 1, "name": "Terra Novice", "color": Color.from_rgb(30, 195, 33)},
    {"time": 10, "name": "Lunar Adept", "color": Color.from_rgb(182, 208, 220)},
    {"time": 50, "name": "Stellar Guardian", "color": Color.from_rgb(18, 103, 130)},
    {"time": 100, "name": "Nebula Seeker", "color": Color.from_rgb(101, 4, 139)},
    {"time": 500, "name": "Galactic Explorer", "color": Color.from_rgb(255, 183, 3)},
    {"time": 1000, "name": "Celestial Voyager", "color": Color.from_rgb(253, 158, 2)},
    {
        "time": 2000,
        "name": "Intergalactic Wayfarer",
        "color": Color.from_rgb(251, 133, 0),
    },
    {"time": 5000, "name": "Cosmic Master", "color": Color.from_rgb(187, 62, 3)},
    {
        "time": 7500,
        "name": "Multiversal Luminary",
        "color": Color.from_rgb(174, 32, 18),
    },
    {"time": 10000, "name": "Galaxial Overlord", "color": Color.from_rgb(170, 0, 6)},
]


def convert_to_readable_time(seconds):
    # Define time units and their corresponding seconds
    time_units = [("day", 24 * 3600), ("hour", 3600), ("minute", 60), ("second", 1)]

    time_string = ""

    for unit, unit_seconds in time_units:
        if seconds >= unit_seconds:
            unit_count = seconds // unit_seconds
            seconds %= unit_seconds

            if unit_count == 1:
                time_string += f"{unit_count} {unit}, "
            elif unit_count > 1:
                time_string += f"{unit_count} {unit}s, "

    # Remove trailing comma and space
    time_string = time_string.rstrip(", ")

    return time_string


def get_time_of_roles() -> list[int]:
    return [role.get("time") for role in ROLES]


def get_roles_names() -> list[str]:
    return [role.get("name") for role in ROLES]


def color_based_on_role(role_name) -> Color:
    for role in ROLES:
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
