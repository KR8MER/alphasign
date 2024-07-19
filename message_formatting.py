from config import GREEN, YELLOW, RED

def format_message(event, headline, description):
    message = "\x1B\x0C"  # Clear display
    
    # Determine color based on event type
    if "warning" in event.lower():
        color = RED
    elif "watch" in event.lower():
        color = YELLOW
    else:  # For advisories and other types
        color = GREEN
    
    # Format event type
    message += f"\x1B \x1Bb{color}\x1B\x1A3{event}"  # MIDDLE, HOLD mode
    
    # Format headline
    message += f"\x1B&\x1Bb{color}\x1B\x1A2{headline}"  # BOTTOM, HOLD mode
    
    # Format description
    message += f"\x1B&\x1Bb{color}\x1B\x1A1{description}"  # BOTTOM, HOLD mode
    
    # Set the message to rotate if it's too long to fit on the display
    message += "\x1Ba"  # ROTATE mode
    
    return message

def format_time_message():
    message = "\x1B\x0C"  # Clear display
    message += f"\x1B \x1Bb{GREEN}\x1B\x1A9\x13"  # MIDDLE, HOLD mode, Time
    message += f"\x1B&\x1Bb{GREEN}\x1B\x1A3\x0B\x38"  # BOTTOM, HOLD mode, Date
    return message

def set_sign_time_and_date(year, month, day, hour, minute):
    time_message = f"\x1B\x0C\x1B\x0F{hour:02d}{minute:02d}"
    date_message = f"\x1B\x0C\x1B\x0F{month:02d}{day:02d}{year:02d}"
    return time_message, date_message
