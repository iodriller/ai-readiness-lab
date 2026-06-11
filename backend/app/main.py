from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.base import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Readiness Lab API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
