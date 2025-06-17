from datetime import datetime, timezone
from pathlib import Path
from fastapi import Query
from typing import Optional
from uuid import uuid4
from bson.json_util import dumps
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from db.mongo import db
from helpers.parsers import (
    is_supported_filetype,
    save_uploaded_file,
    process_document
)

router = APIRouter()
UPLOAD_DIR = Path("resources")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not is_supported_filetype(file.content_type):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    guid = str(uuid4())
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

@router.get("/list")
def list_documents(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    from_date: Optional[str] = Query(None),  # Format: YYYY-MM-DD
    to_date: Optional[str] = Query(None)
):
    query = {}

    if from_date or to_date:
        query["upload_date"] = {}
        if from_date:
            query["upload_date"]["$gte"] = datetime.strptime(from_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        if to_date:
            query["upload_date"]["$lte"] = datetime.strptime(to_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    skip = (page - 1) * limit
    total = db["documents"].count_documents(query)

    cursor = (
        db["documents"]
        .find(query)
        .sort("upload_date", -1)
        .skip(skip)
        .limit(limit)
    )

    documents = []
    for doc in cursor:
        doc["upload_date"] = doc["upload_date"].isoformat()  # convert datetime to ISO string
        doc["_id"] = str(doc["_id"])  # ensure _id is string
        documents.append(doc)

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "documents": documents
    }