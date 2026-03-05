import numpy as np
from PIL import Image
import uuid
import os

def extract_bit_plane(image_path, bit=0):
    """
    Extracts a specific bit plane from an image.
    Bit 0 is the least significant bit (LSB).
    Returns the path to the visualized bit plane.
    """
    img = Image.open(image_path).convert('RGB')
    data = np.array(img)
    
    # Isolate the specific bit
    # (data >> bit) & 1 shifts the bit to the LSB position and masks it
    # We then multiply by 255 to make it visible (0 or 255)
    plane = ((data >> bit) & 1) * 255
    
    # Save the result
    output_path = f"/tmp/analysis_{uuid.uuid4()}.png"
    plane_img = Image.fromarray(plane.astype(np.uint8))
    plane_img.save(output_path)
    
    return output_path
