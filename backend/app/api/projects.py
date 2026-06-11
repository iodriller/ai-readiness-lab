"""Executive-shell project routes: create, fetch, research progress (SSE), brief."""

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.sample import sample_brief
from app.api.schemas import BriefResponse, CreateProjectRequest
from app.db.base import get_session
from app.db.models import ProjectRow
from app.models import Project
from app.models.base import Mode
from app.research import orchestrator

router = APIRouter(prefix="/projects", tags=["projects"])


def _sse_event(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


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
    row = session.get(ProjectRow, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")

    company_name = row.company_name
    mode = Mode(row.mode)

    async def generate():
        async for event in orchestrator.run(project_id, company_name, mode):
            yield _sse_event(event)

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/{project_id}/brief", response_model=BriefResponse)
def get_brief(project_id: str, session: Session = Depends(get_session)) -> BriefResponse:
    row = session.get(ProjectRow, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    stored = row.payload.get("brief")
    if stored:
        return BriefResponse.model_validate(stored)
    return sample_brief(row.company_name)
