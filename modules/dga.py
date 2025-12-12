import datetime
import hashlib
import base64

def generate_domains(seed, date, count=10):
    """
    Generates a list of domain names for a given day based on a seed.
    """
    domains = []
    for i in range(count):
        # Create a unique string for each domain
        data = f"{seed}-{date.strftime('%Y-%m-%d')}-{i}"

        # Use a predictable hash to generate the domain name
        s = hashlib.sha256(data.encode()).digest()

        # Base32 encode to get valid domain characters
        # We'll use a custom base32 alphabet to avoid ambiguous characters
        alphabet = "abcdefghijklmnopqrstuvwxyz234567"
        domain = base64.b32encode(s).decode('utf-8').lower().replace('=', '')

        # Take the first 12 characters for a reasonable length
        domains.append(f"{domain[:12]}.com")

    return domains

if __name__ == '__main__':
    # Example usage
    today = datetime.date.today()
    seed = "mysecretseed"

    print(f"DGA domains for {today} with seed '{seed}':")
    for domain in generate_domains(seed, today):
        print(f"  - {domain}")