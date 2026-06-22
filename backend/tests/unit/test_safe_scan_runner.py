"""
Tests for app/core/safe_scan_runner.py, public_scan handler, and owner_scan handler.

Coverage:
- Do Not Scan blocks before URL validation / DNS resolution (public + owner)
- SSRF block prevents scanner from running (public + owner)
- Policy deny prevents scanner from running (public + owner)
- Successful scan passes validated_hostname to run_public_scan (public + owner)
- Owner report uses site.domain, not validated_hostname
- Owner blocked audit carries actor_id, actor_role, resource_type=site
- Audit log writes .requested and .completed without raw response data
- Static analysis: scans.py must not call run_public_scan directly
- Static analysis: owner_scans.py must not call run_public_scan directly
"""

import ast
import re
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import (
    DomainBlockedError,
    ScanNotAllowedError,
    SSRFBlockedError,
)
from app.core.safe_scan_runner import run_owner_trust_scan, run_public_trust_scan
from app.scanners.result import ScanData


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_db(*, domain_blocked: bool = False) -> AsyncMock:
    """Return a mock AsyncSession. Every DoNotScan query returns the same result."""
    db = AsyncMock()
    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = object() if domain_blocked else None
    db.execute = AsyncMock(return_value=scalar_result)
    db.add = MagicMock()
    db.flush = AsyncMock()
    return db


def _make_db_sequence(*blocked_sequence: bool) -> AsyncMock:
    """
    Return a mock AsyncSession where consecutive db.execute() calls return
    blocked/not-blocked results in the given sequence.
    Use this when the runner may call db.execute more than once (e.g. second
    Do Not Scan check on hostname mismatch).
    """
    db = AsyncMock()
    results = []
    for blocked in blocked_sequence:
        r = MagicMock()
        r.scalar_one_or_none.return_value = object() if blocked else None
        results.append(r)
    db.execute = AsyncMock(side_effect=results)
    db.add = MagicMock()
    db.flush = AsyncMock()
    return db


def _make_scan_data() -> ScanData:
    data = ScanData(domain="example.com")
    data.dns.resolves = True
    data.https.available = True
    data.ssl.valid = True
    return data


# ── Do Not Scan blocks before URL validation ──────────────────────────────────

async def test_do_not_scan_blocks_before_url_validation():
    """
    When domain is in Do Not Scan list, validate_url must never be called.
    Enforces: DNS check precedes any DNS resolution.
    """
    db = _make_db(domain_blocked=True)

    with (
        patch("app.core.safe_scan_runner.validate_url") as mock_validate,
        pytest.raises(DomainBlockedError),
    ):
        await run_public_trust_scan(
            raw_url="https://blocked.example.com",
            actor_ip="1.2.3.4",
            db=db,
        )

    mock_validate.assert_not_called()


async def test_do_not_scan_audit_log_written_on_block():
    """Blocked domain must produce an audit log entry with outcome=blocked."""
    db = _make_db(domain_blocked=True)
    logged: list[dict] = []

    async def capture_log(db, *, action, outcome, **kwargs):
        logged.append({"action": action, "outcome": outcome})

    with (
        patch("app.core.safe_scan_runner.log_event", side_effect=capture_log),
        patch("app.core.safe_scan_runner.validate_url"),
        pytest.raises(DomainBlockedError),
    ):
        await run_public_trust_scan(
            raw_url="https://blocked.example.com",
            actor_ip=None,
            db=db,
        )

    assert any(e["action"] == "scan.blocked_do_not_scan" for e in logged)
    assert all(e["outcome"] != "success" for e in logged)


# ── SSRF block prevents scanner ───────────────────────────────────────────────

async def test_ssrf_block_prevents_run_public_scan():
    """If validate_url raises SSRFBlockedError, run_public_scan must not run."""
    db = _make_db(domain_blocked=False)

    with (
        patch("app.core.safe_scan_runner.validate_url", side_effect=SSRFBlockedError()),
        patch("app.core.safe_scan_runner.run_public_scan") as mock_runner,
        pytest.raises(SSRFBlockedError),
    ):
        await run_public_trust_scan(
            raw_url="http://169.254.169.254/",
            actor_ip="1.2.3.4",
            db=db,
        )

    mock_runner.assert_not_called()


# ── Policy deny prevents scanner ──────────────────────────────────────────────

async def test_policy_deny_prevents_run_public_scan():
    """If check_scan_allowed raises, run_public_scan must not run."""
    db = _make_db(domain_blocked=False)

    with (
        patch("app.core.safe_scan_runner.validate_url", return_value="https://example.com"),
        patch("app.core.safe_scan_runner.check_scan_allowed", side_effect=ScanNotAllowedError()),
        patch("app.core.safe_scan_runner.run_public_scan") as mock_runner,
        pytest.raises(ScanNotAllowedError),
    ):
        await run_public_trust_scan(
            raw_url="https://example.com",
            actor_ip=None,
            db=db,
        )

    mock_runner.assert_not_called()


# ── Successful scan uses validated_hostname ───────────────────────────────────

async def test_successful_scan_uses_validated_hostname():
    """
    run_public_scan must receive the hostname extracted from validate_url's
    return value, not the raw user input.
    """
    db = _make_db(domain_blocked=False)
    scan_data = _make_scan_data()
    captured_domains: list[str] = []

    async def capture_domain(domain: str) -> ScanData:
        captured_domains.append(domain)
        return scan_data

    with (
        patch("app.core.safe_scan_runner.validate_url", return_value="https://example.com"),
        patch("app.core.safe_scan_runner.check_scan_allowed"),
        patch("app.core.safe_scan_runner.run_public_scan", side_effect=capture_domain),
        patch("app.core.safe_scan_runner.log_event", new_callable=AsyncMock),
    ):
        result = await run_public_trust_scan(
            raw_url="HTTPS://EXAMPLE.COM/path?q=1",
            actor_ip=None,
            db=db,
        )

    assert captured_domains == ["example.com"]
    assert result.domain == "example.com"


# ── Audit log: requested and completed, no raw response ───────────────────────

async def test_audit_log_requested_and_completed_written():
    """
    Audit log must record .requested (before scan) and .completed (after).
    Neither entry must contain raw response bodies or header values.
    """
    db = _make_db(domain_blocked=False)
    logged: list[dict] = []
    scan_data = _make_scan_data()

    async def capture_log(db, *, action, outcome, details=None, **kwargs):
        logged.append({"action": action, "outcome": outcome, "details": details})

    with (
        patch("app.core.safe_scan_runner.validate_url", return_value="https://example.com"),
        patch("app.core.safe_scan_runner.check_scan_allowed"),
        patch("app.core.safe_scan_runner.run_public_scan", return_value=scan_data),
        patch("app.core.safe_scan_runner.log_event", side_effect=capture_log),
    ):
        await run_public_trust_scan(
            raw_url="https://example.com",
            actor_ip="9.9.9.9",
            db=db,
        )

    actions = [e["action"] for e in logged]
    assert "scan.public_trust.requested" in actions
    assert "scan.public_trust.completed" in actions

    # No raw response data in any log entry
    forbidden_keys = {"raw_html", "headers", "body", "response"}
    for entry in logged:
        if entry["details"]:
            assert not forbidden_keys.intersection(entry["details"].keys()), (
                f"Audit log entry contains raw response data: {entry['details']}"
            )


async def test_audit_log_failed_written_on_scanner_error():
    """If run_public_scan raises, audit log must record .failed."""
    db = _make_db(domain_blocked=False)
    logged: list[dict] = []

    async def capture_log(db, *, action, outcome, **kwargs):
        logged.append({"action": action, "outcome": outcome})

    with (
        patch("app.core.safe_scan_runner.validate_url", return_value="https://example.com"),
        patch("app.core.safe_scan_runner.check_scan_allowed"),
        patch("app.core.safe_scan_runner.run_public_scan", side_effect=RuntimeError("network timeout")),
        patch("app.core.safe_scan_runner.log_event", side_effect=capture_log),
        pytest.raises(RuntimeError),
    ):
        await run_public_trust_scan(
            raw_url="https://example.com",
            actor_ip=None,
            db=db,
        )

    actions = [e["action"] for e in logged]
    assert "scan.public_trust.failed" in actions
    assert "scan.public_trust.completed" not in actions


# ── Second Do Not Scan check on hostname mismatch ────────────────────────────

async def test_second_do_not_scan_check_runs_on_hostname_mismatch():
    """
    If validate_url returns a URL with a different hostname than the raw input
    (e.g. IDN normalization), the runner must re-check Do Not Scan against the
    validated hostname and block before running any scanner.
    """
    # First db.execute (raw_domain "original.com") → not blocked
    # Second db.execute (validated_hostname "different.com") → blocked
    db = _make_db_sequence(False, True)

    with (
        patch("app.core.safe_scan_runner.validate_url", return_value="https://different.com"),
        patch("app.core.safe_scan_runner.run_public_scan") as mock_runner,
        patch("app.core.safe_scan_runner.log_event", new_callable=AsyncMock),
        pytest.raises(DomainBlockedError),
    ):
        await run_public_trust_scan(
            raw_url="https://original.com",
            actor_ip=None,
            db=db,
        )

    mock_runner.assert_not_called()


async def test_second_do_not_scan_check_skipped_when_hostname_unchanged():
    """
    When validated_hostname == raw_domain (the common case), db.execute is
    called exactly once — no redundant second Do Not Scan query.
    """
    db = _make_db(domain_blocked=False)
    scan_data = _make_scan_data()

    with (
        patch("app.core.safe_scan_runner.validate_url", return_value="https://example.com"),
        patch("app.core.safe_scan_runner.check_scan_allowed"),
        patch("app.core.safe_scan_runner.run_public_scan", return_value=scan_data),
        patch("app.core.safe_scan_runner.log_event", new_callable=AsyncMock),
    ):
        await run_public_trust_scan(
            raw_url="https://example.com",
            actor_ip=None,
            db=db,
        )

    db.execute.assert_called_once()


# ── Static analysis: scans.py must not call run_public_scan directly ──────────

def test_public_scan_handler_does_not_call_run_public_scan_directly():
    """
    After wiring public_scan() to safe_scan_runner, scans.py must not:
      - import run_public_scan from app.scanners.runner
      - import app.scanners.runner at all
      - call run_public_scan() directly

    Uses ast.parse for import checks and re for call-site checks.
    """
    handler_file = (
        Path(__file__).resolve().parent.parent.parent
        / "app" / "api" / "v1" / "scans.py"
    )
    text = handler_file.read_text()
    tree = ast.parse(text, filename=str(handler_file))

    violations: list[str] = []

    for node in ast.walk(tree):
        # Catch: from app.scanners.runner import run_public_scan (or any name)
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if "scanners.runner" in module or "scanners" == module.split(".")[-1]:
                imported = [a.name for a in node.names]
                if "run_public_scan" in imported:
                    violations.append(
                        f"line {node.lineno}: imports run_public_scan from {module}"
                    )
                elif "runner" in imported:
                    violations.append(
                        f"line {node.lineno}: imports scanner runner module from {module}"
                    )
        # Catch: import app.scanners.runner
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "scanners.runner" in alias.name:
                    violations.append(
                        f"line {node.lineno}: imports scanner runner: {alias.name}"
                    )
        # Catch: run_public_scan(...) or obj.run_public_scan(...)
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id == "run_public_scan":
                violations.append(f"line {fn.col_offset}: calls run_public_scan() directly")
            elif isinstance(fn, ast.Attribute) and fn.attr == "run_public_scan":
                violations.append("calls .run_public_scan() via attribute")

    # Belt-and-suspenders: raw string check for the module path
    if re.search(r"app\.scanners\.runner", text):
        violations.append("string 'app.scanners.runner' found in scans.py")

    assert not violations, (
        "scans.py must not reference run_public_scan or app.scanners.runner directly "
        f"— delegate to safe_scan_runner: {violations}"
    )


# ══════════════════════════════════════════════════════════════════════════════
# Owner Trust Scan tests
# ══════════════════════════════════════════════════════════════════════════════

_OWNER_KWARGS = dict(
    domain="example.com",
    actor_id="user-123",
    actor_role="owner",
    site_id="site-abc",
)


# ── Do Not Scan blocks before URL validation ──────────────────────────────────

async def test_owner_do_not_scan_blocks_before_url_validation():
    """DNS check must fire before validate_url (no DNS resolution on blocked domain)."""
    db = _make_db(domain_blocked=True)

    with (
        patch("app.core.safe_scan_runner.validate_url") as mock_validate,
        pytest.raises(DomainBlockedError),
    ):
        await run_owner_trust_scan(**_OWNER_KWARGS, db=db)

    mock_validate.assert_not_called()


async def test_owner_do_not_scan_audit_uses_owner_fields():
    """Blocked audit log must carry actor_id, actor_role, resource_type=site."""
    db = _make_db(domain_blocked=True)
    logged: list[dict] = []

    async def capture_log(db, *, action, outcome, actor_id=None, actor_role=None,
                          resource_type=None, resource_id=None, details=None, **kwargs):
        logged.append({
            "action": action,
            "outcome": outcome,
            "actor_id": actor_id,
            "actor_role": actor_role,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details,
        })

    with (
        patch("app.core.safe_scan_runner.log_event", side_effect=capture_log),
        patch("app.core.safe_scan_runner.validate_url"),
        pytest.raises(DomainBlockedError),
    ):
        await run_owner_trust_scan(**_OWNER_KWARGS, db=db)

    assert len(logged) == 1
    entry = logged[0]
    assert entry["action"] == "scan.owner.blocked_do_not_scan"
    assert entry["outcome"] == "blocked"
    assert entry["actor_id"] == "user-123"
    assert entry["actor_role"] == "owner"
    assert entry["resource_type"] == "site"
    assert entry["resource_id"] == "site-abc"
    # details must not expose the raw domain value
    assert entry.get("details", {}).get("reason") == "do_not_scan"


# ── SSRF block prevents scanner ───────────────────────────────────────────────

async def test_owner_ssrf_block_prevents_run_public_scan():
    """If validate_url raises SSRFBlockedError, run_public_scan must not run."""
    db = _make_db(domain_blocked=False)

    with (
        patch("app.core.safe_scan_runner.validate_url", side_effect=SSRFBlockedError()),
        patch("app.core.safe_scan_runner.run_public_scan") as mock_runner,
        pytest.raises(SSRFBlockedError),
    ):
        await run_owner_trust_scan(**_OWNER_KWARGS, db=db)

    mock_runner.assert_not_called()


# ── Policy deny prevents scanner ──────────────────────────────────────────────

async def test_owner_policy_deny_prevents_run_public_scan():
    """If check_scan_allowed raises, run_public_scan must not run."""
    db = _make_db(domain_blocked=False)

    with (
        patch("app.core.safe_scan_runner.validate_url", return_value="https://example.com"),
        patch("app.core.safe_scan_runner.check_scan_allowed", side_effect=ScanNotAllowedError()),
        patch("app.core.safe_scan_runner.run_public_scan") as mock_runner,
        pytest.raises(ScanNotAllowedError),
    ):
        await run_owner_trust_scan(**_OWNER_KWARGS, db=db)

    mock_runner.assert_not_called()


# ── Scanner uses validated_hostname, report uses site.domain ─────────────────

async def test_owner_scan_uses_validated_hostname_for_scanner():
    """run_public_scan must receive the hostname from validate_url, not site.domain."""
    db = _make_db(domain_blocked=False)
    scan_data = _make_scan_data()
    captured: list[str] = []

    async def capture_domain(domain: str) -> ScanData:
        captured.append(domain)
        return scan_data

    with (
        patch("app.core.safe_scan_runner.validate_url", return_value="https://resolved.example.com"),
        patch("app.core.safe_scan_runner.check_scan_allowed"),
        patch("app.core.safe_scan_runner.run_public_scan", side_effect=capture_domain),
        patch("app.core.safe_scan_runner.log_event", new_callable=AsyncMock),
    ):
        await run_owner_trust_scan(
            domain="example.com",
            actor_id="user-123",
            actor_role="owner",
            site_id="site-abc",
            db=db,
        )

    assert captured == ["resolved.example.com"]


async def test_owner_report_uses_site_domain_not_validated_hostname():
    """
    compute_trust_report must receive site.domain (the registered domain),
    not validated_hostname, so the displayed domain matches the owner's record.
    """
    db = _make_db(domain_blocked=False)
    scan_data = _make_scan_data()
    captured_report_domains: list[str] = []

    def capture_report(domain: str, scan_data) -> dict:
        captured_report_domains.append(domain)
        return {
            "domain": domain,
            "trust_score": 80,
            "trust_level": "good",
            "checks": {},
            "recommendations": [],
        }

    with (
        patch("app.core.safe_scan_runner.validate_url", return_value="https://resolved.example.com"),
        patch("app.core.safe_scan_runner.check_scan_allowed"),
        patch("app.core.safe_scan_runner.run_public_scan", return_value=scan_data),
        patch("app.core.safe_scan_runner.compute_trust_report", side_effect=capture_report),
        patch("app.core.safe_scan_runner.log_event", new_callable=AsyncMock),
    ):
        report = await run_owner_trust_scan(
            domain="example.com",
            actor_id="user-123",
            actor_role="owner",
            site_id="site-abc",
            db=db,
        )

    assert captured_report_domains == ["example.com"]
    assert report["domain"] == "example.com"


# ── Failed audit on scanner error ─────────────────────────────────────────────

async def test_owner_failed_audit_written_on_scanner_error():
    """If run_public_scan raises, audit must record scan.owner.failed."""
    db = _make_db(domain_blocked=False)
    logged: list[dict] = []

    async def capture_log(db, *, action, outcome, **kwargs):
        logged.append({"action": action, "outcome": outcome})

    with (
        patch("app.core.safe_scan_runner.validate_url", return_value="https://example.com"),
        patch("app.core.safe_scan_runner.check_scan_allowed"),
        patch("app.core.safe_scan_runner.run_public_scan", side_effect=RuntimeError("timeout")),
        patch("app.core.safe_scan_runner.log_event", side_effect=capture_log),
        pytest.raises(RuntimeError),
    ):
        await run_owner_trust_scan(**_OWNER_KWARGS, db=db)

    assert any(e["action"] == "scan.owner.failed" for e in logged)


# ── Static analysis: owner_scans.py must not call run_public_scan directly ───

def test_owner_scan_handler_does_not_call_run_public_scan_directly():
    """
    owner_scans.py must not import run_public_scan from app.scanners.runner
    or call it directly — all scan logic must go through run_owner_trust_scan.
    """
    handler_file = (
        Path(__file__).resolve().parent.parent.parent
        / "app" / "api" / "v1" / "owner_scans.py"
    )
    text = handler_file.read_text()
    tree = ast.parse(text, filename=str(handler_file))

    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if "scanners.runner" in module:
                imported = [a.name for a in node.names]
                if "run_public_scan" in imported:
                    violations.append(
                        f"line {node.lineno}: imports run_public_scan from {module}"
                    )
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "scanners.runner" in alias.name:
                    violations.append(
                        f"line {node.lineno}: imports scanner runner: {alias.name}"
                    )
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name) and fn.id == "run_public_scan":
                violations.append(f"line {fn.col_offset}: calls run_public_scan() directly")
            elif isinstance(fn, ast.Attribute) and fn.attr == "run_public_scan":
                violations.append("calls .run_public_scan() via attribute")

    if re.search(r"app\.scanners\.runner", text):
        violations.append("string 'app.scanners.runner' found in owner_scans.py")

    assert not violations, (
        "owner_scans.py must not reference run_public_scan directly "
        f"— delegate to run_owner_trust_scan: {violations}"
    )
