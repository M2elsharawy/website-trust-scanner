# Release Plan

**Product:** Website Trust Advisor  
**Current state:** MVP Feature Complete — RC1 approved for supervised limited trial  
**Main SHA at planning time:** `2514913`  
**Date:** 2026-06-28

---

## Release Overview

| Release | Name | Goal | Status |
|---|---|---|---|
| MVP | MVP Feature Complete | Three-path product: Visitor, Owner, Admin | ✅ Done |
| 1.0.1 | Production Hardening | Unblock public launch — security, infra, real reputation | Planning |
| 1.1 | Design & UX | Visual identity and interaction quality | Planned |
| 1.2 | Beta Trial | Real-user supervised trial | Planned |
| 2.0 | Product Evolution | Feature expansion based on Beta feedback | Planned |

---

## Release 1.0.1 — Production Hardening

### Goal
Resolve all known blockers documented in `RC1_REVIEW_REPORT.md §7` so that the product can move from supervised limited trial to public launch.

### In Scope

| Item | Notes |
|---|---|
| Verify Next.js CVE GHSA-36qx-fr4f-26g5 | Current version: 16.2.9. CVE reportedly affects < 15.2.3. Confirm whether 16.2.9 is patched by checking the official advisory. If patched, close the blocker. If not, upgrade or apply vendor mitigation. |
| Enforce per-domain rate limiting | `DOMAIN_SCAN_LIMIT = "5/hour"` is defined in `rate_limiter.py` but not yet applied in `safe_scan_runner.py:111`. Add enforcement in a dedicated PR. |
| Replace mock reputation provider | `reputation_checker.py` currently returns "clean" for all domains. Integrate a real provider (Google Safe Browsing, VirusTotal, or URLhaus). Wire `REPUTATION_PROVIDER` env var already defined in `.env.example`. |
| Production secrets review | Confirm `SECRET_KEY`, `DATABASE_URL`, `POSTGRES_PASSWORD`, `ALLOWED_ORIGINS`, `ADMIN_API_KEY` are set to real values and not `.env.example` defaults. |
| HTTPS at load balancer | Enforce TLS termination. Confirm `secure=True` cookie flag is active (already conditional on `APP_ENV != development`). |
| CORS origin restriction | Confirm `ALLOWED_ORIGINS` in production is set to the exact frontend domain, not `*`. |
| `passlib` + `bcrypt 4.x` mismatch | Resolve dependency version conflict that causes a warning at startup. Authentication works but the warning should be eliminated before production. |
| `middleware` → `proxy` rename | Next.js 16 deprecated the `middleware` file convention. Rename `frontend/src/middleware.ts` → `frontend/src/proxy.ts`. No logic change. |
| Terms of Service + Privacy Policy | Pages or external links must be present before public registration is opened. |
| Data retention policy enforcement | `DATA_RETENTION_POLICY.md` must be enforced in the production database configuration. |

### Out of Scope

- New features
- UI changes
- Scan logic or scoring changes
- New scanner types
- New API endpoints

### Success Criteria

- [ ] CVE GHSA-36qx-fr4f-26g5 verified as patched or mitigated
- [ ] Per-domain rate limit active and tested
- [ ] Real reputation provider returning live data
- [ ] HTTPS active, cookies flagged `secure=True`
- [ ] No `.env.example` default values in production
- [ ] `passlib` warning eliminated from logs
- [ ] `middleware` deprecation warning eliminated

### Risks

| Risk | Mitigation |
|---|---|
| Real reputation provider adds latency | Set a strict timeout; fall back gracefully if provider is unreachable |
| Per-domain rate limit may require Redis key-per-domain | Already have Redis in the stack — use it as the backend for `slowapi` domain key |
| CVE advisory may affect 16.x | If so, upgrade Next.js — test against existing CI suite before merging |

### Suggested Execution Order

1. CVE verification (read-only first — may close blocker without code change)
2. `passlib` + `middleware` fixes (low-risk, isolated)
3. Per-domain rate limit (backend only, tested in isolation)
4. Real reputation provider (backend only, feature-flagged via `REPUTATION_PROVIDER` env var)
5. Infra checklist (secrets, HTTPS, CORS) — environment configuration, not code
6. ToS + Privacy Policy pages

---

## Release 1.1 — Design & UX

### Goal
Improve visual identity, interaction quality, and bilingual experience without changing any product logic.

### In Scope

- Visual identity refinement (logo, color palette, typography)
- Card layout and spacing improvements
- Homepage layout and hero section
- Illustrations and iconography
- Responsive layout improvements (mobile breakpoints)
- Micro-interactions and loading states
- Arabic / English experience consistency (RTL spacing, font sizing, directionality)
- Accessibility improvements (contrast, focus states, ARIA labels)

### Out of Scope

- Scan logic
- Scoring algorithm
- Backend changes of any kind
- Security policy changes
- Auth flow changes
- New pages or routes (unless purely cosmetic shell pages)
- Any change that requires backend API modification

### Success Criteria

- [ ] Lighthouse mobile score ≥ 80
- [ ] Arabic and English UX reviewed by a bilingual user
- [ ] No regression in existing functionality (CI green, manual QA checklist passed)
- [ ] No backend changes introduced

### Risks

| Risk | Mitigation |
|---|---|
| UI changes may accidentally affect scan form behavior | Run full manual QA checklist after each UI PR |
| RTL changes may break LTR layout | Test both locales in CI screenshots or manual review |

---

## Release 1.2 — Beta Trial

### Goal
Run a supervised limited trial with real, known users to collect feedback before any public launch.

### In Scope

- Deploy to a production-like environment (not localhost)
- Invite a small, known group of users (not publicly listed)
- Monitor error rates and scan volume
- Collect structured UX feedback
- Log issues in a feedback tracker
- Identify UX friction points and bugs not caught in QA
- Document what works and what needs improvement before v2.0

### Out of Scope

- Public registration
- Public listing or SEO
- New features during the trial
- Marketing

### Prerequisites (from 1.0.1)

- HTTPS active
- Real reputation provider integrated
- Per-domain rate limit enforced
- Secrets configured
- ToS + Privacy Policy present

### Success Criteria

- [ ] At least 5 distinct trial users complete the full Visitor flow
- [ ] At least 2 trial users complete the Owner flow (register → verify → scan → FixPlan)
- [ ] Zero data exposure incidents during trial
- [ ] Feedback collected and triaged for v2.0 planning

### Risks

| Risk | Mitigation |
|---|---|
| Trial users encounter bugs not caught in QA | Monitoring and error alerting must be configured before trial starts |
| Scan volume spikes from trial users | Per-domain rate limit and per-IP limit provide protection |
| Reputation mock may cause incorrect "clean" results | Should be resolved in 1.0.1 before trial |

---

## Release 2.0 — Product Evolution

### Goal
Expand the product based on real user feedback collected during Beta Trial. No feature is committed to this release until Beta Trial findings are reviewed.

### Candidate Features (not committed)

These are candidates only. Priority and inclusion will be decided after Beta Trial:

| Candidate | Notes |
|---|---|
| Before/After score comparison | Show improvement after site owner fixes issues |
| Scan history trend chart for owners | Visual progress over time |
| Periodic / scheduled scan reports | Email or in-app notification when score changes |
| Export developer task (ticket format) | Export Fix Plan as a structured task file |
| Admin lead → owner conversion workflow | Convert a lead to an active owner subscription |
| Admin status management UI | Allow admin to update lead status |
| Authorization record gate for deep scan | Required before any admin-triggered deep scan |
| Enhanced Fix Plan guidance | More detailed, role-specific fix instructions |
| Notification system | Alert owner when scan score drops |

### Out of Scope Until 2.0

- Bulk scan
- Port scanning or crawling
- Any offensive capability
- Raw data exposure

### Success Criteria

Defined after Beta Trial findings are reviewed.

---

## Execution Order Summary

```
MVP Feature Complete (done)
     │
     ▼
RC1 Supervised Limited Trial (active)
     │
     ▼
Release 1.0.1 — Production Hardening
     │
     ▼
Release 1.1 — Design & UX
     │
     ▼
Release 1.2 — Beta Trial
     │
     ▼
Release 2.0 — Product Evolution
```

Note: Release 1.1 (Design & UX) may begin in parallel with or immediately after 1.0.1, provided no backend changes are required. Beta Trial (1.2) cannot start until 1.0.1 is complete.
