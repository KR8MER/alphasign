import requests
import logging
import re
from config import NWS_CAP_URL

def clean_description(description):
    # Remove any HTML tags
    description = re.sub('<[^<]+?>', '', description)
    # Replace newlines and multiple spaces with a single space
    description = re.sub('\s+', ' ', description)
    # Remove leading/trailing whitespace
    return description.strip()

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
