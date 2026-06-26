import re
import copy
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

from app.core.auth import verify_token

from ..v1.payments import PAYMENTS_DB as GLOBAL_PAYMENTS

router = APIRouter(prefix="/auth", tags=["auth"])


# --- Pydantic models ---
class LoginRequest(BaseModel):
    nin: str
    password: str

    @field_validator("nin", "password")
    @classmethod
    def reject_blank(cls, v):
        if not v or not v.strip():
            raise ValueError("Value must not be blank")
        return v.strip()

class LoginResponse(BaseModel):
    token: str
    name: str
    email: str
    nin: str

class RegisterRequest(BaseModel):
    nin: str
    name: str
    email: EmailStr
    phone: str
    password: str
    category: str = "citizen"

    @field_validator("nin")
    @classmethod
    def nin_format(cls, v):
        v = v.strip()
        if len(v) < 10 or not v.startswith("T"):
            raise ValueError("NIN must start with T and be at least 10 characters")
        return v.upper()

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Name is required")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        v = v.strip()
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @field_validator("phone")
    @classmethod
    def phone_format(cls, v):
        v = v.strip()
        if v and not re.match(r"^\+?256\d{9}$", v.replace(" ", "")):
            raise ValueError("Phone must be a valid Ugandan number (+256...)")
        return v

    @field_validator("category")
    @classmethod
    def valid_category(cls, v):
        if v not in ("citizen", "business", "visitor"):
            raise ValueError("Category must be citizen, business, or visitor")
        return v

class ForgotPasswordRequest(BaseModel):
    nin: str

    @field_validator("nin")
    @classmethod
    def nin_not_empty(cls, v):
        v = v.strip()
        if len(v) < 10:
            raise ValueError("NIN must be at least 10 characters")
        return v.upper()

class ResetPasswordRequest(BaseModel):
    nin: str
    reset_code: str
    new_password: str

    @field_validator("nin")
    @classmethod
    def nin_not_empty(cls, v):
        v = v.strip()
        if len(v) < 10:
            raise ValueError("NIN must be at least 10 characters")
        return v.upper()

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

class FeedbackRequest(BaseModel):
    category: str = "general"
    rating: int = 5
    message: str = ""

    @field_validator("category")
    @classmethod
    def valid_category(cls, v):
        allowed = {"general", "bug", "feature", "service", "accessibility"}
        if v not in allowed:
            raise ValueError(f"Category must be one of: {', '.join(sorted(allowed))}")
        return v

    @field_validator("rating")
    @classmethod
    def valid_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError("Rating must be between 1 and 5")
        return v

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Message is required")
        return v.strip()

class TwoFactorRequest(BaseModel):
    nin: str
    code: str

class ProfilePhotoResponse(BaseModel):
    photo_url: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

class ChangePasswordResponse(BaseModel):
    message: str


# --- Mock data ---
MOCK_USERS: dict[str, dict] = {
    "T1234567890": {"name": "Grace Akello", "email": "grace.akello@ugpass.go.ug", "phone": "+256 700 000 001", "password": "pass123", "category": "citizen", "photo_url": None, "notifications": ["Welcome to UGSP, Grace!", "Your National ID application has been received."]},
    "T2345678901": {"name": "John Okello", "email": "john.okello@ugpass.go.ug", "phone": "+256 700 000 002", "password": "pass123", "category": "business", "photo_url": None, "notifications": ["Your business registration is under review."]},
    "T9876543210": {"name": "Sarah Nabatanzi", "email": "sarah.nabatanzi@ugpass.go.ug", "phone": "+256 700 000 003", "password": "pass123", "category": "citizen", "photo_url": None, "notifications": ["Your passport application has been approved!"]},
}

PENDING_RESETS: dict[str, str] = {}
PENDING_2FA: dict[str, str] = {}
FEEDBACK_DB: list[dict] = []
REGISTER_COUNTER = len(MOCK_USERS)


# --- Login ---
@router.post("/login")
async def login(req: LoginRequest):
    user = MOCK_USERS.get(req.nin)
    if not user or user.get("password", "") != req.password:
        raise HTTPException(status_code=401, detail="Invalid NIN or password")

    minute_str = f"{datetime.utcnow().minute:02d}"
    code = f"{req.nin[-4:]}{minute_str}"
    PENDING_2FA[req.nin] = code
    return {
        "token": f"2fa_{req.nin}",
        "name": user["name"],
        "email": user["email"],
        "nin": req.nin,
        "demo_2fa_code": code,
    }


# --- 2FA Verification ---
@router.post("/verify-2fa")
async def verify_2fa(req: TwoFactorRequest):
    expected = PENDING_2FA.get(req.nin)
    if not expected:
        raise HTTPException(status_code=400, detail="No 2FA session found. Please login again.")
    if req.code != expected:
        raise HTTPException(status_code=401, detail="Invalid 2FA code")
    del PENDING_2FA[req.nin]
    token = f"ugpass_{req.nin}_{req.nin[:4]}"
    user = MOCK_USERS.get(req.nin)
    return {"token": token, "name": user["name"], "email": user["email"], "nin": req.nin}


# --- Register ---
@router.post("/register")
async def register(req: RegisterRequest):
    global REGISTER_COUNTER
    if req.nin in MOCK_USERS:
        raise HTTPException(status_code=409, detail="An account with this NIN already exists")
    REGISTER_COUNTER += 1
    MOCK_USERS[req.nin] = {
        "name": req.name,
        "email": req.email,
        "phone": req.phone,
        "password": req.password,
        "category": req.category,
        "photo_url": None,
        "notifications": ["Welcome to UGSP! Your account has been created successfully."],
    }
    token = f"ugpass_{req.nin}_{req.nin[:4]}"
    return {"token": token, "name": req.name, "email": req.email, "nin": req.nin, "message": "Account created successfully"}


# --- Forgot Password ---
@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    if req.nin not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="NIN not found")
    code = f"RESET{req.nin[-4:]}"
    PENDING_RESETS[req.nin] = code
    return {"message": f"A reset code has been sent to your registered phone/email. Use code: {code}"}


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    expected = PENDING_RESETS.get(req.nin)
    if not expected or expected != req.reset_code:
        raise HTTPException(status_code=400, detail="Invalid reset code")
    if req.nin not in MOCK_USERS:
        raise HTTPException(status_code=404, detail="NIN not found")
    MOCK_USERS[req.nin]["password"] = req.new_password
    del PENDING_RESETS[req.nin]
    return {"message": "Password reset successfully"}


# --- Feedback ---
@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    entry = {
        "category": req.category,
        "rating": req.rating,
        "message": req.message,
        "created_at": datetime.utcnow().isoformat(),
    }
    FEEDBACK_DB.append(entry)
    return {"message": "Thank you for your feedback!", "id": len(FEEDBACK_DB)}


@router.get("/feedback")
async def list_feedback():
    return list(FEEDBACK_DB)


# --- Document Wallet ---
MOCK_DOCUMENTS: dict[str, list[dict]] = {}

DOCUMENT_TEMPLATES = {
    "T1234567890": [
        {"id": "DOC-001", "type": "National ID", "name": "National Identity Card", "issued": "2024-03-15", "expiry": "2034-03-15", "status": "active", "file_size": "245 KB"},
        {"id": "DOC-002", "type": "Passport", "name": "Uganda Passport", "issued": "2024-06-01", "expiry": "2029-06-01", "status": "active", "file_size": "312 KB"},
        {"id": "DOC-003", "type": "Certificate", "name": "Birth Certificate", "issued": "1995-08-22", "expiry": None, "status": "active", "file_size": "180 KB"},
        {"id": "DOC-004", "type": "Permit", "name": "Business Trading License", "issued": "2025-01-10", "expiry": "2026-01-10", "status": "active", "file_size": "420 KB"},
        {"id": "DOC-005", "type": "Receipt", "name": "Passport Application Receipt", "issued": "2025-11-20", "expiry": None, "status": "active", "file_size": "95 KB"},
    ],
    "T1000000001": [
        {"id": "DOC-101", "type": "National ID", "name": "National Identity Card", "issued": "2024-09-01", "expiry": "2034-09-01", "status": "active", "file_size": "230 KB"},
        {"id": "DOC-102", "type": "Certificate", "name": "Driving Permit", "issued": "2025-02-14", "expiry": "2028-02-14", "status": "active", "file_size": "195 KB"},
    ],
    "T1000000003": [
        {"id": "DOC-201", "type": "National ID", "name": "National Identity Card", "issued": "2023-11-20", "expiry": "2033-11-20", "status": "active", "file_size": "240 KB"},
        {"id": "DOC-202", "type": "Certificate", "name": "Certificate of Incorporation", "issued": "2024-05-30", "expiry": None, "status": "active", "file_size": "1.2 MB"},
        {"id": "DOC-203", "type": "Permit", "name": "Tax Registration Certificate", "issued": "2024-06-15", "expiry": "2027-06-15", "status": "active", "file_size": "350 KB"},
        {"id": "DOC-204", "type": "License", "name": "Import/Export License", "issued": "2025-03-01", "expiry": "2026-03-01", "status": "active", "file_size": "510 KB"},
    ],
}


@router.get("/documents")
async def get_documents(authorization: str = Header(None)):
    nin = verify_token(authorization)
    docs = MOCK_DOCUMENTS.get(nin) or DOCUMENT_TEMPLATES.get(nin, [])
    return docs


# --- Activity Log ---
ACTIVITY_LOG: dict[str, list[dict]] = {
    "T1234567890": [
        {"action": "Logged in", "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat(), "device": "Chrome / Windows", "ip": "41.210.xxx.xxx"},
        {"action": "Viewed service: Passport Application", "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(), "device": "Chrome / Windows", "ip": "41.210.xxx.xxx"},
        {"action": "Submitted passport application", "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat(), "device": "Mobile Safari / iOS", "ip": "41.210.xxx.xxx"},
        {"action": "Paid UGX 250,000 via mobile money", "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat(), "device": "Mobile Safari / iOS", "ip": "41.210.xxx.xxx"},
        {"action": "Updated profile photo", "timestamp": (datetime.utcnow() - timedelta(days=7)).isoformat(), "device": "Chrome / Windows", "ip": "41.210.xxx.xxx"},
        {"action": "Changed password", "timestamp": (datetime.utcnow() - timedelta(days=30)).isoformat(), "device": "Chrome / Windows", "ip": "41.210.xxx.xxx"},
        {"action": "Account created", "timestamp": (datetime.utcnow() - timedelta(days=365)).isoformat(), "device": "Chrome / Windows", "ip": "41.210.xxx.xxx"},
    ],
}


@router.get("/activity")
async def get_activity(authorization: str = Header(None)):
    nin = verify_token(authorization)
    return ACTIVITY_LOG.get(nin, [])


# --- Payment History ---
@router.get("/payments")
async def get_payments(authorization: str = Header(None)):
    nin = verify_token(authorization)
    from ..v1.payments import PAYMENTS_DB
    user_payments = [p for p in PAYMENTS_DB if p["user_nin"] == nin]
    return list(reversed(user_payments))


# --- Change Password ---
@router.post("/change-password", response_model=ChangePasswordResponse)
async def change_password(req: ChangePasswordRequest, authorization: str = Header(None)):
    nin = verify_token(authorization)
    user = MOCK_USERS.get(nin)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user["password"] != req.current_password:
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user["password"] = req.new_password
    return {"message": "Password changed successfully"}


# --- News & Announcements ---
MOCK_NEWS = [
    {"id": 1, "title": "New e-Visa System Launched", "summary": "Uganda launches a fully digital e-Visa system for travellers from 150+ countries.", "date": "2026-06-20", "category": "service", "agency": "DCIC"},
    {"id": 2, "title": "Tax Filing Deadline Extended", "summary": "URA extends the income tax filing deadline to 31st July 2026 for individual taxpayers.", "date": "2026-06-18", "category": "announcement", "agency": "URA"},
    {"id": 3, "title": "NIRA Opens New Regional Offices", "summary": "National Identification Authority opens 5 new regional offices to expedite NIN issuance.", "date": "2026-06-15", "category": "service", "agency": "NIRA"},
    {"id": 4, "title": "Business Registration Now 100% Online", "summary": "URSB completes digital transformation — all business services available via UGSP.", "date": "2026-06-10", "category": "update", "agency": "URSB"},
    {"id": 5, "title": "National Health Insurance Rollout", "summary": "MoH announces phased rollout of the National Health Insurance Scheme starting Q3 2026.", "date": "2026-06-05", "category": "announcement", "agency": "MoH"},
    {"id": 6, "title": "Driving Licence Digital Cards", "summary": "All new driving licences will be issued as digital cards with QR verification codes.", "date": "2026-05-28", "category": "update", "agency": "MIA"},
]


@router.get("/news")
async def get_news():
    return list(MOCK_NEWS)


# --- Help / FAQ ---
HELP_DATA = {
    "categories": [
        {
            "name": "Getting Started",
            "icon": "rocket_launch",
            "faqs": [
                {"q": "How do I create an account?", "a": "Click 'Create an Account' on the login page. Enter your National ID Number (NIN), name, email, phone, and a strong password. Once registered, you'll receive a welcome notification."},
                {"q": "What is a NIN and how do I get one?", "a": "A National Identification Number (NIN) is a unique 11-digit number starting with 'T'. Visit any NIRA office to register for your National ID."},
                {"q": "How does Two-Factor Authentication work?", "a": "After entering your password, a 6-digit code is sent to your registered phone. Enter this code on the 2FA screen to complete login."},
            ],
        },
        {
            "name": "Services & Applications",
            "icon": "grid_view",
            "faqs": [
                {"q": "How do I apply for a service?", "a": "Browse the Services page, click on a service to view details, then click 'Apply Now'. You can track your application status from the Applications page."},
                {"q": "How long do applications take?", "a": "Processing times vary by service — check the 'Turnaround' field on each service card. Simple services take 1-3 days, while complex ones may take 2-4 weeks."},
                {"q": "Can I apply for multiple services at once?", "a": "Yes! Each application is independent. You can apply for as many services as you need."},
            ],
        },
        {
            "name": "Payments",
            "icon": "account_balance_wallet",
            "faqs": [
                {"q": "What payment methods are accepted?", "a": "UGSP accepts Mobile Money (MTN, Airtel), Bank Transfer, and Card Payments (Visa, Mastercard). Mobile Money is the fastest option."},
                {"q": "What is a PRN?", "a": "A Payment Reference Number (PRN) is a unique code generated for each payment. Use it to make payments via your preferred channel."},
                {"q": "How do I get a refund?", "a": "Refund requests must be submitted via the Feedback form. Our team will process eligible refunds within 14 working days."},
            ],
        },
        {
            "name": "Account & Security",
            "icon": "security",
            "faqs": [
                {"q": "How do I reset my password?", "a": "Click 'Forgot Password' on the login page. Enter your NIN, receive a reset code, and set a new password. You can also change your password from Settings."},
                {"q": "Is my data safe?", "a": "Yes. UGSP is fully compliant with Uganda's Data Protection and Privacy Act (DPPA) 2019. All data is encrypted in transit and at rest."},
                {"q": "How do I update my profile?", "a": "Navigate to the Profile page from the sidebar. You can update your photo, phone number, and email address."},
            ],
        },
    ],
}


@router.get("/help")
async def get_help():
    return dict(HELP_DATA)


# --- About UGSP ---
@router.get("/about")
async def get_about():
    return {
        "name": "Unified Government Service Portal (UGSP)",
        "version": "2.0.0",
        "tagline": "Your Gateway to Government Services",
        "description": "UGSP is the Republic of Uganda's unified digital platform for accessing government services online. It provides a single point of access to services across all ministries, departments, and agencies.",
        "ministry": "Ministry of ICT & National Guidance",
        "agency": "National Information Technology Authority (NITA-U)",
        "legal_framework": {
            "dppa_2019": "UGSP complies with the Data Protection and Privacy Act (DPPA) 2019. All personal data is collected, processed, and stored in accordance with Ugandan law.",
            "access_information": "The Access to Information Act 2005 guarantees your right to access information held by public bodies.",
            "e_signature": "Electronic signatures and transactions are legally recognized under the Electronic Transactions Act 2011.",
        },
        "commitments": [
            "Data minimisation — we only collect what is necessary",
            "Transparency — you can view who accessed your data via the Activity Log",
            "Security — end-to-end encryption and multi-factor authentication",
            "Accessibility — designed for all citizens including those with disabilities",
            "No vendor lock-in — built on open standards and interoperable APIs",
        ],
        "stats": {
            "services": 29,
            "ministries": 25,
            "users": "15,000+",
            "applications_processed": "45,000+",
        },
    }


# --- Notifications ---
@router.get("/notifications")
async def get_notifications(authorization: str = Header(None)):
    nin = verify_token(authorization)
    return MOCK_USERS.get(nin, {}).get("notifications", [])


@router.post("/notifications/read")
async def mark_notifications_read(authorization: str = Header(None)):
    nin = verify_token(authorization)
    MOCK_USERS[nin]["notifications"] = []
    return {"message": "Notifications cleared"}


# --- Token verify & profile ---
@router.get("/verify")
async def verify_token(authorization: str = Header(None)):
    nin = verify_token(authorization)
    user = MOCK_USERS.get(nin)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {"valid": True, "nin": nin, "name": user["name"], "email": user["email"]}


@router.get("/profile")
async def get_profile(authorization: str = Header(None)):
    nin = verify_token(authorization)
    user = MOCK_USERS.get(nin)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return {
        "nin": nin,
        "name": user["name"],
        "email": user["email"],
        "phone": user.get("phone", "+256 700 000 000"),
        "nationality": "Ugandan",
        "category": user.get("category", "citizen"),
        "verified": True,
        "photo_url": user.get("photo_url"),
    }
