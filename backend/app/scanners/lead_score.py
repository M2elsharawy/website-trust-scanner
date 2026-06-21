"""
Lead Score computation.

Measures BUSINESS OPPORTUNITY — how much a site could benefit from
security services. This is intentionally the inverse of Trust Score:
a site with more gaps = higher commercial opportunity.

Scoring rubric (base 50, max 100 before clamping):
  No HTTPS                     +20  (critical gap)
  No SSL / SSL issues          +15
  SSL expiry warning           +10  (urgent, time-sensitive)
  No HTTP→HTTPS redirect       +5
  HSTS missing                 +5
  Security headers missing ≥4  +10
  Security headers missing 2-3 +5
  All checks perfect           -20  (low opportunity — they have a team)

Opportunity levels:
  0–29:  low      (well-secured, small opportunity)
  30–59: medium
  60–79: good
  80–100: high    (significant gaps, strong opportunity)
"""

from typing import Literal

from app.scanners.result import ScanData

OpportunityLevel = Literal["low", "medium", "good", "high"]


def compute_lead_score(data: ScanData) -> int:
    score = 50  # neutral baseline

    if not data.https.available:
        score += 20

    if not data.ssl.valid:
        score += 15
    elif data.ssl.expiry_warning:
        score += 10

    if data.https.available and not data.https.redirects_from_http:
        score += 5

    if not data.https.hsts_present:
        score += 5

    missing_headers = data.headers.MAX_SCORE - data.headers.score
    if missing_headers >= 4:
        score += 10
    elif missing_headers >= 2:
        score += 5

    # Site appears very well-secured — low opportunity
    if (
        data.https.available
        and data.ssl.valid
        and not data.ssl.expiry_warning
        and data.https.hsts_present
        and data.headers.score >= 4
    ):
        score -= 20

    return max(0, min(100, score))


def score_to_opportunity_level(score: int) -> OpportunityLevel:
    if score >= 80:
        return "high"
    if score >= 60:
        return "good"
    if score >= 30:
        return "medium"
    return "low"
