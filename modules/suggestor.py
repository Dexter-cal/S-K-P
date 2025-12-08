import logging

def get_suggestions(last_command, targets, current_target):
    """
    Provides contextual suggestions based on the current state of the shell.
    """
    suggestions = []

    # --- Initial State Suggestions ---
    if not targets:
        suggestions.append("Run a 'scan <subnet>' to discover targets on the network (e.g., 'scan 192.168.1.0/24').")
        return suggestions

    # --- Post-Scan Suggestions ---
    if last_command.startswith("scan") and targets:
        suggestions.append("Use 'targets' to view the discovered hosts.")
        suggestions.append(f"Select a target with 'set {list(targets.keys())[0]}' to see more options.")

    # --- Target Selected Suggestions ---
    if current_target:
        suggestions.append("Use 'info' to see detailed information about the current target.")
        suggestions.append("Use 'lure' to launch a social engineering attack.")
        suggestions.append("Use 'covert' or 'icmp' for stealthy C2 communication.")
        suggestions.append("Use 'mitm' to perform a man-in-the-middle attack.")

    # --- General Suggestions ---
    if not current_target and targets:
        suggestions.append(f"Select a target with 'set {list(targets.keys())[0]}' to see more options.")

    if not suggestions:
        suggestions.append("Type 'help' to see a full list of commands.")

    return suggestions
