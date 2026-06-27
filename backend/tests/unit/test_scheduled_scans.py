"""
Tests for app/tasks/scheduled_scans.py.

Coverage:
- Static: scheduled_scans.py must not import or call run_public_scan directly
- _rescan_site delegates to run_owner_trust_scan with correct kwargs
- ScanResult is persisted (db.add + db.flush)
- Score drop >= 10 triggers notify_score_drop
- Score recovery >= 10 triggers notify_score_recovered
- DomainBlockedError from run_owner_trust_scan propagates out
- No previous score skips score comparison entirely
"""

import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import DomainBlockedError
from app.tasks.scheduled_scans import _rescan_site

_SOURCE = (
    Path(__file__).parent.parent.parent
    / "app" / "tasks" / "scheduled_scans.py"
).read_text()


# ── Static analysis ────────────────────────────────────────────────────────────

def test_no_direct_run_public_scan_import():
    assert "from app.scanners.runner import run_public_scan" not in _SOURCE


def test_no_direct_run_public_scan_call():
    assert "run_public_scan(" not in _SOURCE


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_site(domain: str = "example.com", score: float | None = None) -> MagicMock:
    site = MagicMock()
    site.id = uuid.uuid4()
    site.domain = domain
    site.owner_id = uuid.uuid4()
    return site


def _make_db(prev_score: float | None = None) -> AsyncMock:
    """Return a mock AsyncSession with an optional previous ScanResult."""
    db = AsyncMock()
    prev_record = None
    if prev_score is not None:
        prev_record = MagicMock()
        prev_record.trust_score = prev_score
    scalar_result = MagicMock()
    scalar_result.scalar_one_or_none.return_value = prev_record
    db.execute = AsyncMock(return_value=scalar_result)
    db.add = MagicMock()
    db.flush = AsyncMock()
    return db


# ── Functional tests ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rescan_site_calls_run_owner_trust_scan():
    site = _make_site("example.com")
    db = _make_db(prev_score=None)
    fake_report = {"trust_score": 75, "trust_level": "good", "checks": {}}

    with (
        patch(
            "app.tasks.scheduled_scans.run_owner_trust_scan",
            new_callable=AsyncMock,
            return_value=fake_report,
        ) as mock_runner,
        patch("app.tasks.scheduled_scans.notify_scan_complete", new_callable=AsyncMock),
    ):
        await _rescan_site(db, site)

    mock_runner.assert_awaited_once_with(
        domain=site.domain,
        actor_id="scheduler",
        actor_role="system",
        site_id=str(site.id),
        db=db,
    )


@pytest.mark.asyncio
async def test_rescan_site_persists_scan_result():
    site = _make_site("example.com")
    db = _make_db(prev_score=None)
    fake_report = {"trust_score": 70, "trust_level": "good", "checks": {}}

    with (
        patch(
            "app.tasks.scheduled_scans.run_owner_trust_scan",
            new_callable=AsyncMock,
            return_value=fake_report,
        ),
        patch("app.tasks.scheduled_scans.notify_scan_complete", new_callable=AsyncMock),
    ):
        await _rescan_site(db, site)

    db.add.assert_called_once()
    added = db.add.call_args[0][0]
    assert added.trust_score == 70
    assert added.domain == site.domain
    assert added.site_id == site.id
    db.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_rescan_site_score_drop_sends_notification():
    site = _make_site("example.com")
    db = _make_db(prev_score=80)
    fake_report = {"trust_score": 60, "trust_level": "medium", "checks": {}}

    with (
        patch(
            "app.tasks.scheduled_scans.run_owner_trust_scan",
            new_callable=AsyncMock,
            return_value=fake_report,
        ),
        patch("app.tasks.scheduled_scans.notify_scan_complete", new_callable=AsyncMock),
        patch(
            "app.tasks.scheduled_scans.notify_score_drop",
            new_callable=AsyncMock,
        ) as mock_drop,
        patch("app.tasks.scheduled_scans.notify_score_recovered", new_callable=AsyncMock) as mock_recover,
    ):
        await _rescan_site(db, site)

    mock_drop.assert_awaited_once_with(
        db,
        user_id=site.owner_id,
        site_id=site.id,
        domain=site.domain,
        previous_score=80,
        current_score=60,
    )
    mock_recover.assert_not_awaited()


@pytest.mark.asyncio
async def test_rescan_site_score_recovery_sends_notification():
    site = _make_site("example.com")
    db = _make_db(prev_score=55)
    fake_report = {"trust_score": 75, "trust_level": "good", "checks": {}}

    with (
        patch(
            "app.tasks.scheduled_scans.run_owner_trust_scan",
            new_callable=AsyncMock,
            return_value=fake_report,
        ),
        patch("app.tasks.scheduled_scans.notify_scan_complete", new_callable=AsyncMock),
        patch("app.tasks.scheduled_scans.notify_score_drop", new_callable=AsyncMock) as mock_drop,
        patch(
            "app.tasks.scheduled_scans.notify_score_recovered",
            new_callable=AsyncMock,
        ) as mock_recover,
    ):
        await _rescan_site(db, site)

    mock_recover.assert_awaited_once_with(
        db,
        user_id=site.owner_id,
        site_id=site.id,
        domain=site.domain,
        previous_score=55,
        current_score=75,
    )
    mock_drop.assert_not_awaited()


@pytest.mark.asyncio
async def test_rescan_site_domain_blocked_propagates():
    site = _make_site("blocked.com")
    db = _make_db(prev_score=None)

    with (
        patch(
            "app.tasks.scheduled_scans.run_owner_trust_scan",
            new_callable=AsyncMock,
            side_effect=DomainBlockedError(),
        ),
    ):
        with pytest.raises(DomainBlockedError):
            await _rescan_site(db, site)

    db.add.assert_not_called()
    db.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_rescan_site_no_previous_score_skips_comparison():
    site = _make_site("example.com")
    db = _make_db(prev_score=None)
    fake_report = {"trust_score": 70, "trust_level": "good", "checks": {}}

    with (
        patch(
            "app.tasks.scheduled_scans.run_owner_trust_scan",
            new_callable=AsyncMock,
            return_value=fake_report,
        ),
        patch("app.tasks.scheduled_scans.notify_scan_complete", new_callable=AsyncMock),
        patch("app.tasks.scheduled_scans.notify_score_drop", new_callable=AsyncMock) as mock_drop,
        patch("app.tasks.scheduled_scans.notify_score_recovered", new_callable=AsyncMock) as mock_recover,
    ):
        await _rescan_site(db, site)

    mock_drop.assert_not_awaited()
    mock_recover.assert_not_awaited()
