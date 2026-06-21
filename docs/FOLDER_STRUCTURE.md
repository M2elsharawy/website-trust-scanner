# Folder Structure
## Website Trust & Security Advisor

**Version:** Phase 1 Design  
**Stack:** Next.js 14 (Frontend) + FastAPI (Backend)

---

## هيكل المشروع الكامل

```
website-trust-scanner/
├── frontend/                    # Next.js 14 App
├── backend/                     # FastAPI App
├── docs/                        # التوثيق (مرحلة 0 و 1)
├── docker-compose.yml           # تشغيل المشروع كاملًا
├── docker-compose.dev.yml       # overrides للتطوير
├── .env.example                 # نموذج environment variables
└── README.md
```

---

## Frontend Structure

```
frontend/
├── src/
│   ├── app/                           # Next.js App Router
│   │   ├── [locale]/                  # i18n routing (ar | en)
│   │   │   ├── layout.tsx             # Root layout (RTL/LTR، fonts)
│   │   │   ├── page.tsx               # الصفحة الرئيسية — Public Trust Check
│   │   │   │
│   │   │   ├── dashboard/             # Owner Dashboard
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── page.tsx           # Overview
│   │   │   │   ├── sites/
│   │   │   │   │   ├── page.tsx       # قائمة المواقع
│   │   │   │   │   ├── [siteId]/
│   │   │   │   │   │   ├── page.tsx   # تفاصيل موقع
│   │   │   │   │   │   ├── verify/
│   │   │   │   │   │   │   └── page.tsx  # خطوات التحقق من الملكية
│   │   │   │   │   │   └── reports/
│   │   │   │   │   │       └── [reportId]/page.tsx
│   │   │   │   │   └── new/page.tsx   # إضافة موقع
│   │   │   │   └── settings/page.tsx
│   │   │   │
│   │   │   ├── admin/                 # Admin Panel
│   │   │   │   ├── layout.tsx
│   │   │   │   ├── page.tsx           # Admin Overview
│   │   │   │   ├── leads/
│   │   │   │   │   ├── page.tsx       # قائمة Leads
│   │   │   │   │   ├── [leadId]/page.tsx
│   │   │   │   │   └── new/page.tsx
│   │   │   │   ├── clients/
│   │   │   │   │   └── page.tsx       # Active Clients
│   │   │   │   └── audit-logs/
│   │   │   │       └── page.tsx
│   │   │   │
│   │   │   └── auth/
│   │   │       ├── login/page.tsx
│   │   │       └── logout/page.tsx
│   │   │
│   │   └── api/                       # Next.js Route Handlers (للـ BFF patterns)
│   │       └── auth/[...nextauth]/    # إذا استُخدم NextAuth
│   │
│   ├── components/
│   │   ├── ui/                        # مكونات قابلة لإعادة الاستخدام
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx              # severity badges
│   │   │   ├── ScoreGauge.tsx         # Trust/Security Score
│   │   │   ├── LoadingSpinner.tsx
│   │   │   ├── ErrorState.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   └── ProgressBar.tsx
│   │   │
│   │   ├── trust-check/               # Public Trust Check
│   │   │   ├── UrlInput.tsx
│   │   │   ├── ScanProgress.tsx
│   │   │   ├── TrustReport.tsx
│   │   │   ├── RecommendationCard.tsx  # آمن/محظور/تحذير
│   │   │   └── TrustScoreBadge.tsx
│   │   │
│   │   ├── security-report/           # Owner Security Report
│   │   │   ├── SecurityScore.tsx
│   │   │   ├── FindingCard.tsx
│   │   │   ├── FindingsList.tsx
│   │   │   ├── SeverityFilter.tsx
│   │   │   └── ComparisonView.tsx     # قبل/بعد
│   │   │
│   │   ├── dashboard/                 # Owner Dashboard
│   │   │   ├── SiteCard.tsx
│   │   │   ├── SiteStatusBadge.tsx
│   │   │   ├── VerificationSteps.tsx  # DNS TXT verification wizard
│   │   │   └── AlertBanner.tsx        # critical findings
│   │   │
│   │   ├── admin/                     # Admin Components
│   │   │   ├── LeadCard.tsx
│   │   │   ├── LeadStatusBadge.tsx
│   │   │   ├── LeadScoreBadge.tsx
│   │   │   ├── OutreachReport.tsx
│   │   │   └── AuditLogTable.tsx
│   │   │
│   │   └── layout/
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       ├── Footer.tsx
│   │       └── LanguageSwitcher.tsx
│   │
│   ├── hooks/
│   │   ├── useScanPoller.ts           # Polling لحالة الفحص
│   │   ├── useAuth.ts
│   │   └── useLocale.ts
│   │
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts              # Axios instance + interceptors
│   │   │   ├── scans.ts
│   │   │   ├── reports.ts
│   │   │   ├── sites.ts
│   │   │   ├── auth.ts
│   │   │   └── admin.ts
│   │   ├── utils/
│   │   │   ├── url.ts                 # URL formatting helpers
│   │   │   ├── scores.ts              # Score → level mapping
│   │   │   └── dates.ts               # i18n date formatting
│   │   └── constants/
│   │       ├── severity.ts            # color mappings
│   │       └── routes.ts
│   │
│   ├── messages/                      # i18n translations
│   │   ├── ar.json                    # Arabic (source of truth)
│   │   └── en.json                    # English
│   │
│   └── types/                         # TypeScript types مشتركة
│       ├── scan.ts
│       ├── report.ts
│       ├── site.ts
│       ├── lead.ts
│       └── user.ts
│
├── public/
│   ├── fonts/                         # Cairo (AR) + Inter (EN)
│   └── icons/
│
├── tailwind.config.ts
├── next.config.ts
├── middleware.ts                      # next-intl locale detection
├── tsconfig.json
├── package.json
└── Dockerfile
```

---

## Backend Structure

```
backend/
├── app/
│   ├── main.py                        # FastAPI app init، middleware، routers
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── router.py              # يجمع جميع الـ sub-routers
│   │       ├── scans.py               # POST /scans/public، GET /scans/{id}/status
│   │       ├── reports.py             # GET /reports/{id}/{type}
│   │       ├── auth.py                # login، refresh، logout
│   │       ├── sites.py               # CRUD للمواقع + verify
│   │       └── admin/
│   │           ├── __init__.py
│   │           ├── leads.py           # Lead CRUD + audit
│   │           └── audit_logs.py      # Audit log viewer
│   │
│   ├── core/
│   │   ├── config.py                  # Pydantic Settings (env vars)
│   │   ├── security.py                # JWT create/verify، password hash
│   │   ├── url_validator.py           # *** SSRF Prevention *** (Phase 3)
│   │   ├── scan_policy.py             # *** Policy Engine *** (Phase 3)
│   │   ├── rate_limiter.py            # slowapi integration
│   │   └── exceptions.py             # Custom exceptions + handlers
│   │
│   ├── models/                        # SQLAlchemy 2.x models
│   │   ├── base.py                    # Base model (id، timestamps)
│   │   ├── user.py
│   │   ├── site.py
│   │   ├── site_status_history.py
│   │   ├── authorization_record.py
│   │   ├── dns_verification_token.py
│   │   ├── scan.py
│   │   ├── scan_finding.py
│   │   ├── report.py
│   │   ├── lead.py
│   │   ├── do_not_scan.py
│   │   ├── audit_log.py
│   │   └── refresh_token.py
│   │
│   ├── schemas/                       # Pydantic v2 schemas
│   │   ├── scan.py                    # ScanCreate، ScanStatus، etc.
│   │   ├── report.py                  # TrustReport، SecurityReport، etc.
│   │   ├── site.py
│   │   ├── auth.py
│   │   ├── lead.py
│   │   └── common.py                  # Pagination، ErrorResponse، etc.
│   │
│   ├── services/
│   │   ├── scanner/
│   │   │   ├── __init__.py
│   │   │   ├── base_checker.py        # Abstract base مع timeout handling
│   │   │   ├── ssl_checker.py         # SSL/TLS + HTTPS
│   │   │   ├── headers_checker.py     # Security Headers
│   │   │   ├── dns_checker.py         # DNS + SPF + DMARC
│   │   │   └── reputation_checker.py  # Mock + Real providers (Phase 4+)
│   │   │
│   │   ├── verification/
│   │   │   └── dns_txt_verifier.py    # DNS TXT ownership verification
│   │   │
│   │   ├── risk_engine.py             # Trust/Security/Lead Score calculation
│   │   ├── report_generator.py        # JSON report generation
│   │   └── audit_logger.py            # Centralized audit logging
│   │
│   ├── workers/
│   │   ├── celery_app.py              # Celery instance + Redis config
│   │   └── scan_tasks.py              # Task definitions
│   │
│   └── db/
│       ├── base.py                    # SQLAlchemy Base + engine
│       ├── session.py                 # Async session factory
│       └── migrations/                # Alembic
│           ├── env.py
│           ├── script.py.mako
│           └── versions/
│               └── 001_initial_schema.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_url_validator.py      # أهم ملف اختبار في المشروع
│   │   ├── test_scan_policy.py
│   │   ├── test_risk_engine.py
│   │   └── test_report_generator.py
│   └── integration/
│       ├── test_public_scan_api.py
│       └── test_auth_api.py
│
├── requirements.txt
├── requirements.dev.txt               # pytest، black، mypy، etc.
├── pyproject.toml
├── alembic.ini
└── Dockerfile
```

---

## ملفات الجذر

```
website-trust-scanner/
├── docker-compose.yml

services:
  frontend:   # Next.js — port 3000
  backend:    # FastAPI — port 8000
  worker:     # Celery worker (نفس image الـ backend)
  db:         # PostgreSQL — port 5432
  redis:      # Redis — port 6379

├── .env.example                       # نموذج (لا يحتوي قيمًا حقيقية)
├── .gitignore                         # يشمل .env، __pycache__، .next، node_modules
└── README.md
```

---

## قواعد Naming Convention

| النوع | Convention | مثال |
|-------|-----------|------|
| Python files | snake_case | `url_validator.py` |
| Python classes | PascalCase | `UrlValidator` |
| Python functions | snake_case | `validate_url()` |
| TypeScript files | PascalCase (components) / camelCase (utils) | `TrustReport.tsx`, `urlHelpers.ts` |
| TypeScript types | PascalCase | `TrustReportResponse` |
| DB tables | snake_case + plural | `scan_findings` |
| DB columns | snake_case | `created_at` |
| API routes | kebab-case | `/admin/audit-logs` |
| i18n keys | dot.notation | `trust.report.safe_to_browse` |
