"""
Trust score computation.

Aggregates internal ScanData into a safe TrustReport for the API response.
Nothing from ScanData that could be exploitable (IPs, cert details, etc.)
is present in TrustReport.

Scoring rubric (max 100 before penalty):
  DNS resolves            +5
  HTTPS available         +25
  HTTP-to-HTTPS redirect  +5
  SSL valid               +20
  SSL no expiry warning   +5
  HSTS present            +10
  CSP header              +10
  X-Frame-Options         +5
  X-Content-Type-Options  +5
  Referrer-Policy         +5
  Permissions-Policy      +5
  Reputation suspicious   -20 (penalty only; unknown/clean adds 0)
"""

from typing import Literal

from app.scanners.result import ScanData

TrustLevel = Literal["low", "medium", "good", "high"]


def _recalculate_with_weights(data: ScanData) -> int:
    score = 0
    if data.dns.resolves:
        score += 5
    if data.https.available:
        score += 25
        if data.https.redirects_from_http:
            score += 5
        if data.https.hsts_present:
            score += 10
    if data.ssl.valid:
        score += 20
        if not data.ssl.expiry_warning:
            score += 5
    if data.headers.csp_present:
        score += 10
    if data.headers.x_frame_options_present:
        score += 5
    if data.headers.x_content_type_options_present:
        score += 5
    if data.headers.referrer_policy_present:
        score += 5
    if data.headers.permissions_policy_present:
        score += 5
    return score


def _score_to_level(score: int) -> TrustLevel:
    if score >= 80:
        return "high"
    if score >= 60:
        return "good"
    if score >= 30:
        return "medium"
    return "low"


def compute_trust_report(domain: str, data: ScanData) -> dict:
    """
    Returns a safe dict for the API response.

    Contains NO exploitable details (no IPs, no cert subject/issuer,
    no raw header values, no DNS records).
    """
    raw_score = _recalculate_with_weights(data)
    if data.reputation.status == "suspicious":
        raw_score -= 20
    score = max(0, min(100, raw_score))
    level = _score_to_level(score)

    warnings: list[str] = []
    if data.ssl.valid and data.ssl.expiry_warning:
        warnings.append("ssl_expiry_soon")

    recommendations = {
        "safe_to_browse": (
            score >= 30 and data.reputation.status != "suspicious"
        ),
        "safe_for_email": (
            score >= 50 and data.https.available
        ),
        "safe_for_account": (
            score >= 65 and data.https.available and data.ssl.valid
        ),
        "safe_for_payment": (
            score >= 80
            and data.https.available
            and data.ssl.valid
            and data.https.hsts_present
        ),
    }

    return {
        "domain": domain,
        "trust_score": score,
        "trust_level": level,
        "checks": {
            "https": data.https.available,
            "ssl_valid": data.ssl.valid,
            "ssl_expiry_warning": data.ssl.expiry_warning,
            "hsts": data.https.hsts_present,
            "headers_score": data.headers.score,
            "headers_max": data.headers.MAX_SCORE,
            "reputation": (
                "flagged" if data.reputation.status == "suspicious"
                else data.reputation.status
            ),
        },
        "recommendations": recommendations,
        "warnings": warnings,
    }
