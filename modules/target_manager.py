import logging

# In-memory database for targets
# In a real-world application, this would be a persistent database (e.g., SQLite).
TARGET_DATABASE = {}
# Example:
# {
#   "192.168.1.101": {"label": "WebServer", "os": "Linux", "open_ports": [80, 443]},
#   "192.168.1.105": {"label": "FileShare", "os": "Windows", "open_ports": [445]},
# }

def add_target(ip, label="", os="Unknown", open_ports=None):
    """Adds or updates a target in the database."""
    if ip not in TARGET_DATABASE:
        TARGET_DATABASE[ip] = {
            "label": label,
            "os": os,
            "open_ports": open_ports or [],
            "recon": {}  # New field for detailed recon data
        }
        logging.info(f"New target added: {ip}")
    else:
        # Update existing fields if new information is provided
        if label: TARGET_DATABASE[ip]['label'] = label
        if os != "Unknown": TARGET_DATABASE[ip]['os'] = os
        if open_ports: TARGET_DATABASE[ip]['open_ports'] = open_ports
        logging.info(f"Target updated: {ip}")
    return TARGET_DATABASE[ip]

def get_target(ip_or_label):
    """Retrieves a target by its IP address or label."""
    # First, check if it's an IP
    if ip_or_label in TARGET_DATABASE:
        return TARGET_DATABASE[ip_or_label]
    # If not, search by label
    for ip, data in TARGET_DATABASE.items():
        if data.get('label') == ip_or_label:
            return TARGET_DATABASE[ip]
    return None

def list_targets():
    """Returns a list of all targets in the database."""
    return TARGET_DATABASE

def add_recon_data(ip, recon_data):
    """Adds detailed reconnaissance data to a target."""
    if ip in TARGET_DATABASE:
        TARGET_DATABASE[ip]['recon'] = recon_data
        # Also, update the main OS field if a better guess is available from recon
        if recon_data.get('os') and recon_data['os'] != "Unknown":
            TARGET_DATABASE[ip]['os'] = recon_data['os']
        logging.info(f"Detailed recon data added for {ip}")
        return True
    else:
        logging.error(f"Cannot add recon data: Target {ip} not found.")
        return False

def set_target_label(ip, label):
    """Sets a custom label for a target."""
    if ip in TARGET_DATABASE:
        TARGET_DATABASE[ip]['label'] = label
        logging.info(f"Label for {ip} set to '{label}'.")
        return True
    else:
        logging.error(f"Target not found: {ip}")
        return False