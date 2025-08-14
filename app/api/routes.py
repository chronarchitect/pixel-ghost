from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from steganography.lsb import LSB
from steganography.dct import DCT
from steganography.lsb_random import LSBRandom
import shutil
import uuid

router = APIRouter()


@router.get("/")
async def read_root():
    """Health check endpoint."""
    return {"message": "PixelGhost backend is alive!"}


@router.post("/lsb/encode")
async def encode_image(
    image: UploadFile = File(...),
    message: str = Form(...),
):
    """Encode a hidden message into an image using LSB steganography."""
    steg = LSB()
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        steg.encode(input_path, message, output_path)

        return FileResponse(
            path=output_path,
            filename="encoded_image.png",
            media_type="image/png"
        )

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        image.file.close()


@router.post("/lsb/decode")
async def decode_image(
    image: UploadFile = File(...),
):
    """Decode and extract a hidden message from an encoded image."""
    steg = LSB()
    input_path = f"/tmp/input_{uuid.uuid4()}.png"

    try:
        # Save uploaded file to temp path
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Decode message
        decoded_message = steg.decode(input_path)

        return JSONResponse(
            content={"message": decoded_message},
            status_code=200
        )

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        image.file.close()


@router.post("/dct/encode")
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
        steg.encode(cover_path, secret_path, output_path)

        return FileResponse(
            path=output_path,
            filename="encoded_image.png",
            media_type="image/png"
        )

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        cover_image.file.close()
        secret_image.file.close()


@router.post("/dct/decode")
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
        steg.decode(input_path, output_path)

        return FileResponse(
            path=output_path,
            filename="extracted_image.png",
            media_type="image/png"
        )

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        image.file.close()


@router.post("/lsb_random/encode")
async def lsb_random_encode_image(
    image: UploadFile = File(...),
    message: str = Form(...),
    key: str = Form(...),
):
    """Encode a hidden message into an image using LSB steganography with randomized pixel selection."""
    steg = LSBRandom(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"
    output_path = f"/tmp/output_{uuid.uuid4()}.png"

    try:
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        steg.encode(input_path, message, output_path)

        return FileResponse(
            path=output_path,
            filename="encoded_image.png",
            media_type="image/png"
        )

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        image.file.close()


@router.post("/lsb_random/decode")
async def lsb_random_decode_image(
    image: UploadFile = File(...),
    key: str = Form(...),
):
    """Decode and extract a hidden message from an encoded image using LSB steganography with randomized pixel selection."""
    steg = LSBRandom(key=key)
    input_path = f"/tmp/input_{uuid.uuid4()}.png"

    try:
        # Save uploaded file to temp path
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        # Decode message
        decoded_message = steg.decode(input_path)

        return JSONResponse(
            content={"message": decoded_message},
            status_code=200
        )

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    finally:
        image.file.close()
