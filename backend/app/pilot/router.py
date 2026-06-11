"""Guided pilot drill-down routes (spec §11)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.sample import sample_brief
from app.api.schemas import BriefResponse
from app.db.base import get_session
from app.db.models import ProjectRow
from app.models.opportunity import OpportunityCard
from app.pilot.models import PilotPlan, PilotProfile, PilotQuestionsResponse
from app.pilot.questions import QUESTION_IDS, QUESTIONS, technical_checklist
from app.pilot.scorer import score_pilot

router = APIRouter(prefix="/projects", tags=["pilot"])


class PilotIntakeRequest(BaseModel):
    opportunity_name: str = Field(min_length=1)
    answers: dict[str, str] = Field(default_factory=dict)


def _load_brief(row: ProjectRow) -> BriefResponse:
    stored = row.payload.get("brief")
    return BriefResponse.model_validate(stored) if stored else sample_brief(row.company_name)


def _find_card(brief: BriefResponse, name: str) -> OpportunityCard | None:
    return next((c for c in brief.opportunities if c.name == name), None)


def _row_or_404(project_id: str, session: Session) -> ProjectRow:
    row = session.get(ProjectRow, project_id)
    if row is None:
        raise HTTPException(status_code=404, detail="project not found")
    return row


@router.get("/{project_id}/pilot/questions", response_model=PilotQuestionsResponse)
def get_pilot_questions(
    project_id: str,
    opportunity: str = Query(min_length=1),
    session: Session = Depends(get_session),
) -> PilotQuestionsResponse:
    row = _row_or_404(project_id, session)
    if _find_card(_load_brief(row), opportunity) is None:
        raise HTTPException(status_code=404, detail="opportunity not found in this brief")
    return PilotQuestionsResponse(opportunity_name=opportunity, questions=QUESTIONS)


@router.post("/{project_id}/pilot", response_model=PilotPlan)
def submit_pilot_intake(
    project_id: str,
    request: PilotIntakeRequest,
    session: Session = Depends(get_session),
) -> PilotPlan:
    row = _row_or_404(project_id, session)
    card = _find_card(_load_brief(row), request.opportunity_name)
    if card is None:
        raise HTTPException(status_code=404, detail="opportunity not found in this brief")

    answers = {k: v for k, v in request.answers.items() if k in QUESTION_IDS}
    profile = PilotProfile(opportunity_name=request.opportunity_name, answers=answers)
    plan = PilotPlan(
        profile=profile,
        scorecard=score_pilot(card, answers),
        technical_checklist=technical_checklist(answers),
    )

    row.payload = {**row.payload, "pilot": plan.model_dump(mode="json")}
    session.commit()
    return plan


@router.get("/{project_id}/pilot", response_model=PilotPlan | None)
def get_pilot_plan(project_id: str, session: Session = Depends(get_session)) -> PilotPlan | None:
    row = _row_or_404(project_id, session)
    stored = row.payload.get("pilot")
    return PilotPlan.model_validate(stored) if stored else None
