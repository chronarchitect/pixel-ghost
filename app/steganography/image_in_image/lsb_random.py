from PIL import Image
import numpy as np
import random
import hashlib
from ..base import SteganographyBase


class ImageInImageLSBRandom(SteganographyBase):
    """
    LSB Steganography implementation for hiding a secret image inside a cover image
    using pseudorandom pixel selection.

    This implementation uses a key to generate pseudorandom pixel positions for
    enhanced security, making it harder to detect the hidden image.
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

    def encode(self, cover_image_path, secret_image_path, output_path, key=None):
        """
        Hide a secret image inside a cover image using LSB steganography with pseudorandom pixel selection.

        Args:
            cover_image_path (str): Path to the cover image
            secret_image_path (str): Path to the secret image to hide
            output_path (str): Path to save the stego image
            key (str, optional): Override the instance key for this operation

        Raises:
            ValueError: If images cannot be loaded or secret image is too large
        """
        if key is not None:
            self.key = key

        try:
            # Load images
            cover_image = Image.open(cover_image_path).convert("RGB")
            secret_image = Image.open(secret_image_path).convert("RGB")

            # Get image dimensions
            cover_width, cover_height = cover_image.size
            secret_width, secret_height = secret_image.size

            # Check if secret image can fit in cover image
            cover_pixels = cover_width * cover_height * 3  # 3 color channels
            secret_pixels = secret_width * secret_height * 3  # 3 color channels

            # We need space for secret image dimensions (2 * 32 bits) + secret image data (8 bits per channel)
            required_positions = 64 + (secret_pixels * 8)  # 8 bits per pixel component

            if required_positions > cover_pixels:
                raise ValueError(
                    f"Secret image is too large. Required: {required_positions} positions, "
                    f"Available: {cover_pixels} positions"
                )

            print(f"Cover image: {cover_width}x{cover_height}")
            print(f"Secret image: {secret_width}x{secret_height}")
            print(f"Using pseudorandom pixel selection with key: {self.key}")

            # Convert images to numpy arrays
            cover_array = np.array(cover_image)
            secret_array = np.array(secret_image)

            # Flatten arrays for easier processing
            cover_flat = cover_array.flatten()
            secret_flat = secret_array.flatten()

            # First, generate positions for storing dimensions (64 bits)
            dimension_positions = self.generate_pixel_positions(
                self.key + "_dimensions", cover_pixels, 64
            )

            # Then generate positions for the secret image data, excluding dimension positions
            data_positions = self.generate_pixel_positions(
                self.key + "_data",
                cover_pixels,
                secret_pixels * 8,  # 8 bits per pixel component
                exclude_positions=dimension_positions,
            )

            # Embed secret image dimensions
            # Embed secret width (32 bits)
            width_bits = format(secret_width, "032b")
            for i, bit in enumerate(width_bits):
                pos = dimension_positions[i]
                cover_flat[pos] = (cover_flat[pos] & 0xFE) | int(bit)

            # Embed secret height (32 bits)
            height_bits = format(secret_height, "032b")
            for i, bit in enumerate(height_bits):
                pos = dimension_positions[32 + i]
                cover_flat[pos] = (cover_flat[pos] & 0xFE) | int(bit)

            # Embed secret image data
            data_bit_index = 0
            for pixel_value in secret_flat:
                # Convert pixel value to 8-bit binary
                pixel_bits = format(pixel_value, "08b")

                # Embed each bit of the pixel
                for bit in pixel_bits:
                    pos = data_positions[data_bit_index]
                    cover_flat[pos] = (cover_flat[pos] & 0xFE) | int(bit)
                    data_bit_index += 1

            # Reshape back to original dimensions
            stego_array = cover_flat.reshape(cover_array.shape)

            # Convert back to PIL Image and save
            stego_image = Image.fromarray(stego_array.astype(np.uint8))
            stego_image.save(output_path)

            print(
                f"Successfully embedded secret image using random positions. Stego image saved to: {output_path}"
            )

        except Exception as e:
            raise ValueError(f"Error during encoding: {str(e)}")

    def decode(self, stego_image_path, output_path, key=None):
        """
        Extract a hidden image from a stego image using pseudorandom pixel selection.

        Args:
            stego_image_path (str): Path to the stego image
            output_path (str): Path to save the extracted secret image
            key (str, optional): Override the instance key for this operation

        Returns:
            str: Path to the extracted image

        Raises:
            ValueError: If image cannot be loaded or extraction fails
            RuntimeError: If extracted dimensions are invalid or key is incorrect
        """
        if key is not None:
            self.key = key

        try:
            # Load stego image
            stego_image = Image.open(stego_image_path).convert("RGB")
            stego_array = np.array(stego_image)
            stego_flat = stego_array.flatten()

            cover_pixels = len(stego_flat)

            # Generate positions for extracting dimensions (64 bits)
            dimension_positions = self.generate_pixel_positions(
                self.key + "_dimensions", cover_pixels, 64
            )

            # Extract secret image width (first 32 bits)
            width_bits = ""
            for i in range(32):
                pos = dimension_positions[i]
                width_bits += str(stego_flat[pos] & 1)
            secret_width = int(width_bits, 2)

            # Extract secret image height (next 32 bits)
            height_bits = ""
            for i in range(32, 64):
                pos = dimension_positions[i]
                height_bits += str(stego_flat[pos] & 1)
            secret_height = int(height_bits, 2)

            # Validate dimensions
            if secret_width <= 0 or secret_height <= 0:
                raise RuntimeError(
                    "Invalid extracted dimensions. This usually means:\n"
                    "1. The key is incorrect\n"
                    "2. The image has been modified\n"
                    "3. The image does not contain a hidden image"
                )

            if secret_width > 10000 or secret_height > 10000:
                raise RuntimeError(
                    f"Extracted dimensions too large: {secret_width}x{secret_height}. "
                    "The key might be incorrect."
                )

            print(f"Extracting secret image of size: {secret_width}x{secret_height}")

            # Calculate required data positions
            secret_pixels = secret_width * secret_height * 3  # RGB channels

            # Generate positions for extracting secret image data, excluding dimension positions
            data_positions = self.generate_pixel_positions(
                self.key + "_data",
                cover_pixels,
                secret_pixels * 8,  # 8 bits per pixel component
                exclude_positions=dimension_positions,
            )

            # Extract secret image data
            secret_data = []
            data_bit_index = 0

            for _ in range(secret_pixels):
                # Extract 8 bits for each pixel component
                pixel_bits = ""
                for _ in range(8):
                    if data_bit_index >= len(data_positions):
                        raise RuntimeError(
                            "Unexpected end of data while extracting secret image"
                        )

                    pos = data_positions[data_bit_index]
                    pixel_bits += str(stego_flat[pos] & 1)
                    data_bit_index += 1

                # Convert bits to pixel value
                pixel_value = int(pixel_bits, 2)
                secret_data.append(pixel_value)

            # Reshape to image dimensions
            secret_array = np.array(secret_data).reshape(
                (secret_height, secret_width, 3)
            )

            # Convert to PIL Image and save
            secret_image = Image.fromarray(secret_array.astype(np.uint8))
            secret_image.save(output_path)

            print(f"Successfully extracted secret image. Saved to: {output_path}")
            return output_path

        except Exception as e:
            if isinstance(e, RuntimeError):
                raise e
            raise ValueError(f"Error during decoding: {str(e)}")

    def calculate_capacity(self, cover_image_path):
        """
        Calculate the maximum size of secret image that can be embedded.

        Args:
            cover_image_path (str): Path to the cover image

        Returns:
            dict: Maximum dimensions and total pixels that can be embedded
        """
        try:
            cover_image = Image.open(cover_image_path)
            width, height = cover_image.size
            total_pixels = width * height

            # Available positions (3 color channels)
            available_positions = total_pixels * 3

            # Subtract positions needed for dimensions (64 positions)
            usable_positions = available_positions - 64

            # Each secret pixel component needs 8 positions
            max_secret_pixel_components = usable_positions // 8

            # Each secret pixel has 3 components (RGB)
            max_secret_pixels = max_secret_pixel_components // 3

            # Calculate approximate square dimensions
            max_side = int(np.sqrt(max_secret_pixels))

            return {
                "cover_dimensions": f"{width}x{height}",
                "cover_total_pixels": total_pixels,
                "max_secret_pixels": max_secret_pixels,
                "max_square_dimensions": f"{max_side}x{max_side}",
                "available_positions": available_positions,
                "usable_positions": usable_positions,
                "key": self.key,
            }

        except Exception as e:
            raise ValueError(f"Error calculating capacity: {str(e)}")
