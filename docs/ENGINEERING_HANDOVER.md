# Engineering Handover
## Website Trust & Security Advisor

**Date:** 2026-06-29  
**Main commit at handover:** `6366a08` — docs: Supervised Beta Operating Cycle  
**Status:** Engineering phase complete — product in Supervised Beta operational phase  
**Audience:** Founder / product owner taking operational control

---

## 1. Executive Summary

The Website Trust & Security Advisor has been built, hardened, reviewed, and documented across five sequential releases:

| Release | Goal | Status |
|---|---|---|
| MVP | Three-path product: Visitor, Owner, Admin | ✅ Complete |
| 1.0.1 | Production Hardening: SSRF, rate limiting, auth, audit logging | ✅ Complete |
| 1.1 | Design & UX Refresh: visual identity, RTL, bilingual polish | ✅ Complete |
| 1.2 | Beta Preparation: Owner UX fixes, i18n keys, docs | ✅ Code complete (PR #53 open, merge after TB1–TB5 confirmed) |
| Pre-Launch | Validation, decision review, operational gate, beta operating cycle | ✅ Complete |

The product is architecturally sound, security-hardened, and ready for a supervised, invitation-only beta trial with 8–13 known users. All automated quality checks pass. What remains before the trial begins is a set of deployer-owned operational tasks — no engineering work is required.

---

## 2. Current State

### Code quality
| Check | Result |
|---|---|
| TypeScript (`npx tsc --noEmit`) | ✅ Zero errors |
| Production build (`npm run build`) | ✅ 24 routes, zero errors |
| Backend unit tests (`pytest`) | ✅ 214/214 passing |
| Backend lint (ruff) | ✅ Clean |
| Backend migration import check | ✅ Clean |

### Security controls (all verified in code)
| Control | Status |
|---|---|
| Safe Scan Runner 10-step pipeline | ✅ Active |
| SSRF protection (16 blocked ranges + redirect hook) | ✅ Active |
| Do Not Scan gate (pre-DNS, unconditional) | ✅ Active |
| Scan Policy engine (typed, pure logic) | ✅ Active |
| Safe HTTP client (timeout, redirect validation) | ✅ Active |
| Rate limiting: guest 10/h, user 60/h, domain 5/h | ✅ Active |
| bcrypt passwords, JWT with type check, opaque refresh tokens | ✅ Active |
| Refresh token rotation | ✅ Active |
| Account lockout (5 failures → 15 min) | ✅ Active |
| Owner isolation at ORM level | ✅ Active |
| Admin dual-path auth (JWT role + constant-time key) | ✅ Active |
| Audit logging at every scan step | ✅ Active |
| Data minimization (no raw headers/IPs/bodies stored) | ✅ Active |
| Security headers (nosniff, DENY frames, Referrer-Policy) | ✅ Active |
| CSRF protection (SameSite=Lax + production Origin check) | ✅ Active |

### Product flows
| Flow | Status |
|---|---|
| Visitor: URL scan → Trust Score → Usage Decision | ✅ Complete |
| Visitor: Danger banner (low trust) | ✅ Complete |
| Visitor: Trust level guidance (low/medium/good/high) | ✅ Complete |
| Owner: Register → Login → Sites list | ✅ Complete |
| Owner: DNS verification (TXT record) | ✅ Complete |
| Owner: Scan → Fix Plan → Copy instructions | ✅ Complete |
| Owner: PDF report download (bilingual) | ✅ Complete |
| Admin: Leads list + Lead detail | ✅ Complete |
| Admin: Analytics dashboard | ✅ Complete |
| Bilingual Arabic/English + RTL layout | ✅ Complete |

---

## 3. Engineering Complete

The following are considered engineering-complete. Do not modify without a specific beta finding that justifies the change:

**Core pipeline (do not touch)**
- `backend/app/core/safe_scan_runner.py` — 10-step mandatory gate
- `backend/app/core/url_validator.py` — SSRF protection
- `backend/app/core/scan_policy.py` — scan type enforcement
- `backend/app/core/http_client.py` — safe outbound HTTP
- `backend/app/core/security.py` — JWT, bcrypt, refresh tokens

**Auth (do not touch)**
- `backend/app/api/v1/auth.py`
- `backend/app/api/deps.py`

**Scanners (do not touch)**
- All files in `backend/app/scanners/`

**Database (do not touch)**
- `backend/alembic/versions/` — 5 migrations, sequential, applied

**Frontend (stable)**
- All pages and components under `frontend/src/app/[locale]/`
- `frontend/src/components/`
- `frontend/src/messages/en.json` and `ar.json`

---

## 4. Manual Operational Tasks

**These cannot be done in code. The founder/deployer must complete them before the trial begins.**

### True Beta Blockers (must complete before first invitation)

| # | Task | How |
|---|---|---|
| TB1 | Generate `SECRET_KEY` | `python -c "import secrets; print(secrets.token_hex(32))"` → set in `.env` |
| TB2 | Generate `ADMIN_API_KEY` | `python -c "import secrets; print(secrets.token_hex(32))"` → set in `.env` |
| TB3 | Activate HTTPS at load balancer | Configure TLS at nginx/Caddy/cloud LB. HTTP (80) → redirect to HTTPS (443). |
| TB4 | Set `APP_ENV=production` | In `.env`. Activates Secure cookies, CSRF host check, TrustedHostMiddleware. |
| TB5 | Set `ALLOWED_ORIGINS` to trial domain | `ALLOWED_ORIGINS=https://<trial-domain>` in `.env`. Required for CORS to function. |

**Verification commands for each blocker:** see `docs/OPERATIONAL_BETA_LAUNCH_GATE.md §4`

### Additional pre-trial setup

| Task | Notes |
|---|---|
| `POSTGRES_PASSWORD` confirmed non-default | Verify in `.env` |
| `alembic upgrade head` run in production | After first deploy |
| All containers healthy | `docker compose ps` |
| Manual QA checklist completed in staging | `RC1_REVIEW_REPORT.md §4 and §5` |
| `robots.txt` with `Disallow: /` added | Place in `frontend/public/robots.txt` before sending invitations |

### Required before public launch (not needed for supervised beta)

| Task | Notes |
|---|---|
| Real reputation provider (`REPUTATION_PROVIDER`) | Google Safe Browsing or VirusTotal API key |
| Terms of Service page content | Legal text — not engineering |
| Privacy Policy page content | Legal text — not engineering |
| Error monitoring (Sentry or equivalent) | Wire DSN to backend |
| Uptime monitoring (external ping) | Any uptime service |
| Data retention Celery jobs verified | Confirm Celery Beat jobs running |

---

## 5. What Engineering Should NOT Do Now

These actions are explicitly prohibited until beta findings provide specific justification:

| Prohibited | Reason |
|---|---|
| New features | Beta must test what exists |
| Refactoring without a specific bug driving it | Adds risk without addressing a known problem |
| Scanner additions or modifications | Core pipeline is stable and tested |
| Security control changes | Auth and scan protection are solid; changes add risk |
| Schema changes or new migrations | No new data model needed for beta |
| New dependencies | Surface area increase before trial |
| Content-Security-Policy implementation | Acceptable medium-risk gap for supervised beta |
| Release 2.0 planning or implementation | Wait for beta findings |
| Public launch preparation | Wait for beta success |

The one exception: if a P0 or P1 issue appears during the trial, engineering responds with a targeted fix. The fix must be minimal, tested, and not introduce new scope.

---

## 6. Beta Entry Checklist

Before inviting the first user, confirm every item in `docs/OPERATIONAL_BETA_LAUNCH_GATE.md §5`. Summary:

**Infrastructure**
- [ ] TB1 — `SECRET_KEY` verified non-default
- [ ] TB2 — `ADMIN_API_KEY` verified non-default
- [ ] TB3 — HTTPS active, cert valid >30 days
- [ ] TB4 — `APP_ENV=production` confirmed, cookie Secure flag active
- [ ] TB5 — `ALLOWED_ORIGINS` set to trial domain, CORS functional

**Functional smoke test**
- [ ] Home page loads at `https://<trial-domain>`
- [ ] `https://example.com` → Trust Score returned
- [ ] `http://169.254.169.254` → SSRF error (not a scan result)
- [ ] 11th guest scan in 1 hour → 429 response
- [ ] Login → `/sites` redirect
- [ ] Unauthenticated `/sites` → `/login` redirect

**Trial preparation**
- [ ] Beta user list prepared (names, emails, roles)
- [ ] Invitations drafted (scope, feedback channel, "do not share URL" note)
- [ ] `robots.txt` in place
- [ ] Informed testers that reputation data is mock

---

## 7. After the First Beta User — The Operating Cycle

Once the trial is active, follow the cycle documented in `docs/BETA_OPERATING_CYCLE.md`:

```
Active trial (Days 1–17)
  ↓ Founder observes sessions using BETA_FOUNDER_PLAYBOOK.md
  ↓ Records structured notes using BETA_FEEDBACK_TEMPLATE.md
  
Day 18: Retrospective
  ↓ Classify all issues: ISSUE_CLASSIFICATION_GUIDE.md
  ↓ Prioritize: BETA_PRIORITIZATION_FRAMEWORK.md
  ↓ Separate P0/P1 (fix now) from P2 (Release 2.0) from P3/Out of Scope

Post-trial
  ↓ Follow POST_BETA_RELEASE_WORKFLOW.md
  ↓ Update RELEASE_PLAN.md §2.0 with confirmed scope
  ↓ Sprint → Implementation → Validation → Release 2.0
```

**Code freeze rule:** No code changes during Days 1–17 except P0/P1 emergency patches. P1 patches must pass CI before deployment.

---

## 8. Success Criteria for the Beta Trial

The trial is successful if all of the following are true at Day 18:

- [ ] ≥ 5 distinct users completed the full Visitor flow end-to-end
- [ ] ≥ 2 users completed the full Owner flow (register → DNS verify → scan → Fix Plan)
- [ ] Zero P0 incidents during the trial
- [ ] Zero P1 incidents open at Day 18
- [ ] Error rate < 1% of scan requests
- [ ] Structured feedback collected from ≥ 60% of invited users
- [ ] All issues classified and prioritized
- [ ] Release 2.0 candidate backlog drafted

---

## 9. Open Items at Handover

### Open PR — requires founder decision

| PR | Title | Type | Notes |
|---|---|---|---|
| #53 | Release 1.2 Beta Trial Preparation | Frontend + Docs | Owner UX fixes (layout, empty states, retry, RTL score ring). Safe to merge after TB1–TB5 are confirmed. Merge before inviting the first user. |

### Known accepted limitations (not engineering defects)

| Item | Status | Resolution |
|---|---|---|
| Reputation provider is mock | Known — B1 | Replace before public launch |
| Per-domain rate limit silent-passes if Redis down | Known — B2 | Harden before public launch |
| No Content-Security-Policy header | Known — NH1 | Add before public launch |
| Forgot-password email flow not implemented | Known — NH4 | Release 2.0 candidate |
| No ARIA live regions for scan results | Known — NH5 | Release 2.0 candidate |
| No E2E test suite | Known — NH6 | Release 2.0 candidate |

---

## 10. End of Engineering Phase

The core engineering phase of the Website Trust & Security Advisor is complete as of 2026-06-29.

What has been built is a production-quality, bilingual (Arabic/English), security-hardened web application that:
- Helps visitors assess the trustworthiness of websites they encounter
- Helps site owners identify and fix trust signals that affect how visitors perceive their site
- Provides founders with an admin view for operational oversight

It is a **Trust Advisor**, not a security scanner. It surfaces public-facing signals only. It does not perform active exploitation, port scanning, content crawling, or any form of offensive reconnaissance. These constraints are permanent and are enforced both in code (Scan Policy engine, permanently forbidden types) and in product philosophy.

**Engineering's job now is to listen.** Every future change should be grounded in a specific observation from the beta trial — a user who was confused, a flow that failed, a signal that wasn't trusted. Build from evidence, not from assumption.

The next sprint begins after Day 18 of the beta trial, when findings are classified, prioritized, and converted into a confirmed Release 2.0 scope.

---

*Related documents:*  
*`OPERATIONAL_BETA_LAUNCH_GATE.md` · `LAUNCH_DECISION_REVIEW.md` · `BETA_OPERATING_CYCLE.md` · `BETA_FOUNDER_PLAYBOOK.md` · `POST_BETA_RELEASE_WORKFLOW.md` · `PRE_LAUNCH_COMPREHENSIVE_REVIEW.md`*
