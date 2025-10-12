import os
import base64
import random
import string

def generate_random_payload(length=100):
    """
    Generates a random alphanumeric string of a given length.
    """
    if length <= 0:
        raise ValueError("Payload length must be greater than 0")
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length)).encode()

def obfuscate_payload(data, method='base64'):
    """
    Obfuscates the payload using a specified method.
    """
    if method == 'base64':
        return base64.b64encode(data)
    elif method == 'xor':
        key = os.urandom(1)
        return key + bytes([b ^ key[0] for b in data])
    else:
        raise ValueError("Unsupported obfuscation method")

def deobfuscate_payload(obfuscated_data, method='base64'):
    """
    Deobfuscates the payload from a specified method.
    """
    if method == 'base64':
        return base64.b64decode(obfuscated_data)
    elif method == 'xor':
        key = obfuscated_data[:1]
        data = obfuscated_data[1:]
        return bytes([b ^ key[0] for b in data])
    else:
        raise ValueError("Unsupported deobfuscation method")

def xor_encode(payload: bytes, key: int) -> bytes:
    return bytes([b ^ key for b in payload])

def insert_junk(payload: bytes, junk_ratio=0.1) -> bytes:
    junk_bytes = [0x90, 0x91, 0x92]  # NOP-like instructions for x86
    result = bytearray()
    for b in payload:
        result.append(b)
        if random.random() < junk_ratio:
            result.append(random.choice(junk_bytes))
    return bytes(result)

def morph_payload(payload: bytes) -> bytes:
    key = random.randint(1, 255)
    encoded = xor_encode(payload, key)
    morphed = insert_junk(encoded, junk_ratio=0.2)
    return morphed, key

def generate_payload(payload_type='random', length=100, data=None, obfuscate=False, obfuscate_method='base64', morph=False):
    """
    Generates and optionally obfuscates or morphs a payload.
    """
    if payload_type == 'random':
        payload = generate_random_payload(length)
    elif payload_type == 'custom':
        if data is None:
            raise ValueError("Custom payload type requires data.")
        payload = data.encode()
    else:
        raise ValueError("Unsupported payload type.")

    if morph:
        payload, _ = morph_payload(payload)
    elif obfuscate:
        payload = obfuscate_payload(payload, method=obfuscate_method)

    return payload