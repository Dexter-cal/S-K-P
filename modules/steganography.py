import os
import zlib
import random
import hashlib
import base64
import logging
import sys
from PIL import Image
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim

def generate_key():
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key()

def encrypt_data(data, key, method='fernet'):
    """Encrypt data using Fernet or AES."""
    if method == 'fernet':
        fernet = Fernet(key)
        return fernet.encrypt(data)
    elif method == 'aes':
        iv = os.urandom(16)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return iv + encrypted
    else:
        raise ValueError("Unsupported encryption method")

def decrypt_data(encrypted_data, key, method='fernet'):
    """Decrypt data using Fernet or AES."""
    if method == 'fernet':
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data)
    elif method == 'aes':
        iv = encrypted_data[:16]
        encrypted = encrypted_data[16:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(encrypted) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        return unpadder.update(decrypted_padded) + unpadder.finalize()
    else:
        raise ValueError("Unsupported encryption method")

def calculate_capacity(image, bits_per_channel=1):
    """Calculate maximum bytes that can be hidden."""
    height, width, channels = image.shape
    return (height * width * channels * bits_per_channel) // 8

def compress_data(data, level=9):
    """Compress data using zlib."""
    return zlib.compress(data, level)

def decompress_data(compressed_data):
    """Decompress data using zlib."""
    return zlib.decompress(compressed_data)

def get_edge_map(image, threshold=100):
    """Get edge map using Canny for adaptive embedding."""
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, threshold, threshold * 2)
    return edges

def generate_pixel_order(image_shape, seed=None):
    """Generate random pixel order for embedding."""
    height, width = image_shape[:2]
    pixels = [(y, x) for y in range(height) for x in range(width)]
    if seed:
        random.seed(seed)
        random.shuffle(pixels)
    return pixels

def embed_lsb(image, data_bits, bits_per_channel=1, adaptive=False, seed=None):
    """Embed bits into image using LSB, optionally adaptive or random."""
    height, width, channels = image.shape
    if adaptive:
        edge_map = get_edge_map(image)
        pixel_order = [(y, x) for y in range(height) for x in range(width) if edge_map[y, x] > 0]
        if not pixel_order:
            raise ValueError("No edges detected for adaptive embedding")
    else:
        pixel_order = generate_pixel_order(image.shape, seed)

    bit_index = 0
    for y, x in pixel_order:
        for c in range(channels):
            pixel_value = int(image[y, x, c])
            for b in range(bits_per_channel):
                if bit_index < len(data_bits):
                    bit = int(data_bits[bit_index])
                    pixel_value = (pixel_value & ~(1 << b)) | (bit << b)
                    bit_index += 1
            image[y, x, c] = np.clip(pixel_value, 0, 255)
        if bit_index >= len(data_bits):
            break
    if bit_index < len(data_bits):
        raise ValueError("Image capacity insufficient for payload")
    return image

def extract_lsb(image, payload_size, bits_per_channel=1, adaptive=False, seed=None):
    """Extract bits from image using LSB."""
    height, width, channels = image.shape
    if adaptive:
        edge_map = get_edge_map(image)
        pixel_order = [(y, x) for y in range(height) for x in range(width) if edge_map[y, x] > 0]
    else:
        pixel_order = generate_pixel_order(image.shape, seed)

    data_bits = []
    extracted_bytes = 0
    for y, x in pixel_order:
        for c in range(channels):
            pixel_value = image[y, x, c]
            for b in range(bits_per_channel):
                bit = (pixel_value >> b) & 1
                data_bits.append(str(bit))
                if len(data_bits) % 8 == 0:
                    extracted_bytes += 1
                if extracted_bytes >= payload_size:
                    return ''.join(data_bits)
    return ''.join(data_bits)

def bits_to_bytes(bits):
    """Convert bit string to bytes."""
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

def compute_psnr(original, stego):
    """Compute PSNR between two images."""
    mse = np.mean((original - stego) ** 2)
    if mse == 0:
        return float('inf')
    return 20 * np.log10(255.0 / np.sqrt(mse))

def compute_ssim(original, stego):
    """Compute SSIM between two images."""
    # Ensure images are compatible with SSIM calculation
    if original.shape != stego.shape:
        raise ValueError("Input images must have the same dimensions.")

    # SSIM is typically calculated on grayscale images, but can be extended to multichannel
    # by averaging over channels. The `multichannel=True` handles this.
    # However, let's ensure the data types are appropriate.
    if original.dtype != stego.dtype:
        stego = stego.astype(original.dtype)

    # The `data_range` parameter is important. It should be the maximum possible pixel value.
    data_range = 255 if original.dtype == np.uint8 else 1.0

    return ssim(original, stego, multichannel=True, data_range=data_range)

def encode_image(input_path, payload, output_path, bits_per_channel=1, encrypt=False, encrypt_method='fernet', key=None, compress=False, adaptive=False, seed=None, is_file=False, verbose=False, opap=False):
    """Embed payload into image."""
    try:
        image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError("Invalid image file")
        original = image.copy()

        if is_file:
            with open(payload, 'rb') as f:
                data = f.read()
        else:
            data = payload.encode('utf-8')

        if compress:
            data = compress_data(data)
            logging.info(f"Compressed payload to {len(data)} bytes")

        if encrypt:
            if key is None:
                key = generate_key() if encrypt_method == 'fernet' else os.urandom(32)
                key_str = base64.urlsafe_b64encode(key).decode('utf-8')
                print(f"Generated key (save this!): {key_str}")
            else:
                key = base64.urlsafe_b64decode(key)
            data = encrypt_data(data, key, encrypt_method)
            logging.info("Payload encrypted")

        # Add integrity hash
        data_hash = hashlib.sha256(data).digest()
        full_data = len(data).to_bytes(4, 'big') + data_hash + data + b'\x00' * 8

        capacity = calculate_capacity(image, bits_per_channel)
        if len(full_data) > capacity:
            raise ValueError(f"Payload too large ({len(full_data)} bytes) vs capacity ({capacity} bytes)")

        data_bits = ''.join(format(byte, '08b') for byte in full_data)

        image = embed_lsb(image, data_bits, bits_per_channel, adaptive, seed)

        if opap:
            # Simple OPAP: adjust if difference > 2^(bits_per_channel-1)
            # Implement if needed, skipped for brevity
            pass

        cv2.imwrite(output_path, image)
        logging.info(f"Encoded image saved to {output_path}")

        if verbose:
            psnr = compute_psnr(original, image)
            ssim_val = compute_ssim(original, image)
            print(f"PSNR: {psnr:.2f} dB | SSIM: {ssim_val:.4f}")

    except Exception as e:
        print(f"Encoding error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def decode_image(input_path, key=None, encrypt_method='fernet', compress=False, output_file=None, bits_per_channel=1, adaptive=False, seed=None, verbose=False):
    """Extract payload from image."""
    try:
        image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError("Invalid image file")

        capacity = calculate_capacity(image, bits_per_channel)
        # Extract max possible to find length
        data_bits = extract_lsb(image, capacity, bits_per_channel, adaptive, seed)
        full_data = bits_to_bytes(data_bits)

        length = int.from_bytes(full_data[:4], 'big')
        data_hash = full_data[4:36]
        data = full_data[36:36+length]
        end_marker = full_data[36+length:36+length+8]

        if end_marker != b'\x00' * 8:
            raise ValueError("Invalid end marker")

        if hashlib.sha256(data).digest() != data_hash:
            raise ValueError("Integrity check failed")

        if key:
            key = base64.urlsafe_b64decode(key)
            data = decrypt_data(data, key, encrypt_method)
            logging.info("Payload decrypted")

        if compress:
            data = decompress_data(data)
            logging.info("Payload decompressed")

        if output_file:
            with open(output_file, 'wb') as f:
                f.write(data)
            logging.info(f"Extracted to {output_file}")
            return None
        else:
            try:
                return data.decode('utf-8')
            except UnicodeDecodeError:
                print("Binary data extracted; use --output-file", file=sys.stderr)
                return data
    except Exception as e:
        print(f"Decoding error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def chi_square_test(data):
    """
    Performs a Chi-Square test on a list of byte values.
    Returns the Chi-Square statistic and the p-value.
    """
    from scipy.stats import chisquare

    # Count the occurrences of each byte value (0-255)
    observed_freq = np.bincount(data, minlength=256)

    # Expected frequency for a uniform distribution
    expected_freq = np.full(256, len(data) / 256.0)

    # To avoid division by zero, we only consider non-zero expected frequencies
    # Although in this case, it's always non-zero unless the input data is empty
    nonzero_indices = expected_freq > 0

    # Perform the Chi-Square test
    chi2_stat, p_value = chisquare(
        f_obs=observed_freq[nonzero_indices],
        f_exp=expected_freq[nonzero_indices]
    )

    return chi2_stat, p_value

def detect_stego(input_path, bits_per_channel=1):
    """
    Performs a basic Chi-Square analysis to detect LSB steganography.
    """
    try:
        image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError("Invalid image file")

        if image.ndim < 3:
            # Grayscale image, add a channel dimension
            image = image[..., np.newaxis]

        height, width, channels = image.shape

        # Extract the LSBs from each color channel
        lsb_data = []
        for c in range(channels):
            for b in range(bits_per_channel):
                # Extract the b-th bit plane
                plane = (image[:, :, c] >> b) & 1
                lsb_data.extend(plane.flatten())

        # The data for Chi-Square should be byte values, not bits.
        # We can group the bits into bytes.
        # To simplify, we'll analyze the distribution of pixel values in the LSBs.
        # A more common approach is to analyze pairs of values (PoVs).

        # Let's analyze the LSB plane directly.
        # We'll count the number of 0s and 1s.
        lsb_plane = (image & ((1 << bits_per_channel) - 1)).flatten()

        # Perform Chi-Square test on the LSB plane
        chi2, p_value = chi_square_test(lsb_plane)

        # Interpretation
        alpha = 0.05  # Significance level
        if p_value < alpha:
            return f"Potential steganography detected (p-value: {p_value:.4f}). The distribution of LSB values is unusual."
        else:
            return f"No steganography detected (p-value: {p_value:.4f}). The distribution of LSB values appears normal."

    except Exception as e:
        return f"Stego detection error: {str(e)}"