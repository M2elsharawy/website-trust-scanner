"""
Unit tests for the Scan Policy Engine.
"""

import pytest

from app.core.scan_policy import ScanType, check_scan_allowed
from app.core.exceptions import (
    AuthorizationRequiredError,
    DomainBlockedError,
)


SAFE_DOMAIN = "example.com"


# ── Do Not Scan list (highest priority) ──────────────────────────────────────

class TestDoNotScanBlock:
    def test_public_scan_on_blocked_domain_raises(self):
        with pytest.raises(DomainBlockedError) as exc:
            check_scan_allowed(
                domain=SAFE_DOMAIN,
                scan_type=ScanType.PUBLIC_TRUST,
                is_on_do_not_scan_list=True,
            )
        assert exc.value.error_code == "DOMAIN_BLOCKED"

    def test_authorized_scan_on_blocked_domain_still_raises(self):
        """Authorization Record cannot override Do Not Scan."""
        with pytest.raises(DomainBlockedError):
            check_scan_allowed(
                domain=SAFE_DOMAIN,
                scan_type=ScanType.FULL_SECURITY,
                is_on_do_not_scan_list=True,
                has_active_authorization=True,
            )

    def test_all_scan_types_blocked_when_on_list(self):
        for scan_type in ScanType:
            with pytest.raises(DomainBlockedError):
                check_scan_allowed(
                    domain=SAFE_DOMAIN,
                    scan_type=scan_type,
                    is_on_do_not_scan_list=True,
                )


# ── Public trust scan ────────────────────────────────────────────────────────

class TestPublicTrustScan:
    def test_public_trust_allowed_without_auth(self):
        # Must not raise
        check_scan_allowed(
            domain=SAFE_DOMAIN,
            scan_type=ScanType.PUBLIC_TRUST,
            is_on_do_not_scan_list=False,
        )

    def test_public_trust_allowed_with_auth_too(self):
        check_scan_allowed(
            domain=SAFE_DOMAIN,
            scan_type=ScanType.PUBLIC_TRUST,
            is_on_do_not_scan_list=False,
            has_active_authorization=True,
        )


# ── Authorization required for non-public scans ───────────────────────────────

class TestAuthorizationRequired:
    @pytest.mark.parametrize("scan_type", [
        ScanType.SECURITY_HEADERS,
        ScanType.SSL_AUDIT,
        ScanType.CONTENT_SCAN,
        ScanType.FULL_SECURITY,
    ])
    def test_non_public_without_auth_raises(self, scan_type):
        with pytest.raises(AuthorizationRequiredError) as exc:
            check_scan_allowed(
                domain=SAFE_DOMAIN,
                scan_type=scan_type,
                is_on_do_not_scan_list=False,
                has_active_authorization=False,
            )
        assert exc.value.error_code == "AUTHORIZATION_REQUIRED"

    @pytest.mark.parametrize("scan_type", [
        ScanType.SECURITY_HEADERS,
        ScanType.SSL_AUDIT,
        ScanType.CONTENT_SCAN,
        ScanType.FULL_SECURITY,
    ])
    def test_non_public_with_auth_allowed(self, scan_type):
        # Must not raise
        check_scan_allowed(
            domain=SAFE_DOMAIN,
            scan_type=scan_type,
            is_on_do_not_scan_list=False,
            has_active_authorization=True,
        )


# ── Error messages include domain ────────────────────────────────────────────

class TestErrorMessages:
    def test_blocked_error_message_contains_domain(self):
        domain = "evil.example.com"
        with pytest.raises(DomainBlockedError) as exc:
            check_scan_allowed(
                domain=domain,
                scan_type=ScanType.PUBLIC_TRUST,
                is_on_do_not_scan_list=True,
            )
        assert domain in exc.value.message

    def test_auth_error_message_contains_scan_type(self):
        with pytest.raises(AuthorizationRequiredError) as exc:
            check_scan_allowed(
                domain=SAFE_DOMAIN,
                scan_type=ScanType.FULL_SECURITY,
                is_on_do_not_scan_list=False,
                has_active_authorization=False,
            )
        assert "full_security" in exc.value.message
