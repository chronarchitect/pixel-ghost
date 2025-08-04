from PIL import Image


class SteganographyBase:
    """
    Base class for steganography operations.

    This class can be extended to implement specific steganography algorithms.
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
        if image.mode != 'RGB':
            image = image.convert('RGB')

        message += '###'  # Delimiter to indicate end of message
        binary_message = self.to_bin(message)
        data_len = len(binary_message)

        pixels = list(image.getdata())
        new_pixels = []

        idx = 0
        for pixel in pixels:
            if idx < data_len:
                r, g, b = pixel

                if idx < data_len:
                    r = (r & ~1) | int(binary_message[idx])
                    idx += 1
                if idx < data_len:
                    g = (g & ~1) | int(binary_message[idx])
                    idx += 1
                if idx < data_len:
                    b = (b & ~1) | int(binary_message[idx])
                    idx += 1

                new_pixels.append((r, g, b))
            else:
                new_pixels.append(pixel)

        encoded_image = Image.new(image.mode, image.size)
        encoded_image.putdata(new_pixels)
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

        return message[:-3]
