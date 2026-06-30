# Repository Map
## Website Trust & Security Advisor

**Last updated:** 2026-06-29  
**Stack:** Next.js 16.2.9 (App Router) · FastAPI · PostgreSQL · Redis · Celery  
**Main SHA:** `6366a08`

This is the accurate, current map of what exists in the repository and why. For historical planned structure, see `docs/FOLDER_STRUCTURE.md` (superseded).

---

## Root

```
website-trust-scanner/
├── README.md                   # Project overview — start here
├── .env.example                # Environment variable template (no real values)
├── .env                        # Real values — never committed, gitignored
├── .gitignore
├── docker-compose.yml          # Five services: frontend, backend, worker, beat, db, redis
├── backend/                    # FastAPI application
├── frontend/                   # Next.js application
├── docs/                       # 42 documentation files
└── .github/
    └── workflows/ci.yml        # CI: lint, type-check, unit tests, build
```

---

## Backend (`backend/`)

```
backend/
├── Dockerfile
├── pyproject.toml              # Python project config, ruff lint rules
├── requirements.txt            # Production dependencies
├── requirements.dev.txt        # Dev/test dependencies
├── alembic.ini                 # Alembic config (points to backend/alembic/)
│
├── alembic/
│   ├── env.py                  # Alembic environment — loads DATABASE_URL from settings
│   ├── script.py.mako
│   └── versions/
│       ├── 001_security_foundation.py   # Users, sites, do_not_scan, audit_log
│       ├── 002_admin_leads.py           # Leads table
│       ├── 003_auth.py                  # Refresh tokens, account lockout fields
│       ├── 004_scan_results.py          # Scan results table
│       └── 005_notifications.py         # Notifications table
│
└── app/
    ├── main.py                 # FastAPI app init, middleware stack, router mount
    │
    ├── core/                   # Security-critical core — do not modify without review
    │   ├── config.py           # Pydantic Settings — all env vars
    │   ├── security.py         # JWT creation/verification, bcrypt, refresh tokens
    │   ├── url_validator.py    # SSRF protection — 16 blocked ranges, redirect hook
    │   ├── scan_policy.py      # Scan type enforcement — permanently forbidden types
    │   ├── safe_scan_runner.py # 10-step mandatory scan pipeline
    │   ├── http_client.py      # Safe outbound HTTP — timeout, redirect validation
    │   ├── rate_limiter.py     # slowapi limits: guest 10/h, user 60/h, domain 5/h
    │   └── exceptions.py       # Custom exceptions and FastAPI exception handlers
    │
    ├── api/
    │   ├── deps.py             # Auth dependencies: get_current_user, get_admin_user
    │   └── v1/
    │       ├── router.py       # Assembles all sub-routers
    │       ├── auth.py         # POST /auth/login, /auth/refresh, /auth/logout
    │       ├── health.py       # GET /health
    │       ├── scans.py        # POST /public-trust-check (visitor scan)
    │       ├── sites.py        # CRUD /sites + DNS verification
    │       ├── owner_scans.py  # POST/GET /sites/{id}/scans + PDF download
    │       ├── notifications.py
    │       └── admin/
    │           ├── auth.py     # Admin login (JWT role path)
    │           ├── leads.py    # GET /admin/leads, /admin/leads/{id}
    │           └── analytics.py # GET /admin/analytics (summary, trends, audit log)
    │
    ├── models/                 # SQLAlchemy 2.x ORM models
    │   ├── user.py             # User — email, hashed_password, failed_logins, locked_until
    │   ├── site.py             # Site — owner_id, domain, dns_verified, verification_token
    │   ├── scan_result.py      # ScanResult — site_id, score, checks, recommendations
    │   ├── lead.py             # Lead — domain, score, status, outreach fields
    │   ├── audit_log.py        # AuditLog — action, outcome, role, scan_type, timestamp
    │   ├── refresh_token.py    # RefreshToken — token_hash (SHA-256), user_id, expires_at
    │   ├── do_not_scan.py      # DoNotScan — domain blocklist checked before DNS resolution
    │   └── notification.py
    │
    ├── schemas/                # Pydantic v2 request/response schemas
    │   ├── auth.py             # LoginRequest, TokenResponse, RefreshRequest
    │   ├── site.py             # SiteCreate, SiteResponse, VerifyDNSRequest
    │   ├── scan.py             # TrustReport, ChecksSummary, Recommendations
    │   ├── scan_result.py      # ScanResultSummary, ScanResultDetail
    │   └── lead.py             # LeadResponse, LeadDetail
    │
    ├── scanners/               # Passive scanners — surface signals only, no offensive capability
    │   ├── ssl_checker.py      # TLS certificate validity, expiry
    │   ├── https_checker.py    # HTTPS redirect, HSTS header
    │   ├── headers_checker.py  # Security headers: CSP, X-Frame-Options, etc.
    │   ├── dns_checker.py      # DNS records, SPF, DMARC
    │   ├── reputation_checker.py # Domain reputation (currently mock — replace before public launch)
    │   ├── trust_score.py      # compute_trust_report() → sanitized dict only
    │   ├── lead_score.py       # Lead scoring for admin view
    │   ├── result.py           # Shared result types
    │   ├── runner.py           # Internal scanner orchestration (called by safe_scan_runner)
    │   └── outreach.py         # Bilingual outreach email templates
    │
    ├── services/
    │   ├── audit_logger.py     # Centralized audit logging service
    │   ├── dns_verification.py # DNS TXT record ownership verification
    │   ├── notification_service.py
    │   └── pdf_report.py       # PDF report generation (bilingual)
    │
    ├── tasks/
    │   └── scheduled_scans.py  # Celery task definitions + Celery app instance
    │
    ├── workers/
    │   └── celery_app.py       # Celery app configuration (broker, serializer settings)
    │
    └── db/
        ├── base.py             # SQLAlchemy declarative base
        └── session.py          # Async session factory (AsyncSessionLocal)
```

### Tests (`backend/tests/`)

```
backend/tests/
└── unit/
    ├── test_url_validator.py       # SSRF protection — most critical test file
    ├── test_scan_policy.py         # Scan type enforcement
    ├── test_safe_scan_runner.py    # 10-step pipeline
    ├── test_security.py            # JWT, bcrypt, refresh tokens
    ├── test_trust_score.py         # Trust score calculation
    ├── test_http_client.py         # Safe HTTP client
    ├── test_audit_logger.py        # Audit logging
    ├── test_dns_verification.py    # DNS TXT verification
    ├── test_lead_score.py          # Lead scoring
    ├── test_pdf_report.py          # PDF generation
    └── test_scheduled_scans.py     # Celery task definitions
```

214 tests, 214 passing as of `6366a08`.

---

## Frontend (`frontend/`)

```
frontend/
├── Dockerfile
├── package.json                # Next.js 16.2.9, next-intl v4, Tailwind CSS
├── next.config.ts              # next-intl plugin, i18n routing config
├── tailwind.config.ts          # Tailwind with RTL support
├── tsconfig.json
├── postcss.config.mjs
├── proxy.ts                    # next-intl middleware (renamed from middleware.ts per Next.js 16)
│
└── src/
    ├── i18n/
    │   ├── routing.ts          # Locale list: ['ar', 'en'], defaultLocale: 'ar'
    │   ├── request.ts          # Per-request locale resolution
    │   └── navigation.ts       # Locale-aware Link, redirect, useRouter
    │
    ├── messages/
    │   ├── ar.json             # Arabic translations (256 keys)
    │   └── en.json             # English translations (256 keys — must stay in sync)
    │
    ├── components/
    │   ├── TrustResult.tsx     # Visitor scan result: Trust Score ring, Usage Decision
    │   ├── ScanForm.tsx        # URL input form with validation
    │   ├── FixPlan.tsx         # Owner Fix Plan cards with developer instructions
    │   ├── AuthForm.tsx        # Login/Register form
    │   ├── CopyButton.tsx      # Clipboard copy for Fix Plan instructions
    │   ├── LogoutButton.tsx    # Logout with token revocation
    │   ├── LanguageToggle.tsx  # AR/EN switcher
    │   ├── BrandLogo.tsx       # Product logo/wordmark
    │   └── AppFooter.tsx       # Footer with legal links
    │
    └── app/
        └── [locale]/           # All routes are locale-prefixed (/ar/... or /en/...)
            ├── layout.tsx          # Root layout: Cairo font, dir attribute, locale provider
            ├── page.tsx            # Home — Visitor scan + TrustResult
            ├── login/page.tsx      # Owner login
            ├── register/page.tsx   # Owner registration
            ├── forgot-password/page.tsx  # Forgot password (UI only — backend endpoint deferred)
            ├── roadmap/page.tsx    # Public product roadmap
            ├── terms/page.tsx      # Terms of Service (placeholder — legal content needed)
            ├── privacy/page.tsx    # Privacy Policy (placeholder — legal content needed)
            ├── sites/
            │   ├── page.tsx                        # Owner sites list
            │   ├── [siteId]/scans/page.tsx         # Scan history for a site
            │   └── [siteId]/scans/[scanId]/page.tsx # Scan detail + Fix Plan
            └── admin/
                ├── page.tsx            # Admin overview (redirects to leads)
                ├── analytics/page.tsx  # Analytics: summary stats, scan trends, audit log
                └── leads/
                    ├── page.tsx        # Leads list
                    └── [id]/page.tsx   # Lead detail
```

24 routes total, all server-rendered on demand (no static generation).

---

## Docs (`docs/`)

42 files. See `docs/INDEX.md` for the full annotated list with purposes and audience.

---

## CI/CD (`.github/workflows/ci.yml`)

Five checks run on every PR:

| Check | Command | Purpose |
|---|---|---|
| Backend lint | `ruff check` | Python style and error detection |
| Backend unit tests | `pytest` | 214 tests |
| Backend migration import | Python import check | Verify all migrations are importable |
| Frontend type check | `npx tsc --noEmit` | TypeScript correctness |
| Frontend build | `npm run build` | Ensures 24 routes build cleanly |

All five must pass before any PR is merged.

---

## Configuration Files

| File | Purpose |
|---|---|
| `.env.example` | Variable names with placeholder values — committed |
| `.env` | Real values — never committed, listed in `.gitignore` |
| `docker-compose.yml` | Five-service local and production composition |
| `backend/pyproject.toml` | Python project metadata, ruff config, pytest config |
| `backend/alembic.ini` | Alembic migration config |
| `frontend/next.config.ts` | Next.js + next-intl config |
| `frontend/tailwind.config.ts` | Tailwind CSS with RTL utilities |
