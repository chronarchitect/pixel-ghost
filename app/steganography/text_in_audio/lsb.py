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
                delimiter_bits = len(self.delimiter.encode("utf-8")) * 8
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

    def _to_bin(self, data):
        """Convert data to binary format as string."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        if isinstance(data, (bytes, bytearray)):
            return "".join(format(i, "08b") for i in data)
        elif isinstance(data, int):
            return format(data, "08b")
        else:
            raise TypeError("Unsupported data type.")

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
            message_binary = self._to_bin(full_message)

            # Read the original audio file
            with wave.open(input_path, "rb") as audio:
                params = audio.getparams()
                frames = audio.readframes(params.nframes)

            # Convert audio data to numpy array
            if params.sampwidth == 1:
                format_char = "B"
            elif params.sampwidth == 2:
                format_char = "h"
            elif params.sampwidth == 4:
                format_char = "i"
            else:
                raise ValueError(f"Unsupported sample width: {params.sampwidth}")

            # Unpack audio data
            num_samples = len(frames) // params.sampwidth
            audio_data = list(
                struct.unpack(f"{num_samples}{format_char}", frames)
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
            # Clean up output file on error
            if os.path.exists(output_path):
                os.remove(output_path)
            raise Exception(f"Encoding failed: {str(e)}")
        finally:
            # Clean up input file if it was a temporary file
            if "temp_audio_" in input_path and os.path.exists(input_path):
                os.remove(input_path)

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
                format_char = "B"
            elif params.sampwidth == 2:
                format_char = "h"
            elif params.sampwidth == 4:
                format_char = "i"
            else:
                raise ValueError(f"Unsupported sample width: {params.sampwidth}")

            # Unpack audio data
            num_samples = len(frames) // params.sampwidth
            audio_data = list(
                struct.unpack(f"{num_samples}{format_char}", frames)
            )

            # Extract bits from LSBs
            extracted_bits = ""
            for sample in audio_data:
                extracted_bits += self._extract_bit_from_sample(sample)

            # Convert bits to bytes
            bytes_data = bytearray()
            for i in range(0, len(extracted_bits), 8):
                byte = extracted_bits[i : i + 8]
                if len(byte) == 8:
                    bytes_data.append(int(byte, 2))
            
            # Convert bytes to text
            try:
                extracted_text = bytes_data.decode("utf-8", errors="replace")
            except Exception:
                extracted_text = bytes_data.decode("latin-1", errors="replace")

            # Find the delimiter to get the actual message
            if self.delimiter in extracted_text:
                message = extracted_text.split(self.delimiter)[0]
                return message
            else:
                raise ValueError("No hidden message found or delimiter not detected")

        except Exception as e:
            raise Exception(f"Decoding failed: {str(e)}")
        finally:
            # Clean up input file if it was a temporary file
            if "temp_stego_audio_" in input_path and os.path.exists(input_path):
                os.remove(input_path)

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
