from fastapi import APIRouter, UploadFile
from app.services.embeddings import process_and_store

router = APIRouter()


@router.post("/")
async def upload_file(file: UploadFile):
    """
    Accepts a file, processes it, and stores embeddings.
    """
    result = await process_and_store(file)
    return {"message": "File processed", "details": result}
