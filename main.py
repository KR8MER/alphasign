import time
import logging
import signal
import sys
from config import POLL_INTERVAL
from sign_communication import send_to_sign, verify_message
from message_formatting import format_message, format_time_message
from alert_manager import get_active_alert

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
