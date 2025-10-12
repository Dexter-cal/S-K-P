import socket
import logging

def scan_subnet(subnet, port):
    live_hosts = []
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            socket.setdefaulttimeout(0.5)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = s.connect_ex((ip, port))
            if result == 0:
                live_hosts.append(ip)
            s.close()
        except Exception:
            pass
    logging.info(f"Live hosts with open port {port}: {live_hosts}")
    return live_hosts