# Technical Design Document
## Website Trust & Security Advisor

**Version:** 1.0 — Phase 1  
**Status:** Approved for Implementation  
**Stack Decisions Locked:** 2026-06-21

---

## 1. Confirmed Technology Stack

### Frontend
| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Framework | Next.js | 14 (App Router) | SSR + SSG، App Router لتقسيم المسارات حسب الدور |
| Language | TypeScript | 5.x | Type safety إلزامي |
| Styling | Tailwind CSS | 3.x | سريع، RTL-friendly مع direction utilities |
| i18n | next-intl | 3.x | دعم RTL/LTR + locale routing أفضل من next-i18next |
| Forms | React Hook Form + Zod | latest | Validation client-side |
| HTTP Client | Axios | latest | Interceptors للـ JWT refresh |
| State | Zustand | latest | خفيف، لا يحتاج boilerplate |

### Backend
| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Framework | FastAPI | 0.115.x | Async، Pydantic v2، أسرع من Flask |
| Language | Python | 3.12 | أحدث LTS، typing محسّن |
| ORM | SQLAlchemy | 2.x (async) | Async sessions، type-safe |
| Migrations | Alembic | latest | تكامل مع SQLAlchemy |
| Validation | Pydantic | v2 | Performance محسّن بـ 5x |
| Auth | python-jose + passlib | latest | JWT + bcrypt |
| HTTP Scanner | httpx | latest | Async، يدعم timeout و redirects control |
| DNS | dnspython | latest | DNS checks موثوقة |
| SSL | ssl (stdlib) + cryptography | latest | Certificate inspection |

### Queue & Workers
| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Message Broker | Redis 7 | واحد لـ cache والـ queue |
| Task Queue | Celery 5 | أنضج حل لـ Python workers |
| Scheduler | Celery Beat | التقارير الدورية (Phase 9) |
| Rate Limiting | slowapi (FastAPI) + Redis | IP-based وAccount-based |

### Infrastructure
| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Database | PostgreSQL 16 | JSON support، transactions قوية |
| Cache | Redis 7 | Scan results cache + rate limiting |
| Container | Docker + docker-compose | تشغيل بأمر واحد في dev |
| PDF (Phase 10) | WeasyPrint | RTL support أفضل من Puppeteer |

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CLIENT LAYER                      │
│  Browser (Next.js SSR/CSR)                          │
│  ┌──────────────┐ ┌───────────────┐ ┌────────────┐ │
│  │ Public Check │ │ Owner Dashboard│ │Admin Panel │ │
│  └──────────────┘ └───────────────┘ └────────────┘ │
└────────────────────────┬────────────────────────────┘
                         │ HTTPS
┌────────────────────────▼────────────────────────────┐
│                   API LAYER (FastAPI)                │
│  ┌──────────────────────────────────────────────┐   │
│  │  URL Safety Validator → Scan Policy Engine   │   │
│  │  Rate Limiter → Auth Middleware → Router     │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  /api/v1/scans   /api/v1/auth   /api/v1/admin       │
└──────────┬──────────────────────────┬───────────────┘
           │                          │
┌──────────▼──────────┐  ┌───────────▼───────────────┐
│   PostgreSQL 16     │  │      Redis 7               │
│   (persistent data) │  │  (cache + queue + limits)  │
└─────────────────────┘  └───────────┬───────────────┘
                                     │
                          ┌──────────▼──────────┐
                          │   Celery Workers     │
                          │  (background scans) │
                          └─────────────────────┘
```

---

## 3. Request Flow — Public Trust Check

```
User inputs URL
      ↓
Frontend validates format (client-side, UX only)
      ↓
POST /api/v1/scans/public  { url: "https://example.com" }
      ↓
[1] URL Safety Validator (SSRF prevention)
    - Parse URL → reject non-http/https
    - DNS resolve → reject private IPs
    - Reject cloud metadata IPs
      ↓ (if safe)
[2] Scan Policy Engine
    - Check Do Not Scan list
    - Check rate limit (IP-based)
    - Confirm scan_type = "public_trust" is allowed without auth
      ↓ (if allowed)
[3] Create Scan record in DB (status: queued, id: UUID v4)
    Return: { scan_id: UUID, status: "queued" }
      ↓
[4] Celery Worker picks up task
    Runs: SSL + HTTPS + Headers + Reputation (mock) + DNS
    Each checker runs with timeout=8s
      ↓
[5] Risk Engine calculates Trust Score
      ↓
[6] Scan record updated (status: completed, results: JSON)
      ↓
Frontend polls GET /api/v1/scans/{scan_id}/status
      ↓
GET /api/v1/reports/{scan_id}/trust → Trust Report JSON
      ↓
Frontend renders Trust Report (no sensitive details)
```

---

## 4. Async Scan Pattern

كل فحص يسير بهذا النمط — لا blocking HTTP requests في API thread:

```
POST /api/v1/scans/*
  → validate → create DB record (status=queued) → enqueue task → return scan_id

GET /api/v1/scans/{id}/status
  → return current status: queued | running | completed | failed

GET /api/v1/reports/{id}/{type}
  → return report only if status=completed
  → 404 if not found, 202 if still running
```

---

## 5. i18n & RTL/LTR Strategy

### Routing
```
/           → redirect to /ar أو /en (browser detection)
/ar/        → Public Check (Arabic, RTL)
/en/        → Public Check (English, LTR)
/ar/dashboard/  → Owner Dashboard
/en/admin/      → Admin Panel
```

### Implementation
- `next-intl` مع `middleware.ts` للـ locale detection
- جميع النصوص في `messages/ar.json` و `messages/en.json`
- CSS: `dir="rtl"` على `<html>` حسب الـ locale
- Tailwind: استخدام `rtl:` و `ltr:` prefixes
- تاريخ وأرقام: `Intl.DateTimeFormat` و `Intl.NumberFormat` مع locale

### قاعدة:
- لا hard-coded نصوص عربية أو إنجليزية في الكود
- كل نص له مفتاح في ملفات الترجمة
- PDF: WeasyPrint يدعم `direction: rtl` في CSS

---

## 6. Security Architecture Summary

### Layers of Defense (Defense in Depth)

```
Layer 1: Frontend
  - Client-side URL format validation (UX only, NOT security)
  - Rate limit feedback messages
  - No sensitive data displayed

Layer 2: API Gateway (FastAPI Middleware)
  - HTTPS enforced (Nginx/Caddy in production)
  - CORS restricted to known origins
  - Security headers on all responses
  - Request size limits

Layer 3: URL Safety Validator (Phase 3)
  - Scheme whitelist (http/https only)
  - DNS resolution → IP blocklist check
  - Redirect following with re-validation
  - Timeout enforcement

Layer 4: Scan Policy Engine (Phase 3)
  - Do Not Scan list lookup
  - Rate limit enforcement
  - Auth + Role check
  - Site status check
  - Authorization Record validation

Layer 5: Workers
  - Isolated execution
  - Per-checker timeouts (8s default)
  - Response size limits (2MB)
  - No JavaScript execution in scanning

Layer 6: Database
  - Parameterized queries (SQLAlchemy ORM)
  - Encrypted sensitive fields (API keys)
  - UUID primary keys for all public-facing IDs
  - Audit log append-only

Layer 7: Output
  - Report templates are pre-defined (no raw data injection)
  - Trust Report filters out exploitable details
  - PDF sanitization before generation
```

---

## 7. Environment Variables Design

```bash
# Application
APP_ENV=development|production
APP_SECRET_KEY=<random-64-chars>
APP_ALLOWED_ORIGINS=http://localhost:3000

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/trustscanner

# Redis
REDIS_URL=redis://redis:6379/0

# Auth
JWT_SECRET_KEY=<random-64-chars>
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Scan Settings
SCAN_TIMEOUT_SECONDS=8
SCAN_MAX_REDIRECTS=5
SCAN_MAX_RESPONSE_SIZE_MB=2

# Rate Limiting
RATE_LIMIT_GUEST_PER_HOUR=3
RATE_LIMIT_FREE_USER_PER_DAY=10

# Reputation (Phase 4 - Mock in MVP)
REPUTATION_PROVIDER=mock  # → google_safe_browsing | virustotal | urlhaus
GOOGLE_SAFE_BROWSING_API_KEY=  # empty in MVP
VIRUSTOTAL_API_KEY=             # empty in MVP

# Email (Phase 9)
EMAIL_PROVIDER=none  # → resend | sendgrid | smtp
EMAIL_FROM=noreply@example.com

# Admin
SUPER_ADMIN_EMAIL=admin@example.com
SUPER_ADMIN_PASSWORD=<set-on-first-run>
```

**قاعدة:** لا يُقرأ أي من هذه القيم من الكود مباشرة — كلها عبر `core/config.py` (Pydantic Settings).
