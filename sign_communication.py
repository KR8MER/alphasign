import socket
import time
import logging
from config import SIGN_IP, SIGN_PORT, SIGN_ADDRESS, MAX_RETRIES, RETRY_DELAY, VERIFY_DELAY
from alpha_codes import translate_alpha_codes

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
