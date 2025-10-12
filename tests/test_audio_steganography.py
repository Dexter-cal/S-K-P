import unittest
import os
import wave
import struct
from modules.audio_steganography import encode_audio, decode_audio

class TestAudioSteganography(unittest.TestCase):

    def setUp(self):
        # Create a dummy audio file for testing
        self.audio_path = "test_audio.wav"
        self.output_path = "test_output.wav"
        self.payload = "This is a test payload for audio."

        # Create a short silent WAV file
        with wave.open(self.audio_path, 'wb') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(44100)
            for _ in range(1024):
                f.writeframes(struct.pack('h', 0))

    def tearDown(self):
        # Clean up created files
        if os.path.exists(self.audio_path):
            os.remove(self.audio_path)
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def test_encode_decode_audio(self):
        # Test encoding and then decoding
        encode_audio(self.audio_path, self.payload, self.output_path)
        decoded_payload = decode_audio(self.output_path)
        self.assertEqual(self.payload, decoded_payload)

if __name__ == '__main__':
    unittest.main()