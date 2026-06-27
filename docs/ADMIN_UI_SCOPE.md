# Admin UI Scope and Auth Decision

**Date:** 2026-06-24
**Status:** Decision document — no code changes
**Scope:** Admin frontend planning only

---

## Current Admin Backend Capabilities

All admin endpoints require `require_admin` dependency (JWT cookie with `admin`/`super_admin` role, or `X-Admin-Key` header as fallback).

| Endpoint | Function |
|---|---|
| `GET /admin/analytics/summary` | Platform-wide counts: users, sites, scans, risk distribution |
| `GET /admin/analytics/risky-sites` | Sites with trust score < 60, ordered by risk (top 100) |
| `GET /admin/analytics/audit-log` | Recent audit log entries (up to 500), `actor_ip` excluded from response |
| `GET /admin/analytics/scan-trends` | Daily scan counts and average trust score (up to 90 days) |
| `GET /admin/leads` | List all leads with optional status filter |
| `POST /admin/leads` | Create new lead |
| `GET /admin/leads/{id}` | Lead detail |
| `PATCH /admin/leads/{id}/status` | Update lead status (finite state machine enforced) |
| `POST /admin/leads/{id}/audit` | Run surface-level marketing audit via Safe Scan Runner |

---

## Current Admin Frontend Status

**Zero admin pages exist.** The frontend currently contains only:

- Public pages: home, roadmap
- Auth pages: login, register
- Owner flow: sites list, scans list, scan detail, FixPlan

No `/admin/*` routes, no admin navigation, no admin authentication flow in the frontend.

---

## Admin Auth Decision

**The admin frontend must use JWT cookie authentication** — the same mechanism used for the Owner flow — with a user whose role is `admin` or `super_admin`.

**`X-Admin-Key` must NOT be used in the browser UI.** Reasons:
- A static key in the browser is easily extracted from DevTools or network tab.
- It cannot be scoped to a user, session, or expiry.
- It has no logout mechanism.

**`X-Admin-Key` remains a valid internal/API fallback only** — for server-to-server calls, CLI tools, and CI automation. It must never appear in any frontend component, form, or HTTP call initiated from a browser.

**Implication:** An admin user must log in through the existing `/login` route with credentials that have `admin` or `super_admin` role. The backend already supports this. No new auth endpoints are needed.

---

## First Safe Admin UI Slice

When admin UI development begins, the recommended first page is:

**Admin Leads — Read-Only Minimal**

- Route: `/[locale]/admin/leads`
- Data source: `GET /admin/leads`
- Displays: domain, status, created_at, last_audit_at, last_lead_score
- Interactions: status filter only (no create, no edit, no audit trigger)
- Auth: JWT cookie with `admin`/`super_admin` role — same as Owner flow
- Data rules: no raw headers, no IPs, no response bodies, no scan raw data

This page requires no new backend endpoints and exposes no additional data beyond what the API already returns.

**This slice is not implemented yet.** It requires explicit approval before any code is written.

---

## What Is Explicitly Deferred

These items must not be started without explicit approval:

| Feature | Reason Deferred |
|---|---|
| Full Admin Dashboard | Post-MVP scope — premature before basic read-only slice |
| Audit Logs UI | Operational tool, lower user-facing value than leads |
| Do Not Scan management UI | Can be managed via API/DB; no urgency |
| Lead audit trigger from UI | Requires careful scope control; deferred |
| Analytics charts | Visualization layer; deferred until data layer is confirmed |
| PDF export | Post-MVP scope |
| Data export | Post-MVP scope |
| Any scanning controls from UI | Must not be triggered from browser without explicit design review |

---

## Security Boundaries

These apply to every admin page and every admin-triggered action, without exception:

- No port scanning
- No crawling or spider-style enumeration
- No exposed files scan (`.env`, `wp-admin`, `/.git`, etc.)
- No intrusive testing of any kind
- No exploitation or vulnerability probing
- Any outbound scan triggered by an admin action must pass through Safe Scan Runner in the same mandatory order: Do Not Scan → SSRF → URL validation → Scan Policy → Safe HTTP Client
- **Do Not Scan must be checked before any DNS resolution or network call**

---

## Data Exposure Rules

These apply to every admin API response and every admin UI component:

- No raw HTTP headers exposed in any response or UI
- No IP addresses exposed in any response or UI (including `actor_ip` — stored in DB but never returned via API)
- No raw response bodies exposed in any response or UI
- No secrets, tokens, or credentials exposed anywhere
- No sensitive header values exposed (presence/absence only)
- No scan raw data surfaced in the admin UI
- Audit log responses already comply: `actor_ip` is intentionally omitted from `GET /admin/analytics/audit-log`

---

## Open Questions

These must be answered before any admin frontend code is written:

1. **Admin user provisioning:** How is an `admin`/`super_admin` user created? Is there a seed script, a migration, or a manual DB insert? This must be documented before a login flow can be tested.
2. **Admin route protection:** Should admin routes use the same Next.js middleware as the Owner flow, or a separate middleware check for `admin` role?
3. **Admin navigation:** Is the admin UI a separate section of the same app (e.g. `/[locale]/admin/*`) or a separate deployment?
4. **Role visibility:** Should the UI display the user's admin role anywhere, and if so, how?

---

## Next Recommended Step

Answer the Open Questions above, then implement **Admin Leads — Read-Only Minimal** as the first frontend admin slice, following the Data Exposure Rules and Security Boundaries defined in this document.

No code should be written until these questions are answered and explicitly approved.
