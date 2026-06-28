# Design & UX Release Plan — Release 1.1

**Product:** Website Trust Advisor  
**Release:** 1.1 — Design & UX  
**Prerequisite:** Release 1.0.1 (Production Hardening) complete  
**Date:** 2026-06-28

---

## Objective

Improve visual identity, interaction quality, and bilingual (Arabic/English) experience without changing any product logic, API contracts, scan algorithms, or backend code.

Every item in this release is frontend-only. No backend PR may be opened under this release.

---

## Principles

1. **No logic changes.** Scan form behavior, scoring, trust levels, Fix Plan content, and error handling are frozen during 1.1.
2. **No new routes.** Only existing pages are restyled. Shell placeholder pages are acceptable only if they contain no logic and link to no API.
3. **No backend changes.** Any item that requires a new API field, endpoint, or model change is out of scope.
4. **Accessibility first.** Every visual change must maintain or improve WCAG 2.1 AA compliance for contrast, focus states, and ARIA labels.
5. **Bilingual parity.** Every UI change must be verified in both Arabic (RTL) and English (LTR) layouts.

---

## In Scope

### Visual Identity

| Item | Notes |
|---|---|
| Logo and wordmark | Replace placeholder text with a proper SVG mark |
| Color palette | Refine primary, secondary, and semantic colors in `tailwind.config` |
| Typography | Select and apply a consistent type scale; ensure Arabic font renders correctly |
| Favicon | Replace default Next.js favicon |

### Layout & Components

| Item | Notes |
|---|---|
| Homepage hero section | Improve hierarchy, scan form prominence, and value proposition copy placement |
| Trust Score card | Visual polish — score ring, level badge, color-coded confidence |
| Usage Decision cards | Icon refinement, card spacing, verdict color consistency |
| Fix Plan component | Code block styling, copy button feedback animation |
| Navigation bar | Logo placement, language switcher, authenticated vs. unauthenticated states |
| Footer | Links, locale, and legal text placement |

### Responsive Layout

| Item | Notes |
|---|---|
| Mobile breakpoints | All pages must be usable at 375px width |
| Tablet breakpoints | Check 768px layout for scan result and Fix Plan pages |

### Micro-interactions

| Item | Notes |
|---|---|
| Loading states | Spinner or skeleton for scan in progress |
| Copy button | "Copied!" confirmation with short timeout |
| Form validation | Inline error messages styled consistently |
| Language toggle | Smooth direction transition without full page reload flash |

### Arabic / English Consistency

| Item | Notes |
|---|---|
| RTL spacing | Padding/margin direction should flip for Arabic layout |
| Font sizing | Arabic script may need slightly larger base font size for readability |
| Directionality | All icons and arrows must respect `dir` attribute |
| Translation review | Have a bilingual reviewer verify all Arabic strings for naturalness |

### Accessibility

| Item | Notes |
|---|---|
| Contrast ratios | All text must meet WCAG AA (4.5:1 for body, 3:1 for large text) |
| Focus indicators | Visible focus ring on all interactive elements |
| ARIA labels | All icon-only buttons must have `aria-label` |
| Skip links | Add skip-to-content link for keyboard navigation |

---

## Out of Scope

- Scan logic or scoring algorithm changes
- New API endpoints or backend models
- New pages or routes (unless purely static placeholder with no logic)
- Auth flow changes
- Security policy changes
- Any change that requires modifying `backend/`
- PDF export or report generation changes
- New scanner types

---

## Execution Order

1. **Design tokens** — Lock color palette and type scale in `tailwind.config` first; all subsequent changes build on this
2. **Component library audit** — Identify all components that need restyling; create a tracking list
3. **Homepage** — Highest visibility; start here after tokens are locked
4. **Scan result + Trust Score card** — Core visitor experience
5. **Fix Plan** — Core owner experience
6. **Navigation + footer** — Frame for all pages
7. **Responsive pass** — Mobile and tablet review after desktop polish is done
8. **Accessibility audit** — Run Lighthouse and axe after all visual changes
9. **Bilingual review** — Arabic/English QA pass with RTL layout verification
10. **Build + CI green** — `npx tsc --noEmit` and `npm run build` must pass before PR

---

## Success Criteria

- [ ] Lighthouse mobile score ≥ 80 on all three main pages (home, scan result, Fix Plan)
- [ ] Arabic and English layout reviewed by a bilingual user
- [ ] No regressions: CI green, full manual QA checklist from `RC1_REVIEW_REPORT.md §4` passed
- [ ] No backend changes introduced (verify with `git diff main -- backend/`)
- [ ] `npx tsc --noEmit` exits with no errors
- [ ] `npm run build` completes successfully

---

## Risks

| Risk | Mitigation |
|---|---|
| UI changes accidentally affect scan form submission behavior | Run full Visitor QA checklist after every scan-form-adjacent change |
| RTL layout changes break LTR layout | Test both locales on every PR; add locale toggle to manual QA |
| Font loading adds render-blocking resources | Use `next/font` for self-hosted fonts; measure Lighthouse before and after |
| Component restyling breaks existing Tailwind class logic | Prefer adding classes over replacing; review diff carefully |
| Color changes reduce contrast below WCAG AA | Run contrast checker on every color pair change |

---

## PR Convention for 1.1

Each PR in this release must:
- Be scoped to a single component or page area
- Include before/after screenshots in the PR description
- Include the output of `npx tsc --noEmit` (no errors)
- Include manual QA confirmation that the relevant page still works in both locales
- Not touch any file under `backend/`
