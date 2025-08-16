from PIL import Image
import numpy as np
from ..base import SteganographyBase


class ImageInImageLSB(SteganographyBase):
    """
    LSB Steganography implementation for hiding a secret image inside a cover image.

    This implementation embeds the least significant bits of the secret image
    into the least significant bits of the cover image.
    """

    def __init__(self):
        """Initialize the Image-in-Image LSB steganography class."""
        super().__init__()

    def encode(self, cover_image_path, secret_image_path, output_path):
        """
        Hide a secret image inside a cover image using LSB steganography.

        Args:
            cover_image_path (str): Path to the cover image
            secret_image_path (str): Path to the secret image to hide
            output_path (str): Path to save the stego image

        Raises:
            ValueError: If images cannot be loaded or secret image is too large
        """
        try:
            # Load images
            cover_image = Image.open(cover_image_path).convert("RGB")
            secret_image = Image.open(secret_image_path).convert("RGB")

            # Get image dimensions
            cover_width, cover_height = cover_image.size
            secret_width, secret_height = secret_image.size

            # Check if secret image can fit in cover image
            cover_pixels = cover_width * cover_height
            secret_pixels = secret_width * secret_height

            # We need space for secret image dimensions (2 * 32 bits) + secret image data
            required_bits = 64 + (secret_pixels * 24)  # 24 bits per RGB pixel
            available_bits = cover_pixels * 3  # 3 color channels, 1 bit each

            if required_bits > available_bits:
                raise ValueError(
                    f"Secret image is too large. Required: {required_bits} bits, "
                    f"Available: {available_bits} bits"
                )

            print(f"Cover image: {cover_width}x{cover_height}")
            print(f"Secret image: {secret_width}x{secret_height}")
            print(f"Embedding {secret_pixels} pixels into {cover_pixels} pixels")

            # Convert images to numpy arrays
            cover_array = np.array(cover_image)
            secret_array = np.array(secret_image)

            # Flatten arrays for easier processing
            cover_flat = cover_array.flatten()
            secret_flat = secret_array.flatten()

            # Embed secret image dimensions first (32 bits each for width and height)
            bit_index = 0

            # Embed secret width
            width_bits = format(secret_width, "032b")
            for bit in width_bits:
                cover_flat[bit_index] = (cover_flat[bit_index] & 0xFE) | int(bit)
                bit_index += 1

            # Embed secret height
            height_bits = format(secret_height, "032b")
            for bit in height_bits:
                cover_flat[bit_index] = (cover_flat[bit_index] & 0xFE) | int(bit)
                bit_index += 1

            # Embed secret image data
            for pixel_value in secret_flat:
                # Convert pixel value to 8-bit binary
                pixel_bits = format(pixel_value, "08b")

                # Embed each bit of the pixel
                for bit in pixel_bits:
                    if bit_index >= len(cover_flat):
                        raise ValueError("Cover image is too small for secret image")

                    # Clear LSB and set to secret bit
                    cover_flat[bit_index] = (cover_flat[bit_index] & 0xFE) | int(bit)
                    bit_index += 1

            # Reshape back to original dimensions
            stego_array = cover_flat.reshape(cover_array.shape)

            # Convert back to PIL Image and save
            stego_image = Image.fromarray(stego_array.astype(np.uint8))
            stego_image.save(output_path)

            print(
                f"Successfully embedded secret image. Stego image saved to: {output_path}"
            )

        except Exception as e:
            raise ValueError(f"Error during encoding: {str(e)}")

    def decode(self, stego_image_path, output_path):
        """
        Extract a hidden image from a stego image.

        Args:
            stego_image_path (str): Path to the stego image
            output_path (str): Path to save the extracted secret image

        Returns:
            str: Path to the extracted image

        Raises:
            ValueError: If image cannot be loaded or extraction fails
            RuntimeError: If extracted dimensions are invalid
        """
        try:
            # Load stego image
            stego_image = Image.open(stego_image_path).convert("RGB")
            stego_array = np.array(stego_image)
            stego_flat = stego_array.flatten()

            bit_index = 0

            # Extract secret image width (first 32 bits)
            width_bits = ""
            for _ in range(32):
                width_bits += str(stego_flat[bit_index] & 1)
                bit_index += 1
            secret_width = int(width_bits, 2)

            # Extract secret image height (next 32 bits)
            height_bits = ""
            for _ in range(32):
                height_bits += str(stego_flat[bit_index] & 1)
                bit_index += 1
            secret_height = int(height_bits, 2)

            # Validate dimensions
            if secret_width <= 0 or secret_height <= 0:
                raise RuntimeError(
                    f"Invalid extracted dimensions: {secret_width}x{secret_height}"
                )

            if secret_width > 10000 or secret_height > 10000:
                raise RuntimeError(
                    f"Extracted dimensions too large: {secret_width}x{secret_height}"
                )

            print(f"Extracting secret image of size: {secret_width}x{secret_height}")

            # Extract secret image data
            secret_pixels = secret_width * secret_height * 3  # RGB channels
            secret_data = []

            for _ in range(secret_pixels):
                # Extract 8 bits for each pixel component
                pixel_bits = ""
                for _ in range(8):
                    if bit_index >= len(stego_flat):
                        raise RuntimeError(
                            "Unexpected end of data while extracting secret image"
                        )

                    pixel_bits += str(stego_flat[bit_index] & 1)
                    bit_index += 1

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

            # Available bits (3 color channels, 1 bit each)
            available_bits = total_pixels * 3

            # Subtract bits needed for dimensions (64 bits)
            usable_bits = available_bits - 64

            # Each secret pixel needs 24 bits (8 bits × 3 channels)
            max_secret_pixels = usable_bits // 24

            # Calculate approximate square dimensions
            max_side = int(np.sqrt(max_secret_pixels))

            return {
                "cover_dimensions": f"{width}x{height}",
                "cover_total_pixels": total_pixels,
                "max_secret_pixels": max_secret_pixels,
                "max_square_dimensions": f"{max_side}x{max_side}",
                "available_bits": available_bits,
                "usable_bits": usable_bits,
            }

        except Exception as e:
            raise ValueError(f"Error calculating capacity: {str(e)}")
