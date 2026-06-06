from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from steganography.text_in_image.lsb import LSB
from steganography.image_in_image.dct import DCT
from steganography.text_in_image.lsb_random import LSBRandom
from steganography.text_in_image.lsb_random_enc import LSBRandomEnc
from steganography.image_in_image.lsb import ImageInImageLSB
from steganography.image_in_image.lsb_random import ImageInImageLSBRandom
from steganography.image_in_image.lsb_random_enc import ImageInImageLSBRandomEnc
from steganography.text_in_audio.lsb import AudioLSB
from homomorphic.tasks import encrypt_task, decrypt_task, brightness_task
from core.analysis import extract_bit_plane
from tasks import TaskQueueManager
import shutil
import uuid
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
TaskQueueManager.start()

@router.get("/")
async def read_root():
    """Health check endpoint."""
    return {"message": "PixelGhost backend is alive!"}

@router.get("/tasks")
async def list_all_tasks():
    """List all submitted tasks with their IDs."""
    try:
        tasks = TaskQueueManager.get_all_tasks()
        return JSONResponse(content={"tasks": tasks}, status_code=200)
    except Exception as e:
        logger.exception("Error listing tasks")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/analyze/bit-plane")
async def analyze_bit_plane(image: UploadFile = File(...), bit: int = Form(0)):
    """Analyze and extract a specific bit plane for noise visualization."""
    input_path = f"/tmp/analysis_input_{uuid.uuid4()}.png"
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        task_id = TaskQueueManager.submit_task(extract_bit_plane, input_path, bit=bit)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error analyzing bit-plane")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        image.file.close()

# Task status endpoint
@router.get("/task/status/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a submitted task."""
    try:
        status = TaskQueueManager.get_status(task_id)
        if status == "not_found":
            return JSONResponse(content={"task_id": task_id, "status": status}, status_code=404)
        elif status in ["queued", "processing"]:
            return JSONResponse(content={"task_id": task_id, "status": status}, status_code=202)
        elif status == "completed":
            return JSONResponse(content={"task_id": task_id, "status": status}, status_code=200)
        elif status == "failed":
            return JSONResponse(content={"task_id": task_id, "status": status}, status_code=400)
        else:
            return JSONResponse(content={"task_id": task_id, "status": status}, status_code=500)
    except Exception as e:
        logger.exception("Error getting task status")
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Task result endpoint
@router.get("/task/result/{task_id}")
async def get_task_result(task_id: str):
    """Get the result of a completed task."""
    try:
        status = TaskQueueManager.get_status(task_id)
        if status == "not_found":
            return JSONResponse(content={"error": "Task not found"}, status_code=404)
        elif status in ["queued", "processing"]:
            return JSONResponse(content={"error": f"Task is still {status}"}, status_code=202)
        elif status == "failed":
            result = TaskQueueManager.get_result(task_id)
            return JSONResponse(content={"error": result}, status_code=400)
        elif status == "completed":
            result = TaskQueueManager.get_result(task_id)
            if isinstance(result, str) and os.path.exists(result):
                return FileResponse(path=result, filename=result.split("/")[-1])
            return JSONResponse(content={"result": result}, status_code=200)
        return JSONResponse(content={"error": "Unknown status"}, status_code=500)
    except Exception as e:
        logger.exception("Error getting task result")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/text/lsb/encode")
async def encode_text_in_image(image: UploadFile = File(...), message: str = Form(...)):
    """Encode a hidden text message into an image using LSB steganography."""
    logger.info(f"Received LSB encode request. Image: {image.filename}, Message length: {len(message)}")
    steg = LSB()
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        can_fit, _, _ = steg.check_capacity(input_path, message)
        if not can_fit:
            return JSONResponse(content={"error": "Message too long"}, status_code=400)
        task_id = TaskQueueManager.submit_task(steg.encode, input_path, message, output_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error encoding LSB text")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        image.file.close()

@router.post("/text/lsb/decode")
async def decode_text_from_image(image: UploadFile = File(...)):
    """Decode and extract a hidden text message from an encoded image."""
    steg = LSB()
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        task_id = TaskQueueManager.submit_task(steg.decode, input_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error decoding LSB text")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        image.file.close()

@router.post("/text/lsb_random/encode")
async def lsb_random_encode_text_in_image(image: UploadFile = File(...), message: str = Form(...), key: str = Form(...)):
    """Encode a hidden text message into an image using LSB steganography with randomized pixel selection."""
    steg = LSBRandom(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        task_id = TaskQueueManager.submit_task(steg.encode, input_path, message, output_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error encoding LSB random text")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        image.file.close()

@router.post("/text/lsb_random/decode")
async def lsb_random_decode_text_from_image(image: UploadFile = File(...), key: str = Form(...)):
    """Decode and extract a hidden text message from an encoded image using LSB steganography with randomized pixel selection."""
    steg = LSBRandom(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        task_id = TaskQueueManager.submit_task(steg.decode, input_path, key)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error decoding LSB random text")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        image.file.close()

@router.post("/text/lsb_random_enc/encode")
async def lsb_random_enc_encode_text_in_image(image: UploadFile = File(...), message: str = Form(...), key: str = Form(...)):
    """Encode and encrypt a hidden text message into an image using LSB steganography with randomized pixel selection."""
    steg = LSBRandomEnc(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        task_id = TaskQueueManager.submit_task(steg.encode, input_path, message, output_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error encoding LSB random encrypted text")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        image.file.close()

@router.post("/text/lsb_random_enc/decode")
async def lsb_random_enc_decode_text_from_image(image: UploadFile = File(...), key: str = Form(...)):
    """Decode and decrypt a hidden text message from an encoded image using LSB steganography with randomized pixel selection."""
    steg = LSBRandomEnc(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        task_id = TaskQueueManager.submit_task(steg.decode, input_path, key)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error decoding LSB random encrypted text")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        image.file.close()

@router.post("/image/lsb/encode")
async def encode_image_in_image(cover_image: UploadFile = File(...), secret_image: UploadFile = File(...)):
    """Encode a secret image into a cover image using basic LSB steganography."""
    steg = ImageInImageLSB()
    cover_path = f"/tmp/cover_{uuid.uuid4()}.png"
    secret_path = f"/tmp/secret_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"
    try:
        with open(cover_path, "wb") as buffer:
            shutil.copyfileobj(cover_image.file, buffer)
        with open(secret_path, "wb") as buffer:
            shutil.copyfileobj(secret_image.file, buffer)
        can_fit, _, _ = steg.check_capacity(cover_path, secret_path)
        if not can_fit:
            return JSONResponse(content={"error": "Secret image too large"}, status_code=400)
        task_id = TaskQueueManager.submit_task(steg.encode, cover_path, secret_path, output_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error encoding image-in-image LSB")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        cover_image.file.close()
        secret_image.file.close()

@router.post("/image/lsb/decode")
async def decode_image_from_image(stego_image: UploadFile = File(...)):
    """Decode and extract a hidden image from a stego image using basic LSB steganography."""
    steg = ImageInImageLSB()
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/extracted_{uuid.uuid4()}.png"
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(stego_image.file, buffer)
        task_id = TaskQueueManager.submit_task(steg.decode, input_path, output_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error decoding image-in-image LSB")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        stego_image.file.close()

@router.post("/image/lsb_random/encode")
async def encode_image_in_image_random(cover_image: UploadFile = File(...), secret_image: UploadFile = File(...), key: str = Form(...)):
    """Encode a secret image into a cover image using LSB steganography with pseudorandom pixel selection."""
    steg = ImageInImageLSBRandom(key=key)
    cover_path = f"/tmp/cover_{uuid.uuid4()}.png"
    secret_path = f"/tmp/secret_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"
    try:
        with open(cover_path, "wb") as buffer:
            shutil.copyfileobj(cover_image.file, buffer)
        with open(secret_path, "wb") as buffer:
            shutil.copyfileobj(secret_image.file, buffer)
        can_fit, _, _ = steg.check_capacity(cover_path, secret_path)
        if not can_fit:
            return JSONResponse(content={"error": "Secret image too large for random distribution"}, status_code=400)
        task_id = TaskQueueManager.submit_task(steg.encode, cover_path, secret_path, output_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error encoding image-in-image LSB random")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        cover_image.file.close()
        secret_image.file.close()

@router.post("/image/lsb_random/decode")
async def decode_image_from_image_random(stego_image: UploadFile = File(...), key: str = Form(...)):
    """Decode and extract a hidden image from a stego image using LSB steganography with pseudorandom pixel selection."""
    steg = ImageInImageLSBRandom(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/extracted_{uuid.uuid4()}.png"
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(stego_image.file, buffer)
        task_id = TaskQueueManager.submit_task(steg.decode, input_path, output_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error decoding image-in-image LSB random")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        stego_image.file.close()

@router.post("/image/lsb_random_enc/encode")
async def encode_image_in_image_encrypted(cover_image: UploadFile = File(...), secret_image: UploadFile = File(...), key: str = Form(...)):
    """Encode and encrypt a secret image into a cover image using LSB steganography with pseudorandom pixel selection."""
    steg = ImageInImageLSBRandomEnc(key=key)
    cover_path = f"/tmp/cover_{uuid.uuid4()}.png"
    secret_path = f"/tmp/secret_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"
    try:
        with open(cover_path, "wb") as buffer:
            shutil.copyfileobj(cover_image.file, buffer)
        with open(secret_path, "wb") as buffer:
            shutil.copyfileobj(secret_image.file, buffer)
        can_fit, _, _ = steg.check_capacity(cover_path, secret_path)
        if not can_fit:
            return JSONResponse(content={"error": "Secret image too large for random encrypted distribution"}, status_code=400)
        task_id = TaskQueueManager.submit_task(steg.encode, cover_path, secret_path, output_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error encoding image-in-image LSB random encrypted")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        cover_image.file.close()
        secret_image.file.close()

@router.post("/image/lsb_random_enc/decode")
async def decode_image_from_image_encrypted(stego_image: UploadFile = File(...), key: str = Form(...)):
    """Decode and decrypt a hidden image from a stego image using LSB steganography with pseudorandom pixel selection."""
    steg = ImageInImageLSBRandomEnc(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/extracted_{uuid.uuid4()}.png"
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(stego_image.file, buffer)
        task_id = TaskQueueManager.submit_task(steg.decode, input_path, output_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error decoding image-in-image LSB random encrypted")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        stego_image.file.close()

@router.post("/image/dct/encode")
async def dct_encode_image(cover_image: UploadFile = File(...), secret_image: UploadFile = File(...)):
    """Encode a secret image into a cover image using DCT steganography."""
    steg = DCT()
    cover_path = f"/tmp/cover_{uuid.uuid4()}.png"
    secret_path = f"/tmp/secret_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"
    try:
        with open(cover_path, "wb") as buffer:
            shutil.copyfileobj(cover_image.file, buffer)
        with open(secret_path, "wb") as buffer:
            shutil.copyfileobj(secret_image.file, buffer)
        can_fit, _, _ = steg.check_capacity(cover_path, secret_path)
        if not can_fit:
            return JSONResponse(content={"error": "Images must be at least 8x8 pixels for DCT processing"}, status_code=400)
        task_id = TaskQueueManager.submit_task(steg.encode, cover_path, secret_path, output_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error encoding DCT image")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        cover_image.file.close()
        secret_image.file.close()

@router.post("/image/dct/decode")
async def dct_decode_image(image: UploadFile = File(...)):
    """Decode and extract a hidden image from an encoded image using DCT steganography."""
    steg = DCT()
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/extracted_{uuid.uuid4()}.png"
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        task_id = TaskQueueManager.submit_task(steg.decode, input_path, output_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error decoding DCT image")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        image.file.close()

@router.post("/audio/lsb/encode")
async def encode_text_in_audio(audio_file: UploadFile = File(...), message: str = Form(...)):
    """Encode text message into audio file using LSB steganography."""
    audio_path = f"temp_audio_{uuid.uuid4().hex}.wav"
    output_path = f"temp_stego_audio_{uuid.uuid4().hex}.wav"
    try:
        if not audio_file.filename.lower().endswith(".wav"):
            return JSONResponse(content={"error": "Only WAV audio files are supported"}, status_code=400)
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        audio_steg = AudioLSB()
        task_id = TaskQueueManager.submit_task(audio_steg.encode, audio_path, message, output_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error encoding LSB audio")
        if os.path.exists(audio_path): os.remove(audio_path)
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/audio/lsb/decode")
async def decode_text_from_audio(audio_file: UploadFile = File(...)):
    """Decode hidden text message from audio file using LSB steganography."""
    audio_path = f"temp_stego_audio_{uuid.uuid4().hex}.wav"
    try:
        if not audio_file.filename.lower().endswith(".wav"):
            return JSONResponse(content={"error": "Only WAV audio files are supported"}, status_code=400)
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        audio_steg = AudioLSB()
        task_id = TaskQueueManager.submit_task(audio_steg.decode, audio_path)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error decoding LSB audio")
        if os.path.exists(audio_path): os.remove(audio_path)
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/audio/capacity")
async def get_audio_capacity(audio_file: UploadFile = File(...)):
    """Calculate the text capacity of an audio file."""
    audio_path = f"temp_capacity_audio_{uuid.uuid4().hex}.wav"
    try:
        if not audio_file.filename.lower().endswith(".wav"):
            return JSONResponse(content={"error": "Only WAV audio files are supported"}, status_code=400)
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        audio_steg = AudioLSB()
        capacity = audio_steg.calculate_capacity(audio_path)
        if os.path.exists(audio_path): os.remove(audio_path)
        return JSONResponse(content={"capacity": capacity})
    except Exception as e:
        logger.exception("Error getting audio capacity")
        if os.path.exists(audio_path): os.remove(audio_path)
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/homomorphic/encrypt")
async def homomorphic_encrypt(image: UploadFile = File(...), bitlen: int = Form(128)):
    """Encrypt an image using Paillier homomorphic encryption."""
    input_path = f"/tmp/homo_input_{uuid.uuid4()}.png"
    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        task_id = TaskQueueManager.submit_task(encrypt_task, input_path, bitlen=bitlen)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error homomorphic encrypting")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        image.file.close()

@router.post("/homomorphic/decrypt")
async def homomorphic_decrypt(encrypted_png: UploadFile = File(...), metadata_json: UploadFile = File(...), n: str = Form(...), lam: str = Form(...), mu: str = Form(...)):
    """Decrypt a homomorphically encrypted image."""
    png_path = f"/tmp/homo_enc_{uuid.uuid4()}.png"
    json_path = f"/tmp/homo_meta_{uuid.uuid4()}.json"
    try:
        with open(png_path, "wb") as buffer:
            shutil.copyfileobj(encrypted_png.file, buffer)
        with open(json_path, "wb") as buffer:
            shutil.copyfileobj(metadata_json.file, buffer)
        task_id = TaskQueueManager.submit_task(decrypt_task, png_path, json_path, int(n), int(lam), int(mu))
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error homomorphic decrypting")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        encrypted_png.file.close()
        metadata_json.file.close()

@router.post("/homomorphic/brightness")
async def homomorphic_brightness(encrypted_png: UploadFile = File(...), metadata_json: UploadFile = File(...), n: str = Form(...), factor: int = Form(...)):
    """Adjust brightness of an encrypted image homomorphically."""
    png_path = f"/tmp/homo_enc_{uuid.uuid4()}.png"
    json_path = f"/tmp/homo_meta_{uuid.uuid4()}.json"
    try:
        with open(png_path, "wb") as buffer:
            shutil.copyfileobj(encrypted_png.file, buffer)
        with open(json_path, "wb") as buffer:
            shutil.copyfileobj(metadata_json.file, buffer)
        task_id = TaskQueueManager.submit_task(brightness_task, png_path, json_path, int(n), factor)
        return JSONResponse(content={"task_id": task_id}, status_code=202)
    except Exception as e:
        logger.exception("Error homomorphic brightness adjustment")
        return JSONResponse(content={"error": str(e)}, status_code=500)
    finally:
        encrypted_png.file.close()
        metadata_json.file.close()

@router.get("/download")
async def download_file(path: str):
    """Download a file by its absolute path (restricted to /tmp for safety)."""
    if not path.startswith("/tmp/"):
        return JSONResponse(content={"error": "Access denied"}, status_code=403)
    if not os.path.exists(path):
        return JSONResponse(content={"error": "File not found"}, status_code=404)
    return FileResponse(path=path, filename=path.split("/")[-1])
