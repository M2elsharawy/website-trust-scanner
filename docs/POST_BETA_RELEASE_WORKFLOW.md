# Post-Beta Release Workflow
## Website Trust & Security Advisor — From Beta Findings to Release 2.0

**Trigger:** Beta Trial retrospective completed (Day 18)  
**Input:** Priority register from `BETA_PRIORITIZATION_FRAMEWORK.md`  
**Output:** Release 2.0 scope, sprint plan, and closure report

---

## Overview

```
Beta Trial Closes (Day 18)
          │
          ▼
    Step 1: Feedback Summary
          │
          ▼
    Step 2: Issue Selection
          │
          ▼
    Step 3: Roadmap Update
          │
          ▼
    Step 4: Sprint Planning
          │
          ▼
    Step 5: Implementation
          │
          ▼
    Step 6: Validation
          │
          ▼
    Step 7: Release Report
          │
          ▼
    Step 8: Closure Report
```

No step can be skipped. No feature work begins until Steps 1–3 are complete.

---

## Step 1 — Feedback Summary

**Who:** Founder  
**When:** Days 18–19 (immediately after trial ends)  
**Output:** `docs/BETA_TRIAL_FINDINGS.md` (create at this time)

### What to include in the findings document

**1. Participant overview**
- How many Visitor testers completed the full flow?
- How many Owner testers completed registration → DNS verify → scan → Fix Plan?
- Completion rate (completed / invited × 100%)

**2. Trust signal assessment**
- What percentage of users understood the Trust Score without explanation?
- Did users act on the score (e.g., decide not to use a site)?
- What was the most common source of confusion about the score?

**3. Fix Plan assessment**
- Did owner testers find the Fix Plan actionable?
- Which Fix Plan cards were most useful? Least useful?
- Could a developer implement a Fix Plan item without asking for help?

**4. Bilingual experience assessment**
- Were there Arabic UX issues that didn't appear in English testing?
- Was any copy awkward or unnatural in either language?

**5. Issue summary table**

| Priority | Count | Open | Fixed during trial |
|---|---|---|---|
| P0 | 0 | 0 | 0 |
| P1 | ? | ? | ? |
| P2 | ? | ? | ? |
| P3 | ? | ? | ? |

**6. Unresolved items**
List every open P1 and P2 issue that was not fixed during the trial. These must be addressed before Release 2.0.

---

## Step 2 — Issue Selection

**Who:** Founder  
**When:** Day 19–20  
**Input:** Priority register + Feedback Summary  
**Output:** Release 2.0 scope decision

### Selection rules

**Must include in Release 2.0:**
- All open P1 issues (these should be fixed during trial; if not, they block 2.0)
- All P2 issues with 3+ independent observations
- Any Documentation Gap that appeared in 50%+ of sessions

**Should include in Release 2.0 (if effort is justified):**
- P2 issues with 1–2 observations that align with the core product value (Trust Signal, Fix Plan)
- Feature Requests mentioned by 2+ users independently that do not require major architecture changes

**Do not include in Release 2.0 (log, don't commit):**
- Out of Scope items, regardless of how many users requested them
- Feature Requests from only one user
- P3 cosmetic issues unless they directly affect trust in the result
- Any feature that requires adding a new dependency without prior review

### Selection output format

For each item selected for Release 2.0, document:
- Issue ID and description
- Number of sessions in which it appeared
- Estimated effort (S/M/L)
- Why it's in scope for 2.0

---

## Step 3 — Roadmap Update

**Who:** Founder  
**When:** Day 20–21  
**Input:** Issue selection from Step 2  
**Output:** Updated `docs/RELEASE_PLAN.md` §2.0

### What to update

In `RELEASE_PLAN.md`, replace the placeholder "Candidate Features (not committed)" list with the confirmed Release 2.0 scope. Each item must have:
- Source (which Beta finding it addresses)
- Scope boundary (what it includes and what it doesn't)
- Success criterion (how we know it's done)

### What not to change in the roadmap

- Do not add items that were not observed in the Beta Trial
- Do not commit to timelines in the roadmap — only scope
- Do not move Out of Scope items into the roadmap under any label

---

## Step 4 — Sprint Planning

**Who:** Founder + Engineering lead  
**When:** Day 21–22  
**Input:** Confirmed Release 2.0 scope  
**Output:** Prioritized implementation order, one item per PR

### Sprint structure

Release 2.0 uses the same PR discipline as all previous releases:
- One concern per PR (no bundling unrelated changes)
- CI must pass before merge
- Docs updated alongside code changes
- No backend changes without explicit scope definition

### Ordering heuristic

1. Security and data integrity items first
2. Product Blocker fixes (if any open P1s remain)
3. Core flow UX improvements (items that affect trust in the result)
4. Fix Plan improvements
5. Bilingual / RTL fixes
6. Other P2 items
7. Nice-to-have P3 items (if sprint capacity allows)

---

## Step 5 — Implementation

**Who:** Engineering  
**When:** Release 2.0 sprint  
**Constraints:**

- All code changes follow existing patterns (no new architectural patterns without discussion)
- No new dependencies without explicit founder approval
- No changes to the Safe Scan Runner pipeline without security review
- No changes to Auth flow without security review
- No changes to Database schema without migration plan review
- Every PR must reference the Beta issue ID it resolves (e.g., "Fixes B-012")

### Code freeze rule

During Release 2.0 implementation, the product is in active use by beta testers (if the trial is extended) or by early public users (if public launch followed beta). No experimental changes. Every PR must be production-safe.

---

## Step 6 — Validation

**Who:** Founder + Engineering  
**When:** After last Release 2.0 PR is merged  
**Input:** Full diff of Release 2.0 changes  
**Checklist:**

- [ ] All P1 and selected P2 Beta issues are resolved
- [ ] TypeScript check passes (`npx tsc --noEmit`)
- [ ] Production build passes (`npm run build`)
- [ ] Backend unit tests pass (`pytest`)
- [ ] Manual QA of changed flows in staging
- [ ] Bilingual smoke test (all changed UI in both Arabic and English)
- [ ] Security controls verified: SSRF block, rate limits, owner isolation
- [ ] No regression in unchanged flows (Visitor scan, Owner scan, Fix Plan)

---

## Step 7 — Release Report

**Who:** Founder  
**When:** After validation passes  
**Output:** `docs/RELEASE_2_0_REPORT.md` (create at this time)

### What to include

- Release summary: what changed and why
- Issues resolved (with Beta issue IDs)
- Issues deferred (with reason)
- QA results
- Known open items (if any)
- Changes to security posture (if any)
- Deployment checklist (if any new ops tasks required)

---

## Step 8 — Closure Report

**Who:** Founder  
**When:** After Release 2.0 is deployed and stable for 48 hours  
**Output:** Updated `docs/RELEASE_PLAN.md` with Release 2.0 status → Done

### What the closure confirms

- [ ] Release 2.0 is deployed and stable
- [ ] All P0/P1 issues from Beta are resolved
- [ ] No new P0/P1 issues introduced by Release 2.0 changes
- [ ] Monitoring confirms no error rate spike post-deploy
- [ ] Beta users (if still active) confirm improvement
- [ ] Roadmap updated with Release 3.0 direction (if known)

---

*Related: `BETA_OPERATING_CYCLE.md` · `BETA_PRIORITIZATION_FRAMEWORK.md` · `RELEASE_PLAN.md`*
