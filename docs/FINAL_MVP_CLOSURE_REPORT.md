# Final MVP Closure Report

**Date:** 2026-06-26  
**Branch base:** `main` @ `0422254`  
**Status:** ✅ MVP Complete — ready for supervised beta trial

---

## 1. What Was Built

This platform provides a bilingual (Arabic / English) website security and trust advisory service. It has three distinct user paths, all implemented and closed for the MVP.

### 1.1 Visitor (Public) Path — Complete

Any visitor can:
- Enter a URL and receive an instant Trust Score (0–100)
- See a Usage Decision across four dimensions: browsing, account creation, payment, personal data
- Each dimension has a three-state verdict: Suitable / Caution / Not Recommended
- All data comes from surface-level indicator checks only (see Security Boundaries below)
- A clear disclaimer is displayed on both the scan form and the results page
- No registration required

### 1.2 Site Owner Path — Complete

A registered and verified site owner can:
- Register their site and verify DNS ownership via TXT record
- Trigger a scan of their own verified site
- View the Trust Score and a Fix Plan with prioritized issues
- Copy fix instructions formatted for a developer
- Review scan history
- Navigate the full flow in Arabic or English

### 1.3 Admin (Founder) Path — Complete (Read-Only MVP)

An admin user can:
- View a summary dashboard with platform-wide counts (users, sites, verified sites, scans)
- View risk distribution across all scanned sites
- View 30-day scan trends
- View recent audit log entries (no IP addresses exposed)
- Browse the leads list
- View individual lead details including score, status, and notes
- A notice banner on every admin page clarifies the read-only scope

**What admin cannot do (intentional MVP scope limit):**
- Trigger any scan
- Modify lead status
- Export any data
- Access raw scan data or HTTP responses

---

## 2. Security Architecture

Every external network request in the system must pass through the following pipeline, in order:

```
1. Do Not Scan check          ← before any DNS resolution or network call
2. SSRF protection            ← blocks private/loopback/link-local/reserved ranges
3. URL validation             ← normalize, sanitize, reject unsafe schemes
4. Scan Policy                ← enforces allowed check types and scan depth
5. Safe HTTP Client           ← enforces timeouts, size limits, redirect limits
6. Safe Scan Runner           ← orchestrates the above; the only entry point for scans
```

**Public Trust Check**, **Owner Scan**, and **Admin Lead Audit** all route through Safe Scan Runner. No scan path bypasses this pipeline.

### What Is Never Exposed

- Raw HTTP response bodies
- HTTP response headers (only presence/absence of security headers)
- IP addresses (resolved or otherwise)
- Secrets, tokens, or credentials
- Exploitable technical details
- Port scan results
- Crawled content
- Exposed-file enumeration results

---

## 3. What Checks Are Performed

All scans are limited to the following surface-level indicators:

| Check | Method | Notes |
|---|---|---|
| HTTPS | URL scheme + TLS handshake | Pass/fail only |
| SSL validity | Certificate verification | Pass/fail + expiry warning |
| Security headers | Header presence check | Score: N of M headers present |
| Domain reputation | Lookup in reputation list | Clean / Flagged / Unknown |

No port scanning, crawling, exploitation, or deep probing of any kind is performed at any point.

---

## 4. All Routes (Frontend)

| Route | Auth Required | Notes |
|---|---|---|
| `/[locale]` | No | Public scan form |
| `/[locale]/login` | No | Cookie-based JWT auth |
| `/[locale]/register` | No | EmailStr validation |
| `/[locale]/roadmap` | No | Static product roadmap |
| `/[locale]/sites` | Owner | Sites list |
| `/[locale]/sites/[id]/scans` | Owner | Scan history |
| `/[locale]/sites/[id]/scans/[scanId]` | Owner | Scan detail + Fix Plan |
| `/[locale]/admin` | Admin | Dashboard + stats |
| `/[locale]/admin/leads` | Admin | Leads list |
| `/[locale]/admin/leads/[id]` | Admin | Lead detail |
| `/[locale]/admin/analytics` | Admin | Analytics dashboard |

All protected routes redirect to `/[locale]/login` for unauthenticated users. Admin routes additionally check for `admin` or `super_admin` role.

---

## 5. Known Non-Blocking Warnings

| Warning | Impact |
|---|---|
| Next.js `middleware` convention deprecated (use `proxy`) | None — rename is non-urgent |
| `passlib` + `bcrypt 4.x` version mismatch warning | None — auth works correctly |
| `pytest-asyncio` deprecation warnings | None — tests pass |

---

## 6. Pre-Launch Blockers (Not Addressed in MVP)

These must be resolved before any public production launch:

- [ ] **CVE GHSA-36qx-fr4f-26g5** — Next.js i18n middleware bypass; upgrade Next.js or apply documented mitigation before public access
- [ ] **Production secrets management** — `.env` files must not be used in production; use a secrets manager
- [ ] **HTTPS termination** — production deployment must enforce HTTPS at the edge
- [ ] **Per-domain rate limiting** — current rate limiting is per user; per-domain limit is noted as TODO in `safe_scan_runner.py`
- [ ] **Full security review / penetration test** — required before any public-facing deployment

---

## 7. Deferred Features (Post-MVP)

These features were scoped out and must not be started without explicit approval:

| Feature | Reason |
|---|---|
| PDF / report export | Post-MVP |
| Before/After score comparison | Post-MVP |
| Scheduled periodic re-scans | Post-MVP |
| Admin: trigger scan from UI | Requires explicit authorization flow first |
| Admin: update lead status | Post-MVP |
| Admin: export leads/data | Post-MVP |
| Admin: deep scan after authorization | Requires Authorization Record design first |
| Convert Lead to Owner subscription | Post-MVP |

---

## 8. MVP Trial Readiness

The following was verified prior to this closure report:

- [x] Backend starts cleanly from `requirements.txt`
- [x] Frontend builds without TypeScript errors (`npm run build`)
- [x] Database migrations run cleanly (`alembic upgrade head`)
- [x] Full Owner flow works end-to-end (sites → scans → scan detail → Fix Plan)
- [x] Full Admin flow works end-to-end (dashboard → analytics → leads → lead detail)
- [x] Public scan flow works (URL input → Trust Score → Usage Decision → disclaimer)
- [x] Both Arabic and English locales render correctly
- [x] Auth redirects work for all protected routes
- [x] No raw technical data exposed in UI or API responses
- [x] All scans pass through Safe Scan Runner

**Approved for supervised beta trial with known participants. Not approved for public launch.**

---

## 9. Open PRs at Closure

| PR | Title | Status |
|---|---|---|
| #42 | docs: add Limited MVP Trial Plan | Draft — docs only, CI green |
| #43 | feat(admin): analytics dashboard, summary stats, lead disclaimer | Draft — CI green |
