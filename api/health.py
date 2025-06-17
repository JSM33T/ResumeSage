from fastapi import APIRouter
from fastapi.responses import JSONResponse
# from db.mongo import db

router = APIRouter()

@router.get("/")
def check_health():
    return JSONResponse(content={"status": "ok", "message": "System is up and running."})
