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
