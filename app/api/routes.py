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
from tasks import TaskQueueManager
import shutil
import uuid
import os

router = APIRouter()
TaskQueueManager.start()


@router.get("/")
async def read_root():
    """Health check endpoint."""
    return {"message": "PixelGhost backend is alive!"}


# Task status endpoint
@router.get("/task/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a submitted task.
    """
    try:
        status = TaskQueueManager.get_status(task_id)
        return JSONResponse(
            content={"task_id": task_id, "status": status}, status_code=200
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# Task result endpoint
@router.get("/task/result/{task_id}")
async def get_task_result(task_id: str):
    """
    Get the result of a completed task (e.g., download the output file).
    """
    try:
        # Check task status first
        status = TaskQueueManager.get_status(task_id)

        if status == "not_found":
            return JSONResponse(content={"error": "Task not found"}, status_code=404)
        elif status == "queued":
            return JSONResponse(
                content={"error": "Task is still queued"}, status_code=202
            )
        elif status == "processing":
            return JSONResponse(
                content={"error": "Task is still processing"}, status_code=202
            )
        elif status == "failed":
            # Task failed, return error with 400 status code
            result = TaskQueueManager.get_result(task_id)
            return JSONResponse(content={"error": result}, status_code=400)
        elif status == "completed":
            # Task completed successfully
            result = TaskQueueManager.get_result(task_id)
            # If result is a file path, return it as a file response
            if isinstance(result, str):
                # Try to return as file if file exists
                try:
                    # check if file exists
                    if not os.path.exists(result):
                        raise FileNotFoundError(f"File {result} not found.")
                    return FileResponse(path=result, filename=result.split("/")[-1])
                except Exception:
                    # If not a file, return as plain text
                    return JSONResponse(content={"result": result}, status_code=200)
            else:
                # Not a file path, just return as JSON
                return JSONResponse(content={"result": result}, status_code=200)
        else:
            return JSONResponse(
                content={"error": "Unknown task status"}, status_code=500
            )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/text/lsb/encode")
async def encode_text_in_image(
    image: UploadFile = File(...),
    message: str = Form(...),
):
    """Encode a hidden text message into an image using LSB steganography."""
    steg = LSB()
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # steg.encode(input_path, message, output_path)
        task_id = TaskQueueManager.submit_task(
            steg.encode, input_path, message, output_path
        )

        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        image.file.close()


@router.post("/text/lsb/decode")
async def decode_text_from_image(
    image: UploadFile = File(...),
):
    """Decode and extract a hidden text message from an encoded image."""
    steg = LSB()
    input_path = f"/tmp/input_{uuid.uuid4()}.png"

    try:
        # Save uploaded file to temp path
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Decode message
        # decoded_message = steg.decode(input_path)
        task_id = TaskQueueManager.submit_task(steg.decode, input_path)

        # Return the task ID for tracking
        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        image.file.close()


@router.post("/text/lsb_random/encode")
async def lsb_random_encode_text_in_image(
    image: UploadFile = File(...),
    message: str = Form(...),
    key: str = Form(...),
):
    """Encode a hidden text message into an image using LSB steganography with randomized pixel selection."""
    steg = LSBRandom(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Encode message
        # output_path = steg.encode(input_path, message, output_path)
        task_id = TaskQueueManager.submit_task(
            steg.encode, input_path, message, output_path
        )

        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        image.file.close()


@router.post("/text/lsb_random/decode")
async def lsb_random_decode_text_from_image(
    image: UploadFile = File(...),
    key: str = Form(...),
):
    """Decode and extract a hidden text message from an encoded image using LSB steganography with randomized pixel selection."""
    steg = LSBRandom(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"

    try:
        # Save uploaded file to temp path
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Decode message
        # decoded_message = steg.decode(input_path, key)
        task_id = TaskQueueManager.submit_task(steg.decode, input_path, key)

        # Return the task ID for tracking
        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        image.file.close()


@router.post("/text/lsb_random_enc/encode")
async def lsb_random_enc_encode_text_in_image(
    image: UploadFile = File(...),
    message: str = Form(...),
    key: str = Form(...),
):
    """Encode and encrypt a hidden text message into an image using LSB steganography with randomized pixel selection."""
    steg = LSBRandomEnc(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Encode and encrypt message
        # output_path = steg.encode(input_path, message, output_path)
        task_id = TaskQueueManager.submit_task(
            steg.encode, input_path, message, output_path
        )

        # Return the task ID for tracking
        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        image.file.close()


@router.post("/text/lsb_random_enc/decode")
async def lsb_random_enc_decode_text_from_image(
    image: UploadFile = File(...),
    key: str = Form(...),
):
    """Decode and decrypt a hidden text message from an encoded image using LSB steganography with randomized pixel selection."""
    steg = LSBRandomEnc(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"

    try:
        # Save uploaded file to temp path
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Decode and decrypt message
        # decoded_message = steg.decode(input_path)
        task_id = TaskQueueManager.submit_task(steg.decode, input_path, key)

        # Return the task ID for tracking
        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        image.file.close()


# Image-in-Image Steganography Endpoints


@router.post("/image/lsb/encode")
async def encode_image_in_image(
    cover_image: UploadFile = File(...),
    secret_image: UploadFile = File(...),
):
    """Encode a secret image into a cover image using basic LSB steganography."""
    steg = ImageInImageLSB()
    cover_path = f"/tmp/cover_{uuid.uuid4()}.png"
    secret_path = f"/tmp/secret_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"

    try:
        # Save uploaded files to temp paths
        with open(cover_path, "wb") as buffer:
            shutil.copyfileobj(cover_image.file, buffer)
        with open(secret_path, "wb") as buffer:
            shutil.copyfileobj(secret_image.file, buffer)

        # Encode secret image into cover image
        # steg.encode(cover_path, secret_path, output_path)
        task_id = TaskQueueManager.submit_task(steg.encode, cover_path, secret_path, output_path)

        # Return the task ID for tracking
        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        cover_image.file.close()
        secret_image.file.close()


@router.post("/image/lsb/decode")
async def decode_image_from_image(
    stego_image: UploadFile = File(...),
):
    """Decode and extract a hidden image from a stego image using basic LSB steganography."""
    steg = ImageInImageLSB()
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/extracted_{uuid.uuid4()}.png"

    try:
        # Save uploaded file to temp path
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(stego_image.file, buffer)

        # Decode hidden image
        # extracted_path = steg.decode(input_path, output_path)
        task_id = TaskQueueManager.submit_task(steg.decode, input_path, output_path)

        # Return the task ID for tracking
        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        stego_image.file.close()


@router.post("/image/lsb_random/encode")
async def encode_image_in_image_random(
    cover_image: UploadFile = File(...),
    secret_image: UploadFile = File(...),
    key: str = Form(...),
):
    """Encode a secret image into a cover image using LSB steganography with pseudorandom pixel selection."""
    steg = ImageInImageLSBRandom(key=key)
    cover_path = f"/tmp/cover_{uuid.uuid4()}.png"
    secret_path = f"/tmp/secret_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"

    try:
        # Save uploaded files to temp paths
        with open(cover_path, "wb") as buffer:
            shutil.copyfileobj(cover_image.file, buffer)
        with open(secret_path, "wb") as buffer:
            shutil.copyfileobj(secret_image.file, buffer)

        # Encode secret image into cover image
        task_id = TaskQueueManager.submit_task(steg.encode, cover_path, secret_path, output_path)

        # Return the task ID for tracking
        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        cover_image.file.close()
        secret_image.file.close()


@router.post("/image/lsb_random/decode")
async def decode_image_from_image_random(
    stego_image: UploadFile = File(...),
    key: str = Form(...),
):
    """Decode and extract a hidden image from a stego image using LSB steganography with pseudorandom pixel selection."""
    steg = ImageInImageLSBRandom(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/extracted_{uuid.uuid4()}.png"

    try:
        # Save uploaded file to temp path
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(stego_image.file, buffer)

        # Decode hidden image
        task_id = TaskQueueManager.submit_task(steg.decode, input_path, output_path)

        # Return the task ID for tracking
        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        stego_image.file.close()


@router.post("/image/lsb_random_enc/encode")
async def encode_image_in_image_encrypted(
    cover_image: UploadFile = File(...),
    secret_image: UploadFile = File(...),
    key: str = Form(...),
):
    """Encode and encrypt a secret image into a cover image using LSB steganography with pseudorandom pixel selection."""
    steg = ImageInImageLSBRandomEnc(key=key)
    cover_path = f"/tmp/cover_{uuid.uuid4()}.png"
    secret_path = f"/tmp/secret_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"

    try:
        # Save uploaded files to temp paths
        with open(cover_path, "wb") as buffer:
            shutil.copyfileobj(cover_image.file, buffer)
        with open(secret_path, "wb") as buffer:
            shutil.copyfileobj(secret_image.file, buffer)

        # Encode and encrypt secret image into cover image
        task_id = TaskQueueManager.submit_task(steg.encode, cover_path, secret_path, output_path)

        # Return the task ID for tracking
        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        cover_image.file.close()
        secret_image.file.close()


@router.post("/image/lsb_random_enc/decode")
async def decode_image_from_image_encrypted(
    stego_image: UploadFile = File(...),
    key: str = Form(...),
):
    """Decode and decrypt a hidden image from a stego image using LSB steganography with pseudorandom pixel selection."""
    steg = ImageInImageLSBRandomEnc(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/extracted_{uuid.uuid4()}.png"

    try:
        # Save uploaded file to temp path
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(stego_image.file, buffer)

        # Decode and decrypt hidden image
        task_id = TaskQueueManager.submit_task(steg.decode, input_path, output_path)

        # Return the task ID for tracking
        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        stego_image.file.close()


@router.post("image/dct/encode")
async def dct_encode_image(
    cover_image: UploadFile = File(...),
    secret_image: UploadFile = File(...),
):
    """Encode a secret image into a cover image using DCT steganography."""
    steg = DCT()
    cover_path = f"/tmp/cover_{uuid.uuid4()}.png"
    secret_path = f"/tmp/secret_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"

    try:
        # Save uploaded files to temp paths
        with open(cover_path, "wb") as buffer:
            shutil.copyfileobj(cover_image.file, buffer)
        with open(secret_path, "wb") as buffer:
            shutil.copyfileobj(secret_image.file, buffer)

        # Encode secret image into cover image
        # steg.encode(cover_path, secret_path, output_path)
        task_id = TaskQueueManager.submit_task(steg.encode, cover_path, secret_path, output_path)

        # Return the task ID for tracking
        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        cover_image.file.close()
        secret_image.file.close()


@router.post("image/dct/decode")
async def dct_decode_image(
    image: UploadFile = File(...),
):
    """Decode and extract a hidden image from an encoded image using DCT steganography."""
    steg = DCT()
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/extracted_{uuid.uuid4()}.png"

    try:
        # Save uploaded file to temp path
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Decode hidden image
        # steg.decode(input_path, output_path)
        task_id = TaskQueueManager.submit_task(steg.decode, input_path, output_path)

        # Return the task ID for tracking
        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        image.file.close()


# Audio Steganography Routes
@router.post("/audio/lsb/encode")
async def encode_text_in_audio(
    audio_file: UploadFile = File(...), message: str = Form(...)
):
    """Encode text message into audio file using LSB steganography."""
    audio_path = f"temp_audio_{uuid.uuid4().hex}.wav"
    output_path = f"temp_stego_audio_{uuid.uuid4().hex}.wav"

    try:
        # Validate file type
        if not audio_file.filename.lower().endswith(".wav"):
            return JSONResponse(
                content={"error": "Only WAV audio files are supported"}, status_code=400
            )

        # Save uploaded audio file
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        # Create AudioLSB instance and submit task
        audio_steg = AudioLSB()
        task_id = TaskQueueManager.submit_task(
            audio_steg.encode, audio_path, message, output_path
        )

        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        # Clean up files on error
        for path in [audio_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/audio/lsb/decode")
async def decode_text_from_audio(audio_file: UploadFile = File(...)):
    """Decode hidden text message from audio file using LSB steganography."""
    audio_path = f"temp_stego_audio_{uuid.uuid4().hex}.wav"

    try:
        # Validate file type
        if not audio_file.filename.lower().endswith(".wav"):
            return JSONResponse(
                content={"error": "Only WAV audio files are supported"}, status_code=400
            )

        # Save uploaded audio file
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        # Create AudioLSB instance and submit task
        audio_steg = AudioLSB()
        task_id = TaskQueueManager.submit_task(audio_steg.decode, audio_path)

        return JSONResponse(content={"task_id": task_id}, status_code=202)

    except Exception as e:
        # Clean up files on error
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/audio/capacity")
async def get_audio_capacity(audio_file: UploadFile = File(...)):
    """Calculate the text capacity of an audio file."""
    audio_path = f"temp_capacity_audio_{uuid.uuid4().hex}.wav"

    try:
        # Validate file type
        if not audio_file.filename.lower().endswith(".wav"):
            return JSONResponse(
                content={"error": "Only WAV audio files are supported"}, status_code=400
            )

        # Save uploaded audio file
        with open(audio_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        # Calculate capacity
        audio_steg = AudioLSB()
        capacity = audio_steg.calculate_capacity(audio_path)

        # Clean up
        if os.path.exists(audio_path):
            os.remove(audio_path)

        return JSONResponse(content={"capacity": capacity})

    except Exception as e:
        # Clean up files on error
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return JSONResponse(content={"error": str(e)}, status_code=500)
