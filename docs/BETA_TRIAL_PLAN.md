# Beta Trial Plan — Release 1.2

**Product:** Website Trust Advisor  
**Release:** 1.2 — Beta Trial  
**Prerequisite:** Release 1.0.1 complete and verified in a staging environment  
**Date:** 2026-06-28

---

## Objective

Run a supervised, invitation-only trial with a small group of known users to:

1. Collect structured UX feedback from real usage
2. Identify bugs and friction not caught in internal QA
3. Validate that the production security posture holds under real user behavior
4. Produce a prioritized backlog for Release 2.0

The Beta Trial is not a public launch. Users are known, vetted, and invited individually. No public registration, no SEO, no marketing.

---

## Prerequisites (all must be complete before trial begins)

| Prerequisite | Owner | Status |
|---|---|---|
| HTTPS active at load balancer | Infra | ⬜ Not started |
| Real reputation provider integrated | Backend | ⬜ Not started |
| Per-domain rate limit enforced | Backend | ✅ Done (Release 1.0.1) |
| Production secrets configured | Infra | ⬜ Not started |
| Terms of Service page present | Frontend | ⬜ Not started |
| Privacy Policy page present | Frontend | ⬜ Not started |
| `APP_ENV=production` (secure cookies) | Infra | ⬜ Not started |
| Error monitoring / alerting active | Infra | ⬜ Not started |
| Data retention policy enforced in DB | Infra | ⬜ Not started |
| Manual QA checklist from RC1 passed in staging | QA | ⬜ Not started |

---

## Trial Scope

### What trial users can do

- Complete the full **Visitor flow**: enter a URL → receive Trust Score → view Usage Decision
- Complete the full **Owner flow**: register → verify DNS ownership → trigger scan → view Fix Plan → copy developer instructions
- Use both Arabic and English locales
- Report bugs and UX feedback via the designated feedback channel

### What trial users cannot do

- Access the Admin path (admin is founder-only)
- Trigger deep scans or administrative operations
- Invite other users

### What is excluded during the trial

- Public registration (registration link is not promoted publicly)
- SEO indexing (add `robots.txt` with `Disallow: /` before trial starts)
- Marketing or social media references to the trial URL
- New features (no code changes during the active trial period)

---

## User Cohort

| Role | Count | Criteria |
|---|---|---|
| Visitor testers | 5–10 | Test the URL scan and trust result flow only |
| Owner testers | 2–5 | Have a real domain they own; willing to add a DNS TXT record |
| Technical reviewer | 1 | Developer who reviews Fix Plan output for accuracy |

All users must be personally invited and identified before the trial starts. No anonymous access.

---

## Trial Duration

| Phase | Duration | Activity |
|---|---|---|
| Soft launch | Days 1–3 | Invite first 2–3 users; monitor error rates closely |
| Active trial | Days 4–14 | Full cohort; collect feedback daily |
| Wrap-up | Days 15–17 | Final feedback collection; triage bug reports |
| Retrospective | Day 18 | Review findings; produce 2.0 backlog |

Total duration: ~3 weeks. Extend only if a blocking bug requires a patch cycle.

---

## Monitoring Requirements

The following must be active before the trial starts:

| Requirement | Purpose |
|---|---|
| Application error log (structured JSON) | Catch backend exceptions in real usage |
| 5xx rate alerting | Immediate notification if error rate spikes |
| Scan volume tracking | Detect unexpected usage patterns |
| Redis rate limit key monitoring | Verify per-domain and per-IP limits are firing correctly |
| Uptime check (external) | Alert if the service is unreachable |

No user-level behavioral tracking (no analytics pixel, no session recording) during the trial. Structured server logs only.

---

## Feedback Collection

Each trial user receives:

1. A welcome message explaining the product purpose and trial scope
2. A link to a structured feedback form (hosted externally, not in the product)
3. A direct contact for bug reports

Feedback form covers:
- Task completion (could you complete the Visitor flow? the Owner flow?)
- Clarity of Trust Score and Usage Decision
- Fix Plan usefulness (for Owner testers)
- Confusion points or unexpected behavior
- Arabic/English language quality (for bilingual users)
- Overall trust in the result

---

## Bug Triage During Trial

| Severity | Definition | Response |
|---|---|---|
| P0 — Data exposure | Any raw IP, header, or personal data visible in UI or API response | Stop trial; patch immediately |
| P1 — Auth broken | Login, registration, or session management failure | Patch within 24 hours |
| P2 — Core flow blocked | Scan fails for all domains; Fix Plan does not render | Patch within 48 hours |
| P3 — UX friction | Confusing copy, layout issue, edge-case error message | Log for Release 2.0 |
| P4 — Cosmetic | Minor visual inconsistency | Log for Release 1.1 backlog |

No new features may be added during the trial period. Bug fixes only.

---

## Success Criteria

- [ ] At least 5 distinct users complete the full Visitor flow end-to-end
- [ ] At least 2 users complete the full Owner flow (register → DNS verify → scan → Fix Plan)
- [ ] Zero P0 or P1 incidents during the trial
- [ ] Error rate < 1% of scan requests (measured in server logs)
- [ ] Structured feedback collected from ≥ 60% of invited users
- [ ] Findings triaged and v2.0 candidate backlog produced

---

## Post-Trial Deliverables

1. **Bug report** — all P2+ issues found, with reproduction steps
2. **UX friction log** — P3/P4 issues categorized by flow
3. **2.0 candidate backlog** — prioritized feature candidates based on feedback (from `RELEASE_PLAN.md §2.0 Candidate Features`)
4. **Trial retrospective** — what worked, what didn't, what to change before public launch

---

## Risks

| Risk | Mitigation |
|---|---|
| Trial user scans a domain that reputation mock misclassifies as "clean" | Communicate to all users that reputation data is live for Release 1.0.1; confirm mock is replaced before trial starts |
| Trial user adds DNS TXT record but verification fails | Have support contact ready; Owner flow requires DNS propagation (up to 48h) |
| Error rate spikes from an edge-case URL input | Monitor logs in real time during first 3 days; per-IP rate limit provides protection |
| Trial URL is shared publicly by a user | Add robots.txt before trial; do not include the URL in any public document |
| Data retention enforcement not active | Block trial start until retention enforcement is confirmed in the production DB config |

---

## Go / No-Go Checklist

Complete this checklist before sending the first invitation:

### Infrastructure
- [ ] Deployment URL is HTTPS only (no HTTP redirect gap)
- [ ] SSL certificate is valid and not expiring within 30 days
- [ ] `APP_ENV=production` confirmed in deployed env
- [ ] All secrets are non-default values (verified against `.env.example`)

### Security
- [ ] Per-domain rate limit active (verify: scan the same domain 6× in an hour → 429 on 6th request)
- [ ] Per-IP rate limit active (verify: 11th guest scan in an hour → 429)
- [ ] SSRF blocked (verify: `http://169.254.169.254` → error)
- [ ] Open redirect blocked (verify: `?next=//evil.com` → falls back to `/[locale]/sites`)
- [ ] Cookie flags confirmed: `httponly=True`, `samesite=lax`, `secure=True`
- [ ] CORS `ALLOWED_ORIGINS` set to trial domain only

### Legal
- [ ] Terms of Service page accessible (linked from registration and footer)
- [ ] Privacy Policy page accessible (linked from registration and footer)
- [ ] `robots.txt` with `Disallow: /` in place

### Monitoring
- [ ] Error alerting active and tested (trigger a 500 manually; confirm alert fires)
- [ ] Uptime check active

### Manual QA
- [ ] All items in `RC1_REVIEW_REPORT.md §4` passed in staging
- [ ] All items in `RC1_REVIEW_REPORT.md §5` passed in staging
