from datetime import datetime
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from app.core.auth import verify_token

from ..v1.catalogue import SERVICES

router = APIRouter(prefix="/applications", tags=["applications"])


class ApplyRequest(BaseModel):
    service_id: int
    metadata: dict = {}


APPLICATIONS_DB: list[dict] = []
COUNTER = 0

STATUS_FLOW = [
    "draft",
    "submitted",
    "under_review",
    "approved",
    "rejected",
]


@router.post("")
async def create_application(
    req: ApplyRequest,
    authorization: str = Header(None),
):
    global COUNTER
    nin = verify_token(authorization)
    valid_ids = {s["id"] for s in SERVICES if s["active"]}
    if req.service_id not in valid_ids:
        raise HTTPException(status_code=404, detail="Service not found")
    COUNTER += 1
    app = {
        "id": COUNTER,
        "user_nin": nin,
        "service_id": req.service_id,
        "status": "submitted",
        "metadata": req.metadata,
        "submitted_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    APPLICATIONS_DB.append(app)
    return {"application_id": app["id"], "status": app["status"], "message": "Application submitted successfully"}


@router.get("")
async def list_applications(authorization: str = Header(None)):
    nin = verify_token(authorization)
    user_apps = [a.copy() for a in APPLICATIONS_DB if a["user_nin"] == nin]
    service_map = {s["id"]: s["name"] for s in SERVICES}
    for a in user_apps:
        a["service_name"] = service_map.get(a["service_id"], "Unknown Service")
    return user_apps


@router.get("/{app_id}")
async def get_application(app_id: int, authorization: str = Header(None)):
    nin = verify_token(authorization)
    for a in APPLICATIONS_DB:
        if a["id"] == app_id and a["user_nin"] == nin:
            result = a.copy()
            service_map = {s["id"]: s["name"] for s in SERVICES}
            result["service_name"] = service_map.get(result["service_id"], "Unknown Service")
            return result
    raise HTTPException(status_code=404, detail="Application not found")


@router.delete("/{app_id}")
async def delete_application(app_id: int, authorization: str = Header(None)):
    nin = verify_token(authorization)
    for i, a in enumerate(APPLICATIONS_DB):
        if a["id"] == app_id and a["user_nin"] == nin:
            if a["status"] not in ("draft", "submitted"):
                raise HTTPException(status_code=400, detail="Only draft or submitted applications can be deleted")
            APPLICATIONS_DB.pop(i)
            return {"status": "deleted", "message": f"Application #{app_id} deleted"}
    raise HTTPException(status_code=404, detail="Application not found")
