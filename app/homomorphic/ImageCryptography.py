from PIL import Image
import numpy as np
import pickle
import concurrent.futures
import multiprocessing
import os
import json
import math

from . import Paillier

def _encrypt_pixel(args):
    public_key, pix = args
    return Paillier.Encrypt(public_key, pix)

def _decrypt_pixel(args):
    public_key, private_key, pix = args
    return Paillier.Decrypt(public_key, private_key, pix)

def _brightness_pixel(args):
    public_key, pix, factor = args
    return Paillier.homomorphic_add_constant(public_key, pix, factor)

def ImgEncrypt(public_key, plainimg, parallel=True):
    """
    args:
        public_key: Paillier PublicKey object
        plainimg: PIL Image object
        parallel: Whether to use multiprocessing (default: True)
        
    returns:
        cipherimg: Encryption of plainimg
    Encrypts an image
    """
    
    cipherimg_arr = np.asarray(plainimg)
    shape = cipherimg_arr.shape
    pixels = cipherimg_arr.flatten().tolist()
    
    if parallel:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            args = [(public_key, pix) for pix in pixels]
            cipherimg = list(executor.map(_encrypt_pixel, args))
    else:
        cipherimg = [Paillier.Encrypt(public_key, pix) for pix in pixels]
    
    return np.asarray(cipherimg).reshape(shape)


def ImgDecrypt(public_key, private_key, cipherimg, parallel=True):
    """
    args:
        public_key: Paillier PublicKey object
        private_key: Paillier PrivateKey object
        cipherimg: encryption of Image
        parallel: Whether to use multiprocessing (default: True)
        
    returns:
        Image object which is the decryption of cipherimage
    Decrypts ecnrypted image
    """
    shape = cipherimg.shape
    cipher_pixels = cipherimg.flatten().tolist()
    
    if parallel:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            args = [(public_key, private_key, pix) for pix in cipher_pixels]
            plainimg = list(executor.map(_decrypt_pixel, args))
    else:
        plainimg = [Paillier.Decrypt(public_key, private_key, pix) for pix in cipher_pixels]
        
    plainimg = [pix if pix < 255 else 255 for pix in plainimg]
    plainimg = [pix if pix > 0 else 0 for pix in plainimg]
    
    return Image.fromarray(np.asarray(plainimg).reshape(shape).astype(np.uint8))


def homomorphicBrightness(public_key, cipherimg, factor, parallel=True):
    """
    args:
        public_key: Paillier PublicKey object
        cipherimg: n dimensional array containing encryption of image pixels
        factor: Amount of brightness to be added (-ve for decreasing brightness)
        parallel: Whether to use multiprocessing (default: True)
    
    returns:
        n dimensional array containing encryption of image pixels with brightness adjusted
    
    Function to demonstrate homomorphism
    Performs brightness adjust operation on the encrypted image
    """
    shape = cipherimg.shape
    bright_pixels = cipherimg.flatten().tolist()
    
    if parallel:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            args = [(public_key, pix, factor) for pix in bright_pixels]
            brightimg = list(executor.map(_brightness_pixel, args))
    else:
        brightimg = [Paillier.homomorphic_add_constant(public_key, pix, factor) for pix in bright_pixels]
    
    return np.asarray(brightimg).reshape(shape)


def saveEncryptedImg(cipherimg, filename, directory="encrypted-images"):
    """
    args:
        cipherimg: Encryption of an image
        filename: filename to save encryption
        directory: directory to save encryption
        
    saves Encryption of image into a file
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(directory, filename)
    fstream = open(filepath, "wb")
    pickle.dump(cipherimg, fstream)
    fstream.close()


def loadEncryptedImg(filename, directory="encrypted-images"):
    """
    args:
        filename: filename of the Encrypted object
        directory: directory of the Encrypted object
        
    returns:
        n-dimensional array containing ecryption of image
    loads Encrypted image object from file
    """
    filepath = os.path.join(directory, filename)
    fstream = open(filepath, "rb")
    cipherimg = pickle.load(fstream)
    fstream.close()
    return cipherimg


def saveVisualEncryptedImg(cipherimg, filename, directory="encrypted-images"):
    """
    Saves an encrypted image as a visual PNG with a sidecar JSON for metadata.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    shape = cipherimg.shape
    flat_cipher = cipherimg.flatten()

    # Determine max byte length for alignment
    max_val = int(np.max(flat_cipher))
    pixel_byte_len = (max_val.bit_length() + 7) // 8
    
    # Pack into bytes
    byte_stream = bytearray()
    for val in flat_cipher:
        byte_stream.extend(int(val).to_bytes(pixel_byte_len, byteorder='big'))

    # Determine dimensions for PNG (try to make it roughly square)
    total_bytes = len(byte_stream)
    width = int(math.sqrt(total_bytes))
    if width == 0: width = 1
    height = math.ceil(total_bytes / width)
    
    # Pad byte stream to fit width * height
    padding = (width * height) - total_bytes
    byte_stream.extend(b'\x00' * padding)

    # Save PNG
    img = Image.frombytes('L', (width, height), bytes(byte_stream))
    img.save(os.path.join(directory, f"{filename}.png"), "PNG")

    # Save sidecar metadata
    metadata = {
        "shape": list(shape),
        "pixel_byte_len": pixel_byte_len,
        "total_bytes": total_bytes
    }
    with open(os.path.join(directory, f"{filename}.json"), "w") as f:
        json.dump(metadata, f)


def loadVisualEncryptedImg(filename, directory="encrypted-images"):
    """
    Loads an encrypted image from a visual PNG and its sidecar JSON.
    """
    # Load metadata
    json_path = os.path.join(directory, f"{filename}.json")
    if not os.path.exists(json_path):
        # Fallback for when filename includes extension or is full path
        if filename.endswith(".png"):
            filename = filename[:-4]
        json_path = os.path.join(directory, f"{filename}.json")

    with open(json_path, "r") as f:
        metadata = json.load(f)
    
    shape = tuple(metadata["shape"])
    pixel_byte_len = metadata["pixel_byte_len"]
    total_bytes = metadata["total_bytes"]

    # Load PNG bytes
    png_path = os.path.join(directory, f"{filename}.png")
    img = Image.open(png_path)
    all_bytes = img.tobytes()
    byte_stream = all_bytes[:total_bytes]

    # Unpack bytes
    flat_cipher = []
    for i in range(0, total_bytes, pixel_byte_len):
        chunk = byte_stream[i : i + pixel_byte_len]
        flat_cipher.append(int.from_bytes(chunk, byteorder='big'))

    return np.array(flat_cipher).reshape(shape)
