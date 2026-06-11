"""Executive-shell project routes: create, fetch, research progress (SSE), brief."""

import asyncio
import json
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.sample import sample_brief
from app.api.schemas import BriefResponse, CreateProjectRequest
from app.db.base import SessionLocal, get_session
from app.db.models import ProjectRow
from app.models import Project
from app.models.base import ProjectStatus

router = APIRouter(prefix="/projects", tags=["projects"])

# Calm, step-by-step progress shown while research runs (spec §4.3).
RESEARCH_STEPS = [
    "Identifying company profile",
    "Classifying company type and business segments",
    "Finding public financial and strategic signals",
    "Identifying direct competitors and adjacent peers",
    "Searching competitor AI and digital initiatives",
    "Searching industry AI patterns",
    "Building AI opportunity map",
    "Preparing executive brief",
]

# Per-step delay for the mock job; set to 0 in tests for speed.
STEP_DELAY_SECONDS = float(os.getenv("RESEARCH_STEP_DELAY_SECONDS", "0.6"))


def _sse_event(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def _mark_ready(project_id: str) -> None:
    with SessionLocal() as session:
        row = session.get(ProjectRow, project_id)
        if row is None:
            return
        row.status = ProjectStatus.ready.value
        row.payload = {**row.payload, "status": ProjectStatus.ready.value}
        session.commit()


@router.post("", response_model=Project)
def create_project(
    request: CreateProjectRequest, session: Session = Depends(get_session)
) -> Project:
    project = Project(
        company_name=request.company_name,
        user_role=request.user_role,
        mode=request.mode,
    )
    session.add(
        ProjectRow(
            project_id=project.project_id,
            company_name=project.company_name,
            user_role=project.user_role,
            mode=project.mode.value,
            status=project.status.value,
            created_at=project.created_at,
            payload=project.model_dump(mode="json"),
        )
    )
    session.commit()
    return project


@router.get("/{project_id}", response_model=Project)
def get_project(project_id: str, session: Session = Depends(get_session)) -> Project:
    row = session.get(ProjectRow, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    return Project.model_validate(row.payload)


@router.get("/{project_id}/research/stream")
async def stream_research(
    project_id: str, session: Session = Depends(get_session)
) -> StreamingResponse:
    if session.get(ProjectRow, project_id) is None:
        raise HTTPException(status_code=404, detail="project not found")

    async def generate():
        total = len(RESEARCH_STEPS)
        for index, label in enumerate(RESEARCH_STEPS, start=1):
            await asyncio.sleep(STEP_DELAY_SECONDS)
            yield _sse_event({"type": "step", "index": index, "total": total, "label": label})
        _mark_ready(project_id)
        yield _sse_event({"type": "done"})

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/{project_id}/brief", response_model=BriefResponse)
def get_brief(project_id: str, session: Session = Depends(get_session)) -> BriefResponse:
    row = session.get(ProjectRow, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    return sample_brief(row.company_name)
