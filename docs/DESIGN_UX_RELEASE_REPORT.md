# Design & UX Release Report — Release 1.1

**Product:** Website Trust & Security Advisor  
**Release:** 1.1 — Design & UX Refresh  
**Date:** 2026-06-28  
**Branch:** `release/1.1-design-ux-refresh`  
**Status:** Build clean · TypeScript clean · No backend changes

---

## 1. Build & Type Check

| Check | Result |
|---|---|
| `npx tsc --noEmit` | ✓ No errors |
| `npm run build` | ✓ 22 pages compiled, 0 errors |
| Backend diff | ✓ Zero files changed under `backend/` |
| New dependencies | ✓ None added |

---

## 2. New Components

| File | Purpose |
|---|---|
| `frontend/src/components/BrandLogo.tsx` | Reusable SVG shield+checkmark logo with app name. Client component. Used across all pages. |
| `frontend/src/components/AppFooter.tsx` | Shared footer with correct contrast, Roadmap + Terms + Privacy links. Client component. |
| `frontend/src/components/LanguageToggle.tsx` | Locale switcher using `useLocale()` + `usePathname()`. Switches to the same page in the other locale. No props required. |

---

## 3. New Pages (Placeholder, Frontend-Only)

| Route | File | Description |
|---|---|---|
| `/[locale]/terms` | `src/app/[locale]/terms/page.tsx` | Terms of Service placeholder. Uses BrandLogo + AppFooter + LanguageToggle. |
| `/[locale]/privacy` | `src/app/[locale]/privacy/page.tsx` | Privacy Policy placeholder. Same structure as terms. |

Both pages are static, contain no logic, and link to no API. Message keys added to both `en.json` and `ar.json`.

---

## 4. Modified Components

### `BrandLogo` (new) — SVG Shield Logo
- Replaced the inline `"T"` text-in-a-box placeholder across all pages
- 32×32 SVG with blue rounded-rect background, translucent shield outline, white checkmark
- Accepts an optional `href` prop so authenticated pages can link to `/sites` instead of `/`

### `ScanForm.tsx`
- Replaced grey-dot preview cards with descriptive SVG inline icons: Globe (Browse), Envelope (Email), User (Account), Lock (Payment)
- Added a two-ring animated loading spinner that replaces the preview cards during scan
- Improved button focus ring: `focus-visible:ring-2 focus-visible:ring-blue-400`
- Error message now has `role="alert"` for screen readers
- Form card shadow: `shadow-2xl shadow-black/40` for depth on dark background

### `TrustResult.tsx`
- Score ring: increased to `w-32 h-32`, added `ring-offset-2 ring-offset-slate-900` for better visual separation
- Score number: `text-5xl` (was `text-4xl`), `tabular-nums` for consistent number width
- Level label: converted from plain text to a pill badge with `border` + colored background
- Domain display: `font-mono text-xs text-slate-500` to distinguish it from body text
- Pass/Fail check rows: replaced ✓/✗ characters with proper SVG `PassIcon`/`FailIcon` components
- Warnings section: adjusted opacity tokens (`bg-amber-500/8`) for more subtle warning tint
- Reset button: added border + hover border to make it feel like a button, not just text
- Decision cards: reduced opacity suffixes from `/30` to `/15`-`/20` for lighter backgrounds

### `CopyButton.tsx`
- Added `CheckIcon` and `CopyIcon` SVG inline icons
- Added `scale-95` on the copied state for a tactile press animation
- Added `duration-200` to the transition for smooth state change
- Added `aria-label` attribute that updates with the copied/not-copied state

### `AuthForm.tsx`
- Wrapped the form in a page layout with `BrandLogo`, `LanguageToggle`, and `AppFooter`
- Previously the auth form filled the full viewport with no header/footer
- Form inputs use `rounded-xl` (was `rounded-lg`) for consistency with other cards
- Submit button changed from `bg-sky-600` to `bg-blue-600` for palette consistency
- Link to alternate auth mode (login ↔ register) moved inside the card with a border separator

### `FixPlan.tsx`
- No functional changes — already well-structured
- Visual unchanged (issue cards, priority badges, CopyButton already using updated component)

---

## 5. Modified Pages

| Page | Change |
|---|---|
| `[locale]/page.tsx` (homepage) | Replaced inline header/footer with `BrandLogo` + `LanguageToggle` + `AppFooter`; removed unused imports |
| `[locale]/roadmap/page.tsx` | Replaced inline header/footer with shared components; removed `use(params)` call (locale from next-intl context) |
| `[locale]/sites/page.tsx` | Replaced inline logo with `BrandLogo`; added `StatusDot` component for site status; "View Scans" link now styled as a bordered button |
| `[locale]/sites/[siteId]/scans/page.tsx` | Replaced inline logo with `BrandLogo`; scan score displayed in a colored rounded square instead of plain number |
| `[locale]/sites/[siteId]/scans/[scanId]/page.tsx` | Replaced inline logo with `BrandLogo`; score ring uses same `badge` pattern as `TrustResult`; removed unused `tc` translation instance |

---

## 6. Configuration Changes

### `tailwind.config.ts`
- Added `brand.100`, `brand.400`, `brand.900` shades to complete the blue palette
- Added `trust` semantic color tokens: `trust.high` (emerald), `trust.good` (blue), `trust.medium` (amber), `trust.low` (red)
- Added `boxShadow.glow-blue` and `boxShadow.glow-green` for optional glow effects
- `borderRadius` `2xl`/`3xl` confirmed (Tailwind already includes these; no conflict)

### `globals.css`
- No changes needed — existing RTL focus ring and logical property utilities cover all cases

---

## 7. Translation File Changes

Both `en.json` and `ar.json` updated identically:

| Namespace | Keys Added |
|---|---|
| `footer` | `terms_link`, `privacy_link` |
| `terms` | `page_title`, `coming_soon` |
| `privacy` | `page_title`, `coming_soon` |

Existing keys: unchanged. No key was renamed or removed.

---

## 8. Logo & Visual Identity

**Before:** A `w-8 h-8 bg-blue-600 rounded-lg` div with the letter "T" in white  
**After:** An SVG shield with a white checkmark inside a blue rounded rectangle

The shield-and-checkmark is a universally recognized trust/security symbol. It immediately communicates the product purpose without reading the app name.

---

## 9. Footer Contrast Fix

**Before:** `text-slate-700` — near-invisible on `bg-slate-950` background (contrast ratio < 2:1)  
**After:** `text-slate-500` — clearly readable; meets minimum contrast for decorative text

Footer now also includes Roadmap, Terms, and Privacy links at equal visual weight.

---

## 10. Header Consistency

All pages (public and authenticated) now use the same header pattern:
- **Public pages** (home, roadmap, terms, privacy, login, register): `BrandLogo` + `LanguageToggle`
- **Authenticated pages** (sites, scans, scan detail): `BrandLogo` + `LogoutButton`

Previously each page had its own inline header definition; the logo was duplicated 6 times.

---

## 11. RTL/LTR Compatibility

- `LanguageToggle` uses `useLocale()` + `usePathname()` — always links to the same page in the other locale
- `AuthForm` password toggle uses `end-0` (logical property) instead of `right-0` — flips correctly in Arabic
- `AuthForm` password field uses `pe-10` instead of `pr-10` — correct in Arabic layout
- SVG icons use `currentColor` — inherits text color correctly in both directions
- No hardcoded `left`/`right` positioning introduced

---

## 12. Responsive Layout

All new and modified components use:
- `flex-col` → `sm:flex-row` breakpoints where applicable
- `max-w-xl` content constraint with `w-full` base
- No fixed pixel widths except SVG dimensions (32×32, 16×16, 14×14, 12×12)

Minimum 375px width is supported by all existing flex layouts (no changes needed).

---

## 13. Accessibility

| Element | Change |
|---|---|
| Scan form submit | Added `focus-visible:ring-2 focus-visible:ring-blue-400` |
| BrandLogo link | Added `focus-visible:ring-2 focus-visible:ring-blue-500 rounded-lg` |
| AppFooter nav links | Added `focus-visible:ring-2 focus-visible:ring-blue-500` |
| LanguageToggle | Added `focus-visible:ring-2 focus-visible:ring-blue-500` |
| CopyButton | Added `aria-label` that updates with copy state |
| Error messages | `role="alert"` on scan form error |
| SVG icons | `aria-hidden="true"` on all decorative SVGs |

---

## 14. What Was Not Changed

- No backend files modified (`backend/` diff: empty)
- No API contracts changed
- No scanner logic changed
- No scoring algorithm changed
- No auth or session changes
- No new npm packages added
- No database migrations
- No Rate limiting changes
- No raw headers or IP addresses exposed

---

## 15. Known Gaps (Post-1.1 Backlog)

| Item | Notes |
|---|---|
| Terms/Privacy page content | Placeholder only — full content required before public launch (Beta Plan prerequisite) |
| Lighthouse audit score | Not yet measured in this PR; target ≥ 80 on mobile |
| Bilingual review | Arabic strings carry over from 1.0.1; a bilingual user review is recommended before beta |
| Admin pages header | Admin pages retain their existing no-header layout; not in scope for 1.1 |
| Favicon | Still the default Next.js favicon; custom favicon deferred to a dedicated design task |
