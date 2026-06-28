import hashlib

from fastapi import HTTPException

# Shared token store (populated by auth routes)
VALID_TOKENS: dict[str, str] = {}


def verify_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "", 1)
    if not token.startswith("ugpass_"):
        raise HTTPException(status_code=401, detail="Invalid token")
    parts = token.replace("ugpass_", "", 1).split("_", 1)
    if len(parts) < 2:
        raise HTTPException(status_code=401, detail="Invalid token")
    nin, raw = parts[0], parts[1]
    expected = VALID_TOKENS.get(hashlib.sha256(raw.encode()).hexdigest())
    if expected != nin:
        raise HTTPException(status_code=401, detail="Invalid token")
    return nin
