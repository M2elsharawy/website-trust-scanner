"""
Unit tests for the trust score computation.
"""

import pytest

from app.scanners.result import (
    DNSCheckResult,
    HeadersCheckResult,
    HTTPSCheckResult,
    ReputationCheckResult,
    ScanData,
    SSLCheckResult,
)
from app.scanners.trust_score import compute_trust_report, _score_to_level


def _perfect_scan(domain: str = "example.com") -> ScanData:
    return ScanData(
        domain=domain,
        dns=DNSCheckResult(resolves=True),
        https=HTTPSCheckResult(available=True, redirects_from_http=True, hsts_present=True),
        ssl=SSLCheckResult(valid=True, expiry_warning=False),
        headers=HeadersCheckResult(
            csp_present=True,
            x_frame_options_present=True,
            x_content_type_options_present=True,
            referrer_policy_present=True,
            permissions_policy_present=True,
        ),
        reputation=ReputationCheckResult(status="clean"),
    )


def _minimal_scan(domain: str = "example.com") -> ScanData:
    return ScanData(domain=domain)


# ── Score levels ─────────────────────────────────────────────────────────────

class TestScoreToLevel:
    def test_80_is_high(self):
        assert _score_to_level(80) == "high"

    def test_100_is_high(self):
        assert _score_to_level(100) == "high"

    def test_79_is_good(self):
        assert _score_to_level(79) == "good"

    def test_60_is_good(self):
        assert _score_to_level(60) == "good"

    def test_59_is_medium(self):
        assert _score_to_level(59) == "medium"

    def test_30_is_medium(self):
        assert _score_to_level(30) == "medium"

    def test_29_is_low(self):
        assert _score_to_level(29) == "low"

    def test_0_is_low(self):
        assert _score_to_level(0) == "low"


# ── Perfect score ─────────────────────────────────────────────────────────────

class TestPerfectScan:
    def test_perfect_score_is_100(self):
        report = compute_trust_report("example.com", _perfect_scan())
        assert report["trust_score"] == 100

    def test_perfect_level_is_high(self):
        report = compute_trust_report("example.com", _perfect_scan())
        assert report["trust_level"] == "high"

    def test_perfect_all_recommendations(self):
        report = compute_trust_report("example.com", _perfect_scan())
        recs = report["recommendations"]
        assert recs["safe_to_browse"] is True
        assert recs["safe_for_email"] is True
        assert recs["safe_for_account"] is True
        assert recs["safe_for_payment"] is True

    def test_perfect_no_warnings(self):
        report = compute_trust_report("example.com", _perfect_scan())
        assert report["warnings"] == []


# ── Minimal / empty scan ──────────────────────────────────────────────────────

class TestMinimalScan:
    def test_minimal_score_is_zero(self):
        report = compute_trust_report("example.com", _minimal_scan())
        assert report["trust_score"] == 0

    def test_minimal_level_is_low(self):
        report = compute_trust_report("example.com", _minimal_scan())
        assert report["trust_level"] == "low"

    def test_minimal_no_recommendations(self):
        report = compute_trust_report("example.com", _minimal_scan())
        recs = report["recommendations"]
        assert not any(recs.values())


# ── Individual checks contribute correctly ────────────────────────────────────

class TestScoreContributions:
    def test_dns_only(self):
        data = _minimal_scan()
        data.dns.resolves = True
        report = compute_trust_report("example.com", data)
        assert report["trust_score"] == 5

    def test_https_adds_25(self):
        data = _minimal_scan()
        data.dns.resolves = True
        data.https.available = True
        report = compute_trust_report("example.com", data)
        assert report["trust_score"] == 30  # 5 + 25

    def test_http_redirect_adds_5(self):
        data = _minimal_scan()
        data.https.available = True
        data.https.redirects_from_http = True
        report = compute_trust_report("example.com", data)
        assert 5 in [report["trust_score"] - 25]  # redirect = 5 pts

    def test_ssl_valid_adds_25(self):
        data = _minimal_scan()
        data.https.available = True
        data.ssl.valid = True
        report = compute_trust_report("example.com", data)
        assert report["trust_score"] == 25 + 20 + 5  # https + ssl + no expiry warning

    def test_hsts_adds_10(self):
        data = _minimal_scan()
        data.https.available = True
        data.https.hsts_present = True
        report = compute_trust_report("example.com", data)
        assert report["trust_score"] == 25 + 10  # https + hsts

    def test_csp_adds_10(self):
        data = _minimal_scan()
        data.headers.csp_present = True
        report = compute_trust_report("example.com", data)
        assert report["trust_score"] == 10

    def test_reputation_clean_adds_nothing(self):
        data = _minimal_scan()
        data.reputation.status = "clean"
        report = compute_trust_report("example.com", data)
        assert report["trust_score"] == 0  # clean reputation carries no bonus


# ── Reputation suspicious penalty ─────────────────────────────────────────────

class TestReputationPenalty:
    def test_suspicious_penalizes_score(self):
        data = _perfect_scan()
        data.reputation.status = "suspicious"
        report = compute_trust_report("example.com", data)
        assert report["trust_score"] == 80  # 100 - 20 penalty

    def test_suspicious_blocks_safe_to_browse(self):
        data = _perfect_scan()
        data.reputation.status = "suspicious"
        report = compute_trust_report("example.com", data)
        assert report["recommendations"]["safe_to_browse"] is False

    def test_suspicious_shown_as_flagged_in_response(self):
        data = _minimal_scan()
        data.reputation.status = "suspicious"
        report = compute_trust_report("example.com", data)
        assert report["checks"]["reputation"] == "flagged"

    def test_score_clamped_to_zero(self):
        data = _minimal_scan()
        data.reputation.status = "suspicious"
        report = compute_trust_report("example.com", data)
        assert report["trust_score"] == 0


# ── SSL expiry warning ────────────────────────────────────────────────────────

class TestSSLExpiry:
    def test_expiry_warning_in_response(self):
        data = _perfect_scan()
        data.ssl.expiry_warning = True
        report = compute_trust_report("example.com", data)
        assert "ssl_expiry_soon" in report["warnings"]

    def test_expiry_warning_deducts_score(self):
        data = _perfect_scan()
        data.ssl.expiry_warning = True
        report = compute_trust_report("example.com", data)
        assert report["trust_score"] == 95  # perfect 100 - 5 (no expiry bonus)


# ── Response does not contain sensitive fields ────────────────────────────────

class TestSafeResponse:
    def test_no_ip_in_response(self):
        report = compute_trust_report("example.com", _perfect_scan())
        report_str = str(report)
        assert "192.168" not in report_str
        assert "10.0" not in report_str

    def test_domain_in_response(self):
        report = compute_trust_report("example.com", _perfect_scan())
        assert report["domain"] == "example.com"

    def test_no_raw_header_values(self):
        report = compute_trust_report("example.com", _perfect_scan())
        # checks should only have score counts, not header values
        checks = report["checks"]
        assert "headers_score" in checks
        assert "headers_max" in checks
        # Ensure no raw header value keys
        for key in checks:
            assert "value" not in key
