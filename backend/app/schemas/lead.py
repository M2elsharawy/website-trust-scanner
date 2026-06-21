import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator

from app.models.lead import LeadStatus


class LeadCreate(BaseModel):
    domain: str

    @field_validator("domain")
    @classmethod
    def normalise_domain(cls, v: str) -> str:
        v = v.strip().lower().removeprefix("https://").removeprefix("http://").rstrip("/")
        if not v:
            raise ValueError("Domain must not be empty")
        return v


class LeadStatusUpdate(BaseModel):
    status: LeadStatus
    notes: str | None = None


class LeadSummary(BaseModel):
    id: uuid.UUID
    domain: str
    status: LeadStatus
    last_lead_score: int | None
    last_audit_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadDetail(LeadSummary):
    notes: str | None
    added_by: str | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class OutreachReport(BaseModel):
    lead_id: uuid.UUID
    domain: str
    lead_score: int
    opportunity_level: Literal["low", "medium", "good", "high"]
    improvement_areas_en: list[str]
    improvement_areas_ar: list[str]
    outreach_message_en: str
    outreach_message_ar: str
    checks_summary: dict  # safe summary only — no exploitable details
    generated_at: datetime
