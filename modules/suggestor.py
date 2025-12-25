import logging
from modules.exploit_suggester import get_exploit_suggestions

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
        suggestions.append(f"Run a deep reconnaissance scan with 'recon {list(targets.keys())[0]}'.")
        suggestions.append(f"Select a target with 'set {list(targets.keys())[0]}' to see more options.")

    # --- Target Selected Suggestions ---
    if current_target:
        # Check for specific exploit suggestions from recon data
        if 'recon' in current_target and current_target['recon']:
            exploit_suggestions = get_exploit_suggestions(current_target['recon'])
            if exploit_suggestions:
                suggestions.extend(exploit_suggestions)

        suggestions.append("Use 'info' to see detailed information about the current target.")
        suggestions.append("Generate a malicious file for delivery with 'generate_file <type>'.")
        suggestions.append("Use one of the C2 channels to send a command (e.g., 'icmp send <ip> whoami').")
        suggestions.append("Use 'mitm' to perform a man-in-the-middle attack.")

    # --- After Recon Scan ---
    if last_command.startswith("recon"):
        target_ip = last_command.split()[1] if len(last_command.split()) > 1 else None
        if target_ip and targets.get(target_ip) and targets[target_ip].get('recon'):
            exploit_suggestions = get_exploit_suggestions(targets[target_ip]['recon'])
            if exploit_suggestions:
                suggestions.insert(0, f"Vulnerabilities found! Try the APE engine with 'ape unleash {target_ip}'.")
                suggestions.extend(exploit_suggestions)

    # --- After Generating a File ---
    if last_command.startswith("generate_file"):
        file_type = last_command.split()[1] if len(last_command.split()) > 1 else "file"
        suggestions.append(f"Learn about this attack with 'explain {file_type}'.")
        suggestions.append("Deliver the generated file using a C2 channel (e.g., 'covert send_file <ip> <path>').")

    # --- After Generating an Implant ---
    implant_generation_commands = ["icmp generate", "stego_c2 generate", "github_c2 generate"]
    if any(last_command.startswith(cmd) for cmd in implant_generation_commands):
        suggestions.append("Make your implant evasive with 'morph <input_path> <output_path>'.")

    # --- Post-C2 Command Suggestions ---
    c2_commands = ["covert send", "icmp send", "github_c2 command", "stego_c2 command"]
    if any(last_command.startswith(cmd) for cmd in c2_commands):
        suggestions.append("Consider establishing persistence with 'persist <os> <implant_path>'.")

    # --- After Starting C2 Server ---
    if last_command in ["stego_c2 start"]:
        suggestions.append("Now that the C2 server is running, generate an implant.")
        suggestions.append("For a fileless implant, use 'lotl <os> <c2_url>'.")
        suggestions.append("For a file-based implant, use 'stego_c2 generate <path>'.")

    # --- General Suggestions ---
    if not current_target and targets:
        suggestions.append(f"Select a target with 'set {list(targets.keys())[0]}' to see more options.")

    if not suggestions:
        suggestions.append("Type 'help' to see a full list of commands.")

    return suggestions
