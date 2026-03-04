from PIL import Image
import numpy as np
from ..base import SteganographyBase


class LSB(SteganographyBase):
    """
    Least Significant Bit (LSB) steganography implementation.

        This class extends the SteganographyBase class to implement LSB steganography
        for encoding and decoding messages in images.
    """

    def to_bin(self, data):
        """Convert data to binary format as string."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        if isinstance(data, (bytes, bytearray)):
            return "".join(format(i, "08b") for i in data)
        elif isinstance(data, int):
            return format(data, "08b")
        else:
            raise TypeError("Unsupported data type.")

    def check_capacity(self, image_path, message):
        """
        Check if the message can fit in the image.
        Returns (can_fit, required_bits, available_bits)
        """
        image = Image.open(image_path)
        image_array = np.array(image)
        available_bits = image_array.size
        
        message_with_delimiter = message + "###"
        required_bits = len(message_with_delimiter.encode("utf-8")) * 8
        
        return required_bits <= available_bits, required_bits, available_bits

    def encode(self, image_path, message, output_path):
        """Encode a message into an image using LSB steganography."""
        image = Image.open(image_path)
        image_array = np.array(image)
        flat_pixels = image_array.flatten()

        message += "###"  # Delimiter to indicate end of message
        binary_message = self.to_bin(message)
        datalen = len(binary_message)

        if datalen > flat_pixels.size:
            raise ValueError("Message is too long to encode in the image.")

        flat_pixels[:datalen] &= 0b11111110  # Clear the least significant bit
        flat_pixels[:datalen] |= np.array(
            list(map(int, binary_message)), dtype=np.uint8
        )

        encoded_image = flat_pixels.reshape(image_array.shape)
        encoded_image = Image.fromarray(encoded_image)
        encoded_image.save(output_path)

        return output_path

    def decode(self, image_path):
        """Efficiently decode an LSB hidden message from an image using NumPy."""
        image = Image.open(image_path)
        image_array = np.array(image)

        flat_pixels = image_array.flatten()

        # Extract the LSBs
        lsb_array = flat_pixels & 1
        binary_data = "".join(map(str, lsb_array.tolist()))

        # Convert every 8 bits to a byte
        bytes_data = bytearray()
        for i in range(0, len(binary_data), 8):
            bytes_data.append(int(binary_data[i : i + 8], 2))
        
        try:
            message = bytes_data.decode("utf-8", errors="replace")
        except Exception:
            message = bytes_data.decode("latin-1", errors="replace")

        end_idx = message.find("###")
        if end_idx == -1:
            return "No hidden message found or message is incomplete."

        return message[:end_idx]
