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
from modules.osint.database import initialize_database
from modules.osint.media_processor import process_image, process_document
import sqlite3
from modules.osint.database import DB_FILE
from modules.osint.attack_suggestor import suggest_attacks
from modules.osint.facial_recognition import process_faces
from modules.osint.reporting import generate_report
from modules.osint.ai_analyzer import analyze_with_ai

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
    print("  osint             - Access the OSINT profiler")
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
            elif command == "osint":
                handle_osint(args)
            else:
                print(f"Unknown command: {command}")

        except KeyboardInterrupt:
            print("\nUse 'exit' to leave the shell.")
        except Exception as e:
            logging.error(f"An error occurred in the shell: {e}")

def handle_osint(args):
    """Handles the 'osint' command and its subcommands using argparse."""
    parser = argparse.ArgumentParser(description="OSINT Profiler", prog="osint")
    subparsers = parser.add_subparsers(dest="subcommand", help="Available commands")

    # create-folder
    parser_folder = subparsers.add_parser("create-folder", help="Create a new folder for targets")
    parser_folder.add_argument("name", help="The name of the folder")

    # add-target
    parser_target = subparsers.add_parser("add-target", help="Add a new target")
    parser_target.add_argument("name", help="The name of the target")
    parser_target.add_argument("-d", "--description", help="A description for the target")
    parser_target.add_argument("-f", "--folder", help="The folder to add the target to")

    # add-media
    parser_media = subparsers.add_parser("add-media", help="Add a media file to a target")
    parser_media.add_argument("target", help="The name of the target")
    parser_media.add_argument("path", help="The path to the media file")

    # suggest-attacks
    parser_suggest = subparsers.add_parser("suggest-attacks", help="Suggest attack vectors for a target")
    parser_suggest.add_argument("target", help="The name of the target")

    # process-faces
    parser_faces = subparsers.add_parser("process-faces", help="Process media for facial recognition")
    parser_faces.add_argument("target", help="The name of the target")

    # export-report
    parser_report = subparsers.add_parser("export-report", help="Generate an HTML report for a target")
    parser_report.add_argument("target", help="The name of the target")

    try:
        parsed_args = parser.parse_args(args)
        if not parsed_args.subcommand:
            parser.print_help()
            return
    except SystemExit:
        # argparse throws SystemExit on --help or error, so we catch it to prevent the shell from exiting
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        if parsed_args.subcommand == "create-folder":
            cursor.execute("INSERT INTO folders (name) VALUES (?)", (parsed_args.name,))
            conn.commit()
            logger.info(f"Folder '{parsed_args.name}' created successfully.")

        elif parsed_args.subcommand == "add-target":
            folder_id = None
            if parsed_args.folder:
                cursor.execute("SELECT id FROM folders WHERE name = ?", (parsed_args.folder,))
                folder_row = cursor.fetchone()
                if not folder_row:
                    logger.error(f"Folder '{parsed_args.folder}' not found.")
                    return
                folder_id = folder_row[0]

            cursor.execute("INSERT INTO targets (name, description, folder_id) VALUES (?, ?, ?)",
                           (parsed_args.name, parsed_args.description, folder_id))
            conn.commit()
            logger.info(f"Target '{parsed_args.name}' added successfully.")

        elif parsed_args.subcommand == "add-media":
            cursor.execute("SELECT id FROM targets WHERE name = ?", (parsed_args.target,))
            target_row = cursor.fetchone()
            if not target_row:
                logger.error(f"Target '{parsed_args.target}' not found.")
                return

            target_id = target_row[0]
            file_path = parsed_args.path
            file_type = "image" if file_path.lower().endswith(('.png', '.jpg', '.jpeg')) else "document"
            metadata = process_image(file_path) if file_type == "image" else process_document(file_path)

            cursor.execute("INSERT INTO media (target_id, file_path, type) VALUES (?, ?, ?)",
                           (target_id, file_path, file_type))
            media_id = cursor.lastrowid

            for key, value in metadata.items():
                cursor.execute("INSERT INTO metadata (media_id, key, value) VALUES (?, ?, ?)",
                               (media_id, key, value))
            conn.commit()
            logger.info(f"Media '{file_path}' added to target '{parsed_args.target}'.")

        elif parsed_args.subcommand == "suggest-attacks":
            target_name = parsed_args.target
            target_data = {}
            cursor.execute("SELECT id FROM targets WHERE name = ?", (target_name,))
            target_row = cursor.fetchone()
            if not target_row:
                logger.error(f"Target '{target_name}' not found.")
                return

            target_id = target_row[0]

            cursor.execute("SELECT m.key, m.value FROM metadata m JOIN media ON m.media_id = media.id WHERE media.target_id = ?", (target_id,))
            metadata_rows = cursor.fetchall()
            target_data["metadata"] = [f"{key}: {value}" for key, value in metadata_rows]

            cursor.execute("SELECT COUNT(id) FROM faces WHERE target_id = ?", (target_id,))
            face_count = cursor.fetchone()[0]
            target_data["face_count"] = face_count

            suggestions = analyze_with_ai(target_data)
            print(f"\n--- AI-Powered Attack Suggestions for {target_name} ---")
            if suggestions:
                for s in suggestions:
                    print(f"  - {s}")
            else:
                print("  Could not generate suggestions. Check API key and data.")
            print("\n")

        elif parsed_args.subcommand == "process-faces":
            process_faces(parsed_args.target, conn)

        elif parsed_args.subcommand == "export-report":
            generate_report(parsed_args.target, conn)

    except sqlite3.IntegrityError as e:
        logger.error(f"Database integrity error: {e}")
    except sqlite3.Error as e:
        logger.error(f"Database error in command '{parsed_args.subcommand}': {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    initialize_database()
    main()