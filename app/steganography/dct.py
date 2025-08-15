import cv2
import numpy as np
from steganography.base import SteganographyBase


class DCT(SteganographyBase):
    """
    Discrete Cosine Transform (DCT) steganography implementation.

    This class extends the SteganographyBase class to implement DCT
    steganography for encoding and decoding images within images.
    """

    def __init__(self):
        super().__init__()

    def get_metadata_area(self):
        """Return the dimensions of the reserved metadata area (in blocks)."""
        return 1, 1  # Reserve 1x1 blocks (8x8 pixels) for metadata

    def store_dimensions(self, img, height, width):
        """
        Store dimensions in a reserved area before DCT blocks begin.

        Uses 2 bytes each for height and width (allows dimensions up to 65535).
        """
        # Convert dimensions to bytes
        height_bytes = height.to_bytes(2, byteorder="big")
        width_bytes = width.to_bytes(2, byteorder="big")

        # Store in the reserved metadata block (first 8x8 block)
        # This block won't be processed by DCT
        if len(img.shape) == 3:
            # Store in first channel only
            img[0:8, 0:8, 0] = 0  # Clear the block
            img[0, 0, 0] = height_bytes[0]
            img[0, 1, 0] = height_bytes[1]
            img[0, 2, 0] = width_bytes[0]
            img[0, 3, 0] = width_bytes[1]
        else:
            img[0:8, 0:8] = 0  # Clear the block
            img[0, 0] = height_bytes[0]
            img[0, 1] = height_bytes[1]
            img[0, 2] = width_bytes[0]
            img[0, 3] = width_bytes[1]
        return img

    def read_dimensions(self, img):
        """Read dimensions from the reserved metadata area."""
        # Read bytes from the reserved metadata block
        if len(img.shape) == 3:
            height_bytes = bytes([img[0, 0, 0], img[0, 1, 0]])
            width_bytes = bytes([img[0, 2, 0], img[0, 3, 0]])
        else:
            height_bytes = bytes([img[0, 0], img[0, 1]])
            width_bytes = bytes([img[0, 2], img[0, 3]])

        # Convert bytes back to integers
        height = int.from_bytes(height_bytes, byteorder="big")
        width = int.from_bytes(width_bytes, byteorder="big")
        return height, width

    def prepare_image(self, image_path, target_size=None):
        """Read and prepare image for DCT processing."""
        # Read image in BGR format (OpenCV default)
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")

        # Resize if target_size is specified
        # It may distort the image slightly because of aspect ratio changes
        if target_size is not None:
            img = cv2.resize(img, (target_size[1], target_size[0]))

        # Ensure dimensions are multiples of 8 for DCT blocks
        height = img.shape[0] - (img.shape[0] % 8)
        width = img.shape[1] - (img.shape[1] % 8)

        # Crop to dimensions that are multiples of 8
        if len(img.shape) == 3:
            img = img[:height, :width, :]
        else:
            img = img[:height, :width]

        return img

    def embed_bit(self, dct_block, bit):
        """Embed a single bit into a DCT block."""
        # We'll use the middle band coefficients for embedding
        # Modify the (4,3) coefficient to encode the bit
        if bit == 1:
            if dct_block[4, 3] <= 0:
                dct_block[4, 3] = 1
        else:
            if dct_block[4, 3] > 0:
                dct_block[4, 3] = -1
        return dct_block

    def embed_channel(self, cover_channel, secret_binary, stego_channel):
        """Embed binary data into a single channel using DCT."""
        height, width = cover_channel.shape
        bit_count = 0
        secret_size = len(secret_binary)

        # Get metadata area dimensions
        meta_blocks_h, meta_blocks_w = self.get_metadata_area()
        meta_height = meta_blocks_h * 8
        meta_width = meta_blocks_w * 8

        # Start after the metadata area
        for i in range(meta_height, height - 8 + 1, 8):
            for j in range(0 if i > meta_height else meta_width, width - 8 + 1, 8):
                if bit_count >= secret_size:
                    break

                # Get 8x8 block and apply DCT
                block = cover_channel[i : i + 8, j : j + 8].astype(float)
                dct_block = cv2.dct(block)

                # Embed one bit of secret data
                if bit_count < secret_size:
                    dct_block = self.embed_bit(dct_block, secret_binary[bit_count])
                    bit_count += 1

                # Inverse DCT and update stego image
                idct_block = cv2.idct(dct_block)
                stego_channel[i : i + 8, j : j + 8] = np.clip(idct_block, 0, 255)

        return bit_count

    def extract_bit(self, dct_block):
        """Extract a single bit from a DCT block."""
        return 1 if dct_block[4, 3] > 0 else 0

    def extract_channel(self, stego_channel, total_bits):
        """Extract bits from a single channel using DCT."""
        height, width = stego_channel.shape
        extracted_bits = []

        # Get metadata area dimensions
        meta_blocks_h, meta_blocks_w = self.get_metadata_area()
        meta_height = meta_blocks_h * 8
        meta_width = meta_blocks_w * 8

        # Start after the metadata area
        for i in range(meta_height, height - 8 + 1, 8):
            if len(extracted_bits) >= total_bits:
                break
            for j in range(0 if i > meta_height else meta_width, width - 8 + 1, 8):
                if len(extracted_bits) >= total_bits:
                    break

                # Get 8x8 block and apply DCT
                block = stego_channel[i : i + 8, j : j + 8].astype(float)
                dct_block = cv2.dct(block)

                # Extract one bit
                bit = self.extract_bit(dct_block)
                extracted_bits.append(bit)

        return extracted_bits

    def encode(self, cover_path, secret_path, output_path):
        """Embed secret image into cover image using DCT."""
        # Read cover image keeping original color space (BGR)
        cover_img = self.prepare_image(cover_path)

        # Get metadata area size and calculate available blocks
        meta_blocks_h, meta_blocks_w = self.get_metadata_area()
        available_blocks = ((cover_img.shape[0] // 8) * (cover_img.shape[1] // 8)) - (
            meta_blocks_h * meta_blocks_w
        )

        # Calculate maximum secret image size that can fit
        max_bits_per_channel = available_blocks
        if len(cover_img.shape) == 3:
            max_bits = max_bits_per_channel * 3
        else:
            max_bits = max_bits_per_channel

        # Read secret image
        secret_img = self.prepare_image(secret_path)
        total_pixels = max_bits // (24 if len(secret_img.shape) == 3 else 8)

        # Calculate target size while maintaining aspect ratio
        aspect_ratio = secret_img.shape[1] / secret_img.shape[0]
        target_height = int(np.sqrt(total_pixels / aspect_ratio))
        target_width = int(target_height * aspect_ratio)

        # Make sure dimensions are multiples of 8
        target_height = target_height - (target_height % 8)
        target_width = target_width - (target_width % 8)

        # Prepare secret image with proper size
        secret_img = self.prepare_image(secret_path, (target_height, target_width))

        # Determine if images are grayscale
        cover_is_gray = len(cover_img.shape) == 2
        secret_is_gray = len(secret_img.shape) == 2

        # Convert color images to appropriate format
        if cover_is_gray and not secret_is_gray:
            # Convert cover to color by duplicating the channel
            cover_img = cv2.cvtColor(cover_img, cv2.COLOR_GRAY2BGR)
            cover_is_gray = False
        elif not cover_is_gray and secret_is_gray:
            # Convert secret to grayscale
            secret_img = cv2.cvtColor(secret_img, cv2.COLOR_BGR2GRAY)
            secret_is_gray = True

        # Calculate capacity for embedding
        if cover_is_gray:
            cover_blocks = (cover_img.shape[0] // 8) * (cover_img.shape[1] // 8)
            required_bits = secret_img.shape[0] * secret_img.shape[1] * 8
        else:
            cover_blocks = (
                (cover_img.shape[0] // 8) * (cover_img.shape[1] // 8)
            ) * 3  # 3 color channels
            required_bits = (
                secret_img.shape[0]
                * secret_img.shape[1]
                * (24 if not secret_is_gray else 8)
            )

        if required_bits > cover_blocks:
            raise ValueError(
                f"Cover image too small. Can only embed {cover_blocks} bits but need {required_bits} bits."
            )

        # Initialize stego image by copying the cover image
        stego_img = cover_img.copy()

        # Store dimensions directly in the first 4 pixels
        stego_img = self.store_dimensions(stego_img, target_height, target_width)

        if cover_is_gray:
            # Convert secret image to binary and embed
            secret_binary = np.unpackbits(secret_img.astype(np.uint8))
            bit_count = self.embed_channel(cover_img, secret_binary, stego_img)
        else:
            if secret_is_gray:
                # For grayscale secret in color cover, embed same data in each channel
                secret_binary = np.unpackbits(secret_img.astype(np.uint8))
                bits_per_channel = len(secret_binary) // 3

                for channel in range(3):
                    start_idx = channel * bits_per_channel
                    end_idx = (
                        start_idx + bits_per_channel
                        if channel < 2
                        else len(secret_binary)
                    )
                    channel_bits = secret_binary[start_idx:end_idx]
                    self.embed_channel(
                        cover_img[..., channel], channel_bits, stego_img[..., channel]
                    )
                bit_count = len(secret_binary)
            else:
                # For color secret in color cover, embed each channel separately
                total_bits = 0
                for channel in range(3):
                    secret_binary = np.unpackbits(
                        secret_img[..., channel].astype(np.uint8)
                    )
                    bits = self.embed_channel(
                        cover_img[..., channel], secret_binary, stego_img[..., channel]
                    )
                    total_bits += bits
                bit_count = total_bits

        # Save the stego image
        cv2.imwrite(output_path, stego_img)
        return bit_count, (target_height, target_width)

    def decode(self, stego_path, output_path):
        """Extract hidden image from stego image."""
        # Read stego image
        stego_img = self.prepare_image(stego_path)
        is_color = len(stego_img.shape) == 3

        # Read dimensions from the first 4 pixels
        secret_height, secret_width = self.read_dimensions(stego_img)

        # Calculate number of bits needed for the image data
        if is_color:
            bits_per_channel = secret_height * secret_width * 8
            total_bits = bits_per_channel * 3
        else:
            total_bits = secret_height * secret_width * 8

        if is_color:
            # Extract from each channel
            extracted_image = np.zeros((secret_height, secret_width, 3), dtype=np.uint8)
            for channel in range(3):
                extracted_bits = self.extract_channel(
                    stego_img[..., channel], bits_per_channel
                )
                if len(extracted_bits) < bits_per_channel:
                    raise ValueError(
                        f"Not enough bits extracted from channel {channel}"
                    )

                # Convert bits to channel data
                channel_data = np.packbits(extracted_bits)[
                    : secret_height * secret_width
                ]
                extracted_image[..., channel] = channel_data.reshape(
                    secret_height, secret_width
                )
        else:
            # Extract from grayscale image
            extracted_bits = self.extract_channel(stego_img, total_bits)
            if len(extracted_bits) < total_bits:
                raise ValueError("Not enough bits extracted")

            # Convert bits to image
            image_data = np.packbits(extracted_bits)[: secret_height * secret_width]
            extracted_image = image_data.reshape(secret_height, secret_width)

        # Save extracted image
        cv2.imwrite(output_path, extracted_image)
        return extracted_image
