"""Persistence round-trip: Pydantic model -> row -> Pydantic model."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models import ProjectRow
from app.models import Project
from app.models.base import Mode


@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as s:
        yield s


def test_project_row_round_trips(session):
    project = Project(company_name="Occidental", user_role="CTO", mode=Mode.discover_opportunities)
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

    row = session.get(ProjectRow, project.project_id)
    assert row is not None
    assert Project.model_validate(row.payload) == project
