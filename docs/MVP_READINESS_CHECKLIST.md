# MVP Readiness Checklist

**Date:** 2026-06-24
**Scope:** Owner MVP — initial verified flow for site owners
**Status:** ✅ Verified — ready for supervised beta testing

---

## Current Status

Owner MVP has been manually verified end-to-end. The backend starts cleanly from `requirements.txt` (including `email-validator`), the frontend builds and serves all Owner flow pages, and the full authenticated flow from sites list → scans list → scan detail → FixPlan works in both Arabic and English locales.

No raw technical data (headers, IPs, response bodies, secrets) is exposed at any point in the flow.

---

## What Works Now

| Area | Status |
|---|---|
| Backend startup (no manual installs) | ✅ |
| Frontend build + production start | ✅ |
| Database migrations (`alembic upgrade head`) | ✅ |
| Arabic locale (`/ar/*`) | ✅ |
| English locale (`/en/*`) | ✅ |
| Auth redirect (unauthenticated → login) | ✅ |
| User registration with `EmailStr` validation | ✅ |
| Cookie-based JWT authentication | ✅ |
| Sites list (`GET /api/v1/sites`) | ✅ |
| Scans list (`GET /api/v1/sites/{id}/scans`) | ✅ |
| Scan detail (`GET /api/v1/sites/{id}/scans/{scanId}`) | ✅ |
| FixPlan component (7 narrow check fields only) | ✅ |
| CopyButton for developer instructions | ✅ |

---

## Owner MVP Verified Flow

The following checks were confirmed passing in the final manual E2E test (after PR #32 + PR #33):

- [x] Backend starts cleanly from `requirements.txt` — no manual package installs required
- [x] Frontend builds without TypeScript errors
- [x] Frontend starts and serves all routes
- [x] `alembic upgrade head` completes without errors on a clean database
- [x] `/ar/sites` returns 200 for authenticated users
- [x] `/en/sites` returns 200 for authenticated users
- [x] `/ar/sites` redirects (307) to `/ar/login` for unauthenticated users
- [x] `/en/sites` redirects (307) to `/en/login` for unauthenticated users
- [x] Auth redirect middleware works correctly
- [x] Sites list endpoint returns correct data shape
- [x] Scans list endpoint returns `trust_score` and `scanned_at`
- [x] Scan detail endpoint returns `trust_score` + `result_json.checks` (7 fields only)
- [x] FixPlan component renders and receives narrow props only
- [x] No raw HTTP headers exposed in any response or UI
- [x] No IP addresses exposed in any response or UI
- [x] No raw response bodies exposed in any response or UI
- [x] No secrets or sensitive values exposed in any response or UI

---

## Security Boundaries (Non-Negotiable)

These constraints apply to every scan, check, and API call in the system:

- No port scanning
- No crawling or spider-style enumeration
- No exposed files scan (`.env`, `wp-admin`, `/.git`, etc.)
- No intrusive testing of any kind
- No exploitation or vulnerability probing
- Raw HTTP response bodies must never be stored or exposed
- IP addresses must never be exposed in UI or API responses
- Sensitive header values must never be exposed (only presence/absence)
- Raw response bodies must never be exposed
- Secrets must never be logged, stored in results, or returned via API
- Any outbound scan must pass through, in order:
  1. **Do Not Scan** check — before any DNS resolution or network call
  2. **SSRF protection** — block private/loopback/link-local ranges
  3. **URL validation** — normalize and sanitize the target
  4. **Scan Policy** — enforce scope and allowed check types
  5. **Safe HTTP Client** — enforce timeouts, size limits, redirect limits
  6. **Safe Scan Runner** — orchestrate and enforce all of the above
- Do Not Scan **must** be checked before any DNS resolution or network call

---

## What Is Intentionally Not Included

These features are deferred and must not be started without explicit approval:

| Feature | Reason Deferred |
|---|---|
| Dashboard | Post-MVP scope |
| PDF export | Post-MVP scope |
| Data export | Post-MVP scope |
| Per-domain rate limiting | Post-MVP scope |
| Callback URL after login redirect | Post-MVP scope |
| Owner Scan migration to Safe Scan Runner | Next milestone |
| Before/After comparison view | Next milestone |
| Periodic scan reports | Next milestone |
| Admin lead outreach automation | Post-MVP scope |
| Admin deep scan (post-authorization) | Post-MVP scope |

---

## Known Non-Blocking Warnings

These warnings exist in the current codebase and are known to be non-breaking:

| Warning | Source | Impact |
|---|---|---|
| `middleware` file convention deprecated, use `proxy` | Next.js 16 | None — rename is safe but non-urgent |
| `passlib.handlers.bcrypt: error reading bcrypt version` | `passlib` + `bcrypt 4.x` version mismatch | None — authentication works correctly |
| `pytest-asyncio` deprecation warnings | Test suite | None — tests pass, update is non-urgent |
| Next.js CVE GHSA-36qx-fr4f-26g5 (i18n middleware bypass) | Next.js < 15.2.3 advisory | Low — mitigation required before public launch |

---

## Pre-Launch Blockers (Not Yet Addressed)

These items must be resolved before any public or production launch:

- [ ] CVE GHSA-36qx-fr4f-26g5: upgrade Next.js or apply mitigation
- [ ] Production environment hardening (secrets management, HTTPS termination, rate limits)
- [ ] Rate limiting per domain (not just per user — TODO noted in safe_scan_runner.py)
- [ ] Full penetration test or security review before public access

---

## Completed Since This Checklist Was Written

- [x] Owner Scan migrated to Safe Scan Runner — PR #20 (`run_owner_trust_scan` in `safe_scan_runner.py`)
- [x] Admin Lead Audit migrated to Safe Scan Runner — PR #35
- [x] Admin read-only MVP closed — PRs #37, #38, #39, #40
- [x] Owner locale navigation links fixed (next/link → @/i18n/navigation) — PR #41
- [x] Admin analytics dashboard added (summary stats, risk distribution, scan trends, audit log) — PR #43
- [x] Owner scan detail: disclaimer + back navigation added
- [x] Admin lead detail: surface-level disclaimer added
- [x] Final MVP Closure Report written (`docs/FINAL_MVP_CLOSURE_REPORT.md`)
- [x] All three user paths (Visitor, Owner, Admin) confirmed complete and tested via Playwright
