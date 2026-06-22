# Security Review Checklist

This document covers the 10 security domains verified during the Phase 12 security audit.
It serves as the reference for future security reviews and PR approvals.

---

## 1. SSRF Prevention

| Check | File | Status |
|-------|------|--------|
| Every outbound HTTP request goes through `validate_url()` | `app/core/url_validator.py` | ✅ |
| 18+ blocked IP ranges: loopback, private, link-local, cloud metadata (169.254.169.254), CGN, documentation, multicast, unspecified | `url_validator.py:_BLOCKED_NETWORKS` | ✅ |
| DNS resolution checked after hostname lookup to prevent DNS rebinding | `url_validator.py:_resolve_hostname()` | ✅ |
| Redirect targets re-validated via `validate_redirect_url()` | `url_validator.py:validate_redirect_url()` | ✅ |
| `allow_http=False` by default; only the public scan endpoint passes `allow_http=True` | `app/api/v1/scans.py` | ✅ |
| Scheduled worker validates stored domains before scanning | `app/tasks/scheduled_scans.py:_rescan_site()` | ✅ |
| Owner scan endpoint validates stored domains before scanning | `app/api/v1/owner_scans.py:run_owner_scan()` | ✅ |

---

## 2. Scan Policy Engine

| Check | File | Status |
|-------|------|--------|
| Single enforcement point: `check_scan_allowed()` called before any scan | `app/core/scan_policy.py` | ✅ |
| Priority order: Do Not Scan → permanently forbidden types → public types → Authorization Required | `scan_policy.py:check_scan_allowed()` | ✅ |
| Only `PUBLIC_TRUST` is open without authentication | `scan_policy.py:_PUBLIC_SCAN_TYPES` | ✅ |
| Permanently forbidden types are documented and blocked regardless of role | `scan_policy.py:_PERMANENTLY_FORBIDDEN` | ✅ |
| All scan endpoints call `check_scan_allowed()`: public API, owner API, scheduled worker | `scans.py`, `owner_scans.py`, `scheduled_scans.py` | ✅ |

---

## 3. Do Not Scan (DNS Block List)

| Check | File | Status |
|-------|------|--------|
| Do Not Scan is the highest-priority check — no role or record can override it | `scan_policy.py` lines 71–75 | ✅ |
| Public scan endpoint checks the `do_not_scan` table before any scan | `app/api/v1/scans.py` | ✅ |
| Owner scan endpoint checks the `do_not_scan` table before any scan | `app/api/v1/owner_scans.py` | ✅ |
| Scheduled worker checks the `do_not_scan` table for each site before scanning | `app/tasks/scheduled_scans.py` | ✅ |
| Blocked scan attempts are audit-logged with `outcome="blocked"` | `scans.py`, `owner_scans.py`, `scheduled_scans.py` | ✅ |
| Case-insensitive unique index on `lower(domain)` prevents bypass via case variation | `alembic/versions/001_security_foundation.py` | ✅ |

---

## 4. Authorization Record

| Check | File | Status |
|-------|------|--------|
| All non-public scan types (`SECURITY_HEADERS`, `SSL_AUDIT`, `CONTENT_SCAN`, `FULL_SECURITY`) require an Authorization Record | `scan_policy.py` lines 87–94 | ✅ |
| Admin role alone is NOT sufficient for deep scans — Authorization Record is required | `scan_policy.py:check_scan_allowed()` | ✅ |
| Authorization check is in the policy engine, not in the role check | `scan_policy.py` (separate from `admin/auth.py`) | ✅ |
| Scheduled worker runs `PUBLIC_TRUST` only — no deep scans without authorization | `scheduled_scans.py:_rescan_site()` | ✅ |

---

## 5. Authentication & JWT Cookies

| Check | File | Status |
|-------|------|--------|
| Access tokens stored in httpOnly cookies (not accessible to JavaScript) | `app/api/v1/auth.py:_set_auth_cookies()` | ✅ |
| Refresh tokens stored in httpOnly cookies with path restriction (`/api/v1/auth/refresh`) | `auth.py:_set_auth_cookies()` | ✅ |
| `secure=True` in production; `secure=False` in development only | `auth.py` — conditional on `settings.app_env` | ✅ |
| `samesite="lax"` on all auth cookies | `auth.py:_set_auth_cookies()` | ✅ |
| Access token lifetime: 15 minutes | `app/core/config.py:access_token_expire_minutes` | ✅ |
| Refresh token lifetime: 7 days | `config.py:refresh_token_expire_days` | ✅ |
| Only SHA-256 hash of refresh token stored in DB (raw token never persisted) | `app/core/security.py:hash_refresh_token()` | ✅ |
| Refresh tokens rotated on every use (old token revoked, new token issued) | `auth.py:refresh()` | ✅ |
| Account locked after 5 failed login attempts for 15 minutes | `auth.py:login()`, `config.py` | ✅ |
| Passwords hashed with bcrypt (passlib, pinned to bcrypt==4.2.1) | `security.py:hash_password()` | ✅ |

---

## 6. CSRF Protection

| Check | File | Status |
|-------|------|--------|
| SameSite=Lax on all auth cookies provides primary CSRF defence | `auth.py:_set_auth_cookies()` | ✅ |
| Server-side Origin header check in production for non-GET/HEAD/OPTIONS requests | `app/main.py:csrf_origin_check()` | ✅ |
| Bearer (Authorization header) requests excluded from CSRF check (CSRF-immune by design) | `main.py:csrf_origin_check()` lines 77–78 | ✅ |
| CSRF check is production-only; development mode skips it to avoid blocking local tools | `main.py` — conditional on `settings.app_env` | ✅ |
| Allowed origins controlled by `settings.allowed_origins` (env var, no hardcoding) | `app/core/config.py` | ✅ |

---

## 7. Audit Logging

| Check | File | Status |
|-------|------|--------|
| `actor_ip` stored in `audit_logs` table for forensics | `app/models/audit_log.py` | ✅ |
| `actor_ip` is NEVER returned in any API response | `app/api/v1/admin/analytics.py:get_audit_log()` — field explicitly omitted | ✅ |
| 20 sensitive key categories stripped from `details` before persistence | `app/services/audit_logger.py:_SENSITIVE_KEYS` | ✅ |
| Sensitive keys are replaced with `"[REDACTED]"` sentinel (presence is logged, value is not) | `audit_logger.py:_sanitize_details()` | ✅ |
| `log_event()` never raises — audit failure does not break business logic | `audit_logger.py:log_event()` lines 91–109 | ✅ |
| All auth events logged: register, login, lockout, logout | `auth.py` | ✅ |
| All scan events logged: blocked, completed | `scans.py`, `owner_scans.py`, `scheduled_scans.py` | ✅ |
| All site events logged: add, verify, verify_failed | `sites.py` | ✅ |

---

## 8. Scheduled Scan Worker Security

| Check | File | Status |
|-------|------|--------|
| Worker passes every domain through `validate_url()` before scanning | `scheduled_scans.py:_rescan_site()` | ✅ |
| Worker checks `do_not_scan` table for each site before scanning | `scheduled_scans.py:_rescan_site()` | ✅ |
| Worker calls `check_scan_allowed()` with the correct scan type | `scheduled_scans.py:_rescan_site()` | ✅ |
| Blocked scans are audit-logged with `outcome="blocked"` | `scheduled_scans.py:_rescan_site()` | ✅ |
| Worker only runs `PUBLIC_TRUST` scans (no deep scans, no override) | `scheduled_scans.py` — `ScanType.PUBLIC_TRUST` hardcoded | ✅ |
| Individual scan failure does not stop the entire batch | `scheduled_scans.py:_async_rescan_all()` — `try/except` per site | ✅ |

---

## 9. PDF Report Security

| Check | File | Status |
|-------|------|--------|
| PDF does not include raw HTTP response bodies | `app/services/pdf_report.py` — only `trust_score`, `trust_level`, `checks`, `recommendations` extracted | ✅ |
| PDF does not include raw IP addresses | `pdf_report.py` — no IP fields from scan data | ✅ |
| PDF does not include raw header values (only pass/fail booleans) | `pdf_report.py` — `check_labels_*` maps key → human label, no raw values | ✅ |
| PDF does not include certificate details | `pdf_report.py` — `ssl_valid` and `ssl_expiry_ok` are booleans only | ✅ |
| Arabic text rendered correctly (RTL, ligatures) via arabic-reshaper + python-bidi | `pdf_report.py:_ar()` | ✅ |
| Arabic section appears before English section | `pdf_report.py:generate_pdf_report()` — Arabic block first, `HRFlowable` divider, English block | ✅ |
| PDF access requires ownership of the site (authenticated, verified owner) | `owner_scans.py:_get_active_site()` | ✅ |

---

## 10. Data Exposure (Public Trust Check)

| Check | File | Status |
|-------|------|--------|
| Public trust check returns only: `trust_score`, `trust_level`, `checks` (booleans), `recommendations` | `app/schemas/scan.py:TrustReport` | ✅ |
| No raw IPs, header values, certificate serial numbers, or hostname details in public response | `app/scanners/trust_score.py:compute_trust_report()` | ✅ |
| Public endpoint is rate-limited to prevent enumeration | `scans.py` — `@limiter.limit(GUEST_SCAN_LIMIT)` = 10/hour | ✅ |
| No authentication required for public check (by design) | `scans.py` — no `Depends(get_current_user)` | ✅ |
| Scan data passes through policy engine even for anonymous requests | `scans.py` — `check_scan_allowed()` called before `run_public_scan()` | ✅ |
| Admin analytics endpoint excludes `actor_ip` from all audit log responses | `admin/analytics.py:get_audit_log()` | ✅ |
| Admin endpoints require admin/super_admin role OR valid `X-Admin-Key` (constant-time compare) | `admin/auth.py:require_admin()` | ✅ |

---

## Audit Summary

**Critical security fixes applied in this audit:**

1. `app/tasks/scheduled_scans.py` — `_rescan_site()` now enforces URL validation, Do Not Scan check, and `check_scan_allowed()` before any outbound request. Previously called `run_public_scan()` directly.

2. `app/api/v1/owner_scans.py` — `run_owner_scan()` now enforces URL validation, Do Not Scan check, and `check_scan_allowed()` before any outbound request. Previously called `run_public_scan()` directly.

**Lint cleanup:** 17 pre-existing ruff warnings resolved (unused imports, unused variables).

**CI expanded:** Added `backend-lint` (ruff) and `backend-migrations` (import check) jobs to `.github/workflows/ci.yml`.

**No functional changes** to scanning logic, trust scoring, authentication, PDF generation, or any user-facing feature.
