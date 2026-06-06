import os
import uuid
from PIL import Image
from . import Paillier
from . import ImageCryptography

def encrypt_task(input_path, bitlen=128):
    """
    Task to encrypt an image.
    Returns keys and paths to encrypted PNG and JSON metadata.
    """
    public_key, private_key = Paillier.generate_keys(bitlen)
    plainimg = Image.open(input_path).convert("RGB")
    
    # Encrypt
    cipherimg = ImageCryptography.ImgEncrypt(public_key, plainimg, parallel=True)
    
    # Save
    task_id = str(uuid.uuid4())
    filename = f"enc_{task_id}"
    output_dir = "/tmp/pixel-ghost-homomorphic"
    os.makedirs(output_dir, exist_ok=True)
    
    ImageCryptography.saveVisualEncryptedImg(cipherimg, filename, directory=output_dir)
    
    return {
        "public_key": {"n": public_key.n},
        "private_key": {"lam": private_key.λ, "mu": private_key.μ},
        "encrypted_png": os.path.join(output_dir, f"{filename}.png"),
        "metadata_json": os.path.join(output_dir, f"{filename}.json")
    }

def decrypt_task(png_path, json_path, n, lam, mu):
    """
    Task to decrypt an image.
    """
    public_key = Paillier.PublicKey(n)
    private_key = Paillier.PrivateKey(lam=lam, mu=mu)
    
    # Load
    directory = os.path.dirname(png_path)
    filename = os.path.basename(png_path).replace(".png", "")
    cipherimg = ImageCryptography.loadVisualEncryptedImg(filename, directory=directory)
    
    # Decrypt
    decrypted_img = ImageCryptography.ImgDecrypt(public_key, private_key, cipherimg, parallel=True)
    
    # Save
    task_id = str(uuid.uuid4())
    output_path = f"/tmp/decrypted_{task_id}.png"
    decrypted_img.save(output_path)
    
    return output_path

def brightness_task(png_path, json_path, n, factor):
    """
    Task to perform homomorphic brightness adjustment.
    """
    public_key = Paillier.PublicKey(n)
    
    # Load
    directory = os.path.dirname(png_path)
    filename = os.path.basename(png_path).replace(".png", "")
    cipherimg = ImageCryptography.loadVisualEncryptedImg(filename, directory=directory)
    
    # Brightness adjust
    bright_cipher = ImageCryptography.homomorphicBrightness(public_key, cipherimg, factor, parallel=True)
    
    # Save
    task_id = str(uuid.uuid4())
    new_filename = f"bright_{task_id}"
    output_dir = "/tmp/pixel-ghost-homomorphic"
    os.makedirs(output_dir, exist_ok=True)
    
    ImageCryptography.saveVisualEncryptedImg(bright_cipher, new_filename, directory=output_dir)
    
    return {
        "encrypted_png": os.path.join(output_dir, f"{new_filename}.png"),
        "metadata_json": os.path.join(output_dir, f"{new_filename}.json")
    }
