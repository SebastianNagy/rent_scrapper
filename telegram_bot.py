import os
import requests
import multiprocessing as mp
from dotenv import load_dotenv

from utils import log

load_dotenv()  # Load environment variables from .env file
TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')
API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/"
OFFSET = None  # Initialize offset for updates


def update_step(scrappers):
    """
    This function is called periodically to check for new updates from the Telegram Bot API.
    It fetches updates and processes them if any new messages are received.
    """
    try:
        updates = get_updates()
        for update in updates:
            if 'message' in update:
                message = update['message'].get('text', '')
                chat_id = update['message']['chat']['id']
                # log(f"Received message: {message} from chat ID: {chat_id}")
                
                if message.startswith('/status'):
                    log("Received /status command from chat")

                    status_updates = []
                    for scrapper in scrappers:
                        status_updates.append(scrapper.get_status_update())
                    send_telegram_message("\n".join(status_updates))

    except Exception as e:
        log(f"Error in bot_update_step: {e}")

def get_updates(timeout=30):
    global OFFSET
    """
    Fetches new updates from the Telegram Bot API using long polling.
    `offset` is used to tell the API which updates you have already processed.
    """
    params = {'timeout': timeout, 'offset': OFFSET}
    try:
        response = requests.get(API_URL + 'getUpdates', params=params, timeout=timeout + 5)
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()['result']

        # Update the offset to the last processed update ID + 1
        if result:
            OFFSET = result[-1]['update_id'] if OFFSET is None else result[-1]['update_id'] + 1
        return result
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching updates: {e}")
        return []


def send_telegram_message(message):
    """Sends a message to the specified Telegram chat using the bot."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log("Telegram token or chat ID is not set. Cannot send message.")
        return

    url = API_URL + "sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        # 'parse_mode': 'Markdown'
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            log(f"Failed to send Telegram message. Status code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        log(f"Error sending Telegram message: {e}")
