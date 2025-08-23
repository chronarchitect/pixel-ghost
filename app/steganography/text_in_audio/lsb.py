"""
LSB Text-in-Audio Steganography

This module implements Least Significant Bit (LSB) steganography for hiding
text data inside audio files. It modifies the least significant bits of
audio samples to embed secret text data.

Author: Pixel Ghost Steganography Project
"""

import numpy as np
import wave
import struct
import os
from steganography.base import SteganographyBase


class AudioLSB(SteganographyBase):
    """
    LSB Steganography implementation for hiding text in audio files.

    This class provides methods to embed and extract text data in audio files
    using the Least Significant Bit technique. It works with WAV audio files
    and modifies the LSBs of audio samples to store the secret text.
    """

    def __init__(self):
        """Initialize the AudioLSB steganography instance."""
        super().__init__()
        self.delimiter = "###END_OF_MESSAGE###"  # Delimiter to mark end of hidden text

    def calculate_capacity(self, audio_path):
        """
        Calculate the maximum text capacity of an audio file.

        Args:
            audio_path (str): Path to the audio file

        Returns:
            dict: Dictionary containing capacity information
        """
        try:
            with wave.open(audio_path, "rb") as audio:
                frames = audio.getnframes()
                sample_width = audio.getsampwidth()
                channels = audio.getnchannels()
                framerate = audio.getframerate()

                # Total number of samples
                total_samples = frames * channels

                # Each sample can hide 1 bit in its LSB
                # We need 8 bits per character + delimiter
                delimiter_bits = len(self.delimiter) * 8
                available_bits = total_samples - delimiter_bits
                max_characters = available_bits // 8

                return {
                    "audio_duration_seconds": frames / framerate,
                    "total_samples": total_samples,
                    "sample_width_bytes": sample_width,
                    "channels": channels,
                    "framerate": framerate,
                    "available_bits": available_bits,
                    "max_characters": max_characters,
                    "delimiter_overhead_bits": delimiter_bits,
                }

        except Exception as e:
            raise Exception(f"Error calculating capacity: {str(e)}")

    def _text_to_binary(self, text):
        """
        Convert text to binary representation.

        Args:
            text (str): Text to convert

        Returns:
            str: Binary representation of the text
        """
        return "".join(format(ord(char), "08b") for char in text)

    def _binary_to_text(self, binary_data):
        """
        Convert binary data back to text.

        Args:
            binary_data (str): Binary string to convert

        Returns:
            str: Converted text
        """
        text = ""
        for i in range(0, len(binary_data), 8):
            byte = binary_data[i : i + 8]
            if len(byte) == 8:
                text += chr(int(byte, 2))
        return text

    def _embed_bit_in_sample(self, sample, bit):
        """
        Embed a single bit in an audio sample using LSB.

        Args:
            sample (int): Audio sample value
            bit (str): Bit to embed ('0' or '1')

        Returns:
            int: Modified sample with embedded bit
        """
        if bit == "1":
            return sample | 1  # Set LSB to 1
        else:
            return sample & ~1  # Set LSB to 0

    def _extract_bit_from_sample(self, sample):
        """
        Extract the LSB from an audio sample.

        Args:
            sample (int): Audio sample value

        Returns:
            str: Extracted bit ('0' or '1')
        """
        return str(sample & 1)

    def encode(self, input_path, message, output_path):
        """
        Embed text message into an audio file using LSB steganography.

        Args:
            input_path (str): Path to the cover audio file
            message (str): Text message to hide
            output_path (str): Path to save the stego audio file

        Returns:
            str: Path to the output stego audio file
        """
        try:
            # Add delimiter to mark end of message
            full_message = message + self.delimiter
            message_binary = self._text_to_binary(full_message)

            # Read the original audio file
            with wave.open(input_path, "rb") as audio:
                params = audio.getparams()
                frames = audio.readframes(params.nframes)

            # Convert audio data to numpy array
            if params.sampwidth == 1:
                dtype = np.uint8
                format_char = "B"
            elif params.sampwidth == 2:
                dtype = np.int16
                format_char = "h"
            elif params.sampwidth == 4:
                dtype = np.int32
                format_char = "i"
            else:
                raise ValueError(f"Unsupported sample width: {params.sampwidth}")

            # Unpack audio data
            audio_data = list(
                struct.unpack(f"{len(frames)//params.sampwidth}{format_char}", frames)
            )

            # Check if we have enough capacity
            if len(message_binary) > len(audio_data):
                raise ValueError(
                    f"Message too long. Available bits: {len(audio_data)}, needed: {len(message_binary)}"
                )

            # Embed the message bits
            for i, bit in enumerate(message_binary):
                audio_data[i] = self._embed_bit_in_sample(audio_data[i], bit)

            # Pack the modified audio data
            modified_frames = struct.pack(
                f"{len(audio_data)}{format_char}", *audio_data
            )

            # Write the stego audio file
            with wave.open(output_path, "wb") as stego_audio:
                stego_audio.setparams(params)
                stego_audio.writeframes(modified_frames)

            return output_path

        except Exception as e:
            # Clean up output file on error, but keep input file
            if os.path.exists(output_path):
                os.remove(output_path)
            raise Exception(f"Encoding failed: {str(e)}")

    def decode(self, input_path):
        """
        Extract hidden text message from an audio file.

        Args:
            input_path (str): Path to the stego audio file

        Returns:
            str: Extracted text message
        """
        try:
            # Read the stego audio file
            with wave.open(input_path, "rb") as audio:
                params = audio.getparams()
                frames = audio.readframes(params.nframes)

            # Convert audio data to numpy array
            if params.sampwidth == 1:
                dtype = np.uint8
                format_char = "B"
            elif params.sampwidth == 2:
                dtype = np.int16
                format_char = "h"
            elif params.sampwidth == 4:
                dtype = np.int32
                format_char = "i"
            else:
                raise ValueError(f"Unsupported sample width: {params.sampwidth}")

            # Unpack audio data
            audio_data = list(
                struct.unpack(f"{len(frames)//params.sampwidth}{format_char}", frames)
            )

            # Extract bits from LSBs
            extracted_bits = ""
            for sample in audio_data:
                extracted_bits += self._extract_bit_from_sample(sample)

            # Convert bits to text
            extracted_text = self._binary_to_text(extracted_bits)

            # Find the delimiter to get the actual message
            if self.delimiter in extracted_text:
                message = extracted_text.split(self.delimiter)[0]
                return message
            else:
                raise ValueError("No hidden message found or delimiter not detected")

        except Exception as e:
            raise Exception(f"Decoding failed: {str(e)}")

    def validate_audio_file(self, audio_path):
        """
        Validate if the audio file is suitable for steganography.

        Args:
            audio_path (str): Path to the audio file

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            if not os.path.exists(audio_path):
                return False

            with wave.open(audio_path, "rb") as audio:
                params = audio.getparams()
                # Check if it's a valid WAV file with supported sample width
                return params.sampwidth in [1, 2, 4] and params.nframes > 0

        except Exception:
            return False
