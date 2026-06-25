import uuid
from datetime import datetime
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/payments", tags=["payments"])

PAYMENTS_DB: list[dict] = []


class CheckoutRequest(BaseModel):
    service_id: int
    amount: float
    channel: str = "mobile_money"


def _get_user_nin(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.replace("Bearer ", "", 1)
    if not token.startswith("ugpass_"):
        raise HTTPException(status_code=401, detail="Invalid token")
    parts = token.replace("ugpass_", "", 1).split("_", 1)
    if len(parts) < 1 or len(parts[0]) < 10:
        raise HTTPException(status_code=401, detail="Invalid token")
    return parts[0]


@router.post("/checkout")
async def checkout(
    req: CheckoutRequest,
    authorization: str = Header(None),
):
    nin = _get_user_nin(authorization)
    prn = f"UG{datetime.utcnow().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"

    payment = {
        "prn": prn,
        "user_nin": nin,
        "service_id": req.service_id,
        "amount": req.amount,
        "channel": req.channel,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "paid_at": None,
    }
    PAYMENTS_DB.append(payment)

    return {
        "prn": prn,
        "amount": req.amount,
        "channel": req.channel,
        "status": "pending",
        "message": f"Payment Reference Number (PRN) generated. Use {prn} to pay via {req.channel}.",
    }


@router.get("/{prn}")
async def get_payment(prn: str):
    for p in PAYMENTS_DB:
        if p["prn"] == prn:
            return p
    raise HTTPException(status_code=404, detail="Payment not found")


@router.post("/{prn}/confirm")
async def confirm_payment(prn: str):
    for p in PAYMENTS_DB:
        if p["prn"] == prn:
            p["status"] = "paid"
            p["paid_at"] = datetime.utcnow().isoformat()
            return {"prn": prn, "status": "paid", "message": "Payment confirmed successfully"}
    raise HTTPException(status_code=404, detail="Payment not found")
