# Operational Beta Launch Gate
## Website Trust & Security Advisor — Release 1.2

**Date:** 2026-06-29  
**Main commit at gate creation:** `51b4c78` — docs: Launch Decision Review — supervised beta go/no-go  
**PR #55 status:** ✅ Merged  
**Purpose:** Single operational checklist the founder/deployer must complete before sending the first beta invitation

---

## 1. Purpose of This Document

This document is the terminal gate between the validated codebase and the supervised Beta Trial. It translates the decision in `LAUNCH_DECISION_REVIEW.md` into concrete verification steps — one blocker at a time, one responsible party at a time.

**Engineering work is complete. What remains is deployer work.**

This document does not require any code changes, any PRs, or any backend modifications. It is a configuration and verification checklist. The founder/deployer owns every item.

---

## 2. Current State Summary

| Layer | Status |
|---|---|
| Code / Product | ✅ Complete — all three user paths functional |
| Security pipeline | ✅ Complete — SSRF, Do Not Scan, Scan Policy, rate limiting, auth |
| TypeScript check | ✅ Clean — zero errors |
| Production build | ✅ 24 routes, zero errors |
| Backend unit tests | ✅ 214/214 passing |
| Pre-launch review | ✅ Done — `PRE_LAUNCH_COMPREHENSIVE_REVIEW.md` merged in PR #54 |
| Launch decision | ✅ Done — `LAUNCH_DECISION_REVIEW.md` merged in PR #55 |
| **Operations** | ❌ **Pending — 5 True Beta Blockers unresolved** |

---

## 3. Final Launch Decision

From `LAUNCH_DECISION_REVIEW.md`:

> **READY FOR SUPERVISED BETA WITH MANUAL CONDITIONS**
>
> The 5 True Beta Blockers are all environment configuration tasks (~1–2 hours). Zero engineering work required to start the trial.

---

## 4. True Beta Blockers — Verification Gates

Each blocker must be confirmed **before** sending any beta invitation. Work through them in order — TB3 (HTTPS) and TB4 (APP_ENV) are infrastructure dependencies for the others.

---

### TB1 — `SECRET_KEY` at insecure default

| Field | Detail |
|---|---|
| **Responsible** | Founder / deployer |
| **Risk if skipped** | Any JWT is trivially forgeable. An attacker using the default `"change-me-in-production"` value can impersonate any user, including admin, without knowing any password. |
| **Needs code change?** | No — environment variable only |
| **How to fix** | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` — set result as `SECRET_KEY` in production `.env` |
| **How to verify (without exposing value)** | `docker compose exec backend python -c "from app.core.config import settings; assert settings.secret_key != 'change-me-in-production', 'FAIL'; print('PASS')"` |
| **Passing state** | Script prints `PASS` |
| **Failing state** | Script prints `FAIL` or raises AssertionError — do not proceed |

---

### TB2 — `ADMIN_API_KEY` at insecure default

| Field | Detail |
|---|---|
| **Responsible** | Founder / deployer |
| **Risk if skipped** | Anyone who knows the default key `"change-me-admin-key"` has full admin API access: list all leads, trigger audits, view all scans, manage do-not-scan list. |
| **Needs code change?** | No — environment variable only |
| **How to fix** | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` — set result as `ADMIN_API_KEY` in production `.env` |
| **How to verify (without exposing value)** | `docker compose exec backend python -c "from app.core.config import settings; assert settings.admin_api_key != 'change-me-admin-key', 'FAIL'; print('PASS')"` |
| **Passing state** | Script prints `PASS` |
| **Failing state** | Script prints `FAIL` — do not proceed |

---

### TB3 — HTTPS not active at load balancer

| Field | Detail |
|---|---|
| **Responsible** | Hosting provider / infra |
| **Risk if skipped** | Passwords, session cookies, and all user data are transmitted in plaintext. Unacceptable for any real-user deployment. |
| **Needs code change?** | No — load balancer / reverse proxy configuration only (nginx, Caddy, or cloud provider LB) |
| **How to fix** | Configure TLS termination at the load balancer. Redirect all HTTP (port 80) to HTTPS (port 443). Obtain an SSL certificate (Let's Encrypt is free). |
| **How to verify** | `curl -sI http://<trial-domain> \| head -3` → should return `301` or `302` redirect to `https://`. Then: `curl -sI https://<trial-domain> \| head -3` → should return `200`. SSL certificate check: `echo \| openssl s_client -connect <trial-domain>:443 2>/dev/null \| openssl x509 -noout -dates` → confirm `notAfter` is more than 30 days away. |
| **Passing state** | HTTP redirects to HTTPS. Certificate valid and not expiring within 30 days. |
| **Failing state** | HTTP does not redirect, or certificate is invalid/expired — do not send invitations |

---

### TB4 — `APP_ENV` not set to `production`

| Field | Detail |
|---|---|
| **Responsible** | Founder / deployer |
| **Risk if skipped** | Three security controls are inactive without `production` mode: (1) `Secure` cookie flag is off — cookies sent over HTTP, (2) CSRF host/origin check is off, (3) `TrustedHostMiddleware` is off. |
| **Needs code change?** | No — environment variable only |
| **How to fix** | Set `APP_ENV=production` in production `.env` |
| **How to verify** | `docker compose exec backend python -c "from app.core.config import settings; assert settings.app_env == 'production', 'FAIL'; print('PASS')"` |
| **Cookie flag verification** | After login via the trial domain: open browser DevTools → Application → Cookies → confirm the `access_token` cookie shows `HttpOnly: ✓`, `Secure: ✓`, `SameSite: Lax` |
| **Passing state** | Script prints `PASS`. Cookie flags confirmed in DevTools. |
| **Failing state** | Script prints `FAIL`, or cookie is missing the `Secure` flag — do not proceed |

---

### TB5 — `ALLOWED_ORIGINS` set to localhost

| Field | Detail |
|---|---|
| **Responsible** | Founder / deployer |
| **Risk if skipped** | CORS blocks all API requests from the real domain. The application is literally non-functional in production — every fetch call returns a CORS error. |
| **Needs code change?** | No — environment variable only |
| **How to fix** | Set `ALLOWED_ORIGINS=https://<trial-domain>` in production `.env`. Use the exact domain with protocol — no trailing slash, no wildcards. |
| **How to verify** | `docker compose exec backend python -c "from app.core.config import settings; origins = settings.allowed_origins; assert not any('localhost' in o for o in origins), 'FAIL'; print('PASS', origins)"` |
| **Functional verification** | Open `https://<trial-domain>` in browser, scan a URL, and confirm the result loads. If CORS is misconfigured, the browser console will show `Access-Control-Allow-Origin` errors and the scan form will hang. |
| **Passing state** | Script prints `PASS` with the correct domain. Scan form works end-to-end. |
| **Failing state** | Script prints `FAIL`, or scan form hangs with CORS errors in console — fix `ALLOWED_ORIGINS` and restart backend |

---

## 5. Pre-Invitation Checklist

Complete in this order after all 5 True Beta Blockers are confirmed:

### Infrastructure
- [ ] **TB1** — `SECRET_KEY` verified non-default (verification script passes)
- [ ] **TB2** — `ADMIN_API_KEY` verified non-default (verification script passes)
- [ ] **TB3** — HTTPS active, HTTP redirects to HTTPS, certificate valid >30 days
- [ ] **TB4** — `APP_ENV=production` confirmed, cookie `Secure` flag active in browser
- [ ] **TB5** — `ALLOWED_ORIGINS` set to trial domain, scan form functional end-to-end

### Database
- [ ] `alembic upgrade head` completed successfully
- [ ] `POSTGRES_PASSWORD` confirmed non-default in `.env`
- [ ] All containers healthy: `docker compose ps`

### Functional smoke test (5 minutes)
- [ ] Home page loads at `https://<trial-domain>`
- [ ] Visitor scan: enter `https://example.com` → receives Trust Score
- [ ] SSRF block: enter `http://169.254.169.254` → receives error (not a scan result)
- [ ] Rate limit: confirm guest can scan (first 10 succeed, 11th returns 429)
- [ ] Login at `/login` → redirects to `/sites`
- [ ] Unauthenticated `/sites` → redirects to `/login`

### Manual QA (staging)
- [ ] Full manual QA checklist from `RC1_REVIEW_REPORT.md §4` passed in staging
- [ ] Full manual QA checklist from `RC1_REVIEW_REPORT.md §5` passed in staging

### Beta cohort preparation
- [ ] Beta user list prepared (name, email, role: visitor / owner tester)
- [ ] Informed all beta testers: reputation data is mock — results may not reflect real-world blacklists
- [ ] Invitation message drafted (product context, trial scope, feedback channel, bug report contact)
- [ ] `robots.txt` with `Disallow: /` placed in `frontend/public/` before invitations go out

---

## 6. What Must NOT Happen Now

This section documents explicit prohibitions to prevent scope creep during the operational phase.

| Prohibited action | Reason |
|---|---|
| Add new Features | Beta must test what exists, not what's being built |
| Modify Frontend / UX | Stable for trial; changes during trial invalidate feedback |
| Modify Backend / API | Any change resets QA coverage |
| Modify Auth / Sessions | Auth is solid; changes create risk |
| Modify Scanner / Scoring | Core logic must be stable during trial |
| Modify Database / Migrations | Schema changes require revalidation |
| Add new Dependencies | Increases surface area before trial begins |
| Change CI configuration | CI is green and correct |
| Start Release 1.3 | Beta findings must inform next priorities |
| Begin Public Launch | Trial must complete first |
| Auto-merge any PR | All PRs during beta are manual review |

---

## 7. What the Engineering Track Should Not Touch

These files are in stable, tested state. No changes until post-Beta findings are reviewed:

- `backend/app/core/safe_scan_runner.py`
- `backend/app/core/url_validator.py`
- `backend/app/core/scan_policy.py`
- `backend/app/core/http_client.py`
- `backend/app/core/security.py`
- `backend/app/api/v1/auth.py`
- `backend/app/api/deps.py`
- `backend/app/scanners/`
- `backend/alembic/versions/`
- `frontend/src/proxy.ts` (renamed from `middleware.ts` in Release 1.0.1 — Next.js 16 convention)
- `frontend/src/messages/en.json` and `ar.json`

---

## 8. Final Decision

```
┌─────────────────────────────────────────────────────────────┐
│                   LAUNCH GATE DECISION                      │
├──────────────────┬──────────────────────────────────────────┤
│ Code / Product   │ ✅  READY                                │
│ Security (code)  │ ✅  READY                                │
│ QA (automated)   │ ✅  READY (214 tests passing)            │
├──────────────────┼──────────────────────────────────────────┤
│ Operations       │ ❌  PENDING — 5 blockers unresolved      │
├──────────────────┼──────────────────────────────────────────┤
│ Supervised Beta  │ 🔒  LOCKED until TB1–TB5 confirmed       │
│ Public Launch    │ 🔒  LOCKED until post-beta items done    │
└──────────────────┴──────────────────────────────────────────┘

VERDICT:
  Pre-Launch Validation:  CLOSED ✅
  Operational Beta Gate:  PENDING MANUAL COMPLETION ❌

ACTION REQUIRED:
  Deployer must confirm TB1–TB5 using the verification steps
  in Section 4, complete the checklist in Section 5, then
  send the first beta invitation.
  
  Engineering: no further action required for beta start.
```

---

*This document is the operational output of the Strategic Execution Mode — Close Pre-Launch Validation session (2026-06-29). No code was modified. All items pending in this document are founder/deployer responsibilities.*
