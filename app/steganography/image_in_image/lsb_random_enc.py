from PIL import Image
import numpy as np
import random
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from ..base import SteganographyBase


class ImageInImageLSBRandomEnc(SteganographyBase):
    """
    Enhanced LSB Steganography implementation for hiding a secret image inside a cover image with:
    1. Pseudorandom pixel selection
    2. Image data encryption
    3. Key derivation for both pixel selection and encryption

    This provides maximum security for image-in-image steganography.
    """

    def __init__(self, key="default_key"):
        """Initialize with a master key for both pixel selection and encryption."""
        super().__init__()
        self.master_key = key
        # Derive separate keys for pixel selection and encryption
        self._setup_keys()

    def _setup_keys(self):
        """Setup different keys for pixel selection and encryption using key derivation."""
        # Use master key to derive two different keys
        encryption_salt = b"image_encryption_salt"

        # Key for pixel selection (use SHA-256 for consistency with original implementation)
        pixel_key = hashlib.sha256(f"{self.master_key}_pixel".encode()).hexdigest()
        self.pixel_key = pixel_key

        # Key for encryption (use PBKDF2 for secure key derivation)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=encryption_salt,
            iterations=480000,
        )
        encryption_key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        self.fernet = Fernet(encryption_key)

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

        return sorted(positions)  # Sort for consistent access pattern

    def _serialize_image_data(self, image_array):
        """
        Serialize image array to bytes for encryption.

        Args:
            image_array: NumPy array of image data

        Returns:
            bytes: Serialized image data
        """
        # Convert to bytes and add metadata
        height, width, channels = image_array.shape

        # Create header with dimensions
        header = f"{width},{height},{channels}:".encode()

        # Flatten image data and convert to bytes
        image_bytes = image_array.flatten().tobytes()

        return header + image_bytes

    def _deserialize_image_data(self, data_bytes):
        """
        Deserialize bytes back to image array.

        Args:
            data_bytes: Serialized image data

        Returns:
            numpy.ndarray: Image array
        """
        # Find the separator
        separator = b":"
        header_end = data_bytes.find(separator)
        if header_end == -1:
            raise ValueError("Invalid serialized image data format")

        # Parse header
        header = data_bytes[:header_end].decode()
        width, height, channels = map(int, header.split(","))

        # Extract image data
        image_data = data_bytes[header_end + 1 :]

        # Convert back to numpy array
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        image_array = image_array.reshape((height, width, channels))

        return image_array

    def encode(self, cover_image_path, secret_image_path, output_path, key=None):
        """
        Hide and encrypt a secret image inside a cover image using LSB steganography
        with pseudorandom pixel selection.

        Args:
            cover_image_path (str): Path to the cover image
            secret_image_path (str): Path to the secret image to hide
            output_path (str): Path to save the stego image
            key (str, optional): Override the instance key for this operation

        Raises:
            ValueError: If images cannot be loaded or secret image is too large
        """
        if key is not None:
            self.master_key = key
            self._setup_keys()

        try:
            # Load images
            cover_image = Image.open(cover_image_path).convert("RGB")
            secret_image = Image.open(secret_image_path).convert("RGB")

            # Get image dimensions
            cover_width, cover_height = cover_image.size
            secret_width, secret_height = secret_image.size

            print(f"Cover image: {cover_width}x{cover_height}")
            print(f"Secret image: {secret_width}x{secret_height}")
            print(f"Using encrypted pseudorandom pixel selection")

            # Convert secret image to numpy array and serialize
            secret_array = np.array(secret_image)
            serialized_data = self._serialize_image_data(secret_array)

            # Encrypt the serialized image data
            encrypted_data = self.fernet.encrypt(serialized_data)

            # Convert encrypted data to binary
            encrypted_binary = "".join(format(byte, "08b") for byte in encrypted_data)
            data_length = len(encrypted_binary)

            # Check if encrypted data can fit in cover image
            cover_pixels = cover_width * cover_height * 3  # 3 color channels
            required_positions = 32 + data_length  # 32 bits for length + encrypted data

            if required_positions > cover_pixels:
                raise ValueError(
                    f"Encrypted secret image is too large. Required: {required_positions} positions, "
                    f"Available: {cover_pixels} positions"
                )

            # Convert cover image to numpy array
            cover_array = np.array(cover_image)
            cover_flat = cover_array.flatten()

            # First, generate positions for storing data length (32 bits)
            length_positions = self.generate_pixel_positions(
                self.pixel_key + "_length", cover_pixels, 32
            )

            # Then generate positions for the encrypted data, excluding length positions
            data_positions = self.generate_pixel_positions(
                self.pixel_key + "_data",
                cover_pixels,
                data_length,
                exclude_positions=length_positions,
            )

            # Embed data length (32 bits)
            length_bits = format(data_length, "032b")
            for i, bit in enumerate(length_bits):
                pos = length_positions[i]
                cover_flat[pos] = (cover_flat[pos] & 0xFE) | int(bit)

            # Embed encrypted data
            for i, bit in enumerate(encrypted_binary):
                pos = data_positions[i]
                cover_flat[pos] = (cover_flat[pos] & 0xFE) | int(bit)

            # Reshape back to original dimensions
            stego_array = cover_flat.reshape(cover_array.shape)

            # Convert back to PIL Image and save
            stego_image = Image.fromarray(stego_array.astype(np.uint8))
            stego_image.save(output_path)

            print(
                f"Successfully embedded encrypted secret image. Stego image saved to: {output_path}"
            )

        except Exception as e:
            raise ValueError(f"Error during encoding: {str(e)}")

    def decode(self, stego_image_path, output_path, key=None):
        """
        Extract and decrypt a hidden image from a stego image using pseudorandom pixel selection.

        Args:
            stego_image_path (str): Path to the stego image
            output_path (str): Path to save the extracted secret image
            key (str, optional): Override the instance key for this operation

        Returns:
            str: Path to the extracted image

        Raises:
            ValueError: If image cannot be loaded or extraction fails
            RuntimeError: If extracted data length is invalid or decryption fails
        """
        if key is not None:
            self.master_key = key
            self._setup_keys()

        try:
            # Load stego image
            stego_image = Image.open(stego_image_path).convert("RGB")
            stego_array = np.array(stego_image)
            stego_flat = stego_array.flatten()

            cover_pixels = len(stego_flat)

            # Generate positions for extracting data length (32 bits)
            length_positions = self.generate_pixel_positions(
                self.pixel_key + "_length", cover_pixels, 32
            )

            # Extract data length
            length_bits = ""
            for i in range(32):
                pos = length_positions[i]
                length_bits += str(stego_flat[pos] & 1)
            data_length = int(length_bits, 2)

            # Validate data length
            if data_length <= 0 or data_length > cover_pixels:
                raise RuntimeError(
                    "Invalid encrypted data length detected. This usually means:\n"
                    "1. The decryption key is incorrect\n"
                    "2. The image has been modified\n"
                    "3. The image does not contain a hidden image"
                )

            print(f"Extracting encrypted data of length: {data_length} bits")

            # Generate positions for extracting encrypted data, excluding length positions
            data_positions = self.generate_pixel_positions(
                self.pixel_key + "_data",
                cover_pixels,
                data_length,
                exclude_positions=length_positions,
            )

            # Extract encrypted data bits
            encrypted_bits = ""
            for i in range(data_length):
                pos = data_positions[i]
                encrypted_bits += str(stego_flat[pos] & 1)

            # Convert bits to bytes
            encrypted_bytes = bytearray()
            for i in range(0, len(encrypted_bits), 8):
                if i + 8 <= len(encrypted_bits):
                    byte_bits = encrypted_bits[i : i + 8]
                    encrypted_bytes.append(int(byte_bits, 2))

            try:
                # Decrypt the data
                decrypted_data = self.fernet.decrypt(bytes(encrypted_bytes))

                # Deserialize back to image array
                secret_array = self._deserialize_image_data(decrypted_data)

                # Convert to PIL Image and save
                secret_image = Image.fromarray(secret_array.astype(np.uint8))
                secret_image.save(output_path)

                print(
                    f"Successfully extracted and decrypted secret image. Saved to: {output_path}"
                )
                return output_path

            except Exception as e:
                raise RuntimeError(
                    "Failed to decrypt the extracted data. The encryption key is incorrect or the data is corrupted."
                )

        except Exception as e:
            if isinstance(e, RuntimeError):
                raise e
            raise ValueError(f"Error during decoding: {str(e)}")

    def calculate_capacity(self, cover_image_path):
        """
        Calculate the maximum size of secret image that can be embedded (considering encryption overhead).

        Args:
            cover_image_path (str): Path to the cover image

        Returns:
            dict: Maximum dimensions and encryption overhead information
        """
        try:
            cover_image = Image.open(cover_image_path)
            width, height = cover_image.size
            total_pixels = width * height

            # Available positions (3 color channels)
            available_positions = total_pixels * 3

            # Subtract positions needed for data length (32 positions)
            usable_positions = available_positions - 32

            # Estimate encryption overhead (Fernet adds ~57 bytes of overhead)
            # Plus our serialization header (estimated ~20 bytes)
            estimated_overhead_bytes = 77
            estimated_overhead_bits = estimated_overhead_bytes * 8

            # Calculate maximum raw image data size in bits
            max_raw_bits = usable_positions - estimated_overhead_bits

            # Convert to bytes and then to RGB pixels
            max_raw_bytes = max_raw_bits // 8
            max_secret_pixels = max_raw_bytes // 3  # 3 bytes per RGB pixel

            # Calculate approximate square dimensions
            max_side = int(np.sqrt(max_secret_pixels)) if max_secret_pixels > 0 else 0

            return {
                "cover_dimensions": f"{width}x{height}",
                "cover_total_pixels": total_pixels,
                "max_secret_pixels": max_secret_pixels,
                "max_square_dimensions": f"{max_side}x{max_side}",
                "available_positions": available_positions,
                "usable_positions": usable_positions,
                "estimated_overhead_bits": estimated_overhead_bits,
                "key": self.master_key,
            }

        except Exception as e:
            raise ValueError(f"Error calculating capacity: {str(e)}")
