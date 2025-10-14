import socket
import threading
import logging

def forward(source, destination):
    """
    Forwards data between two sockets.
    """
    while True:
        try:
            data = source.recv(1024)
            if data:
                destination.sendall(data)
            else:
                break
        except Exception as e:
            logging.error(f"Error during forwarding: {e}")
            break
    source.close()
    destination.close()

def start_port_forwarder(listen_host, listen_port, forward_host, forward_port):
    """
    Starts a TCP port forwarder.
    """
    logging.info(f"Starting port forwarder: {listen_host}:{listen_port} -> {forward_host}:{forward_port}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((listen_host, listen_port))
    server_socket.listen(5)

    while True:
        try:
            client_socket, addr = server_socket.accept()
            logging.info(f"Accepted connection from {addr}")

            forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            forward_socket.connect((forward_host, forward_port))

            # Start forwarding in both directions
            threading.Thread(target=forward, args=(client_socket, forward_socket)).start()
            threading.Thread(target=forward, args=(forward_socket, client_socket)).start()

        except Exception as e:
            logging.error(f"Error in port forwarder main loop: {e}")
            break

    server_socket.close()