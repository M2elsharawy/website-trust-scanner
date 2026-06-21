from pydantic import BaseModel, field_validator
from typing import Literal


class PublicScanRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def url_must_be_non_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL must not be empty")
        return v


class ChecksSummary(BaseModel):
    https: bool
    ssl_valid: bool
    ssl_expiry_warning: bool
    hsts: bool
    headers_score: int
    headers_max: int
    reputation: Literal["clean", "flagged", "unknown"]


class Recommendations(BaseModel):
    safe_to_browse: bool
    safe_for_email: bool
    safe_for_account: bool
    safe_for_payment: bool


class TrustReport(BaseModel):
    domain: str
    trust_score: int
    trust_level: Literal["low", "medium", "good", "high"]
    checks: ChecksSummary
    recommendations: Recommendations
    warnings: list[str]
