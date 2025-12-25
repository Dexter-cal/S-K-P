import logging
import subprocess
import xml.etree.ElementTree as ET

# --- Simple Local CVE Database ---
# In a real tool, this would be a much larger, updatable database.
CVE_DATABASE = {
    "vsftpd 2.3.4": ["CVE-2011-2523 - Remote Code Execution"],
    "proftpd 1.3.3c": ["CVE-2010-4221 - Remote Code Execution"],
    "apache httpd 2.4.29": ["CVE-2021-41773 - Path Traversal", "CVE-2021-42013 - Path Traversal"],
    "openssh 7.2": ["CVE-2018-15473 - User Enumeration"]
}

def check_for_vulnerabilities(nmap_results):
    """
    Cross-references discovered services with a local CVE database.
    """
    if not nmap_results:
        return nmap_results

    for port in nmap_results['ports']:
        service_string = f"{port['product']} {port['version']}".lower().strip()
        for cve_key, cves in CVE_DATABASE.items():
            if cve_key.lower() in service_string:
                port['vulnerabilities'] = cves
    return nmap_results

def run_nmap_scan(target_ip):
    """
    Runs a detailed Nmap scan for service version and OS detection.
    Parses the XML output and returns a structured dictionary of results.
    """
    logging.info(f"Starting deep reconnaissance scan on {target_ip}...")
    results = {
        "ip": target_ip,
        "os": "Unknown",
        "ports": []
    }

    try:
        # -sV: Service/Version info
        # -O: Enable OS detection
        # -oX -: Output XML to stdout
        command = ["nmap", "-sV", "-O", target_ip, "-oX", "-"]
        process = subprocess.run(command, capture_output=True, text=True, check=True)

        # Parse the XML output
        root = ET.fromstring(process.stdout)

        for host in root.findall('host'):
            # Find OS information
            os_match = host.find('os/osmatch')
            if os_match is not None and int(os_match.get('accuracy')) > 90:
                results['os'] = os_match.get('name')

            # Find port and service information
            ports = host.find('ports')
            for port in ports.findall('port'):
                if port.find('state').get('state') == 'open':
                    service = port.find('service')
                    port_info = {
                        "port": port.get('portid'),
                        "protocol": port.get('protocol'),
                        "service": service.get('name', 'unknown'),
                        "product": service.get('product', ''),
                        "version": service.get('version', '')
                    }
                    results['ports'].append(port_info)

        logging.info(f"Recon scan on {target_ip} complete.")

        # Add vulnerability information to the results
        results_with_vulns = check_for_vulnerabilities(results)

        return results_with_vulns

    except FileNotFoundError:
        logging.error("Nmap is not installed or not in your PATH. Please install it.")
        print("Error: Nmap is not installed. Please install it to use the recon module.")
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"Nmap scan failed: {e.stderr}")
        print(f"Error: Nmap scan failed. Ensure the target is reachable and you have permissions. Details: {e.stderr}")
        return None
    except Exception as e:
        logging.error(f"An error occurred while parsing Nmap output: {e}")
        return None
