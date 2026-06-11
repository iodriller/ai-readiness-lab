import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.projects import router as projects_router
from app.api.settings import router as settings_router
from app.db.base import init_db
from app.pilot.router import router as pilot_router
from app.qa.router import router as qa_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Readiness Lab API", version="0.1.0", lifespan=lifespan)
app.include_router(projects_router)
app.include_router(qa_router)
app.include_router(settings_router)
app.include_router(pilot_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def _static_dir() -> Path | None:
    """Locate the built frontend (frontend/dist).

    In the PyInstaller bundle the assets are unpacked next to the executable
    (sys._MEIPASS). In a source checkout they live at frontend/dist. Returns None
    when no build is present (the dev backend runs API-only).
    """
    import os

    override = os.getenv("AIRL_STATIC_DIR")
    candidates = [Path(override)] if override else []
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        candidates.append(Path(bundle_root) / "frontend_dist")
    candidates.append(Path(__file__).resolve().parents[2] / "frontend" / "dist")
    for path in candidates:
        if path.is_dir() and (path / "index.html").exists():
            return path
    return None


# Serve the built single-page app from the same origin as the API, so the
# packaged desktop window loads the whole product from one local server.
_dist = _static_dir()
if _dist is not None:
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="spa")
