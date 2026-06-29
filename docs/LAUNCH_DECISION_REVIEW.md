# Launch Decision Review
## Website Trust & Security Advisor — Release 1.2 Beta Trial

**Date:** 2026-06-29  
**Input documents:** `PRE_LAUNCH_COMPREHENSIVE_REVIEW.md` · `BETA_TRIAL_READINESS_REPORT.md` · `RELEASE_1_2_BETA_PREPARATION.md` · `BETA_TRIAL_PLAN.md` · `RELEASE_PLAN.md`  
**Purpose:** Convert multi-angle review findings into a single, pragmatic go/no-go decision  
**Scope:** Supervised, invitation-only Beta Trial (5–15 known users) — NOT public launch

---

## 1. Executive Summary

After reviewing all four prior documents and the live codebase, this document draws a hard line between what **actually blocks the supervised beta** versus what is best practice for a future public launch.

The previous reviews correctly identified every risk and gap. What they did not do is distinguish between the risk profile of a **supervised trial with 5–15 known, named users under direct founder oversight** versus a **public launch with anonymous users at scale**. That distinction is the entire purpose of this document.

**The engineering work is done. The product is ready. The blockers are all infra/ops/legal tasks** — none require touching code.

**Final decision: Ready for supervised beta with manual conditions.**  
There are 5 True Beta Blockers. All are configuration or deployment tasks. None are code changes. Once the founder/deployer completes those 5 items, the trial can begin.

---

## 2. Current Status

| Dimension | Status |
|---|---|
| Codebase quality | ✅ Production-grade |
| Security pipeline (SSRF, Do Not Scan, Scan Policy) | ✅ Complete and tested |
| Auth (bcrypt, JWT, lockout, rotation) | ✅ Solid |
| Owner isolation | ✅ Enforced at ORM level |
| Admin auth | ✅ Dual-path (JWT + constant-time key) |
| TypeScript check | ✅ Zero errors |
| Production build | ✅ 24 routes, zero errors |
| Backend unit tests | ✅ 214/214 passed |
| Visitor flow | ✅ Complete and tested |
| Owner flow | ✅ Complete (UX gaps fixed in Release 1.2) |
| Admin path | ✅ Functional (founder-only) |
| Bilingual (AR/EN) | ✅ Full parity, RTL correct |
| Production secrets | ❌ Default values — must change before deploy |
| HTTPS | ❌ Infra task — not yet confirmed |
| ALLOWED_ORIGINS | ❌ Set to localhost — must change before deploy |
| APP_ENV | ❌ Set to `development` — must change before deploy |
| Reputation provider | ⚠️ Mock — negotiable for supervised beta (see §4) |
| Terms of Service | ⚠️ Placeholder — negotiable for supervised beta (see §4) |
| Privacy Policy | ⚠️ Placeholder — negotiable for supervised beta (see §4) |
| Error monitoring | ⚠️ Absent — negotiable for supervised beta (see §5) |

---

## 3. Decision Framework

This review uses three distinct risk contexts:

| Context | Who uses it | Registration | Oversight |
|---|---|---|---|
| **Supervised Beta Trial** | 5–15 known, named, personally invited users | Invitation-only — not public | Founder watching logs in real time |
| **Public Launch** | Open to anyone | Public registration | Automated monitoring required |
| **Commercial Launch** | Paying customers, businesses | Public + legal agreement | Full compliance stack required |

**A supervised beta trial is fundamentally different from a public launch.** The threat model for 15 known users under direct founder oversight is not the same as 1,000 anonymous users. This document applies the correct threat model to each item.

---

## 4. True Beta Blockers

These 5 items prevent the Beta Trial from starting. None require engineering work — they are all deployer/infra tasks.

| # | Blocker | Why it blocks supervised beta | Who resolves it |
|---|---|---|---|
| **TB1** | `SECRET_KEY` is `"change-me-in-production"` | Any JWT is trivially forgeable. An attacker knowing the default key can impersonate any user including admin. Unacceptable even with 1 real user. | Deployer |
| **TB2** | `ADMIN_API_KEY` is `"change-me-admin-key"` | Admin API accepts the default key. Anyone who knows defaults has full admin access (list all leads, trigger audits, view all scans). Unacceptable even with 1 real user. | Deployer |
| **TB3** | HTTPS not active at load balancer | Without TLS, passwords and cookies are transmitted in plaintext. Unacceptable for any real-user deployment, even supervised. | Infra |
| **TB4** | `APP_ENV` not set to `"production"` | Without this, `Secure` cookie flag is off, CSRF host check is off, and TrustedHostMiddleware is off. These controls only activate in production mode. | Deployer |
| **TB5** | `ALLOWED_ORIGINS` set to `"http://localhost:3000"` | CORS blocks all API requests from the real domain. The app is literally non-functional in production without this change. | Deployer |

**Resolution for all 5:** Generate secrets (`python -c "import secrets; print(secrets.token_hex(32))"`), set in production `.env`, confirm `APP_ENV=production`. No code changes required. Estimated effort: 1–2 hours.

---

## 5. Required Before Public Launch

These items do NOT block a supervised, invitation-only Beta Trial with known users under founder oversight. They MUST be resolved before any form of public registration or public URL promotion.

| # | Item | Why it's NOT a beta blocker | Why it blocks public launch |
|---|---|---|---|
| **PL1** | Real reputation provider (`REPUTATION_PROVIDER=mock`) | Beta testers see slightly optimistic results (no domain flagged as bad reputation). This is a UX/accuracy gap, not a security or data exposure gap. Disclose to beta testers. | All public users receive inaccurate reputation data at scale. Undermines product credibility. |
| **PL2** | Terms of Service published | For 5–15 personally invited users under direct communication, you can share terms informally. Not legally equivalent to published ToS, but the risk is manageable for this cohort size and duration. | Required for any public registration. Legal exposure without it. |
| **PL3** | Privacy Policy published | Same reasoning as ToS. For personally invited beta testers you know personally, the practical risk is manageable short-term. | Required before processing data from unknown EU users at scale. GDPR obligation. |
| **PL4** | Error monitoring tool (Sentry/equivalent) | The founder can watch structured server logs directly during a supervised trial with 15 users. Logs exist; alerts don't. This is acceptable for a short, supervised trial. | At public scale, manual log monitoring is not viable. 5xx spikes will go undetected. |
| **PL5** | Data retention Celery jobs verified in production | Beta generates minimal data. 24-hour public scan retention may not apply if Celery isn't running, but the data volume from 15 users is negligible short-term. | At public scale, indefinite storage violates the retention policy and creates storage growth risk. |
| **PL6** | Uptime monitoring (external check) | Founder can notice downtime during a short supervised trial through direct observation. | Required at public launch. Users expect SLA transparency. |
| **PL7** | `robots.txt` with `Disallow: /` | If the trial URL is not publicly shared or promoted, search engines are unlikely to discover it. Add as a precaution before sending invitations. | Required before any public URL promotion. |
| **PL8** | Database password at non-default value | This is technically bundled with TB2 — but confirming `POSTGRES_PASSWORD` is non-default is worth calling out separately. The DB should not be reachable with default credentials. | — |

> **Note on `robots.txt`:** This is the easiest item on the whole list — a 3-line file in `frontend/public/`. It is worth adding before sending the first invitation as a low-cost precaution, even though it doesn't block the beta functionally. The user asked us not to touch code, but this is a pure content file; the decision to add it is the deployer's.

---

## 6. Nice To Have / Post-Beta

These improve the product but are not blockers for any near-term milestone. Log for Release 2.0 planning.

| # | Item | Notes |
|---|---|---|
| **NH1** | Content-Security-Policy header | XSS mitigation. Medium risk for this app since no user-generated HTML is rendered in the browser. Safe to defer post-beta. |
| **NH2** | DNS TXT record value shown in Owner UI | Currently the owner sees "verification pending" with no in-app guidance on the actual TXT record to add. Reduces support overhead but doesn't block the flow. |
| **NH3** | Startup assertion on insecure defaults | A runtime check that raises if `SECRET_KEY == "change-me-in-production"` when `APP_ENV=production`. Prevents accidental misconfigured redeploys. Engineering task, safe to defer. |
| **NH4** | Forgot password email flow | UI link exists; backend endpoint is not implemented. Documented as known gap. No beta tester will be blocked if the founder resets passwords manually. |
| **NH5** | ARIA live regions for scan results | Screen reader users don't get an audible announcement when a scan result loads. Accessibility improvement, not a blocking UX issue. |
| **NH6** | E2E test suite (Playwright) | No automated end-to-end tests. Manual QA checklist covers this for now. |
| **NH7** | Redis startup health check / warning | Per-domain rate limit silently passes if Redis is unavailable. A startup warning would surface this operationally. Low risk for supervised beta. |
| **NH8** | Passlib deprecation fix | Non-breaking warning in Python 3.11. Will break in Python 3.13. No urgency for current environment. |
| **NH9** | Per-domain rate limit hardening | Currently silently passes if Redis is down. For a supervised beta of 15 users this is acceptable. Harden before public launch. |
| **NH10** | Self-service data deletion UI | GDPR right-to-erasure is documented in policy but no UI exists. For personally invited beta testers, deletion can be handled manually by the founder. |

---

## 7. What Is Already Ready

The following require zero additional work and are confirmed production-ready:

**Security controls:**
- Safe Scan Runner 10-step mandatory pipeline
- SSRF protection (16 blocked network ranges, redirect validation, post-DNS re-check)
- Do Not Scan gate (pre-DNS, unconditional)
- Scan Policy engine (typed, pure logic, tested)
- Safe HTTP client (timeout, connection cap, redirect validation, fixed User-Agent)
- Permanently forbidden scan types (port scan, XSS test, SQLi test, etc.)
- Rate limiting (guest 10/hour per IP, user 60/hour per account, domain 5/hour)
- bcrypt password hashing, JWT with type check, opaque refresh tokens with rotation
- Account lockout (5 failed logins → 15-minute lock)
- Owner isolation at ORM level (no IDOR possible)
- Admin dual-path auth (JWT role OR constant-time key compare)
- Audit logging at every scan step and admin action
- Data minimization (no raw headers, IPs, or response bodies stored)
- Security headers (nosniff, DENY frames, Referrer-Policy, no-store)
- CSRF protection (SameSite=Lax + production Origin/Referer check)
- OpenAPI docs hidden in production

**Product flows:**
- Visitor flow: URL scan → Trust Score → Usage Decision → 4 trust levels → Danger banner → Fix guidance
- Owner flow: Register → Login → Sites list → Scan history → Scan detail → Fix Plan → PDF download
- Admin path: Leads list → Lead detail → Analytics → All role-gated
- Full bilingual (Arabic + English) with correct RTL layout, logical CSS, score ring `dir="ltr"` fix

**Quality:**
- TypeScript: zero errors
- Production build: 24 routes, zero errors
- Unit tests: 214/214 passing
- Translation parity: all namespaces verified in both languages

---

## 8. What the Founder/Deployer Must Do Manually

Engineering cannot do these — they require access to the production environment:

| Task | Command/Action |
|---|---|
| Generate `SECRET_KEY` | `python -c "import secrets; print(secrets.token_hex(32))"` |
| Generate `ADMIN_API_KEY` | `python -c "import secrets; print(secrets.token_hex(32))"` |
| Generate `POSTGRES_PASSWORD` | `openssl rand -base64 32` |
| Set `APP_ENV=production` | In production `.env` file |
| Set `ALLOWED_ORIGINS=https://<trial-domain>` | In production `.env` file |
| Configure TLS at load balancer | Infra task (nginx/Caddy/cloud LB) |
| Run Alembic migrations | `docker compose exec backend alembic upgrade head` |
| Confirm Celery worker and beat are running | `docker compose ps` → all services healthy |
| Complete manual QA checklist | `RC1_REVIEW_REPORT.md §4 and §5` in staging |
| Prepare beta user invitation list | Names + emails + roles (visitor / owner tester) |
| Inform beta testers about mock reputation | "Reputation data is for testing; results may not reflect real-world reputation" |

**For pre-public launch (additional tasks for the founder):**
- Integrate real reputation provider (Google Safe Browsing or VirusTotal API key → set `REPUTATION_PROVIDER` and API key env var)
- Write and publish Terms of Service page content (legal, not engineering)
- Write and publish Privacy Policy page content (legal, not engineering)
- Configure error monitoring (Sentry DSN → add to backend env → wire `sentry_sdk.init`)
- Configure uptime monitoring (external ping service)
- Verify Celery Beat retention jobs are firing (check scheduled task logs)

---

## 9. What Engineering Should Not Touch Now

Per the explicit constraints of this task and to preserve stability before the trial:

| Category | What not to change | Reason |
|---|---|---|
| Backend | `safe_scan_runner.py`, `url_validator.py`, `scan_policy.py`, `http_client.py` | Pipeline is complete and tested. Any change risks regression. |
| Auth | `auth.py`, `security.py`, `deps.py` | Auth is solid. Changes to auth before a real-user trial are high-risk. |
| Scanner | Any file in `backend/app/scanners/` | Scan logic is stable. |
| Scoring | Trust score calculation | Stable. |
| Database | Alembic migrations | No schema changes needed for beta. |
| Frontend | Any UX or layout changes | UX gaps are fixed in Release 1.2. |
| Dependencies | `requirements.txt`, `package.json` | No new dependencies until beta findings are reviewed. |
| CI | `.github/workflows/` | CI is green and correct. |
| Reputation provider | `reputation_checker.py` | This requires backend change + real API key. It's a deployer/infra task, not a code task, for now. When integrating a real provider, do it in a dedicated PR. |

---

## 10. Final Decision

### **READY FOR SUPERVISED BETA WITH MANUAL CONDITIONS**

The product code is complete and security-hardened. The supervised Beta Trial can begin as soon as the founder/deployer completes the 5 True Beta Blockers (TB1–TB5) — all of which are environment configuration tasks that take approximately 1–2 hours.

**Decision matrix:**

| Question | Answer |
|---|---|
| Is the code safe to expose to real users? | **Yes** — all security controls are active and tested |
| Is anything broken that blocks user flows? | **No** — all three paths (Visitor, Owner, Admin) are functional |
| Is there a realistic path to data exposure with default secrets? | **Yes** — TB1 and TB2 must be resolved first |
| Can the trial proceed without real reputation data? | **Yes** — with explicit disclosure to beta testers |
| Can the trial proceed without published ToS/Privacy Policy? | **Yes** — for a small, personally invited cohort under direct oversight |
| Is manual QA in staging required before invitations? | **Yes** — this is non-negotiable; it's the only functional verification step |
| Is the product ready for public launch today? | **No** — PL1–PL7 must be resolved first |

### Recommended path to first beta invitation

```
TODAY — Infra sprint (1–2 hours):
  ☐ Generate real SECRET_KEY, ADMIN_API_KEY, POSTGRES_PASSWORD
  ☐ Set APP_ENV=production
  ☐ Set ALLOWED_ORIGINS=https://<trial-domain>
  ☐ Configure HTTPS at load balancer
  ☐ Run docker compose up --build in staging
  ☐ Run alembic upgrade head
  ☐ Confirm all services healthy

BEFORE INVITATIONS — Staging QA (2–4 hours):
  ☐ Complete manual QA checklist (RC1_REVIEW_REPORT.md §4 and §5)
  ☐ Test SSRF block (http://169.254.169.254 → error)
  ☐ Test rate limit (11th guest scan in 1 hour → 429)
  ☐ Confirm cookies: httponly=True, samesite=lax, secure=True
  ☐ Confirm no default secrets in deployed env

BEFORE FIRST INVITATION — Communicate to beta testers:
  ☐ Reputation data is mock; results are for flow testing, not real-world accuracy
  ☐ Terms and Privacy Policy are in draft; beta participation is informal

AFTER BETA TRIAL — Before public launch:
  ☐ Integrate real reputation provider
  ☐ Publish Terms of Service
  ☐ Publish Privacy Policy
  ☐ Configure error monitoring
  ☐ Configure uptime monitoring
  ☐ Verify Celery retention jobs
  ☐ Add robots.txt
```

---

*This document is the output of a review-only pass on the codebase and prior documentation. No code was written or modified. All items classified as "Deployer must do" require access to the production environment and are outside the scope of engineering PRs.*
