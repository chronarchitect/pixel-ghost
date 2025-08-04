from PIL import Image
import numpy as np
from steganography.base import SteganographyBase

class LSB(SteganographyBase):
    """
Least Significant Bit (LSB) steganography implementation.

    This class extends the SteganographyBase class to implement LSB steganography
    for encoding and decoding messages in images.
    """

    def to_bin(self, data):
        """Convert data to binary format as string."""
        if isinstance(data, str):
            return ''.join(format(ord(i), '08b') for i in data)
        elif isinstance(data, bytes) or isinstance(data, bytearray):
            return ''.join(format(i, '08b') for i in data)
        elif isinstance(data, int):
            return format(data, '08b')
        else:
            raise TypeError("Unsupported data type.")

    def encode(self, image_path, message, output_path):
        """Encode a message into an image using LSB steganography."""
        image = Image.open(image_path)
        image_array = np.array(image)
        flat_pixels = image_array.flatten()

        message += '###'  # Delimiter to indicate end of message
        binary_message = self.to_bin(message)
        datalen = len(binary_message)

        if datalen > flat_pixels.size:
            raise ValueError("Message is too long to encode in the image.")
        
        flat_pixels[:datalen] &= 0b11111110  # Clear the least significant bit
        flat_pixels[:datalen] |= np.array(list(map(int, binary_message)), dtype=np.uint8)

        encoded_image = flat_pixels.reshape(image_array.shape)
        encoded_image = Image.fromarray(encoded_image, mode=image.mode)
        encoded_image.save(output_path)

    def decode(self, image_path):
        """Decode the hidden message from an image."""
        image = Image.open(image_path)
        pixels = list(image.getdata())

        binary_data = ''
        for pixel in pixels:
            for channel in pixel[:3]:
                binary_data += str(channel & 1)

        message = ''
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i:i+8]
            char = chr(int(byte, 2))
            message += char
            if message.endswith('###'):
                break
        if not message.endswith('###'):
            return "No hidden message found or message is incomplete."

        return message[:-3]
