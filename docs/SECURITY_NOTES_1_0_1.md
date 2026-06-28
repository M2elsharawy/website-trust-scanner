# Security Notes — Release 1.0.1

**Date:** 2026-06-28  
**Scope:** CVE assessment and dependency security review for Release 1.0.1 Production Hardening

---

## CVE GHSA-36qx-fr4f-26g5 — Next.js i18n Middleware Bypass

### Summary

| Item | Value |
|---|---|
| CVE ID | GHSA-36qx-fr4f-26g5 |
| Affected versions | Next.js < 15.2.3 |
| Project version | Next.js **16.2.9** |
| Status | **NOT AFFECTED** |
| Action required | None |

### Assessment

The advisory affects Next.js versions below 15.2.3. This project runs Next.js 16.2.9, which is a later major version and is not affected by the vulnerability.

The vulnerability involves an i18n middleware bypass that could allow unauthenticated access to protected routes. In this project, route protection uses cookie presence checks in the middleware (now `proxy.ts`) plus server-side session validation on every authenticated API call. Even if a locale bypass were possible in an older version, the backend API enforces authentication independently.

**Blocker B3 from RC1 Review Report §7 is closed.**

---

## CVE GHSA-qx2v-qp2m-jg93 — PostCSS ReDoS

### Summary

| Item | Value |
|---|---|
| CVE ID | GHSA-qx2v-qp2m-jg93 |
| Severity | Moderate |
| Affected package | `postcss < 8.4.31` |
| Location | `node_modules/next/node_modules/postcss` (bundled by Next.js) |
| Status | **Upstream dependency — cannot fix independently** |
| Action required | Monitor Next.js releases; upgrade when a patched version ships |

### Assessment

The vulnerable `postcss` copy is bundled inside Next.js's own `node_modules`. It is not directly imported by application code and is only used during the CSS build step. The `npm audit fix --force` suggestion would downgrade Next.js to 9.3.3 — this is not acceptable and must not be applied.

**Risk in this application:** Minimal. PostCSS ReDoS requires passing attacker-controlled CSS through the build pipeline, which does not occur at runtime in a deployed Next.js application. This is a build-time tool, not a runtime risk.

**Mitigation:** Track the Next.js changelog. When a version ≥ 16.2.9 ships with a patched postcss bundled, upgrade.

---

## `passlib` + `bcrypt 4.x` Version Mismatch

### Summary

| Item | Value |
|---|---|
| Package | `passlib==1.7.4` + `bcrypt==4.2.1` |
| Symptom | Warning at startup: `passlib: error reading bcrypt version` |
| Authentication impact | **None** — passwords hash and verify correctly |
| Status | Documented — fix deferred pending dependency audit |

### Assessment

`passlib 1.7.4` reads `bcrypt.__about__.__version__` to detect the bcrypt version. The `__about__` module was removed in `bcrypt 4.0.0`. This causes a version-detection warning at startup that passlib catches internally. All password hashing and verification operations work correctly.

**Fix path:** Pin `bcrypt<4.0.0` in `requirements.txt` after verifying compatibility with all other packages that depend on `cffi` (bcrypt 3.x uses cffi; bcrypt 4.x is Rust-based and does not). Scheduled for a dedicated dependency update PR to allow isolated testing.

---

## middleware.ts → proxy.ts Rename

### Summary

| Item | Value |
|---|---|
| Next.js deprecation | `middleware` file convention deprecated in Next.js 16 |
| Change | `frontend/src/middleware.ts` → `frontend/src/proxy.ts` |
| Logic change | None — content is identical |
| Status | **Done in this release** |

Next.js 16 emits `⚠ The "middleware" file convention is deprecated. Please use "proxy" instead.` The rename eliminates this build warning. No functional change.

---

## Production Secrets Checklist

The following must be set to non-default values before any production deployment. Current defaults are placeholders only.

| Variable | Default (`.env.example`) | Production requirement |
|---|---|---|
| `SECRET_KEY` | `change-me-in-production` | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ADMIN_API_KEY` | `change-me-admin-key` | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `POSTGRES_PASSWORD` | `change-me-password` | Strong random value |
| `ALLOWED_ORIGINS` | `http://localhost:3000` | Exact production frontend URL only |
| `REPUTATION_PROVIDER` | `mock` | Real provider (`google_safe_browsing` or `virustotal`) |
| `APP_ENV` | `development` | `production` (enables `secure=True` cookies) |

No secrets from `.env.example` may appear in a production deployment. The CI pipeline does not inject `.env` into the build — secrets must be configured via the deployment environment (Docker secrets, cloud secret manager, or platform env vars).

---

## CORS Configuration

`ALLOWED_ORIGINS` must be set to the exact production frontend domain in production. The value `*` is never acceptable for an authenticated application.

Example (production):
```
ALLOWED_ORIGINS=https://app.yourdomain.com
```

`TrustedHostMiddleware` in `backend/app/main.py` enforces the host header. `CORSMiddleware` enforces the origin. Both are active and environment-aware.
