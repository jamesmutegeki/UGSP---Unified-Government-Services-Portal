from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.middleware import DPPAComplianceMiddleware
from app.api.v1 import auth, catalogue, applications, payments
from app.api.v1.uploads.photo import router as uploads_router

app = FastAPI(
    title="Unified Government Service Portal (UGSP) — API",
    description="Backend API for the Republic of Uganda's Unified Government Service Portal",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(DPPAComplianceMiddleware)

app.include_router(auth.router)
app.include_router(catalogue.router)
app.include_router(applications.router)
app.include_router(payments.router)
app.include_router(uploads_router)

STATIC_DIR = Path(__file__).resolve().parent / "static"
UPLOADS_DIR = STATIC_DIR / "uploads"


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.0.0", "portal": "UGSP"}


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/sw.js")
async def service_worker():
    return FileResponse(STATIC_DIR / "sw.js", media_type="application/javascript",
                        headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"})


app.mount("/static/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
