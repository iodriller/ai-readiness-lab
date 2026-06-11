"""OpportunityCard — a ranked, credible AI pilot opportunity (spec §8.3)."""

from pydantic import BaseModel

from app.models.base import Level, TimeToPilot


class OpportunityCard(BaseModel):
    name: str
    category: str
    executive_summary: str
    why_now: str
    competitive_pressure: str
    business_value: Level
    pilot_feasibility: Level
    risk_level: Level
    time_to_pilot: TimeToPilot
    recommended_first_step: str
    technical_depth_required: Level
