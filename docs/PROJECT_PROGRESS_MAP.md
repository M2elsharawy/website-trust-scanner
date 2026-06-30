# Project Progress Map

**Last updated:** 2026-06-29  
**Last SHA on main:** `6366a08`

---

## 1. Current State

| Component | Status |
|-----------|--------|
| Public Trust Check → Safe Scan Runner | ✅ Complete — PR #18 |
| Product Roadmap page | ✅ Complete — PR #19 |
| Owner Scan → Safe Scan Runner | ✅ Complete — PR #20 |
| Usage Decision UX (visitor result) | ✅ Complete — PR #21 |
| Owner Fix Plan + CopyButton | ✅ Complete — PRs #22–#33 (multiple) |
| Admin Lead Audit → Safe Scan Runner | ✅ Complete — PR #35 |
| Admin UI Scope docs | ✅ Complete — PR #36 |
| Admin route protection + shell | ✅ Complete — PR #37 |
| Admin Leads list (read-only) | ✅ Complete — PR #38 |
| Admin Lead Detail (read-only) | ✅ Complete — PR #39 |
| Admin MVP Closure Pass | ✅ Complete — PR #40 |
| Owner locale navigation fix + docs polish | ✅ Complete — PR #41 |
| Admin analytics dashboard (summary, scan trends, audit log) | ✅ Complete — PR #43 |
| UX polish: LogoutButton, FixPlan fix, open redirect fix, score explanation | ✅ Complete — PR #45 |

---

## 2. Current Product Position

### Visitor (Public)
- Scans a URL → gets Trust Score → sees Usage Decision (4 cards, 3-state verdict)
- Advisory results only — surface-level indicators, not a security certification
- No sensitive technical details exposed
- **Status: MVP Feature Complete**

### Site Owner
- Can register a site, verify DNS ownership, trigger a scan, view results, view Fix Plan, copy developer instructions
- All scans pass through Safe Scan Runner
- **Status: MVP Feature Complete**

### Admin (Founder)
- Read-only MVP: view leads list, lead detail, analytics dashboard
- Analytics: summary stats, 30-day scan trend chart, audit log (action/outcome/role/type/time)
- Notice banner clarifies read-only scope in both languages
- No scan trigger, no status update, no export in UI
- **Status: Read-only MVP Feature Complete — mutations deferred**

---

## 3. Completed PRs

| PR | Title | SHA | Notes |
|----|-------|-----|-------|
| #18 | Public Trust Check → Safe Scan Runner | `f5bbc58` | Squash merged |
| #19 | Product Roadmap page | `3825518` | Squash merged |
| #20 | Owner Scan → Safe Scan Runner | `d8d8896` | Squash merged |
| #21 | Usage Decision UX for visitor result | `2726da5` | Squash merged |
| #22–#33 | Owner Fix Plan + CopyButton | various | Squash merged |
| #35 | Admin Lead Audit → Safe Scan Runner | — | Squash merged |
| #36–#41 | Admin UI MVP (route guard, leads, detail, closure, locale fix) | various | Squash merged |
| #43 | Admin analytics dashboard | `9e28101` | Squash merged |
| #45 | UX polish + open redirect fix | `a8549cc` | Squash merged |

---

## 4. Engineering Phase Status

**Engineering phase is complete.** All three user paths are implemented, tested, and documented. The product is in the Supervised Beta operational phase.

### Completed since last map update

| Release | Delivered | PRs |
|---|---|---|
| 1.0.1 Production Hardening | SSRF, per-domain rate limit, per-IP rate limit, account lockout, refresh token rotation, audit logging | #46–#52 |
| 1.1 Design & UX Refresh | Cairo font, RTL layout, danger banner, advisor tone, roadmap page, forgot-password UI | #53-series |
| 1.2 Beta Prep | Owner dashboard UX (layout, empty states, retry), RTL score ring fix, new i18n keys | PR #53 (open draft) |
| Pre-Launch Validation | 8-angle comprehensive review, launch decision, operational gate, beta operating cycle | PRs #54–#57 |

### Open PRs (not yet on main)

| PR | Title | Type | Status |
|---|---|---|---|
| #53 | Release 1.2 Beta Trial Preparation | Frontend + Docs | Open draft — do not merge until TB1–TB5 confirmed by deployer |

---

## 6. Strict Boundaries (permanent)

These constraints apply to every session unless explicitly lifted with a new decision:

- No new scanners
- No deep/intrusive scanning
- No crawling
- No port scanning
- No exposed-files enumeration
- No backend changes without explicit approval
- No auto-merge of any PR
- No outbound requests outside URL validator
- No redirects without re-validation
- No raw headers, IPs, response bodies, or exploitable details in API or UI
- No new dependencies without explicit approval
- No scheduled/admin changes without explicit approval
- No PDF changes without explicit approval

---

## 7. Decision Rule

Before every new phase, answer these four questions:

1. **كنا فين؟** Where were we before this phase started?
2. **وصلنا لفين؟** What did this phase deliver?
3. **فاضل إيه؟** What is still remaining?
4. **المرحلة القادمة هدفها إيه؟** What is the concrete goal of the next phase?

Update this file at the end of each phase before opening a PR.

---

## 8. Architecture Snapshot

```
backend/
  app/
    core/
      safe_scan_runner.py   ← run_public_trust_scan + run_owner_trust_scan
      url_validator.py      ← SSRF protection (do not modify)
      scan_policy.py        ← scan type enforcement (do not modify)
    scanners/
      trust_score.py        ← compute_trust_report → sanitized dict only
    api/v1/
      public_trust.py       ← POST /public-trust-check
      owner_scans.py        ← POST/GET /sites/{id}/scans
    schemas/
      scan.py               ← TrustReport, ChecksSummary, Recommendations
      scan_result.py        ← ScanResultSummary, ScanResultDetail

frontend/
  src/
    app/[locale]/
      page.tsx              ← home (public scan + TrustResult)
      roadmap/page.tsx      ← static roadmap
      login/ register/      ← auth pages
    components/
      TrustResult.tsx       ← visitor scan result (Usage Decision UX)
      ScanForm.tsx
      AuthForm.tsx
    messages/
      ar.json               ← Arabic translations
      en.json               ← English translations
```
