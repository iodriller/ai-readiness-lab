from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.projects import router as projects_router
from app.db.base import init_db
from app.qa.router import router as qa_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Readiness Lab API", version="0.1.0", lifespan=lifespan)
app.include_router(projects_router)
app.include_router(qa_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
