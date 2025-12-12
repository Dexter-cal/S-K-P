import os
from modules.steganography import encode_image
from modules.discovery import discover_files

def get_user_input(prompt, default=None):
    """
    Prompts the user for input with an optional default value.
    """
    if default:
        return input(f"{prompt} [{default}]: ") or default
    return input(f"{prompt}: ")

def yes_no_question(prompt):
    """
    Asks a yes/no question and returns a boolean.
    """
    while True:
        answer = get_user_input(f"{prompt} (y/n)").lower()
        if answer in ['y', 'yes']:
            return True
        elif answer in ['n', 'no']:
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def encode_wizard():
    """
    An interactive wizard to guide the user through the encoding process.
    """
    print("\n--- Steganography Encoding Wizard ---")
    print("This wizard will help you hide a message or file in an image.")

    # Get payload type
    is_file_payload = yes_no_question("Are you hiding a file?")
    if is_file_payload:
        payload = get_user_input("Enter the path to the file you want to hide")
    else:
        payload = get_user_input("Enter the message you want to hide")

    # Discover and select cover image
    print("\nNext, let's find an image to hide your payload in.")
    search_path = get_user_input("Enter a directory to search for images", default=".")
    images = discover_files('image', search_path)

    if not images:
        print("No images found in that directory.")
        return

    print("\nAvailable images:")
    for i, img in enumerate(images):
        print(f"  {i+1}: {img}")

    while True:
        try:
            choice = int(get_user_input("Select an image by number"))
            input_image = images[choice - 1]
            break
        except (ValueError, IndexError):
            print("Invalid selection. Please try again.")

    # Get output path
    default_output = f"encoded_{os.path.basename(input_image)}"
    output_image = get_user_input("Enter the name for the output image", default=default_output)

    # Advanced options
    print("\n--- Advanced Options ---")
    encrypt = yes_no_question("Do you want to encrypt the payload?")
    key = None
    if encrypt:
        key = get_user_input("Enter an encryption key (optional, will be generated if left blank)")

    compress = yes_no_question("Do you want to compress the payload?")

    # Perform encoding
    print(f"\nEncoding your payload into {input_image}...")
    try:
        encode_image(
            input_path=input_image,
            payload=payload,
            output_path=output_image,
            is_file=is_file_payload,
            encrypt=encrypt,
            key=key,
            compress=compress
        )
        print(f"\nSuccess! Your payload has been hidden in {output_image}")
    except Exception as e:
        print(f"\nAn error occurred during encoding: {e}")
        print("Please try again with a different image or a smaller payload.")