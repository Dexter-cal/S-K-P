import wave
import struct
import logging

def encode_audio(input_path, payload, output_path):
    """
    Embeds a payload into a WAV audio file.
    """
    try:
        with wave.open(input_path, 'rb') as audio:
            params = audio.getparams()
            n_channels, sampwidth, framerate, n_frames, comptype, compname = params

            if sampwidth != 2:
                raise ValueError("Only 16-bit WAV files are supported.")

            frames = audio.readframes(n_frames)
            samples = struct.unpack(f'{n_frames * n_channels}h', frames)

            # Prepare payload
            data = payload.encode('utf-8')
            data_len = len(data)
            data_bits = ''.join(format(byte, '08b') for byte in data)
            len_bits = format(data_len, '032b')
            full_bits = len_bits + data_bits

            if len(full_bits) > len(samples):
                raise ValueError("Audio file is too short for the payload.")

            new_samples = list(samples)
            for i, bit in enumerate(full_bits):
                sample = new_samples[i]
                new_samples[i] = (sample & ~1) | int(bit)

            with wave.open(output_path, 'wb') as out_audio:
                out_audio.setparams(params)
                new_frames = struct.pack(f'{n_frames * n_channels}h', *new_samples)
                out_audio.writeframes(new_frames)

        logging.info(f"Payload successfully embedded in {output_path}")

    except Exception as e:
        logging.error(f"Audio encoding error: {e}")

def decode_audio(input_path):
    """
    Extracts a payload from a WAV audio file.
    """
    try:
        with wave.open(input_path, 'rb') as audio:
            params = audio.getparams()
            n_channels, sampwidth, framerate, n_frames, comptype, compname = params

            if sampwidth != 2:
                raise ValueError("Only 16-bit WAV files are supported.")

            frames = audio.readframes(n_frames)
            samples = struct.unpack(f'{n_frames * n_channels}h', frames)

            # Extract length
            len_bits = ""
            for i in range(32):
                len_bits += str(samples[i] & 1)

            payload_len = int(len_bits, 2)

            # Extract payload
            data_bits = ""
            for i in range(32, 32 + payload_len * 8):
                data_bits += str(samples[i] & 1)

            payload_bytes = bytes(int(data_bits[i:i+8], 2) for i in range(0, len(data_bits), 8))
            return payload_bytes.decode('utf-8', errors='ignore')

    except Exception as e:
        logging.error(f"Audio decoding error: {e}")
        return None