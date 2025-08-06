from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from pathlib import Path
import subprocess

app = FastAPI()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
# Restrict directory permissions to owner only if possible
try:
    UPLOAD_DIR.chmod(0o700)
except PermissionError:
    pass

API_TOKEN = os.environ.get("API_TOKEN", "secret-token")
security = HTTPBearer()

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".jpeg"}
MAX_SIZE = 5 * 1024 * 1024  # 5 MB


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing token")


def scan_for_viruses(file_path: Path):
    """Scan file using clamscan if available."""
    try:
        result = subprocess.run(
            ["clamscan", "--no-summary", str(file_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            text=True,
        )
        if "FOUND" in result.stdout:
            raise HTTPException(status_code=400, detail="Malware detected in file")
    except FileNotFoundError:
        # clamscan not installed; skip scanning
        pass


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    verify_token(credentials)

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")

    contents = await file.read()
    size = len(contents)
    if size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    safe_name = os.path.basename(file.filename)
    dest_path = UPLOAD_DIR / safe_name
    with open(dest_path, "wb") as out_file:
        out_file.write(contents)

    scan_for_viruses(dest_path)

    return {"filename": safe_name}


@app.get("/download/{filename}")
async def download_file(
    filename: str, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    verify_token(credentials)

    safe_name = os.path.basename(filename)
    file_path = UPLOAD_DIR / safe_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)
