from fastapi import HTTPException


def verify_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "", 1)
    if not token.startswith("ugpass_"):
        raise HTTPException(status_code=401, detail="Invalid token")
    parts = token.replace("ugpass_", "", 1).split("_", 1)
    if len(parts) < 1 or len(parts[0]) < 10:
        raise HTTPException(status_code=401, detail="Invalid token")
    return parts[0]
