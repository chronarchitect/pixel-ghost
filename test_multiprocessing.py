import multiprocessing
import uuid

class LSB:
    def encode(self, image_path, message, output_path):
        return "success"

def test():
    steg = LSB()
    input_path = "test"
    message = "hi"
    output_path = "out"
    
    try:
        with multiprocessing.Pool(1) as pool:
            result = pool.apply(steg.encode, (input_path, message, output_path))
            print(result)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
