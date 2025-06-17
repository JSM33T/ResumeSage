import os
import logging
from logging.handlers import TimedRotatingFileHandler
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from api import document, health

load_dotenv()

# Load logging flags
log_error = os.getenv("LOG_ERROR", "false").lower() == "true"
log_all = os.getenv("LOG_ALL", "false").lower() == "true"

# Configure loggers
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG if log_all else logging.ERROR)

if log_error or log_all:
    handler = TimedRotatingFileHandler("logs/app.log", when="midnight", backupCount=7)
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global error logging
@app.middleware("http")
async def log_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        if log_error:
            logger.exception(f"Unhandled exception on {request.url.path}")
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

# Routers
app.include_router(health.router, prefix="/api/health")

app.include_router(document.router, prefix="/api/document")