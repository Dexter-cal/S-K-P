import unittest
import os
import cv2
import numpy as np
from modules.steganography import encode_image, decode_image

class TestSteganography(unittest.TestCase):

    def setUp(self):
        # Create a dummy image for testing
        self.image_path = "test_image.png"
        self.output_path = "test_output.png"
        self.payload = "This is a test payload."

        # Create a simple 20x20 black image
        image = np.zeros((20, 20, 3), dtype=np.uint8)
        cv2.imwrite(self.image_path, image)

    def tearDown(self):
        # Clean up created files
        if os.path.exists(self.image_path):
            os.remove(self.image_path)
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def test_encode_decode(self):
        # Test encoding and then decoding
        encode_image(
            input_path=self.image_path,
            payload=self.payload,
            output_path=self.output_path,
            is_file=False
        )
        decoded_payload = decode_image(
            input_path=self.output_path
        )
        self.assertEqual(self.payload, decoded_payload)

if __name__ == '__main__':
    unittest.main()