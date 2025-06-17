from pathlib import Path
from uuid import uuid4
import pdfplumber
import docx

def is_supported_filetype(content_type: str) -> bool:
    return content_type in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

def save_uploaded_file(upload_dir: Path, guid: str, file_bytes: bytes, filename: str) -> Path:
    folder = upload_dir / guid
    folder.mkdir(parents=True, exist_ok=True)
    dest_path = folder / filename

    with open(dest_path, "wb") as f:
        f.write(file_bytes)

    return dest_path

def process_pdf(file_path: Path) -> str:
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    return text.strip()

def process_docx(file_path: Path) -> str:
    doc = docx.Document(file_path)
    text = "\n".join(para.text for para in doc.paragraphs)
    return text.strip()

def process_document(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return process_pdf(file_path)
    elif ext == ".docx":
        return process_docx(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
