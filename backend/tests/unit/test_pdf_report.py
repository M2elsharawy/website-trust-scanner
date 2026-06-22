"""Unit tests for PDF report generation."""

import pytest

from app.services.pdf_report import generate_pdf_report


def _sample_report(score: int = 75) -> dict:
    return {
        "trust_score": score,
        "trust_level": "good",
        "checks": {
            "https_available": True,
            "https_redirects": True,
            "hsts": False,
            "ssl_valid": True,
            "ssl_expiry_ok": True,
            "headers_csp": False,
            "headers_xfo": True,
            "headers_xcto": True,
            "headers_rp": False,
            "headers_pp": False,
            "reputation": True,
            "dns_resolves": True,
        },
        "recommendations": ["safe_to_browse", "safe_for_email"],
    }


class TestPDFReport:
    def test_returns_bytes(self):
        pdf = generate_pdf_report("example.com", _sample_report())
        assert isinstance(pdf, bytes)

    def test_valid_pdf_header(self):
        pdf = generate_pdf_report("example.com", _sample_report())
        assert pdf[:4] == b"%PDF"

    def test_minimum_size(self):
        pdf = generate_pdf_report("example.com", _sample_report())
        assert len(pdf) > 10_000

    def test_perfect_score_report(self):
        report = _sample_report(100)
        report["trust_level"] = "high"
        report["checks"] = {k: True for k in report["checks"]}
        pdf = generate_pdf_report("perfect.example.com", report)
        assert pdf[:4] == b"%PDF"

    def test_zero_score_report(self):
        report = _sample_report(0)
        report["trust_level"] = "low"
        report["checks"] = {k: False for k in report["checks"]}
        report["recommendations"] = []
        pdf = generate_pdf_report("bad.example.com", report)
        assert pdf[:4] == b"%PDF"

    def test_empty_checks_report(self):
        report = {"trust_score": 50, "trust_level": "medium", "checks": {}, "recommendations": []}
        pdf = generate_pdf_report("example.com", report)
        assert pdf[:4] == b"%PDF"

    def test_arabic_domain_in_report(self):
        # Domain is used in headers — must not crash with unicode
        pdf = generate_pdf_report("مثال.com", _sample_report())
        assert pdf[:4] == b"%PDF"
