# Engineering Notes
## Website Trust & Security Advisor

**Last updated:** 2026-06-29  
**Audience:** Engineers making changes to this codebase  
**Purpose:** Record the reasoning behind key decisions so future engineers understand what they're modifying and why

---

## Files That Must Not Be Changed Without a Security Review

These files implement the core security controls. A subtle change can silently break a protection without any test failing immediately:

| File | What it protects | Risk of incorrect change |
|---|---|---|
| `backend/app/core/url_validator.py` | SSRF protection — 16 blocked network ranges | A missed range can allow the server to be used to probe internal infrastructure |
| `backend/app/core/scan_policy.py` | Permanently forbidden scan types | Removing a forbidden type enables offensive capability |
| `backend/app/core/safe_scan_runner.py` | 10-step mandatory pipeline | Reordering steps or short-circuiting any gate can bypass security controls |
| `backend/app/core/security.py` | JWT, bcrypt, refresh token rotation | Auth bugs can enable account takeover or token replay |
| `backend/app/api/deps.py` | Auth dependency injection | Controls who can call every protected endpoint |
| `backend/alembic/versions/` | Database schema migrations | Must remain sequential; modifying applied migrations corrupts production schema |

**Rule:** If you need to change any of these files, write the specific reason in the PR description. The PR must reference what beta finding or security finding justified the change.

---

## Why the Safe Scan Runner Is a Sequential Pipeline

The 10-step pipeline in `safe_scan_runner.py` is sequential by design. The steps are not arbitrary — each one depends on the previous:

1. The Do Not Scan check happens **before DNS resolution** so that a domain in the blocklist cannot be resolved to an IP that avoids the blocklist.
2. The SSRF check happens **before** the HTTP client sends any request, and again **after** DNS resolution (because a hostname can resolve to a private IP after passing the initial check).
3. Rate limiting happens **after** URL validation so invalid URLs don't consume rate limit budget.
4. Audit logging happens **both before and after** the scan so that attempted scans are recorded even if they fail.

Reordering steps to gain a performance improvement can silently break the security model.

---

## Why the Scan Policy Engine Is Pure Functions

`scan_policy.py` contains only pure functions with no I/O, no database access, and no async operations. This is intentional:

- It can be called synchronously from any context without async overhead
- It can be unit-tested exhaustively without mocking any dependencies
- The permanently forbidden type list is a Python constant, not a database configuration, so it cannot be changed at runtime by an admin or API call

If you need to add a new scan type, the forbidden list in `scan_policy.py` must be reviewed. Never make the forbidden list configurable at runtime.

---

## Why SSRF Protection Checks After DNS Resolution

The SSRF check in `url_validator.py` uses a redirect hook that re-validates the resolved IP after every redirect. This is because:

- A domain can be configured to resolve to a private IP (DNS rebinding attack)
- An initial IP check at parse time does not protect against redirects to internal addresses
- The HTTP client is configured to re-validate every redirect destination

This means the SSRF protection adds a DNS round trip before every scan. That is intentional and must not be removed to improve performance.

---

## Why Refresh Tokens Are Stored as SHA-256 Hashes

Refresh tokens are stored as SHA-256 hashes in the `refresh_tokens` table, not as plaintext. This is because:

- If the database is compromised, stored plaintext tokens could be used to impersonate users without knowing their passwords
- SHA-256 is deterministic (token → hash is always the same), so lookup is possible without storing plaintext
- On rotation, the old hash is deleted and a new token+hash pair is issued

The access tokens (JWT) are not stored at all — they are verified by signature only. This is also intentional.

---

## Why Owner Isolation Is at the ORM Level, Not the API Level

Every query that returns a site or scan result includes an `owner_id` filter in the SQLAlchemy query, not just in the API route handler. The reasoning:

- An API-level check can be accidentally bypassed if a new route is added and the check is forgotten
- An ORM-level filter means that even if a new route is added, it cannot return another owner's data because the query physically cannot find it

Do not change site or scan queries to remove the `owner_id` filter, even when it appears redundant.

---

## Why the Admin Has Dual-Path Authentication

The admin has two valid authentication paths:
1. JWT with `role=admin` or `role=super_admin`
2. `X-Admin-Key` header compared in constant time

The dual-path exists because:
- JWT tokens expire (15 minutes) and require a refresh flow
- For programmatic/API access (e.g., monitoring scripts, internal tooling), a long-lived API key is more practical
- The constant-time comparison prevents timing attacks on the API key

Both paths are active simultaneously. This is not a fallback — either path is valid independently.

---

## Why the Trust Score Is Computed from Public Signals Only

The Trust Score intentionally excludes anything that requires privileged access to the target system. The constraints are:

1. **Legal:** Probing a system the user does not own may violate computer access laws in many jurisdictions
2. **Product philosophy:** The product answers "what would a visitor observe?" not "how secure is this system internally?"
3. **Liability:** Claiming a system is "secure" based on a passive public check would be inaccurate and misleading

The `scan_policy.py` permanently forbidden list enforces this at the code level.

---

## Why Data Minimization Is Applied Before Storage

Scan results are sanitized before being stored in the database. Raw HTTP response headers, server software versions, internal IP addresses, and response bodies are stripped. The reasons:

- Stored raw headers can expose infrastructure information of the scanned site
- If the database is compromised, sanitized data has minimal intelligence value
- The product does not need raw data to compute the Trust Score

The `trust_score.py` function returns a sanitized dict, not a raw scanner output. Nothing else is stored.

---

## Why the Reputation Provider Is Mock by Default

The `reputation_checker.py` currently returns "clean" for all domains. This is a known accepted limitation (B1):

- Real reputation providers (Google Safe Browsing, VirusTotal) require API keys and have rate limits
- The mock allows development and testing without external dependencies
- The `REPUTATION_PROVIDER` env var is already wired — replacing it requires only an API key and a provider implementation

This must be replaced before public launch. It is acceptable for the supervised beta because the user cohort is small and known.

---

## Known Accepted Limitations (not bugs)

These are known gaps documented in `docs/LAUNCH_DECISION_REVIEW.md`. They are intentionally accepted for the supervised beta and must be addressed before public launch:

| ID | Item | Why it's accepted now |
|---|---|---|
| B1 | Reputation provider is mock | Small known cohort; replace before public launch |
| B2 | Per-domain rate limit silently passes if Redis is down | Supervised beta; harden before public launch |
| NH1 | No Content-Security-Policy header | Medium risk; add before public launch |
| NH4 | Forgot-password email flow not implemented (UI exists, backend deferred) | Release 2.0 candidate |
| NH5 | No ARIA live regions for scan results | Accessibility gap; Release 2.0 candidate |
| NH6 | No E2E test suite | Unit tests cover core logic; E2E deferred to Release 2.0 |

---

## Naming Conventions

| Context | Convention | Example |
|---|---|---|
| Python files | `snake_case` | `safe_scan_runner.py` |
| Python classes | `PascalCase` | `SafeScanRunner` |
| Python functions | `snake_case` | `run_public_trust_scan()` |
| TypeScript components | `PascalCase` | `TrustResult.tsx` |
| TypeScript utilities | `camelCase` | `parseLocale.ts` |
| Database tables | `snake_case + plural` | `scan_results` |
| Database columns | `snake_case` | `created_at`, `owner_id` |
| API routes | `kebab-case` | `/public-trust-check` |
| i18n keys | `dot.notation` | `trustResult.scoreLabel` |
| Environment variables | `SCREAMING_SNAKE_CASE` | `SECRET_KEY`, `ALLOWED_ORIGINS` |

---

## The Code Freeze Rule

During Days 1–17 of the beta trial:
- No code changes except P0 (data exposure, auth bypass) and P1 (complete flow broken) emergency patches
- P1 patches must pass CI before deployment
- P0 patches require: immediate investigation, minimal targeted fix, CI pass, staging verification, then deployment

This freeze exists so that observations during the trial reflect a stable product, not a moving target.
