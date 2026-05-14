from fastapi import APIRouter, UploadFile, File
import shutil

from app.services.pdf_service import extract_text
from app.storage import document_store

router = APIRouter()

UPLOAD_FOLDER = "uploads"


@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = f"{UPLOAD_FOLDER}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # extract text
    text = extract_text(file_path)

    # store text
    document_store.document_text = text

    return {
        "message": "PDF uploaded successfully"
    }