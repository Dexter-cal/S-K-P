import logging
import random

# A simple knowledge base for the suggestor
# In a real-world scenario, this would be a more complex database or model.
KNOWLEDGE_BASE = {
    "scan_results": [],
    "successful_attacks": {}, # e.g., {"192.168.1.105": "smb_exploit"}
    "failed_attacks": {},
}

def update_knowledge_base(event_type, data):
    """Updates the knowledge base with new information."""
    if event_type == "scan":
        KNOWLEDGE_BASE["scan_results"].extend(data)
    elif event_type == "success":
        ip, exploit = data
        KNOWLEDGE_BASE["successful_attacks"][ip] = exploit
    elif event_type == "failure":
        ip, exploit = data
        if ip not in KNOWLEDGE_BASE["failed_attacks"]:
            KNOWLEDGE_BASE["failed_attacks"][ip] = []
        KNOWLEDGE_BASE["failed_attacks"][ip].append(exploit)

def get_suggestion(context):
    """
    Generates a suggestion based on the current context and knowledge base.
    """
    logging.info("Suggestor AI: Analyzing context for recommendations...")

    # Example context: {"current_target": "192.168.1.105", "open_ports": [445]}

    target = context.get("current_target")
    if not target:
        # If no target, suggest a scan
        if not KNOWLEDGE_BASE["scan_results"]:
            return "No targets known. Suggest running a 'scan' to discover hosts."
        else:
            # Suggest a high-value target from a previous scan
            # (Simplified logic)
            high_value_target = random.choice(KNOWLEDGE_BASE["scan_results"])
            return f"Consider setting a target. {high_value_target['ip']} looks interesting."

    # If a target is set, suggest an attack
    open_ports = context.get("open_ports", [])

    # "Learning from mistakes" - don't suggest failed attacks
    failed_exploits = KNOWLEDGE_BASE["failed_attacks"].get(target, [])

    if 445 in open_ports and "smb_exploit" not in failed_exploits:
        return f"Target {target} has port 445 open. Suggest using the 'smb_exploit' module."
    if 80 in open_ports and "web_clone" not in failed_exploits:
        return f"Target {target} has port 80 open. Suggest using 'lure web' to clone their website."

    return "No obvious attack vectors found for the current target."