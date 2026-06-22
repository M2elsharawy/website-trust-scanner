import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ScanResultSummary(BaseModel):
    id: uuid.UUID
    domain: str
    trust_score: int
    scanned_at: datetime

    model_config = {"from_attributes": True}


class ScanResultDetail(BaseModel):
    id: uuid.UUID
    site_id: uuid.UUID
    domain: str
    trust_score: int
    result_json: dict[str, Any]
    scanned_at: datetime

    model_config = {"from_attributes": True}
