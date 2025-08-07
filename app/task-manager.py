import multiprocessing
import uuid

task_queue = multiprocessing.Queue()
task_status = {}

def encode_worker():
    from steganography.lsb import LSB

    while True:
        task_id, image_path, message, output_path = task_queue.get()
        try:
            steg = LSB()
            steg.encode(image_path, message, output_path)
            task_status[task_id] = {
                "status": "completed",
                "output_path": output_path
            }
        except Exception as e:
            task_status[task_id] = {
                "status": "failed",
                "error": str(e)
            }

    # Start background thread on startup
    def start_encode_worker():
        worker = multiprocessing.Process(target=encode_worker)
        worker.daemon = True
        worker.start()