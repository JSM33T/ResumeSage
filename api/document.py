from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from db.mongo import db
from helpers.parsers import (
    is_supported_filetype,
    save_uploaded_file,
    process_document,
    generate_guid
)

router = APIRouter()
UPLOAD_DIR = Path("resources")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not is_supported_filetype(file.content_type):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    guid = generate_guid()
    file_bytes = await file.read()
    dest_path = save_uploaded_file(UPLOAD_DIR, guid, file_bytes, file.filename)

    try:
        process_document(dest_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db["documents"].insert_one({
        "_id": guid,
        "filename": file.filename,
        "stored_path": str(dest_path),
        "upload_date": datetime.now(timezone.utc),
        "indexed": False
    })

    return JSONResponse(content={"message": "File uploaded", "guid": guid})
