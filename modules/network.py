import requests
import logging

def send_to_server(url, data):
    """
    Sends data to a remote server via an HTTP POST request.
    """
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        logging.info(f"Data successfully sent to {url}. Server response: {response.text}")
        return True, response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send data to {url}: {e}")
        return False, str(e)

def send_to_telegram(bot_token, chat_id, message):
    """
    Sends a message to a Telegram chat using a bot.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logging.info("Message successfully sent to Telegram.")
        return True, response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send message to Telegram: {e}")
        return False, str(e)