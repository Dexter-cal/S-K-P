import logging
from modules.target_manager import get_target
from modules.exploit_suggester import get_exploit_commands

class APE:
    def __init__(self, process_command_func):
        self.process_command = process_command_func

    def unleash(self, target_ip):
        """
        Unleashes the Automated Persistent Exploitation engine on a target.
        """
        logging.info(f"Unleashing APE on {target_ip}...")

        target_data = get_target(target_ip)
        if not target_data:
            print(f"Error: Target {target_ip} not found.")
            return

        if 'recon' not in target_data or not target_data['recon']:
            print("Error: No reconnaissance data found for this target. Run 'recon' first.")
            return

        vulnerabilities = []
        for port in target_data['recon'].get('ports', []):
            if 'vulnerabilities' in port:
                for vuln in port['vulnerabilities']:
                    vulnerabilities.append(vuln.split(' ')[0])

        if not vulnerabilities:
            print("No known vulnerabilities found for this target.")
            return

        print(f"Found {len(vulnerabilities)} potential vulnerabilities. Attempting to exploit...")

        for cve in vulnerabilities:
            commands = get_exploit_commands(cve)
            if commands:
                print(f"\n--- Attempting to exploit {cve} ---")
                for command_template in commands:
                    command = command_template.replace("{TARGET_IP}", target_ip)
                    print(f"Executing: {command}")
                    # Use the main shell's command processor to execute the command
                    self.process_command(command)
                print("------------------------------------")
            else:
                print(f"No automated exploit available for {cve}.")
