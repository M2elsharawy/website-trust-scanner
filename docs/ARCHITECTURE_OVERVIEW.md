# Architecture Overview
## Website Trust & Security Advisor

**Last updated:** 2026-06-29  
**Audience:** New team members, founder, technical reviewers  
**Level:** System-level — no implementation detail

---

## What This Product Does

The Website Trust & Security Advisor helps three types of users:

- **Visitors** assess the trustworthiness of any website before interacting with it
- **Site owners** understand what public-facing signals affect how visitors perceive their site, and get actionable instructions to improve them
- **The admin (founder)** monitors the platform, views leads, and tracks scan activity

It is a **Trust Advisor**, not a security scanner. The distinction is deliberate and permanent:
- It surfaces what a visitor can observe about a site (HTTPS, certificate validity, security headers, DNS hygiene, domain reputation)
- It does not perform penetration testing, port scanning, content crawling, active exploitation, or any form of offensive reconnaissance
- Results are advisory indicators, not security certifications

---

## System Topology

```
                    ┌─────────────────────────────────┐
                    │         Load Balancer / TLS       │
                    │    (nginx / Caddy / cloud LB)     │
                    └────────────┬────────────────────-─┘
                                 │ HTTPS only
              ┌──────────────────┼──────────────────────┐
              │                  │                       │
     ┌────────▼──────┐  ┌────────▼──────┐       ┌──────▼──────┐
     │  Next.js 16   │  │   FastAPI     │       │  Celery     │
     │  Frontend     │  │   Backend     │       │  Worker +   │
     │  :3000        │  │   :8000       │       │  Beat       │
     └───────────────┘  └──────┬───────┘       └──────┬──────┘
                                │                       │
                       ┌────────┴────────┐    ┌────────┴────────┐
                       │  PostgreSQL     │    │     Redis        │
                       │  (persistence)  │    │  (rate limits,  │
                       └─────────────────┘    │   Celery broker)│
                                              └─────────────────┘
```

All external HTTP requests from the backend pass through the Safe Scan Runner pipeline before reaching the internet.

---

## The Three User Paths

### Visitor Path

```
User enters a URL
      │
      ▼
ScanForm (frontend) → POST /api/v1/public-trust-check
      │
      ▼
Safe Scan Runner (10-step pipeline)
      │
      ▼
Trust Score + Checks Summary + Usage Decision
      │
      ▼
TrustResult component renders:
  • Trust Score ring (0–100)
  • Trust level: Low / Medium / Good / High
  • Usage Decision: Avoid / Proceed with Caution / Safe to Use
  • Danger banner (if score < 40)
```

No authentication required. Subject to guest rate limit (10 scans/hour per IP).

### Owner Path

```
Register → Login (JWT access token + httpOnly refresh token)
      │
      ▼
Add site → DNS TXT verification (proves domain ownership)
      │
      ▼
Request scan → POST /sites/{id}/scans
      │
      ▼
Safe Scan Runner (owner scan variant — same pipeline)
      │
      ▼
ScanResult stored in database (sanitized — no raw headers or IPs)
      │
      ▼
Fix Plan rendered — 6 check categories:
  • HTTPS / SSL
  • Security headers
  • DNS hygiene (SPF, DMARC)
  • Domain reputation
  • Trust signals
  • Recommendations
      │
      ▼
Owner copies developer instructions or downloads PDF report (bilingual)
```

Requires authentication. Subject to user rate limit (60 scans/hour) and domain rate limit (5/hour per domain).

### Admin Path

```
Admin login → JWT with role=admin/super_admin  OR  X-Admin-Key header
      │
      ▼
Leads list → Lead detail (read-only)
Analytics dashboard:
  • Summary statistics
  • 30-day scan trend chart
  • Audit log (action / outcome / role / scan type / timestamp)
```

Admin UI is read-only. No scan trigger, no status mutation, no bulk operations in the current release.

---

## The Safe Scan Runner

Every outbound scan request — visitor, owner, or any future trigger — must pass through the Safe Scan Runner. It is a mandatory 10-step pipeline:

```
Step 1:  Do Not Scan check      — blocklist checked before any DNS resolution
Step 2:  SSRF protection        — 16 blocked network ranges (RFC1918, loopback, link-local, etc.)
Step 3:  URL validation         — scheme, host, path constraints
Step 4:  DNS resolution         — hostname resolved; resulting IP re-checked against blocked ranges
Step 5:  Scan Policy check      — forbidden scan types rejected (port scan, crawl, exploit, etc.)
Step 6:  Rate limit check       — per-IP, per-user, per-domain limits enforced
Step 7:  Audit log (pre-scan)   — action and intent recorded before any outbound request
Step 8:  Passive scanners       — SSL, HTTPS, headers, DNS, reputation run in parallel
Step 9:  Audit log (post-scan)  — outcome, score, scan type recorded
Step 10: Return sanitized result — raw headers, IPs, server names stripped before response
```

The pipeline cannot be bypassed. There is no code path that allows an outbound scan request to skip any step.

---

## Trust Score

The Trust Score (0–100) is computed from passive public-facing checks:

| Category | What is checked |
|---|---|
| HTTPS | Is HTTPS active? Does HTTP redirect to HTTPS? |
| SSL certificate | Is the certificate valid? Is it expired? Who issued it? |
| Security headers | X-Frame-Options, X-Content-Type-Options, Referrer-Policy, HSTS |
| DNS configuration | SPF record present and valid? DMARC record present? |
| Domain reputation | Is the domain flagged by reputation providers? |

Score thresholds:
- **0–39:** Low — Danger banner shown to visitor
- **40–59:** Medium — Proceed with caution
- **60–79:** Good — Generally trustworthy signals
- **80–100:** High — Strong public-facing trust signals

The score reflects public-facing signals only. A high score does not certify internal security.

---

## Security Controls Summary

| Control | Where | What it does |
|---|---|---|
| SSRF protection | `url_validator.py` | Blocks requests to RFC1918, loopback, link-local, metadata endpoints |
| Do Not Scan gate | `safe_scan_runner.py` | Checks domain against blocklist before DNS resolution |
| Scan Policy | `scan_policy.py` | Permanently forbidden: port scan, crawl, exploit, brute force, raw header exposure |
| Per-domain rate limit | `safe_scan_runner.py` + Redis | Max 5 scans/hour per domain |
| Per-IP rate limit | `rate_limiter.py` | Max 10 scans/hour for guests |
| Per-user rate limit | `rate_limiter.py` | Max 60 scans/hour for authenticated users |
| JWT authentication | `security.py` | Access tokens (15 min), refresh tokens (7 days, SHA-256 stored) |
| Refresh token rotation | `security.py` | Token rotated on every use, old token invalidated |
| Account lockout | `security.py` | 5 failed logins → 15-minute lockout |
| Owner isolation | ORM queries | Every site and scan query filters by `owner_id` |
| Admin dual-path auth | `deps.py` + `admin/auth.py` | JWT role check OR constant-time X-Admin-Key compare |
| Data minimization | `trust_score.py` | Raw headers, IPs, response bodies stripped before storage |
| Audit logging | `audit_logger.py` | Every scan step logged: action, outcome, role, scan type, timestamp |
| Security headers | `main.py` middleware | X-Content-Type-Options, X-Frame-Options, Referrer-Policy on all responses |
| CSRF protection | `main.py` | SameSite=Lax cookies + production Origin check |

---

## Bilingual Architecture

The product is bilingual (Arabic/English) from the database layer to the UI:

- **Frontend routing:** `next-intl` v4 with locale prefix (`/ar/...`, `/en/...`), defaultLocale=`ar`
- **RTL layout:** `dir` attribute set from locale in root layout; Tailwind RTL utilities used throughout
- **Translations:** 256 keys in `ar.json` and `en.json` — must stay in sync
- **PDF reports:** Generated bilingually (both languages in one PDF)
- **Backend messages:** Error messages and outreach templates exist in both languages

---

## What Is Not In This Product

These capabilities are permanently excluded by product philosophy and enforced in `scan_policy.py`:

- Port scanning
- Vulnerability scanning or CVE detection
- Content crawling or file enumeration
- Active exploitation or payload injection
- Brute-force testing
- Raw HTTP header/response exposure
- Bulk scanning of third-party domains
- Any capability that could be used offensively against a target the user does not own
