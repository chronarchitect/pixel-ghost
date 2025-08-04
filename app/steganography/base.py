from PIL import Image


class SteganographyBase:
    """
    Base class for steganography operations.

    This class can be extended to implement specific steganography algorithms.
    """

    def encode():
        """Encode a message into an image."""
        raise NotImplementedError("Subclasses should implement this method.")

    def decode():
        """Decode a hidden message from an image."""
        raise NotImplementedError("Subclasses should implement this method.")
