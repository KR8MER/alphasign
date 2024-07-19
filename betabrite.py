import socket
import requests
import time
import logging
from datetime import datetime
import signal
import sys
import re

# Configuration
SIGN_IP = "192.168.2.250"
SIGN_PORT = 10001
SIGN_ADDRESS = "01"
NWS_CAP_URL = "https://api.weather.gov/alerts/active?zone=MDZ013"
POLL_INTERVAL = 60  # Seconds
VERIFY_DELAY = 2  # Seconds
MAX_RETRIES = 3
RETRY_DELAY = 5  # Seconds

# Color codes
GREEN = "\x1C2"
YELLOW = "\x1C8"
RED = "\x1C1"

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Alpha codes dictionary
ALPHA_CODES = {
    '\x00': '[NUL]', '\x01': '[SOH]', '\x02': '[STX]', '\x03': '[ETX]', '\x04': '[EOT]',
    '\x05': '[ENQ]', '\x06': '[ACK]', '\x07': '[BEL]', '\x08': '[BS]', '\x09': '[HT]',
    '\x0A': '[LF]', '\x0B': '[VT]', '\x0C': '[FF]', '\x0D': '[CR]', '\x0E': '[SO]',
    '\x0F': '[SI]', '\x10': '[DLE]', '\x11': '[DC1]', '\x12': '[DC2]', '\x13': '[DC3]',
    '\x14': '[DC4]', '\x15': '[NAK]', '\x16': '[SYN]', '\x17': '[ETB]', '\x18': '[CAN]',
    '\x19': '[EM]', '\x1A': '[SUB]', '\x1B': '[ESC]', '\x1C': '[FS]', '\x1D': '[GS]',
    '\x1E': '[RS]', '\x1F': '[US]',
    '\x1C1': '[RED]', '\x1C2': '[GREEN]', '\x1C3': '[AMBER]', '\x1C4': '[DIM RED]',
    '\x1C5': '[DIM GREEN]', '\x1C6': '[BROWN]', '\x1C7': '[ORANGE]', '\x1C8': '[YELLOW]',
    '\x1C9': '[RAINBOW1]', '\x1CA': '[RAINBOW2]', '\x1CB': '[COLOR MIX]', '\x1CC': '[AUTOCOLOR]',
    '\x1B"': '[TOP]', '\x1B ': '[MIDDLE]', '\x1B&': '[BOTTOM]', '\x1B0': '[FILL]',
    '\x1B\x1A1': '[5x5 FONT]', '\x1B\x1A2': '[5x7 FONT]', '\x1B\x1A3': '[7x6 FONT]',
    '\x1B\x1A4': '[7x11 FONT]', '\x1B\x1A5': '[7 SHADOW FONT]', '\x1B\x1A6': '[8x16 FONT]',
    '\x1B\x1A7': '[10x12 FONT]', '\x1B\x1A8': '[FULL FONT]',
    '\x1Ba': '[ROTATE]', '\x1Bb': '[HOLD]', '\x1Bc': '[FLASH]', '\x1Bd': '[RESERVED]',
    '\x1Be': '[ROLL UP]', '\x1Bf': '[ROLL DOWN]', '\x1Bg': '[ROLL LEFT]', '\x1Bh': '[ROLL RIGHT]',
    '\x1Bi': '[WIPE UP]', '\x1Bj': '[WIPE DOWN]', '\x1Bk': '[WIPE LEFT]', '\x1Bl': '[WIPE RIGHT]',
    '\x1Bm': '[SCROLL]', '\x1Bn': '[AUTOMODE]', '\x1Bo': '[ROLL IN]', '\x1Bp': '[ROLL OUT]',
    '\x1Bq': '[WIPE IN]', '\x1Br': '[WIPE OUT]', '\x1Bs': '[COMPRESSED ROTATE]',
    '\x1Bt': '[EXPLODE]', '\x1Bu': '[CLOCK]',
    '\x1Bn0': '[TWINKLE]', '\x1Bn1': '[SPARKLE]', '\x1Bn2': '[SNOW]', '\x1Bn3': '[INTERLOCK]',
    '\x1Bn4': '[SWITCH]', '\x1Bn5': '[SLIDE]', '\x1Bn6': '[SPRAY]', '\x1Bn7': '[STARBURST]',
    '\x1Bn8': '[WELCOME]', '\x1Bn9': '[SLOT MACHINE]', '\x1BnA': '[NEWS FLASH]',
    '\x1BnB': '[TRUMPET ANIMATION]', '\x1BnC': '[CYCLE COLORS]',
    '\x13': '[CALL TIME]', '\x0B8': '[CALL DATE]',
    '\x1D0': '[WIDE OFF]', '\x1D1': '[WIDE ON]', '\x1D2': '[DOUBLE WIDE ON]',
    '\x1D3': '[DOUBLE WIDE OFF]',
    '\x1E0': '[PROPORTIONAL]', '\x1E1': '[FIXED WIDTH]',
    '\x1B \x1Bb': '[MIDDLE-HOLD]',
    '\x1B&\x1Bb': '[BOTTOM-HOLD]',
    '\x1B \x1Bc': '[MIDDLE-FLASH]',
    '\x1B&\x1Bc': '[BOTTOM-FLASH]',
}

def translate_alpha_codes(message):
    translated = ""
    i = 0
    while i < len(message):
        if message[i:i+3] in ALPHA_CODES:
            translated += ALPHA_CODES[message[i:i+3]]
            i += 3
        elif message[i:i+2] in ALPHA_CODES:
            translated += ALPHA_CODES[message[i:i+2]]
            i += 2
        elif message[i] in ALPHA_CODES:
            translated += ALPHA_CODES[message[i]]
            i += 1
        else:
            translated += message[i]
            i += 1
    return translated

def calculate_checksum(data):
    return sum(data) & 0xFFFF

def construct_alpha_packet(command, text='', file_label='A'):
    packet = b"\x00\x00\x00\x00\x00"  # Five NULL bytes
    packet += b"\x01"  # SOH
    packet += b"x" + SIGN_ADDRESS.encode()  # Type Code "x" (78H) for the sign, Sign Address
    packet += b"\x02"  # STX
    packet += command.encode() + file_label.encode() + text.encode()
    packet += b"\x03"  # ETX
    checksum = calculate_checksum(packet[packet.index(b"\x02"):])
    packet += f"{checksum:04X}".encode()
    packet += b"\x04"  # EOT
    
    return packet

def communicate_with_sign(packet, expect_response=False):
    for attempt in range(MAX_RETRIES):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10)
                s.connect((SIGN_IP, SIGN_PORT))
                s.sendall(packet)
                if expect_response:
                    response = s.recv(1024)
                    return response
            return True
        except Exception as e:
            logging.error(f"Error communicating with sign (attempt {attempt + 1}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return None

def send_to_sign(message, file_label='A'):
    packet = construct_alpha_packet('A', message, file_label)
    result = communicate_with_sign(packet)
    if result:
        translated_message = translate_alpha_codes(message)
        logging.info(f"Sent to sign: {translated_message}")
        return True
    return False

def read_from_sign(file_label='A'):
    packet = construct_alpha_packet('B', file_label=file_label)
    response = communicate_with_sign(packet, expect_response=True)
    
    if response and len(response) > 33:  # Minimum valid response length
        try:
            null_bytes, soh, type_code, sign_address, stx, command_code, file_label, *rest = response.split(b'\x03', 1)[0].split(b'\x02')
            text_data = b'\x02'.join(rest)
            etx, checksum, eot = response.split(b'\x03', 1)[1].split(b'\x04')

            if (null_bytes.count(b'\x00') == 20 and
                soh == b'\x01' and
                type_code == b'0' and
                sign_address == b'00' and
                command_code == b'A' and
                eot == b''):
                
                calculated_checksum = calculate_checksum(stx + command_code + file_label + text_data + b'\x03')
                if f"{calculated_checksum:04X}".encode() == checksum:
                    content = text_data.decode('ascii', errors='ignore')
                    translated_content = translate_alpha_codes(content)
                    logging.info(f"Read from sign: {translated_content}")
                    return content
                else:
                    logging.error("Checksum verification failed.")
            else:
                logging.error("Invalid response structure.")
        except Exception as e:
            logging.error(f"Error parsing sign response: {e}")
    else:
        logging.error("Received an invalid response from the sign.")
    return None

def verify_message(sent_message, file_label='A'):
    time.sleep(VERIFY_DELAY)
    read_message = read_from_sign(file_label)
    if read_message:
        sent_stripped = ''.join(char for char in sent_message if ord(char) >= 32)
        read_stripped = ''.join(char for char in read_message if ord(char) >= 32)
        
        if sent_stripped in read_stripped:
            logging.info("Message verified successfully.")
            return True
        else:
            logging.error("Message verification failed. Sign content doesn't match sent message.")
            logging.debug(f"Sent (translated): {translate_alpha_codes(sent_message)}")
            logging.debug(f"Read (translated): {translate_alpha_codes(read_message)}")
            return False
    else:
        logging.error("Failed to verify message (couldn't read from sign).")
        return False

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
    
    if send_to_sign(time_message, file_label=' ') and send_to_sign(date_message, file_label=';'):
        logging.info(f"Set sign time to {hour:02d}:{minute:02d} and date to {month:02d}/{day:02d}/{year:02d}")
        return True
    else:
        logging.error("Failed to set sign time and date")
        return False

def clean_description(description):
    # Remove any HTML tags
    description = re.sub('<[^<]+?>', '', description)
    # Replace newlines and multiple spaces with a single space
    description = re.sub('\s+', ' ', description)
    # Remove leading/trailing whitespace
    description = description.strip()
    return description

def get_active_alert():
    try:
        response = requests.get(NWS_CAP_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data["features"]:
            alert = data["features"][0]["properties"]
            event = alert["event"]
            headline = clean_description(alert["headline"])
            description = clean_description(alert["description"])
            return event, headline, description
        else:
            return None, None, None
    except requests.Timeout:
        logging.error("Timeout error fetching NWS data")
        return None, None, None
    except requests.RequestException as e:
        logging.error(f"Error fetching NWS data: {e}")
        return None, None, None

def signal_handler(sig, frame):
    logging.info('Program terminated by user')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    current_alert = None
    while True:
        try:
            event, headline, description = get_active_alert()
            if description and description != current_alert:
                current_alert = description
                logging.info(f"New alert received: {event} - {headline}")
                
                message = format_message(event, headline, description)
                if send_to_sign(message) and verify_message(message):
                    logging.info("Alert sent and verified successfully.")
                else:
                    logging.error("Failed to send or verify alert. Will retry in the next cycle.")
            elif not description:
                if current_alert:
                    logging.info("Alert no longer active. Switching to time display.")
                    current_alert = None
                
                time_message = format_time_message()
                if send_to_sign(time_message) and verify_message(time_message):
                    logging.info("Time and date message sent and verified successfully.")
                else:
                    logging.error("Failed to send or verify time and date. Will retry in the next cycle.")
            else:
                logging.info("No change in active alert. Maintaining current display.")
            
            time.sleep(POLL_INTERVAL)
        except Exception as e:
            logging.error(f"Unexpected error in main loop: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
