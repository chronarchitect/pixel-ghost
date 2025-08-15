from PIL import Image
import numpy as np
import random
import hashlib
from steganography.base import SteganographyBase


class LSBRandom(SteganographyBase):
    """
    Least Significant Bit (LSB) steganography implementation with pseudorandom pixel selection.

    This implementation uses a key to generate pseudorandom pixel positions for increased security.
    """

    def __init__(self, key="default_key"):
        """Initialize with a key for pseudorandom number generation."""
        super().__init__()
        self.key = key

    def generate_pixel_positions(
        self, key, max_pixels, num_positions, exclude_positions=None
    ):
        """
        Generate pseudorandom unique pixel positions using a key.

        Args:
            key: The key to use for random seed
            max_pixels: Maximum number of pixels available
            num_positions: Number of positions to generate
            exclude_positions: List of positions to exclude (to avoid overlap)

        Returns:
            List of unique pixel positions
        """
        # Create a seed from the key using SHA-256
        seed = int(hashlib.sha256(key.encode()).hexdigest(), 16)
        random.seed(seed)

        if exclude_positions:
            # Create a set of available positions excluding the ones we want to avoid
            available_positions = set(range(max_pixels)) - set(exclude_positions)
            if len(available_positions) < num_positions:
                raise ValueError("Not enough available positions after exclusion")

            # Convert back to list and sample from it
            positions = random.sample(list(available_positions), num_positions)
        else:
            # If no positions to exclude, sample directly from the range
            positions = random.sample(range(max_pixels), num_positions)

        return positions

    def to_bin(self, data):
        """Convert data to binary format as string."""
        if isinstance(data, str):
            return "".join(format(ord(i), "08b") for i in data)
        elif isinstance(data, bytes) or isinstance(data, bytearray):
            return "".join(format(i, "08b") for i in data)
        elif isinstance(data, int):
            return format(data, "08b")
        else:
            raise TypeError("Unsupported data type.")

    def encode(self, image_path, message, output_path, key=None):
        """
        Encode a message into an image using LSB steganography with pseudorandom pixel selection.

        Args:
            image_path (str): Path to the cover image
            message (str): Message to hide
            output_path (str): Path to save the stego image
            key (str, optional): Override the instance key for this operation
        """
        if key is not None:
            self.key = key

        image = Image.open(image_path)
        image_array = np.array(image)
        flat_pixels = image_array.flatten()

        binary_message = self.to_bin(message)
        datalen = len(binary_message)

        if datalen > flat_pixels.size:
            raise ValueError("Message is too long to encode in the image.")

        # First, generate positions for the length (32 bits)
        length_binary = format(datalen, "032b")  # 32 bits for length
        length_positions = self.generate_pixel_positions(
            self.key + "_length", flat_pixels.size, 32
        )

        # Then generate positions for the message, excluding the length positions
        pixel_positions = self.generate_pixel_positions(
            self.key, flat_pixels.size, datalen, exclude_positions=length_positions
        )

        # Embed message length
        for i, pos in enumerate(length_positions):
            flat_pixels[pos] &= 0b11111110  # Clear LSB
            flat_pixels[pos] |= int(length_binary[i])

        # Embed message
        for i, pos in enumerate(pixel_positions):
            flat_pixels[pos] &= 0b11111110  # Clear LSB
            flat_pixels[pos] |= int(binary_message[i])

        encoded_image = flat_pixels.reshape(image_array.shape)
        # Convert to PIL Image without deprecated mode parameter
        encoded_image = Image.fromarray(encoded_image)
        encoded_image.save(output_path)

    def decode(self, image_path, key=None):
        """
        Decode an LSB hidden message from an image using pseudorandom pixel selection.

        Args:
            image_path (str): Path to the stego image
            key (str, optional): Override the instance key for this operation

        Returns:
            str: The hidden message or error message if no valid message is found

        Raises:
            ValueError: If the image cannot be read or if the key is invalid
            RuntimeError: If the extracted message length is invalid
        """
        if key is not None:
            self.key = key

        try:
            image = Image.open(image_path)
        except Exception as e:
            raise ValueError(f"Could not open image file: {str(e)}")

        image_array = np.array(image)
        flat_pixels = image_array.flatten()

        try:
            # First, extract the length
            length_positions = self.generate_pixel_positions(
                self.key + "_length", flat_pixels.size, 32
            )
            length_binary = ""
            for pos in length_positions:
                length_binary += str(flat_pixels[pos] & 1)
            datalen = int(length_binary, 2)

            # Validate the extracted length
            if datalen <= 0 or datalen > flat_pixels.size:
                raise RuntimeError(
                    "Invalid message length detected. This is usually because one or more of the following:\n"
                    "1. The key is incorrect\n"
                    "2. The image has been modified\n"
                    "3. The image does not contain a hidden message"
                )

        except ValueError as e:
            raise RuntimeError(f"Failed to extract message length: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error while decoding: {str(e)}")

        # Generate pixel positions for message extraction, excluding length positions
        pixel_positions = self.generate_pixel_positions(
            self.key, flat_pixels.size, datalen, exclude_positions=length_positions
        )

        # Extract LSBs from the selected positions
        binary_data = ""
        for pos in pixel_positions:
            binary_data += str(flat_pixels[pos] & 1)

        # Convert every 8 bits to a character
        chars = [
            chr(int(binary_data[i : i + 8], 2)) for i in range(0, len(binary_data), 8)
        ]
        return "".join(chars)
