import socket
import logging

# A simple model of common IoT device ports
IOT_DEVICE_PORTS = {
    554: "RTSP (IP Cameras)",
    8883: "MQTT (IoT Hubs)",
    1900: "UPnP (Printers, Routers)",
    5683: "CoAP (IoT Devices)",
    20002: "D-Link (Cameras)",
}

def scan_for_iot_devices(subnet):
    """
    Scans a subnet for common IoT device ports.
    """
    logging.info(f"Scanning subnet {subnet} for IoT devices...")
    found_devices = []

    for port, service in IOT_DEVICE_PORTS.items():
        logging.info(f"Scanning for {service} on port {port}...")
        for i in range(1, 255):
            ip = f"{subnet}{i}"
            try:
                socket.setdefaulttimeout(0.1)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if s.connect_ex((ip, port)) == 0:
                    device_info = {"ip": ip, "port": port, "service": service}
                    found_devices.append(device_info)
                    logging.info(f"Found potential IoT device: {device_info}")
                s.close()
            except Exception:
                pass

    logging.info(f"IoT scan complete. Found {len(found_devices)} potential devices.")
    return found_devices