import logging
import time
from scapy.all import ICMP, IP, send, sniff

def send_icmp_covert(target_ip, payload):
    """
    Sends a payload via ICMP tunneling.
    """
    logging.info(f"Sending payload via ICMP to {target_ip}...")

    # Split into chunks that fit within a packet
    chunk_size = 100 # Arbitrary chunk size
    chunks = [payload[i:i+chunk_size] for i in range(0, len(payload), chunk_size)]

    for i, chunk in enumerate(chunks):
        packet = IP(dst=target_ip) / ICMP() / chunk
        send(packet, verbose=False)
        logging.info(f"Sent chunk {i+1}/{len(chunks)}")
        time.sleep(0.1)

    logging.info("ICMP payload transmission complete.")

def listen_icmp_covert(timeout=60):
    """
    Listens for a payload sent via ICMP tunneling.
    """
    logging.info("Listening for ICMP traffic...")

    payload_chunks = []

    def packet_handler(packet):
        if ICMP in packet and packet[ICMP].type == 8: # Echo request
            if packet.haslayer('Raw'):
                chunk = packet['Raw'].load
                payload_chunks.append(chunk)
                logging.info(f"Received chunk of size {len(chunk)}")

    sniff(filter="icmp", prn=packet_handler, timeout=timeout)

    if not payload_chunks:
        logging.warning("No ICMP chunks received.")
        return None

    return b"".join(payload_chunks)