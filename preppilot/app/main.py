from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers import auth, interviews

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

app = FastAPI(title="PrepPilot", description="AI mock interview coach", version="1.0.0")
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(interviews.router)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC_DIR / "index.html")
