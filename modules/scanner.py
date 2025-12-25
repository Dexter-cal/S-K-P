import socket
import logging
import ipaddress

# A simple heuristic model for port-based threat scoring
PORT_THREAT_MODEL = {
    21: 8,   # FTP - Often misconfigured
    22: 2,   # SSH - Secure, but a high-value target
    23: 9,   # Telnet - Insecure
    25: 5,   # SMTP - Can be used for spam
    80: 4,   # HTTP - Common attack vector
    110: 7,  # POP3 - Insecure
    139: 8,  # NetBIOS - Often vulnerable
    443: 3,  # HTTPS - Secure, but a high-value target
    445: 9,  # SMB - Major vulnerability vector (e.g., EternalBlue)
    3306: 6, # MySQL - Database access
    3389: 8, # RDP - Common target for brute-force
    5900: 7, # VNC - Remote desktop
}
DEFAULT_THREAT_SCORE = 5

def get_threat_score(port):
    """
    Returns a threat score for a given port based on the model.
    """
    return PORT_THREAT_MODEL.get(port, DEFAULT_THREAT_SCORE)

def scan_host(ip, ports):
    """
    Scans a single host for open ports and calculates a threat score.
    """
    open_ports = []
    total_threat_score = 0
    for port in ports:
        try:
            socket.setdefaulttimeout(0.2)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if s.connect_ex((ip, port)) == 0:
                open_ports.append(port)
                total_threat_score += get_threat_score(port)
            s.close()
        except Exception:
            pass
    return open_ports, total_threat_score

def intelligent_scan(subnet, ports_to_scan=None):
    """
    Performs an "intelligent" scan of a subnet, ranking hosts by threat score.
    Handles CIDR notation for subnets.
    """
    if ports_to_scan is None:
        ports_to_scan = list(PORT_THREAT_MODEL.keys())

    live_hosts = []
    try:
        network = ipaddress.ip_network(subnet, strict=False)
        logging.info(f"Starting intelligent scan of subnet {network}...")

        for ip_obj in network.hosts():
            ip = str(ip_obj)
            open_ports, score = scan_host(ip, ports_to_scan)
            if open_ports:
                live_hosts.append({
                    "ip": ip,
                    "open_ports": open_ports,
                    "threat_score": score
                })
    except ValueError:
        logging.error(f"Invalid subnet format: {subnet}. Please use CIDR notation (e.g., 192.168.1.0/24).")
        print(f"Error: Invalid subnet '{subnet}'. Please use CIDR notation (e.g., 192.168.1.0/24).")
        return []

    # Sort hosts by threat score in descending order
    sorted_hosts = sorted(live_hosts, key=lambda x: x['threat_score'], reverse=True)

    logging.info("Intelligent scan complete.")
    return sorted_hosts
