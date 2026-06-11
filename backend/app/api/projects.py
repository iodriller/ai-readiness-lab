"""Executive-shell project routes: create, fetch, research progress (SSE), brief."""

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.sample import sample_brief
from app.api.schemas import BriefResponse, CreateProjectRequest, ProjectSummary
from app.db.base import get_session
from app.db.models import ProjectRow
from app.models import CompanyIntelligenceProfile, PeerClassification, Project
from app.models.base import Mode
from app.report.generator import render_markdown, render_pdf
from app.research import orchestrator

router = APIRouter(prefix="/projects", tags=["projects"])


def _sse_event(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def _load_brief(row: ProjectRow) -> BriefResponse:
    stored = row.payload.get("brief")
    return BriefResponse.model_validate(stored) if stored else sample_brief(row.company_name)


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


@router.get("", response_model=list[ProjectSummary])
def list_projects(session: Session = Depends(get_session)) -> list[ProjectSummary]:
    """Recent reviews for the home screen, newest first."""
    rows = session.execute(select(ProjectRow).order_by(ProjectRow.created_at.desc())).scalars()
    return [
        ProjectSummary(
            project_id=r.project_id,
            company_name=r.company_name,
            user_role=r.user_role,
            mode=r.mode,
            status=r.status,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]


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
    return _load_brief(row)


def _report_filename(company: str, ext: str) -> str:
    slug = "".join(c if c.isalnum() else "-" for c in company).strip("-").lower() or "company"
    return f"ai-readiness-{slug}.{ext}"


@router.get("/{project_id}/report.md")
def get_report_markdown(project_id: str, session: Session = Depends(get_session)) -> Response:
    row = session.get(ProjectRow, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    markdown = render_markdown(_load_brief(row), row.payload.get("qa_history", []))
    filename = _report_filename(row.company_name, "md")
    return Response(
        content=markdown,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{project_id}/report.pdf")
def get_report_pdf(project_id: str, session: Session = Depends(get_session)) -> Response:
    row = session.get(ProjectRow, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    pdf = render_pdf(_load_brief(row), row.payload.get("qa_history", []))
    filename = _report_filename(row.company_name, "pdf")
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{project_id}/peers", response_model=list[PeerClassification])
def get_peers(project_id: str, session: Session = Depends(get_session)) -> list[PeerClassification]:
    """Peer classifications with stated reasons — the 'why is X a vendor not a
    competitor?' explanation (spec §3.3). Empty until research with an LLM runs."""
    row = session.get(ProjectRow, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    return [PeerClassification.model_validate(p) for p in row.payload.get("peers", [])]


@router.get("/{project_id}/profile", response_model=CompanyIntelligenceProfile | None)
def get_profile(
    project_id: str, session: Session = Depends(get_session)
) -> CompanyIntelligenceProfile | None:
    """The structured company profile (identity, peers, signals). Null until
    research with an LLM runs."""
    row = session.get(ProjectRow, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    stored = row.payload.get("profile")
    return CompanyIntelligenceProfile.model_validate(stored) if stored else None
