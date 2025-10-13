import json
import hashlib
import base64
import logging

def derive_key_from_profile(profile_path):
    """
    Derives a deterministic encryption key from a target's profile file.
    """
    try:
        with open(profile_path, 'r') as f:
            profile = json.load(f)

        # Create a stable, ordered string from the profile's identifiers
        # The order is important to ensure the key is deterministic.
        key_material = ""
        for key in sorted(profile.keys()):
            key_material += str(profile[key])

        if not key_material:
            logging.error("Profile is empty. Cannot derive key.")
            return None

        # Use SHA-256 to hash the key material into a 32-byte key
        # This is suitable for use with Fernet (AES-128 in CBC mode)
        hashed_key = hashlib.sha256(key_material.encode()).digest()

        # Fernet keys must be URL-safe base64 encoded
        fernet_key = base64.urlsafe_b64encode(hashed_key)

        logging.info(f"Successfully derived encryption key from {profile_path}")
        return fernet_key

    except FileNotFoundError:
        logging.error(f"Profile file not found: {profile_path}")
        return None
    except Exception as e:
        logging.error(f"Failed to derive key from profile: {e}")
        return None