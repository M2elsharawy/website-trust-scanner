# Website Trust & Security Advisor
## مساعد الثقة والأمان للمواقع الإلكترونية

A bilingual (Arabic/English) web application that helps visitors assess the trustworthiness of websites, helps site owners identify and fix public-facing trust signals, and gives founders an admin view for operational oversight.

**Current status:** Supervised Beta — invitation-only trial, 8–13 known users  
**Last main SHA:** `6366a08`  
**Engineering phase:** Complete

---

## Quick Start (Local Development)

```bash
cp .env.example .env          # fill in real values — see docs/LOCAL_SETUP.md
docker compose up -d
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000/docs
```

---

## Product Overview

Three user paths, one codebase:

| Path | Who | What they do |
|---|---|---|
| Visitor | Anyone | Enter a URL → get a Trust Score and Usage Decision |
| Owner | Registered, DNS-verified | Register a site → scan → view Fix Plan → export PDF report |
| Admin | Founder (JWT role + API key) | View leads, analytics dashboard, audit log |

This is a **Trust Advisor**, not a security scanner. It surfaces public-facing signals only — HTTPS, SSL, security headers, DNS configuration, reputation. It does not perform penetration testing, port scanning, content crawling, or any form of offensive reconnaissance. These constraints are permanent and enforced in code.

---

## Repository Navigation

| Document | Purpose |
|---|---|
| [docs/INDEX.md](docs/INDEX.md) | Full index of all 42 documentation files |
| [docs/REPOSITORY_MAP.md](docs/REPOSITORY_MAP.md) | Current file and folder map (what is where and why) |
| [docs/ARCHITECTURE_OVERVIEW.md](docs/ARCHITECTURE_OVERVIEW.md) | System architecture without implementation detail |
| [docs/ENGINEERING_NOTES.md](docs/ENGINEERING_NOTES.md) | Why decisions were made — what not to change |
| [docs/FUTURE_ENGINEERING_NOTES.md](docs/FUTURE_ENGINEERING_NOTES.md) | What a returning team needs to know first |
| [docs/LOCAL_SETUP.md](docs/LOCAL_SETUP.md) | Developer environment setup |
| [docs/ENGINEERING_HANDOVER.md](docs/ENGINEERING_HANDOVER.md) | Handover document for operational phase |

---

## Development Principles

- No offensive capabilities. No port scanning. No crawling. No active exploitation.
- Every outbound request passes through the Safe Scan Runner 10-step pipeline — mandatory.
- SSRF protection is unconditional — 16 blocked network ranges, redirect re-validation.
- Bilingual (Arabic + English) from day one. RTL layout is a first-class concern.
- No new dependencies without explicit approval.
- No backend changes without explicit scope definition.
- No schema changes without a migration plan review.

---

## Release History

| Release | Goal | Status |
|---|---|---|
| MVP | Three-path product: Visitor, Owner, Admin | ✅ Done |
| 1.0.1 | Production Hardening: SSRF, rate limiting, auth, audit logging | ✅ Done |
| 1.1 | Design & UX Refresh: Cairo font, RTL, danger banner, advisor tone | ✅ Done |
| 1.2 | Beta Preparation: Owner UX, i18n keys, docs | ✅ Code complete — PR #53 open |
| Pre-Launch | Comprehensive review, launch gate, beta operating cycle | ✅ Done |
| 2.0 | Feature expansion based on Beta findings | Planned — post Day 18 |

---

## Beta Trial

The product is in an invitation-only supervised beta (18-day cycle).

- **Code freeze:** No changes during Days 1–17 except P0/P1 emergency patches.
- **Operating guide:** `docs/BETA_FOUNDER_PLAYBOOK.md`
- **Issue tracking:** `docs/ISSUE_CLASSIFICATION_GUIDE.md` + `docs/BETA_PRIORITIZATION_FRAMEWORK.md`
- **Post-trial workflow:** `docs/POST_BETA_RELEASE_WORKFLOW.md`
