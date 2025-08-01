class SteganographyBase:
    """
    Base class for steganography operations.
    This class can be extended to implement specific steganography algorithms.
    """
    def encode(self, image, data):
        raise NotImplementedError("Subclasses should implement this method.")

    def decode(self, image):
        raise NotImplementedError("Subclasses should implement this method.")