from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from steganography.lsb import LSB
import shutil
import uuid

router = APIRouter()


@router.get("/")
async def read_root():
    """Health check endpoint."""
    return {"message": "PixelGhost backend is alive!"}


@router.post("/encode")
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


@router.post("/decode")
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
