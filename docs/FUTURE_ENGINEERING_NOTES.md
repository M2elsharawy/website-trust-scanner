# Future Engineering Notes
## Website Trust & Security Advisor

**Last updated:** 2026-06-29  
**Audience:** A developer or team returning to this codebase after an extended absence  
**Purpose:** The things you need to know *before* you start reading code — context that isn't obvious from the files themselves

---

## The Most Important Thing to Understand First

This product is a **Website Trust Advisor**, not a security scanner. That distinction is not marketing — it is a hard technical constraint encoded in `backend/app/core/scan_policy.py`. The permanently forbidden scan type list in that file cannot be worked around without explicitly removing the enforcement. Before adding any new capability, read `scan_policy.py` and ask: does this capability belong in a Trust Advisor, or in a vulnerability scanner?

If you are tempted to add port scanning, XSS testing, content crawling, or raw header exposure — stop. Those are out of scope by design, not by omission.

---

## Where to Start If You've Never Seen This Codebase

1. Read `docs/ARCHITECTURE_OVERVIEW.md` — understand what the system does at the level of user flows and security guarantees before reading any code
2. Read `docs/ENGINEERING_NOTES.md` — understand why key decisions were made before changing anything
3. Read `docs/REPOSITORY_MAP.md` — understand where every file lives
4. Read `docs/LOCAL_SETUP.md` — get a working environment
5. Run `pytest` from `backend/` — 214 tests should pass
6. Run `npx tsc --noEmit` from `frontend/` — zero TypeScript errors
7. Run `npm run build` from `frontend/` — 24 routes, zero errors

If any of steps 5–7 fail, fix that first before making any changes.

---

## The State of the Codebase When This Was Written (2026-06-29)

- Five releases delivered: MVP, 1.0.1 (hardening), 1.1 (UX), 1.2 (beta prep), Pre-Launch
- The product is in a supervised beta trial (invitation-only, 8–13 users)
- All automated checks pass: TypeScript clean, build clean, 214/214 tests passing
- PR #53 (Release 1.2 Beta Trial Preparation) is open as a draft — contains frontend improvements waiting for the deployer to confirm TB1–TB5 before merging
- PR #58 (Engineering Final Handover) is open as a draft — docs-only
- Main branch SHA: `6366a08`

---

## Things That Might Surprise You

**The frontend uses Next.js App Router with next-intl v4.** All routes are under `src/app/[locale]/`. The locale can be `ar` or `en`, default is `ar`. The file `src/proxy.ts` is the next-intl middleware (renamed from `middleware.ts` because Next.js 16 deprecated that name). Do not rename it back.

**There are two celery-related files.** `backend/app/tasks/scheduled_scans.py` contains both the Celery app instance and task definitions. `backend/app/workers/celery_app.py` also creates a Celery app instance for the worker process configuration. This duplication is intentional for deployment separation — the worker uses the workers module, the tasks use the tasks module.

**The admin has dual authentication.** A request to an admin endpoint can be authenticated by either a JWT with `role=admin` or by the `X-Admin-Key` header. Both are active simultaneously. The key is compared in constant time.

**The reputation checker is a mock.** `backend/app/scanners/reputation_checker.py` currently returns "clean" for all domains regardless of the input. This is a known accepted limitation (B1) for the supervised beta. The `REPUTATION_PROVIDER` env var is already wired to switch to a real provider — it just needs an API key.

**The forgot-password UI exists but the backend endpoint does not.** `frontend/src/app/[locale]/forgot-password/page.tsx` renders a form, but there is no corresponding backend endpoint. This was deferred to Release 2.0. Do not assume the flow works end-to-end.

**The `docker-compose.yml` worker and beat services exist but Celery tasks are minimal.** The scheduled scan infrastructure is present but the actual scheduled tasks are minimal. Verify what Celery Beat jobs are configured before relying on any scheduled behavior.

**i18n keys must stay in sync.** The `frontend/src/messages/ar.json` and `en.json` files must have identical key sets — 256 keys each as of this writing. Adding a key in one without the other will cause runtime errors in the opposite locale. The CI does not currently check for key parity.

---

## What the Beta Trial Was Testing (context for interpreting findings)

The supervised beta ran with 8–13 invited users across three cohorts:
- **Visitor testers (5–8 people):** Did the Trust Score communicate trustworthiness without explanation?
- **Owner testers (2–4 people):** Could a site owner complete DNS verification and understand the Fix Plan?
- **Technical reviewer (1 person):** Were the Fix Plan developer instructions accurate and safe?

If you are looking at Release 2.0 planning after the trial, the findings are in `docs/BETA_TRIAL_FINDINGS.md` (created on Day 18 of the trial). Use `docs/POST_BETA_RELEASE_WORKFLOW.md` to understand the process for converting findings into Release 2.0 scope.

---

## Things That Are Deliberately Simple (and Should Stay That Way)

**The Trust Score algorithm is straightforward.** It is a weighted sum of binary or categorical checks. It is not a machine learning model. Do not replace it with something more complex without evidence that complexity improves user understanding — the goal is explainability, not precision.

**The Fix Plan cards are static per check type.** There are six check categories (HTTPS, SSL, headers, DNS, reputation, general). The Fix Plan for each category is generated from a fixed template per finding type, not from AI or dynamic generation. This is intentional — the instructions must be accurate and safe, not creative.

**The Admin UI is read-only by design.** There are no mutation endpoints in the admin routes (no status update, no scan trigger, no bulk operation). Adding mutations requires explicit security review of authorization boundaries.

---

## Known Technical Debt (acceptable, not critical)

| Item | Where | Why it's accepted |
|---|---|---|
| Celery beat job list is minimal | `tasks/scheduled_scans.py` | Beta doesn't need heavy automation |
| No E2E test suite | — | Unit tests cover logic; E2E deferred to Release 2.0 |
| Data retention jobs not verified in production | `DATA_RETENTION_POLICY.md` | Small beta; manual review sufficient |
| No Content-Security-Policy header | `main.py` | Acceptable medium risk for supervised beta |
| Forgot-password backend not implemented | `auth.py` | Release 2.0 candidate |
| Reputation provider is mock | `reputation_checker.py` | Replace before public launch |
| Per-domain rate limit passes silently if Redis is down | `safe_scan_runner.py` | Harden before public launch |

---

## If You're Building Release 2.0

Before writing any code:

1. Read `docs/BETA_TRIAL_FINDINGS.md` (created on Day 18 of the trial)
2. Read `docs/POST_BETA_RELEASE_WORKFLOW.md` — follow the 8-step process
3. Confirm the Release 2.0 scope is documented in `docs/RELEASE_PLAN.md §2.0` with specific beta finding references
4. Do not add any feature that was not observed as a problem during the trial

The post-beta workflow document has a rule: every PR in Release 2.0 must reference the Beta issue ID it resolves. Do not add scope without a finding to justify it.

---

## If You're Launching to the Public

Before opening public registration:

1. Replace the mock reputation provider (`REPUTATION_PROVIDER` env var + `reputation_checker.py`)
2. Implement the forgot-password email flow
3. Add Content-Security-Policy header to `main.py`
4. Add Terms of Service content to the `terms/` page
5. Add Privacy Policy content to the `privacy/` page
6. Wire error monitoring (Sentry or equivalent)
7. Configure uptime monitoring (external ping)
8. Verify Celery Beat data retention jobs are running
9. Add `robots.txt` to `frontend/public/` (currently missing — do not advertise the domain until ready)
10. Harden the per-domain rate limit Redis fallback behavior

None of these require architecture changes. They are configuration and content tasks. See `docs/LAUNCH_DECISION_REVIEW.md §Required Before Public Launch` for the full list.

---

## How to Make a Change Safely

For any change to core pipeline, auth, or scanner files:

1. Write down the specific problem you're solving (one sentence)
2. Write down what the change does (one sentence)
3. Write down what could go wrong (one sentence)
4. Run `pytest` — all 214 tests must pass after your change
5. Run `npx tsc --noEmit` — zero TypeScript errors
6. Run `npm run build` — 24 routes, zero errors
7. Open a PR with a single concern — no bundling unrelated changes
8. Reference the beta finding or bug report that justified the change

For security-critical files (`url_validator.py`, `scan_policy.py`, `safe_scan_runner.py`, `security.py`, `deps.py`): add a note in the PR description explaining the security impact of the change.
