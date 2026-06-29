# Beta Operating Cycle
## Website Trust & Security Advisor — Release 1.2

**Date:** 2026-06-29  
**Status:** Active — trial has not started yet  
**Prerequisite:** All 5 True Beta Blockers from `OPERATIONAL_BETA_LAUNCH_GATE.md` confirmed by deployer

---

## 1. Purpose of the Beta Trial

The supervised Beta Trial is not a soft public launch. It is a structured observation exercise with a small, known group of users whose goal is to surface friction, confusion, and bugs that internal QA cannot find.

Specific goals in order of priority:

1. **Validate the Trust Signal** — Do real users understand what a Trust Score means? Do they trust it? Does it change their behavior?
2. **Validate the Fix Plan** — Do site owners find the Fix Plan actionable? Can a developer use it without asking for help?
3. **Identify friction in both flows** — Where do users get stuck, confused, or give up?
4. **Confirm security posture under real usage** — Do rate limits fire correctly? Does SSRF protection hold? Are there any unexpected error paths?
5. **Produce a prioritized backlog for Release 2.0** — Turn observations into decisions.

---

## 2. Cohort

| Role | Count | Profile |
|---|---|---|
| **Visitor testers** | 5–8 | People who will test the URL scan and Trust Score flow only. No account needed. |
| **Owner testers** | 2–4 | People who own a real domain and are willing to add a DNS TXT record. |
| **Technical reviewer** | 1 | A developer who reviews the Fix Plan output for accuracy and actionability. |

**Total: 8–13 participants.** All personally invited. All identified by name before invitations go out. No anonymous access.

Do not exceed 13 participants in the first round. The goal is depth of feedback, not breadth.

---

## 3. Duration

| Phase | Days | Activity |
|---|---|---|
| **Soft launch** | Days 1–3 | Invite 2–3 users only. Monitor error rates in real time. Confirm flows work end-to-end with real users before expanding. |
| **Active trial** | Days 4–14 | Full cohort. Collect structured feedback via the `BETA_FEEDBACK_TEMPLATE.md`. Follow up on gaps or confusion within 24 hours. |
| **Wrap-up** | Days 15–17 | Final feedback collection. Confirm no open P0/P1 incidents. Produce issue list. |
| **Retrospective** | Day 18 | Classify issues using `ISSUE_CLASSIFICATION_GUIDE.md`. Prioritize using `BETA_PRIORITIZATION_FRAMEWORK.md`. Produce 2.0 backlog. |

**Total: 18 days.** Extend only if a P2 bug requires a patch cycle during the trial. Never extend for feature additions.

---

## 4. What We Monitor

### Operational metrics (founder watches directly)

| Signal | What it tells us | How to check |
|---|---|---|
| Backend 5xx rate | Unexpected errors in real usage | Structured server logs |
| Scan latency | Is the scan fast enough to feel responsive? | Logs: `scan.completed` event with duration |
| Per-domain rate limit | Is the 5/hour limit firing correctly? | Logs: `rate_limit.domain.exceeded` events |
| Per-IP rate limit | Is guest scan protection working? | Logs: `rate_limit.ip.exceeded` events |
| Failed login attempts | Account lockout working? | Logs: `auth.login.failed` events |
| 404 patterns | Navigation confusion or broken links | Access logs |

### User experience signals (collected via feedback template)

- Did the user understand the Trust Score without explanation?
- Did the user understand what to do next after seeing the score?
- Did the Owner tester successfully add the DNS TXT record without support?
- Did the Fix Plan feel actionable or overwhelming?
- Did the bilingual experience (Arabic/English) feel natural?

### What we are NOT tracking

- No analytics pixels
- No session recording
- No click maps
- No heatmaps
- Structured server logs only, no personal behavioral tracking

---

## 5. When to Stop the Trial Immediately

Stop the trial and suspend invitations if any of the following occur:

| Condition | Action |
|---|---|
| Raw scan data (IP addresses, HTTP headers, file paths) visible in the UI or API response | Stop immediately. Do not resume until patched and re-tested. |
| Any user reports seeing another user's data | Stop immediately. Full incident review before resuming. |
| Auth failure allowing unauthenticated access to `/sites` or scan history | Stop immediately. |
| Backend 5xx rate exceeds 5% of requests over a 30-minute window | Investigate immediately. Suspend new scans if cause unknown. |
| A security researcher or user reports a potential vulnerability | Take it seriously. Assess in private. Do not dismiss without review. |
| Reputation provider returns data that appears fabricated or internally inconsistent | Suspend reputation display pending provider verification. |

Do not continue a trial with a known P0 issue open. Fix first, resume second.

---

## 6. From Feedback to Release

```
Week 1–2: Active trial
   ↓
   Founder collects feedback using BETA_FEEDBACK_TEMPLATE.md
   
Day 18: Retrospective
   ↓
   Classify all issues using ISSUE_CLASSIFICATION_GUIDE.md
   ↓
   Prioritize using BETA_PRIORITIZATION_FRAMEWORK.md
   ↓
   Separate: P0/P1 (fix now) from P2 (Release 2.0) from P3/Out of Scope (log, don't commit)
   
Post-trial: Release Planning
   ↓
   Update RELEASE_PLAN.md §2.0 with Beta findings
   ↓
   Follow POST_BETA_RELEASE_WORKFLOW.md for implementation
   ↓
   Release 2.0
```

No feature work during the active trial. Code freeze from Day 1 to Day 17. Bug fixes for P0/P1 only.

---

## 7. Success Criteria

The trial is considered successful if all of the following are true at Day 18:

- [ ] At least 5 distinct users completed the full Visitor flow end-to-end
- [ ] At least 2 users completed the full Owner flow (register → DNS verify → scan → Fix Plan)
- [ ] Zero P0 or P1 incidents during the trial
- [ ] Error rate < 1% of scan requests (measured in server logs)
- [ ] Structured feedback collected from ≥ 60% of invited users
- [ ] Issue list produced and classified
- [ ] 2.0 candidate backlog drafted

---

*Related documents: `OPERATIONAL_BETA_LAUNCH_GATE.md` · `BETA_FEEDBACK_TEMPLATE.md` · `ISSUE_CLASSIFICATION_GUIDE.md` · `BETA_PRIORITIZATION_FRAMEWORK.md` · `POST_BETA_RELEASE_WORKFLOW.md` · `BETA_FOUNDER_PLAYBOOK.md`*
