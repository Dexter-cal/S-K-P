import logging
import time
from scapy.all import Ether, ARP, sendp

# A magic value to identify our custom packets
COVERT_MAGIC_VALUE = b'\xDE\xAD\xBE\xEF'
CHUNK_SIZE = 10 # Small chunk size for demonstration

def send_arp_covert(target_ip, payload):
    """
    Sends a payload to a target IP using a covert channel in ARP packets.
    The payload is hidden in the padding of the Ethernet frame.
    """
    logging.info(f"Preparing to send a payload of {len(payload)} bytes to {target_ip} via ARP covert channel.")

    # First, send a "start" packet to let the listener know the total size
    start_packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip, psrc='0.0.0.0', op='who-has')
    start_packet.add_payload(COVERT_MAGIC_VALUE + b'START' + len(payload).to_bytes(4, 'big'))
    sendp(start_packet, verbose=False)

    time.sleep(0.1) # Give the listener a moment to prepare

    # Send the payload in chunks
    for i in range(0, len(payload), CHUNK_SIZE):
        chunk = payload[i:i+CHUNK_SIZE]
        packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip, psrc='0.0.0.0', op='who-has')
        packet.add_payload(COVERT_MAGIC_VALUE + chunk)
        sendp(packet, verbose=False)
        logging.info(f"Sent chunk {i//CHUNK_SIZE + 1}...")
        time.sleep(0.05)

    # Send an "end" packet
    end_packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip, psrc='0.0.0.0', op='who-has')
    end_packet.add_payload(COVERT_MAGIC_VALUE + b'END')
    sendp(end_packet, verbose=False)

    logging.info("Payload transmission complete.")

def listen_arp_covert(timeout=60):
    """
    Listens for a covert payload sent via ARP packets.
    """
    logging.info("Starting ARP covert listener...")

    payload_data = bytearray()
    expected_size = -1

    def packet_handler(packet):
        nonlocal expected_size, payload_data

        if ARP in packet and packet[ARP].op == 1: # who-has
            if packet.haslayer('Raw'):
                raw_data = packet['Raw'].load
                if raw_data.startswith(COVERT_MAGIC_VALUE):
                    data = raw_data[len(COVERT_MAGIC_VALUE):]

                    if data.startswith(b'START'):
                        expected_size = int.from_bytes(data[5:], 'big')
                        logging.info(f"Receiving a payload of {expected_size} bytes.")
                    elif data.startswith(b'END'):
                        logging.info("End of transmission received.")
                        return True # Stop sniffing
                    else:
                        payload_data.extend(data)
                        logging.info(f"Received chunk, total size: {len(payload_data)}/{expected_size if expected_size != -1 else '?'}")
        return False

    from scapy.all import sniff
    sniff(filter="arp", prn=packet_handler, stop_filter=packet_handler, timeout=timeout)

    if expected_size != -1 and len(payload_data) == expected_size:
        logging.info("Payload reassembled successfully.")
        return bytes(payload_data)
    else:
        logging.error("Failed to reassemble payload. Data may be incomplete.")
        return None