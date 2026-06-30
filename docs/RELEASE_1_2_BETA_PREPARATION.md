# Release 1.2 — Beta Trial Preparation

**Product:** Website Trust & Security Advisor  
**Release:** 1.2 — Beta Trial Preparation  
**Date:** 2026-06-29  
**Base:** Release 1.1 — Design & UX Refresh (`6e6594d`)  
**PR:** Release 1.2 Beta Trial Preparation (this PR — do not merge until pre-launch ops checklist is confirmed)

---

## Goal

Make the product ready for a supervised, invitation-only beta trial with known users. No new features. Frontend and docs only. Fix only what blocks a clear, trustworthy beta experience.

---

## Scope

| Area | Changed? |
|---|---|
| `frontend/` — Owner dashboard UX | ✅ Yes — empty states, error recovery, layout fix |
| `frontend/` — Translation keys | ✅ Yes — new `empty_hint` and `retry` keys in both languages |
| `frontend/` — RTL fix (scan detail) | ✅ Yes — `dir="ltr"` on owner scan score ring |
| `docs/` — Beta readiness report | ✅ Yes |
| `docs/` — Release notes | ✅ Yes (this file) |
| `backend/` | ❌ No changes |
| API contracts | ❌ No changes |
| Auth / session logic | ❌ No changes |
| Scanner / scan runner | ❌ No changes |
| Scoring algorithm | ❌ No changes |
| Database / migrations | ❌ No changes |
| New npm dependencies | ❌ None |

---

## Changes

### 1. `frontend/src/app/[locale]/sites/page.tsx`

**Problem:** `justify-center` on the main container caused the sites list to float in the vertical middle of the page — looks broken when there are 2+ sites.

**Fix:** Changed `justify-center` → `justify-start pt-10`.

**Problem:** Empty state was plain text with no guidance. New owners seeing an empty dashboard had no indication of what to do next.

**Fix:** Replaced plain text with a card containing a context hint: "Your sites will appear here once your account is set up. Contact your account manager if you have questions."

**Problem:** Error state had no retry mechanism. The only recovery was a manual page reload.

**Fix:** Added a "Try again" / "حاول مجددًا" button that re-triggers the data fetch using `retryKey` state increment.

---

### 2. `frontend/src/app/[locale]/sites/[siteId]/scans/page.tsx`

Same three fixes as the sites dashboard:

- `justify-center` → `justify-start pt-8` (layout fix)
- Empty state card with `empty_hint`: "Your first scan result will appear here once it is ready."
- Error state retry button

---

### 3. `frontend/src/app/[locale]/sites/[siteId]/scans/[scanId]/page.tsx`

**Problem:** The owner scan detail page's trust score ring had no `dir="ltr"` wrapper. In Arabic RTL mode, the `/100` text and score layout could appear reversed.

**Fix:** Wrapped the score ring and badge in a `div` with `dir="ltr"` — consistent with the same fix in `TrustResult.tsx` (applied in Release 1.1).

---

### 4. `frontend/src/messages/en.json` and `ar.json`

New keys added to two namespaces:

**`owner_sites`:**
- `retry` — "Try again" / "حاول مجددًا"
- `empty_hint` — context for empty sites dashboard

**`owner_scans_list`:**
- `retry` — "Try again" / "حاول مجددًا"
- `empty_hint` — context for empty scans list

No existing keys renamed or removed.

---

### 5. `docs/BETA_TRIAL_READINESS_REPORT.md`

Full readiness audit: all three user paths, security controls, accessibility, translation parity, build results, known non-blockers, and go/no-go checklist.

---

## What Was NOT Changed

| Item | Reason |
|---|---|
| Scanner / Safe Scan Runner | No new scan types; pipeline unchanged |
| Rate limiting enforcement | Backend change; deferred to 1.0.1 / post-beta |
| Reputation provider | Backend change; deferred to 1.0.1 / post-beta |
| Admin page headers | Out of scope; admin is founder-only |
| Terms / Privacy content | Legal work needed; placeholder pages exist |
| Forgot Password backend | Backend endpoint not yet built |
| Auth redesign | Out of scope |
| New features | None |

---

## Build Verification

| Check | Result |
|---|---|
| `npx tsc --noEmit` | ✅ No errors |
| `npm run build` | ✅ 15 routes, 0 errors |
| New npm dependencies | ✅ None added |

---

## Pre-Launch Ops Checklist (deployer must confirm)

Before allowing any beta tester to access the product:

- [ ] HTTPS active at load balancer (TLS termination)
- [ ] `SECRET_KEY` set to a real value (not `.env.example` default)
- [ ] `DATABASE_URL` and `POSTGRES_PASSWORD` set to real values
- [ ] `ALLOWED_ORIGINS` in production = exact frontend domain (not `*`)
- [ ] `ADMIN_API_KEY` set to a real value
- [ ] Cookie `secure=True` flag confirmed active (`APP_ENV != development`)

None of these require code changes — they are environment configuration items.

---

## Beta Trial Guidelines

- Trial is **invitation-only** — do not publicly list the URL or post on social media
- Invite no more than 10 visitor testers and 5 owner testers for the first round
- Monitor error rates and scan volume during the trial
- Collect structured feedback (UX friction, confusion points, missing clarity)
- Log issues for v2.0 planning
- Do not add features during the trial period

---

## Next Milestone

After Beta Trial feedback is collected and triaged: **Release 2.0 — Product Evolution** (features determined by Beta feedback).
