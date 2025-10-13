import requests
import logging

# Note: This uses the Pastebin API, which requires an API key for posting.
# The user will need to provide their own key in the config.json file.
PASTEBIN_API_KEY = None # To be loaded from config
PASTEBIN_POST_URL = "https://pastebin.com/api/api_post.php"
PASTEBIN_RAW_URL = "https://pastebin.com/raw/"

def post_to_pastebin(title, content):
    """
    Posts content to Pastebin and returns the URL of the new paste.
    """
    if not PASTEBIN_API_KEY:
        logging.error("Pastebin API key not configured. Cannot post.")
        return None

    params = {
        'api_dev_key': PASTEBIN_API_KEY,
        'api_option': 'paste',
        'api_paste_code': content,
        'api_paste_name': title,
        'api_paste_private': '1', # 0=public, 1=unlisted, 2=private
        'api_paste_expire_date': '10M', # Expire in 10 minutes
    }
    try:
        response = requests.post(PASTEBIN_POST_URL, data=params)
        if response.status_code == 200 and not response.text.startswith("Bad API request"):
            paste_url = response.text
            logging.info(f"Successfully posted to Pastebin: {paste_url}")
            return paste_url
        else:
            logging.error(f"Failed to post to Pastebin: {response.text}")
            return None
    except Exception as e:
        logging.error(f"Error posting to Pastebin: {e}")
        return None

def get_from_pastebin(paste_id):
    """
    Retrieves the raw content of a Pastebin paste.
    """
    url = PASTEBIN_RAW_URL + paste_id
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            logging.error(f"Failed to retrieve from Pastebin (ID: {paste_id}): Status {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error retrieving from Pastebin: {e}")
        return None