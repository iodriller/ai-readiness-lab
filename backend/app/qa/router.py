"""Q&A router: POST /projects/{id}/qa (spec §10)."""

from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.db.models import ProjectRow
from app.qa.classifier import classify
from app.qa.composer import StructuredAnswer, compose_answer
from app.qa.retriever import gather_context

router = APIRouter(prefix="/projects", tags=["qa"])


class QARequest(BaseModel):
    question: str = Field(min_length=1)


def _create_llm():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    from app.llm.client import AnthropicClient

    return AnthropicClient(api_key=api_key)


@router.post("/{project_id}/qa", response_model=StructuredAnswer)
def ask_question(
    project_id: str,
    request: QARequest,
    session: Session = Depends(get_session),
) -> StructuredAnswer:
    ctx = gather_context(project_id, session)
    if ctx is None:
        raise HTTPException(status_code=404, detail="project not found")

    question_type = classify(request.question)
    llm = _create_llm()
    answer = compose_answer(request.question, question_type, ctx, llm)

    # Persist to qa_history so future questions can reference prior answers.
    row = session.get(ProjectRow, project_id)
    history: list[dict] = row.payload.get("qa_history", [])
    history.append({"question": request.question, "answer": answer.model_dump()})
    row.payload = {**row.payload, "qa_history": history}
    session.commit()

    return answer
