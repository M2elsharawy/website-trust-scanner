# Beta Prioritization Framework
## Website Trust & Security Advisor — Release 1.2 Beta

This framework converts classified issues into actionable decisions. Every issue that comes out of `ISSUE_CLASSIFICATION_GUIDE.md` gets a priority here. Priority determines timing, not importance — all issues are important; priority determines when and whether they get fixed.

---

## Priority Levels

### P0 — Stop and Fix

**Definition:** An issue that makes the supervised trial unsafe to continue, or that puts a real user's data or security at risk.

**Response:** Stop new scans or stop the trial entirely. Investigate. Fix. Re-verify. Resume only after the fix is confirmed in staging.

**Time to resolution:** Immediate — do not wait until the retrospective.

**Who acts:** Founder + engineering lead. No parallel work on anything else until resolved.

| Condition | P0 |
|---|---|
| Raw scan data (IP, headers, file paths) visible in UI or API | ✅ |
| One user's data visible to another user | ✅ |
| Admin panel accessible without authentication | ✅ |
| SSRF protection bypassed | ✅ |
| Account credentials exposed in any channel | ✅ |
| Active exploitation of the product by any user | ✅ |

**P0 issue count target:** Zero during trial. If P0 appears, the trial is paused until it is resolved and re-tested.

---

### P1 — Fix Within 24 Hours

**Definition:** A user cannot complete a core product flow — Visitor scan, Owner scan, or Fix Plan view — without founder intervention. The product is non-functional for this use case.

**Response:** Fix and deploy to production during the active trial. No code freeze exception needed — P1 patches are the only code changes allowed during the trial period.

**Time to resolution:** Within 24 hours of confirmation.

**Who acts:** Engineering lead. Patch must pass CI and be reviewed before deployment.

| Condition | P1 |
|---|---|
| Scan form returns error for all valid HTTPS URLs | ✅ |
| Fix Plan fails to render | ✅ |
| Registration creates no account | ✅ |
| Arabic locale shows broken/untranslated UI | ✅ |
| Owner scan returns 500 for all active sites | ✅ |
| Login fails for all users | ✅ |

**P1 issue count target:** Zero open P1 issues at Day 18.

---

### P2 — Fix in Release 2.0

**Definition:** The product works, but the issue creates meaningful friction for a significant portion of users, or the bug is noticeable and reproducible even if it doesn't block the core flow.

**Response:** Log with full reproduction details. Add to Release 2.0 backlog. Do not fix during the active trial.

**Time to resolution:** Release 2.0 sprint.

**Escalation rule:** If the same P2 issue appears independently in 3+ sessions, consider whether it should be elevated to P1.

| Condition | P2 |
|---|---|
| Score ring shows `NaN` for edge-case domains | ✅ |
| PDF report download fails for specific scan IDs | ✅ |
| Date formatting shows UTC instead of local time | ✅ |
| Trust level label missing or untranslated in a specific scenario | ✅ |
| "Try again" button triggers duplicate fetch | ✅ |
| UX friction observed in 3+ sessions independently | Consider escalating |

---

### P3 — Log and Review Post-Beta

**Definition:** Minor issues, cosmetic bugs, and UX friction that appears in isolated sessions and doesn't affect trust in the product or completion of the core flow.

**Response:** Log. Do not prioritize for Release 2.0 until Beta findings are fully reviewed.

**Time to resolution:** Decided at Release 2.0 planning session.

| Condition | P3 |
|---|---|
| Minor spacing or alignment issue on desktop | ✅ |
| A single user found one translation awkward | ✅ |
| Score ring appears slightly small on a specific phone model | ✅ |
| "Back to Sites" link not immediately visible | ✅ |
| Feature Request mentioned by only one user | ✅ |

---

### Out of Scope — Do Not Schedule

**Definition:** Items that fall outside the product's stated purpose as a Website Trust & Security Advisor. These are never added to the backlog regardless of how many users request them.

**Response:** Log for visibility. Respond to user politely. Do not add to any backlog.

| Item | Reason |
|---|---|
| Port scanning | Offensive capability — product philosophy prohibits |
| XSS / SQLi testing | Active exploitation — permanently forbidden |
| Bulk scan / crawler | Requires ownership proof per domain |
| Raw HTTP header display | Product strips this intentionally |
| IP address disclosure | Infrastructure reconnaissance |
| Competitive analysis features | Out of scope |

---

## Priority Assignment Matrix

| Classification (from Issue Guide) | Default Priority |
|---|---|
| Security Blocker | P0 |
| Product Blocker | P1 |
| UX Friction (isolated, 1–2 sessions) | P3 |
| UX Friction (widespread, 3+ sessions) | P2 |
| Bug (blocks core flow) | P1 |
| Bug (noticeable, reproducible, non-blocking) | P2 |
| Bug (cosmetic, isolated) | P3 |
| Documentation Gap | P3 (unless widespread → P2) |
| Feature Request (in-scope) | P3 (input to 2.0 planning) |
| Feature Request (out of scope) | Out of Scope |
| Out of Scope | Out of Scope |

---

## Priority Register Template

Use this table to log all issues during the trial:

| ID | Date | User | Classification | Priority | Description | Status |
|---|---|---|---|---|---|---|
| B-001 | | V-01 | UX Friction | P3 | User didn't see trust level badge | Open |
| B-002 | | O-02 | Documentation Gap | P3 | DNS TXT value not shown in product | Open |
| ... | | | | | | |

**Status values:** Open · In Progress · Fixed (with commit SHA) · Won't Fix · Out of Scope

---

## Decision Rules During Trial

1. **Never add a feature during the active trial** — feature requests are logged, not built.
2. **P0 and P1 are the only code changes allowed** during Days 1–17.
3. **P1 patches must pass CI** before deployment — no exceptions.
4. **The founder makes all priority calls** — engineering does not self-assign priority.
5. **Widespread P2 (3+ sessions) is reviewed daily** — if it reaches 5+ sessions, elevate to P1.
6. **Out of Scope is final** — no escalation path. The product is an Advisor, not a Scanner.

---

*Related: `ISSUE_CLASSIFICATION_GUIDE.md` · `POST_BETA_RELEASE_WORKFLOW.md`*
