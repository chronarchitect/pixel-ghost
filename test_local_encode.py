import sys
import os
from PIL import Image
from app.steganography.text_in_image.lsb import LSB

def test_local_failure():
    # Setup
    test_image_path = "/tmp/test_local.png"
    img = Image.new('RGB', (10, 10), color='red')
    img.save(test_image_path)
    
    steg = LSB()
    message = "hi"
    output_path = "/tmp/output_local.png"
    
    print(f"Testing LSB encode locally...")
    try:
        # Simulate the encode call from the route
        result = steg.encode(test_image_path, message, output_path)
        print(f"Encode success: {result}")
        
    except Exception as e:
        print(f"Caught exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Add app directory to path
    sys.path.append(os.path.join(os.getcwd(), "app"))
    test_local_failure()
