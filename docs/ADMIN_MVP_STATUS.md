# Admin MVP Status

Documents the current state of the admin frontend as of the MVP closure pass (PRs #37–#39).

## What exists

### Pages

| Route | File | Status |
|---|---|---|
| `/admin` | `app/[locale]/admin/page.tsx` | Built — admin home with MVP notice |
| `/admin/leads` | `app/[locale]/admin/leads/page.tsx` | Built — read-only lead list |
| `/admin/leads/[id]` | `app/[locale]/admin/leads/[id]/page.tsx` | Built — read-only lead detail |

### Access control

All three pages require a valid `access_token` cookie and a role of `admin` or `super_admin`, verified server-side via `GET /api/v1/auth/me`. Unauthenticated or unauthorized requests redirect immediately.

### Data displayed

**Lead list** (`/admin/leads`): domain, status label, lead score, last audit date, creation date.

**Lead detail** (`/admin/leads/[id]`): domain, status label, lead score, last audit date, creation date, last updated date, notes (if present).

### What is intentionally absent

- `added_by` — excluded to avoid exposing admin email/username in the UI.
- Raw scan data, HTTP response headers, IP addresses, secrets.
- No outbound scan trigger, no status update, no export.

## What is read-only

Everything. The admin MVP is display-only. There are no forms, buttons, or mutations of any kind.

## What is deferred

The items below are out of scope for this MVP and require explicit approval before implementation:

- Status update (change lead status from the UI)
- Scan trigger (initiate a lead audit from the UI)
- Authorization record (record approval before deeper scan)
- Lead-to-owner conversion
- Export / PDF report
- Audit log UI
- Analytics / scan trends
- Do-not-scan management UI
- Deep scan access (any scan must still pass through the Safe Scan Runner)

## PRs that built this

| PR | What it added |
|---|---|
| #37 | Admin route protection + minimal `/admin` shell |
| #38 | `/admin/leads` read-only list |
| #39 | `/admin/leads/[id]` read-only detail |
