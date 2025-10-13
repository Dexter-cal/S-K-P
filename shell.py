import readline
import logging
from modules.target_manager import list_targets, set_target_label, add_target, get_target
from modules.scanner import intelligent_scan

from modules.steganography import encode_image, decode_image

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
    print("  exit              - Exit the shell")

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
    # Add more module options here
    else:
        print("This module has no configurable options.")


def main_loop():
    """The main interactive loop for the shell."""
    global current_target, prompt

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

                    if current_module:
                        module_options[option_name] = option_value
                        print(f"{option_name} => {option_value}")
                    else:
                        # Handle global set, like setting a target
                        if option_name == 'target':
                            target_id = option_value
                            target_info = get_target(target_id)
                            if target_info:
                                current_target = target_info
                                ip_for_prompt = [ip for ip, data in list_targets().items() if data == target_info][0]
                                module_options['rhost'] = ip_for_prompt # Automatically set RHOST
                                print(f"Current target set to: {ip_for_prompt}")
                            else:
                                print(f"Target not found: {target_id}")
                        else:
                            print("No module selected. Use 'use <module>' first.")
                else:
                    print("Usage: set <option_name> <value>")
            elif command == "info":
                if current_target:
                    print("\n--- Target Information ---")
                    # Find the IP if we only have the label
                    ip_addr = [ip for ip, data in list_targets().items() if data == current_target][0]
                    print(f"  IP: {ip_addr}")
                    for key, value in current_target.items():
                        print(f"  {key.capitalize()}: {value}")
                else:
                    print("No target selected. Use 'set <ip_or_label>' to select one.")
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
                    rhost = module_options.get("RHOST")

                    if not all([payload, output, rhost]):
                        print("Missing required options. Use 'options' to see what's needed.")
                        continue

                    target_info = get_target(rhost)
                    if not target_info:
                        print(f"Target '{rhost}' not found.")
                        continue

                    # Assuming the IP is the path to the image for this demo
                    input_path = [ip for ip, data in list_targets().items() if data == target_info][0]

                    print(f"Running stego/encode on {input_path}...")
                    encode_image(input_path, payload, output)
                    print("Module execution finished.")
            else:
                print(f"Unknown command: {command}")

        except KeyboardInterrupt:
            print("\nUse 'exit' to leave the shell.")
        except Exception as e:
            logging.error(f"An error occurred in the shell: {e}")

if __name__ == "__main__":
    # For now, let's add a dummy target for testing
    add_target("192.168.1.101", label="WebServer")
    main_loop()