# Project Progress Map

**Last updated:** 2026-06-26  
**Last SHA on main:** `0422254`

---

## 1. Current State

| Component | Status |
|-----------|--------|
| Public Trust Check → Safe Scan Runner | ✅ Complete — PR #18 |
| Product Roadmap page | ✅ Complete — PR #19 |
| Owner Scan → Safe Scan Runner | ✅ Complete — PR #20 |
| Usage Decision UX (visitor result) | ✅ Complete — PR #21 |
| Owner Fix Plan + CopyButton | ✅ Complete — PRs #22–#33 |
| Admin Lead Audit → Safe Scan Runner | ✅ Complete — PR #35 |
| Admin UI Scope docs | ✅ Complete — PR #36 |
| Admin route protection + shell | ✅ Complete — PR #37 |
| Admin Leads list (read-only) | ✅ Complete — PR #38 |
| Admin Lead Detail (read-only) | ✅ Complete — PR #39 |
| Admin MVP Closure Pass | ✅ Complete — PR #40 |
| Owner locale navigation fix + docs polish | ✅ Complete — PR #41 |
| docs: Limited MVP Trial Plan | ✅ Complete — PR #42 (pending merge) |
| Admin analytics dashboard + summary stats | ✅ Complete — PR #43 (pending merge) |
| Owner scan detail: disclaimer + back nav | ✅ Complete — this PR |
| Final MVP Closure Report + checklist update | ✅ Complete — this PR |

---

## 2. Current Product Position

### Visitor (Public)
- Scans a URL → gets Trust Score → sees Usage Decision (4 cards, 3-state verdict)
- Disclaimer shown on form and on results page
- No sensitive technical details exposed
- **Status: MVP complete**

### Site Owner
- Can register a site, verify DNS ownership, trigger a scan, view results, view Fix Plan, copy developer instructions
- Scan detail page shows disclaimer + back navigation
- All scans pass through Safe Scan Runner
- **Status: MVP complete**

### Admin (Founder)
- Read-only MVP:
  - Dashboard with 4 summary stat cards (users, sites, verified sites, scans)
  - Analytics page: risk distribution, 30-day scan trends, recent audit log
  - Leads list and lead detail with surface-level disclaimer
  - Notice banner clarifies read-only scope in both languages
- No scan trigger, no status update, no export in UI
- **Status: Read-only MVP complete — mutations deferred**

---

## 3. Completed PRs

| PR | Title | Notes |
|----|-------|-------|
| #18 | Public Trust Check → Safe Scan Runner | Squash merged |
| #19 | Product Roadmap page | Squash merged |
| #20 | Owner Scan → Safe Scan Runner | Squash merged |
| #21 | Usage Decision UX for visitor result | Squash merged |
| #35 | Admin Lead Audit → Safe Scan Runner | Merged |
| #36 | Admin UI Scope docs | Merged |
| #37 | Admin route protection + shell | Merged |
| #38 | Admin Leads list | Merged |
| #39 | Admin Lead Detail | Merged |
| #40 | Admin MVP Closure Pass | Merged |
| #41 | Owner locale navigation fix | Merged |
| #42 | docs: Limited MVP Trial Plan | Pending merge |
| #43 | Admin analytics dashboard + stats | Pending merge |

---

## 4. Remaining Product Work

### Deferred (requires explicit approval before starting)
- [ ] Before/After score comparison (owner)
- [ ] PDF / report export
- [ ] Scheduled periodic re-scans
- [ ] Admin: trigger scan with authorization flow
- [ ] Admin: update lead status
- [ ] Admin: convert Lead to Owner subscription
- [ ] Admin: deep scan post-authorization (requires Authorization Record design)

### Pre-launch blockers (not MVP scope)
- [ ] CVE GHSA-36qx-fr4f-26g5: upgrade Next.js or apply mitigation
- [ ] Production secrets management
- [ ] HTTPS termination at edge
- [ ] Per-domain rate limiting
- [ ] Security review / penetration test

---

## 5. Strict Boundaries (permanent)

These constraints apply to every session unless explicitly lifted:

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

## 6. Decision Rule

Before every new phase, answer these four questions:

1. **كنا فين؟** Where were we before this phase started?
2. **وصلنا لفين؟** What did this phase deliver?
3. **فاضل إيه؟** What is still remaining?
4. **المرحلة القادمة هدفها إيه؟** What is the concrete goal of the next phase?

Update this file at the end of each phase before opening a PR.

---

## 7. Architecture Snapshot

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
      public_trust.py       ← POST /scans/public
      owner_scans.py        ← POST/GET /sites/{id}/scans
      admin/
        leads.py            ← GET /admin/leads + GET /admin/leads/{id}
        analytics.py        ← GET /admin/analytics/summary|scan-trends|audit-log
    schemas/
      scan.py               ← TrustReport, ChecksSummary, Recommendations
      scan_result.py        ← ScanResultSummary, ScanResultDetail

frontend/
  src/
    app/[locale]/
      page.tsx              ← home (public scan + TrustResult)
      roadmap/page.tsx      ← static roadmap
      login/ register/      ← auth pages
      sites/                ← owner sites list
      sites/[id]/scans/     ← owner scans list
      sites/[id]/scans/[scanId]/  ← owner scan detail + FixPlan
      admin/                ← admin home + stats
      admin/analytics/      ← analytics dashboard
      admin/leads/          ← leads list
      admin/leads/[id]/     ← lead detail
    components/
      TrustResult.tsx       ← visitor scan result (Usage Decision UX)
      ScanForm.tsx          ← public scan input
      FixPlan.tsx           ← owner/admin fix plan cards
      CopyButton.tsx        ← copy-to-clipboard button
      AuthForm.tsx          ← login / register form
    messages/
      ar.json               ← Arabic translations
      en.json               ← English translations
```
