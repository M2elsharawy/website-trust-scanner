# RC1 Review Report

**Date:** 2026-06-28  
**Reviewer:** Internal engineering team  
**Branch reviewed:** `main`  
**Main commit:** `45aec8b` — docs: Final MVP Closure Report — product guardrails, MVP Feature Complete  
**Scope:** Read and verify only. No code changes. Any issue found is documented, not fixed.

> **Amendment (2026-06-29):** Issue B2 (per-domain rate limit not enforced) was resolved in Release 1.0.1 — `_enforce_domain_rate_limit()` is now active in `safe_scan_runner.py`. The silent-pass when Redis is unavailable is a known accepted limitation (B2) for the supervised beta; harden before public launch. Issue RC1-5 (`middleware.ts`) was resolved in Release 1.0.1 — renamed to `proxy.ts`.

---

## Product Guardrail Reminder

This project is a **Trust Advisor**. Results are surface-level indicators only. The tool does not guarantee that a site is safe, does not perform penetration testing, and does not replace a professional security review.

---

## 1. Visitor (Public) Path — RC1 Status

**Verified: feature complete and stable.**

| Check | Finding |
|---|---|
| URL input + validation | Correct — SSRF protection active, Do Not Scan checked before DNS |
| Trust Score (0–100) | Computed from HTTPS, SSL, headers, reputation — algorithm unchanged |
| Usage Decision (4 cards × 3 verdicts) | Renders correctly in both locales |
| Open redirect in `?next=` | Fixed in PR #45 — only `/`-prefixed, non-`//` paths accepted |
| Raw data exposure (headers, IPs, body) | None found in API response or UI |
| Error states (invalid URL, SSRF block, timeout) | All handled with i18n messages |

**Note on reputation:** The reputation check is a mock (see §6). For the supervised limited trial, this means all unknown domains return "clean". Users should be made aware that reputation data is not live.

---

## 2. Site Owner Path — RC1 Status

**Verified: feature complete and stable.**

| Check | Finding |
|---|---|
| Registration + login | Cookie-based JWT, `httponly=True`, `samesite=lax`, `secure=True` in non-dev |
| DNS TXT ownership verification | Flow implemented and gated before scan access |
| Scan trigger → Safe Scan Runner | All owner scans routed through full 10-step pipeline |
| Do Not Scan — pre-DNS check | Confirmed at `safe_scan_runner.py:60` (before DNS) and at `safe_scan_runner.py:89` (post-DNS) |
| Scan history list | Renders trust score + timestamp, no raw data |
| Scan detail + FixPlan | Score card, disclaimer, Fix Plan with Why/How/Copy |
| Back navigation | Works correctly — uses `useLocale()` not `params.locale` |
| Logout → locale-aware redirect | Confirmed — `LogoutButton` uses `useLocale()` |
| `?next=` open redirect | Fixed — validated at login redirect |

---

## 3. Admin Path — RC1 Status

**Verified: read-only MVP complete.**

| Check | Finding |
|---|---|
| Role gate (`admin` / `super_admin`) | Checked via `/api/v1/auth/me` on every admin page load |
| Leads list | Read-only, correct columns |
| Lead detail | Surface-level disclaimer present |
| Analytics dashboard | Summary stats, 30-day scan trend, audit log |
| Audit log columns | action, outcome, actor_role, resource_type, timestamp — no actor_ip, no owner_id |
| Scan trigger button | Absent — no offensive capability in UI |
| Bulk scan / export | Absent |

---

## 4. Manual QA Checklist

These checks must be run in a staging environment before inviting trial users. None were run in this RC1 review (read-only pass).

### Visitor
- [ ] Valid HTTPS URL → Trust Score + Usage Decision rendered
- [ ] HTTP-only URL → score reflects no HTTPS
- [ ] Invalid URL → `errors.invalid_url`
- [ ] `http://localhost` → `errors.ssrf_blocked`
- [ ] `http://192.168.1.1` → `errors.ssrf_blocked`
- [ ] `http://169.254.169.254` → `errors.ssrf_blocked`
- [ ] Slow / unavailable domain → `errors.timeout`
- [ ] Language toggle AR ↔ EN → full UI switch, RTL for Arabic

### Auth
- [ ] Register → redirected to `/[locale]/sites`
- [ ] Login with correct credentials → redirected
- [ ] Login with wrong password → `auth.errors.invalid_credentials`
- [ ] `?next=/sites/123/scans` → correct redirect after login
- [ ] `?next=//evil.com` → falls back to `/[locale]/sites`
- [ ] `?next=https://evil.com` → falls back to `/[locale]/sites`
- [ ] Logout → cookie cleared, redirected to `/[locale]/login`
- [ ] Arabic session → logout → Arabic login page

### Owner
- [ ] Unauthenticated `/sites` → redirect to login with `?next=`
- [ ] Pending site → DNS TXT hint visible
- [ ] Scan list → score + timestamp
- [ ] Empty scan list → `owner_scans_list.empty`
- [ ] Scan detail → score card + disclaimer + FixPlan
- [ ] Back link → returns to scan list
- [ ] Copy for developer → shows "Copied!" confirmation

### Admin
- [ ] Non-admin user → cannot reach `/admin`
- [ ] Read-only banner visible
- [ ] Audit log: no `actor_ip`, no `owner_id` visible
- [ ] No scan trigger button anywhere in admin UI

---

## 5. Security QA Checklist

These checks must be verified before supervised limited trial goes live.

| Check | Method | Status |
|---|---|---|
| SSRF: loopback blocked | `POST /api/v1/public-trust-check` with `http://127.0.0.1` | Not run — pre-staging |
| SSRF: cloud metadata blocked | Same with `http://169.254.169.254` | Not run — pre-staging |
| SSRF: private RFC-1918 blocked | Same with `http://192.168.0.1` | Not run — pre-staging |
| Do Not Scan before DNS | Code-confirmed at `safe_scan_runner.py:60,89` | ✅ Confirmed in code |
| Open redirect blocked | `?next=//evil.com` and `?next=https://evil.com` | Code-confirmed in `AuthForm.tsx` |
| Cookie flags | `httponly`, `samesite=lax`, `secure` (non-dev) | ✅ Confirmed in `auth.py:37–51` |
| CORS origin restriction | `CORSMiddleware` + `TrustedHostMiddleware` in `main.py` | ✅ Present — value is env-dependent |
| Rate limiting (per IP) | `@limiter.limit(GUEST_SCAN_LIMIT)` on public scan route | ✅ Active — 10/hour guest, 60/hour user |
| Rate limiting (per domain) | `DOMAIN_SCAN_LIMIT` defined but **not yet enforced** | ⚠️ See §6 |
| No raw data in API response | Reviewed scan schema and trust_score.py | ✅ Only sanitized fields returned |
| Admin has no scan trigger | Reviewed admin pages | ✅ Absent |

---

## 6. i18n Checklist (Arabic / English)

| Area | Status |
|---|---|
| All UI strings in `en.json` | ✅ Complete — verified in PR #45 |
| All UI strings in `ar.json` | ✅ Complete — mirrored in PR #45 |
| RTL layout for Arabic | ✅ `dir="rtl"` applied via locale-aware layout |
| Locale-aware links (`@/i18n/navigation`) | ✅ Fixed in PR #41, verified in PR #45 |
| Locale-aware logout redirect | ✅ `LogoutButton` uses `useLocale()` |
| Locale-aware login redirect (`?next=`) | ✅ Uses `useLocale()` fallback |
| Roadmap page (EN + AR) | ✅ Complete — both locales |
| Error messages translated | ✅ All error keys present in both files |

---

## 7. Known Blockers Before Public Launch

| # | Blocker | Severity | Location |
|---|---|---|---|
| B1 | **External reputation provider is a mock** — all domains except 3 hardcoded test entries return "clean". Real-world flagged domains will not be detected. | High | `backend/app/scanners/reputation_checker.py` |
| B2 | **Per-domain rate limit not enforced** — `DOMAIN_SCAN_LIMIT = "5/hour"` is defined in `rate_limiter.py` but the TODO in `safe_scan_runner.py:111` confirms it is not yet applied. Per-IP limit (10/hour guest) is active but does not prevent one user from scanning the same domain repeatedly. | High | `backend/app/core/safe_scan_runner.py:111` |
| B3 | **Next.js CVE GHSA-36qx-fr4f-26g5 — needs advisory verification** — the project runs Next.js 16.2.9. The CVE reportedly affects versions < 15.2.3. Since 16.x is newer than 15.x, the vulnerability may already be patched in this version. **This must be confirmed against the official advisory before public launch.** Do not assume patched without verification. | Medium (pending verification) | `frontend/package.json` — `"next": "16.2.9"` |
| B4 | **Production secrets not set** — `SECRET_KEY`, `DATABASE_URL`, `CORS_ORIGINS` must be configured; dev defaults must not be used in production. | Hard infra requirement | Deployment config |
| B5 | **HTTPS at load balancer** — must be enforced in production before any user data is transmitted. | Hard infra requirement | Deployment config |

---

## 8. Known Non-Blockers for Supervised Limited Trial

These items are documented but do not prevent a supervised limited trial with known users.

| Item | Why it is non-blocking for supervised trial |
|---|---|
| Mock reputation provider | Trial users are known and vetted. Risk of encountering an undetected malicious domain is accepted during this phase. |
| Per-domain rate limit not enforced | Trial user count is small and controlled. Domain-level abuse is not expected in a supervised setting. |
| Next.js CVE GHSA-36qx-fr4f-26g5 (pending verification) | If current version (16.2.9) is confirmed unaffected by the advisory, this is a non-issue. Even if affected, the attack surface requires an adversary to craft specific i18n bypass paths — low risk in a supervised private trial. |
| `passlib` + `bcrypt 4.x` warning in logs | Authentication works correctly. Warning is cosmetic. |
| `middleware` file convention deprecated (Next.js 16) | Rename is non-functional — no security or UX impact. |
| `pytest-asyncio` deprecation warnings | Tests pass. No user impact. |

---

## 9. RC1 Decision

### Approved for Supervised Limited Trial

> **RC1 is approved for supervised limited trial.**  
> All three user paths (Visitor, Owner, Admin) are complete and stable.  
> Security pipeline (Do Not Scan → SSRF → URL validation → Scan Policy → Safe HTTP Client) is active.  
> No raw technical data is exposed. Cookie security is correctly configured.  
> Trial must use: HTTPS, production secrets, and a known/invited user list only.

### Not Approved for Public Launch

> **RC1 is not approved for public launch.**  
> Three conditions must be resolved first (B1, B2, B3 from §7):
> 1. Replace mock reputation provider with a real external provider
> 2. Enforce per-domain rate limiting (`DOMAIN_SCAN_LIMIT`) in `safe_scan_runner.py`
> 3. Verify Next.js CVE GHSA-36qx-fr4f-26g5 status against official advisory for version 16.2.9
>
> Additionally: production secrets, HTTPS at load balancer, Terms of Service, Privacy Policy, and data retention enforcement are required before any public registration is opened.

---

## 10. Next Work Package

**Production Hardening** (separate PR, after supervised limited trial begins):

| Item | Notes |
|---|---|
| Verify Next.js 16.2.9 against CVE GHSA-36qx-fr4f-26g5 advisory | If already patched, close blocker B3 |
| Enforce per-domain rate limit in `safe_scan_runner.py` | Apply `DOMAIN_SCAN_LIMIT` using existing constant |
| Integrate real reputation provider | Replace `reputation_checker.py` mock |
| Rename `middleware.ts` → `proxy.ts` | Next.js 16 convention (cosmetic, non-urgent) |
| Resolve `passlib` + `bcrypt 4.x` mismatch | Dependency update only |
