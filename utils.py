from discord import Color

time_based_roles = {
    1: "Cloud Chaser",
    10: "Sky Explorer",
    50: "Star Gazer",
    100: "Moon Walker",
    500: "Astral Voyager",
    1000: "Galactic Nomad",
    2000: "Celestial Navigator",
    5000: "Time Traveler",
    7500: "Eternal Skyfarer",
    10000: "Supernova Sage",
}

role_colors = {
    "Cloud Chaser": Color.from_rgb(240, 248, 255),  # Alice Blue
    "Sky Explorer": Color.from_rgb(173, 216, 230),  # Light Blue
    "Star Gazer": Color.from_rgb(255, 215, 0),  # Gold
    "Moon Walker": Color.from_rgb(255, 250, 205),  # LemonChiffon
    "Astral Voyager": Color.from_rgb(255, 255, 0),  # Yellow
    "Galactic Nomad": Color.from_rgb(144, 238, 144),  # LightGreen
    "Celestial Navigator": Color.from_rgb(173, 216, 230),  # Light Blue
    "Time Traveler": Color.from_rgb(255, 99, 71),  # Tomato
    "Eternal Skyfarer": Color.from_rgb(255, 215, 0),  # Gold
    "Supernova Sage": Color.from_rgb(178, 34, 34),  # Fire Brick
}


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
