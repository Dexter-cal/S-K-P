import platform
import subprocess
import json
import logging
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [Profiler] - %(message)s')

def get_mac_address():
    """Returns the MAC address of the primary network interface."""
    try:
        # The : format is more standard across platforms
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
        return mac
    except Exception as e:
        logging.error(f"Could not get MAC address: {e}")
        return None

def get_cpu_serial():
    """
    Returns the CPU serial number.
    (This is highly OS-specific and may not work on all systems.)
    """
    try:
        if platform.system() == "Windows":
            return subprocess.check_output("wmic cpu get ProcessorId").decode().strip().split('\n')[1]
        elif platform.system() == "Linux":
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if "Serial" in line:
                        return line.split(':')[1].strip()
        # macOS does not easily expose a CPU serial number
    except Exception as e:
        logging.error(f"Could not get CPU serial: {e}")
    return None

def get_hostname():
    """Returns the computer's network name."""
    return platform.node()

def main():
    """
    Gathers system identifiers and saves them to a profile file.
    """
    print("--- Target System Profiler ---")

    profile = {
        "hostname": get_hostname(),
        "mac_address": get_mac_address(),
        "cpu_serial": get_cpu_serial(),
        "os": platform.system(),
        "os_version": platform.version(),
    }

    # Filter out any identifiers we couldn't retrieve
    profile = {k: v for k, v in profile.items() if v is not None}

    if not profile:
        logging.error("Could not retrieve any unique identifiers. Cannot create profile.")
        return

    output_filename = f"profile_{profile['hostname']}.json"
    with open(output_filename, 'w') as f:
        json.dump(profile, f, indent=4)

    print(f"\nSystem profile created successfully!")
    print(f"  Hostname: {profile.get('hostname')}")
    print(f"  MAC Address: {profile.get('mac_address')}")
    print(f"  CPU Serial: {profile.get('cpu_serial')}")
    print(f"\nProfile saved to: {output_filename}")

if __name__ == "__main__":
    main()