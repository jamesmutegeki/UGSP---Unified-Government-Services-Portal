import os
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Header, HTTPException

from app.core.auth import verify_token

router = APIRouter(prefix="/uploads", tags=["uploads"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent.parent / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {"image/jpeg", "image/jpg"}
MAX_SIZE = 5 * 1024 * 1024


@router.post("/photo")
async def upload_photo(
    file: UploadFile = File(...),
    authorization: str = Header(None),
):
    nin = verify_token(authorization)
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only JPEG files are accepted")
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 5MB limit")
    ext = "jpg"
    filename = f"{nin}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = UPLOAD_DIR / filename
    with open(filepath, "wb") as f:
        f.write(content)
    photo_url = f"/static/uploads/{filename}"
    return {"photo_url": photo_url, "message": "Photo uploaded successfully"}
