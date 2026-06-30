# Final MVP Closure Report

**Date:** 2026-06-28  
**Last main SHA:** `a8549cc`  
**Merged PRs this sprint:** #43 (admin analytics), #45 (UX polish + open redirect fix)  
**Prepared by:** Internal engineering team

> **Amendment (2026-06-29):** Per-domain rate limiting, identified as a blocker in this report, was implemented in Release 1.0.1 via `_enforce_domain_rate_limit()` in `safe_scan_runner.py`. References to it as a TODO or missing control below are historical — the control is now active.

---

## Product Guardrails

This project is a **Trust Advisor**, not a scanner. The following constraints are permanent and apply to every scan, feature, and API endpoint.

- **Advisory only.** Results are surface-level indicators (HTTPS, SSL certificate validity, security headers, domain reputation). The tool does not guarantee that a website is safe, and outputs must not be treated as a security certification.
- **Not a replacement for professional testing.** This tool does not perform penetration testing, vulnerability assessment, or any form of intrusive analysis. A professional penetration test is required before drawing security conclusions about a target.
- **No offensive tools in Admin.** The Admin interface has no scan trigger, no bulk scan, no attack-simulation capability, and no features that can be used offensively against third-party domains.
- **Deep scan requires ownership proof + authorization.** Any scan beyond surface indicators requires verified site ownership (DNS TXT record) and an explicit authorization record before activation. No deep scan may be triggered without both.
- **Pipeline is mandatory for every outbound request.** Regardless of trigger source, every scan must traverse in order: Do Not Scan check (before any DNS resolution) → SSRF protection → URL validation → Scan Policy → Safe HTTP Client. Safe Scan Runner orchestrates this pipeline and must not be bypassed.

---

## 1. Visitor (Public) Path — Status

**Complete.**

A visitor can enter any URL, receive a Trust Score (0–100), and see a Usage Decision across four categories:

| Category | Verdict states |
|---|---|
| Browsing | Suitable / Use Caution / Not Recommended |
| Create Account | Suitable / Use Caution / Not Recommended |
| Payment | Suitable / Use Caution / Not Recommended |
| Personal Data | Suitable / Use Caution / Not Recommended |

Security indicators checked: HTTPS presence, SSL validity, SSL expiry, security headers score, domain reputation. No penetration testing, no crawling, no port scanning. All outbound requests pass through the 10-step Safe Scan Runner pipeline (Do Not Scan → SSRF → URL validation → Scan Policy → Safe HTTP Client).

No raw technical data (headers, IPs, response bodies, secrets) is exposed in the UI or API at any point.

---

## 2. Site Owner Path — Status

**MVP Feature Complete.**

Verified end-to-end flow:

1. Register an account (email + password, `preferred_lang`)
2. Add a site (domain registration)
3. Verify ownership via DNS TXT record
4. Trigger a scan (passes through Safe Scan Runner)
5. View scan history (trust score + timestamp per scan)
6. View scan detail (score card + FixPlan)
7. Copy Fix Plan instructions for a developer (one button, formatted text)
8. Re-scan to track improvement

Locale-aware navigation (Arabic / English) works throughout. Unauthenticated requests redirect to `/[locale]/login?next=[path]`. The `?next=` parameter is validated — only internal paths starting with `/` and not `//` are accepted (open redirect fix merged in PR #45).

Pending verification hint shown for unverified sites. Back-navigation and disclaimer text present on scan detail page.

---

## 3. Founder / Admin Path — Status

**Read-only MVP Feature Complete.**

| Capability | Status |
|---|---|
| View leads list (domain, status, score, dates) | ✅ |
| View lead detail (all fields + surface disclaimer) | ✅ |
| Analytics dashboard (summary stats + 30-day scan trend + audit log) | ✅ |
| Read-only notice banner in both languages | ✅ |
| Role gate (`admin` / `super_admin` only, checked via `/auth/me`) | ✅ |
| Scan trigger from admin UI | ❌ Intentionally absent |
| Status mutation from admin UI | ❌ Intentionally absent |
| Export / bulk actions from admin UI | ❌ Intentionally absent |

The audit log displays: action, outcome, actor_role, resource_type, timestamp. Actor IP addresses and owner IDs are **not** displayed in the UI, even if present in backend records.

---

## 4. What Was Accomplished

| PR | Deliverable |
|---|---|
| #18 | Public Trust Check → Safe Scan Runner migration |
| #19 | Product Roadmap page (EN + AR) |
| #20 | Owner Scan → Safe Scan Runner migration |
| #21 | Usage Decision UX (4-card, 3-verdict visitor result) |
| #22–#33 | Owner Fix Plan + CopyButton (multiple iterations) |
| #35 | Admin Lead Audit → Safe Scan Runner migration |
| #36 | Admin UI scope documentation |
| #37 | Admin route protection + shell layout |
| #38 | Admin Leads list (read-only) |
| #39 | Admin Lead Detail (read-only) |
| #40 | Admin MVP Closure Pass |
| #41 | Owner locale navigation fix + docs polish |
| #43 | Admin analytics dashboard (summary, scan trends, audit log) |
| #45 | UX polish: LogoutButton, FixPlan client directive, TrustResult personal_data fix, score explanation, password show/hide, back-navigation, disclaimer, open redirect fix in `?next=` |

---

## 5. What Is Intentionally Forbidden (Security Constraints)

The following are permanently prohibited unless the scope is explicitly expanded with a documented decision:

**Scanner scope:**
- Port scanning
- Crawling / spider-style enumeration
- Exposed-files scanning (`.env`, `wp-admin`, `/.git`, etc.)
- Intrusive testing or vulnerability probing of any kind
- Exploitation or proof-of-concept execution

**Data exposure:**
- Raw HTTP headers exposed in UI or API responses
- IP addresses exposed in UI or API responses
- Raw HTTP response bodies stored or displayed
- Secrets, tokens, or sensitive values in logs, results, or API responses
- Actor IP addresses in admin UI
- Owner IDs in admin UI
- `resource_id` in audit log table

**Admin capabilities:**
- Scan trigger from admin UI without owner authorization record
- Bulk scan / scan-all
- Status mutation from admin UI (in current MVP)
- Data export or PDF generation
- Any feature that makes the tool offensive

**Pipeline bypass:**
- Do Not Scan must be checked before any DNS resolution or network call
- Every outbound scan must traverse all 10 Safe Scan Runner steps in order

---

## 6. What Is Deferred (Post-MVP)

| Feature | Reason |
|---|---|
| Before/After score comparison view | Next milestone — needs scan history schema extension |
| Periodic / scheduled scan reports | Post-MVP — requires background job infrastructure |
| Export developer task (ticket format) | Post-MVP |
| Admin lead → owner / subscription workflow | Post-MVP — requires status mutation UI |
| Admin status management UI | Post-MVP — requires authorization record first |
| Authorization record before deep scan | Required before any admin-triggered deep scan |
| Dashboard (custom analytics views) | Post-MVP |
| PDF report generation | Post-MVP |
| Per-domain rate limiting | TODO noted in `safe_scan_runner.py` — pre-launch blocker |
| Next.js CVE GHSA-36qx-fr4f-26g5 mitigation | Pre-public-launch blocker (see §9) |
| External Reputation Provider integration | Current implementation uses a mock/stub reputation check. A real provider (e.g. Google Safe Browsing, VirusTotal, or equivalent) must be integrated before production use. |

---

## 7. Is the Project Ready for Supervised Limited Trial?

**Yes — ready for supervised limited trial.**

All three user paths (visitor, owner, admin) work end-to-end. The security pipeline is complete. No raw data is exposed. Locale support (Arabic, English) is verified.

Conditions for a limited trial:
- [ ] Deploy behind HTTPS with a real SSL certificate
- [ ] Configure environment variables (`SECRET_KEY`, `DATABASE_URL`, `BACKEND_URL`, `NEXT_PUBLIC_API_URL`) — do not use defaults
- [ ] Run `alembic upgrade head` on a clean production database
- [ ] Verify `CORS_ORIGINS` is set to the production frontend domain only
- [ ] Confirm cookie settings (`httponly`, `samesite=lax`, `secure=true`) are enforced in production
- [ ] Invite a small number of known users — do not list publicly

---

## 8. Is the Project Ready for Public Launch?

**No. Conditions that must be met first:**

| Condition | Blocker level |
|---|---|
| CVE GHSA-36qx-fr4f-26g5 (Next.js i18n middleware bypass < 15.2.3) — upgrade or apply mitigation | **Hard blocker** |
| Per-domain rate limiting (not just per-user) | **Hard blocker** — without it, the scanner can be abused to probe third-party domains at scale |
| Production secrets management (no `.env` defaults in prod) | **Hard blocker** |
| HTTPS termination with valid certificate at the load balancer | **Hard blocker** |
| Independent security review or penetration test of the running application | **Strong recommendation** |
| Monitoring and alerting (uptime, error rates, scan volume anomalies) | Required before sustained public traffic |
| Terms of Service and Privacy Policy linked from the UI | Required before public registration |
| Data retention policy enforced in production (see `DATA_RETENTION_POLICY.md`) | Required before public registration |

---

## 9. Remaining Risks

| Risk | Severity | Notes |
|---|---|---|
| CVE GHSA-36qx-fr4f-26g5: Next.js i18n middleware can be bypassed | High | Blocks public launch. Upgrade to Next.js ≥ 15.2.3 or apply vendor mitigation. |
| Per-domain rate limiting missing | High | A logged-in user can scan the same third-party domain repeatedly. Noted as TODO in `safe_scan_runner.py`. |
| `passlib` + `bcrypt 4.x` version mismatch warning | Low | Authentication works. Logs a warning. Non-blocking but should be resolved. |
| `middleware` file convention deprecated (Next.js 16) | Low | Rename `middleware.ts` → `proxy.ts`. Non-breaking. |
| `pytest-asyncio` deprecation warnings | Low | Tests pass. Update is non-urgent. |
| Admin deep scan has no authorization record gate in UI | Medium | The UI has no deep scan trigger at all (safe), but the backend must enforce the authorization check before any future UI exposes this. |
| SSRF protection covers known private ranges; cloud metadata variants may evolve | Low | `url_validator.py` covers `169.254.169.254` and all RFC-1918 ranges. Review when deploying to new cloud providers. |

---

## 10. Manual QA Checklist (Pre-Trial)

Run this checklist in the staging environment before inviting any trial users.

### Visitor Flow
- [ ] Enter a valid HTTPS URL → receives Trust Score and Usage Decision
- [ ] Enter an HTTP-only URL → score reflects no HTTPS
- [ ] Enter an invalid URL → shows `errors.invalid_url`
- [ ] Enter a loopback URL (e.g., `http://localhost`) → blocked with `errors.ssrf_blocked`
- [ ] Enter a private IP URL → blocked with `errors.ssrf_blocked`
- [ ] Enter `http://169.254.169.254` → blocked
- [ ] Scan a flagged domain → reputation shows Flagged
- [ ] Slow/unavailable domain → shows `errors.timeout`
- [ ] Switch language (AR ↔ EN) → all text changes, RTL layout applies for Arabic
- [ ] No IP address, raw header, or raw body visible in browser DevTools network tab for scan response

### Auth Flow
- [ ] Register with valid email + password → redirected to `/[locale]/sites`
- [ ] Register with duplicate email → shows `auth.errors.email_taken`
- [ ] Log in with correct credentials → redirected to `/[locale]/sites`
- [ ] Log in with wrong password → shows `auth.errors.invalid_credentials`
- [ ] Log in with `?next=/sites/123/scans` → redirected to `/sites/123/scans` after login
- [ ] Log in with `?next=//evil.com` → redirected to `/[locale]/sites` (open redirect blocked)
- [ ] Log in with `?next=https://evil.com` → redirected to `/[locale]/sites` (open redirect blocked)
- [ ] Logout button → cookie cleared, redirected to `/[locale]/login`
- [ ] Locale preserved in logout redirect (Arabic login → Arabic login page)

### Owner Flow
- [ ] Unauthenticated access to `/sites` → redirect to `/[locale]/login?next=/[locale]/sites`
- [ ] Sites list shows all registered sites with correct status badges
- [ ] Pending site shows DNS TXT hint
- [ ] View Scans link → shows scan history list
- [ ] Empty scan history → shows `owner_scans_list.empty`
- [ ] Click scan → shows score card, disclaimer, FixPlan
- [ ] Back navigation (← Back to scan history) works correctly
- [ ] FixPlan shows issues with Why / How / Copy for developer
- [ ] Copy for developer button shows "Copied!" confirmation
- [ ] No raw headers, IPs, or response bodies in Fix Plan text

### Admin Flow
- [ ] Non-admin user cannot access `/admin` → redirect or 403
- [ ] Admin sees read-only notice banner
- [ ] Leads list loads with correct columns
- [ ] Lead detail shows surface-level disclaimer
- [ ] Analytics dashboard loads summary stats
- [ ] Audit log shows action, outcome, actor_role, resource_type, timestamp
- [ ] Audit log does NOT show actor_ip or owner_id
- [ ] No scan trigger button anywhere in admin UI

---

## 11. Production Readiness Checklist

### Infrastructure
- [ ] HTTPS with valid certificate (not self-signed)
- [ ] `SECRET_KEY` set to a 32+ byte random value (not the dev default)
- [ ] `DATABASE_URL` points to a managed production database
- [ ] `CORS_ORIGINS` restricted to the production frontend domain
- [ ] `NEXT_PUBLIC_API_URL` set to the production backend URL
- [ ] Cookie flags: `httponly=True`, `samesite=lax`, `secure=True`
- [ ] `DEBUG=False` in all production processes
- [ ] Log level set appropriately (no DEBUG logs in production)

### Security
- [ ] Next.js CVE GHSA-36qx-fr4f-26g5 mitigated (upgrade or patch)
- [ ] Per-domain rate limiting implemented before public launch
- [ ] `alembic upgrade head` run on clean production DB
- [ ] No `.env` defaults active in production
- [ ] SSRF bypass test: `curl -X POST /api/v1/public-trust-check -d '{"url":"http://169.254.169.254"}'` → blocked
- [ ] Do Not Scan list seeded (internal domains, admin endpoints)

### Operational
- [ ] Uptime monitoring configured
- [ ] Error alerting configured (5xx spike, scan failure spike)
- [ ] Database backups scheduled and tested
- [ ] Log retention policy applied
- [ ] Terms of Service page linked from registration
- [ ] Privacy Policy page linked from registration

### Pre-Launch Sign-Off
- [ ] Manual QA checklist above completed in staging
- [ ] Security review (internal or external) completed
- [ ] Data retention policy (`DATA_RETENTION_POLICY.md`) enforced
- [ ] Scan volume anomaly detection in place

---

## 12. Summary Answer to Governing Questions

| Question | Answer |
|---|---|
| **Visitor path complete?** | Yes — Trust Score, Usage Decision (4 cards × 3 verdicts), no sensitive data exposed |
| **Owner path complete?** | MVP Feature Complete — registration, DNS verification, scan, history, Fix Plan, copy-for-developer, re-scan |
| **Admin path complete?** | Read-only MVP Feature Complete — leads list, lead detail, analytics, audit log; mutations deferred |
| **What was built?** | Full three-path advisory tool: 45 PRs, complete Safe Scan Runner pipeline, bilingual UI (AR/EN) |
| **What is forbidden?** | Port scan, crawl, intrusive test, raw data exposure, actor IP in UI, admin scan trigger, bulk scan |
| **What is deferred?** | Before/After comparison, scheduled reports, admin mutations, export, deep scan authorization gate, real reputation provider |
| **Ready for supervised limited trial?** | Yes — with HTTPS, real secrets, and a known user list |
| **Ready for public launch?** | No — CVE GHSA-36qx-fr4f-26g5, per-domain rate limiting, and real reputation provider must be resolved first |
| **Biggest security risk?** | Next.js CVE (i18n bypass) + missing per-domain rate limit + mock reputation provider |
| **Manual QA done?** | Checklist above — run in staging before trial |
| **Production checklist?** | Section 11 above — 20 items across infrastructure, security, operations |
| **Can this be called MVP?** | Yes — all three user journeys work end-to-end, securely, bilingually, as an advisory tool |
