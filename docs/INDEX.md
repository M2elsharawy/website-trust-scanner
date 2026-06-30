# Documentation Index
## Website Trust & Security Advisor

**Last updated:** 2026-06-29  
**Total documents:** 42  
**Main SHA:** `6366a08`

Use this index to find the right document for any question. Documents are grouped by audience and purpose. Within each group they are ordered from "read first" to "reference later."

---

## Start Here (any audience)

| Document | Purpose | When to read |
|---|---|---|
| `README.md` | Project overview, quick start, release history | First document — every new reader |
| `docs/ARCHITECTURE_OVERVIEW.md` | How the system works without implementation detail | Before reading any code |
| `docs/REPOSITORY_MAP.md` | Where every file lives and why | When navigating the codebase for the first time |
| `docs/ENGINEERING_NOTES.md` | Why decisions were made — what not to change | Before modifying any core file |
| `docs/FUTURE_ENGINEERING_NOTES.md` | What a returning team needs to know first | After a long absence from the codebase |

---

## Product Definition

| Document | Purpose | Phase |
|---|---|---|
| `docs/PRD.md` | Product Requirements Document — full scope, user stories | Planning |
| `docs/MVP1_SCOPE.md` | MVP 1 scope boundaries | Planning |
| `docs/PERMISSIONS_TABLE.md` | Role-based permission matrix (Visitor / Owner / Admin) | Planning |
| `docs/SITE_STATUS_TABLE.md` | Site lifecycle state machine | Planning |
| `docs/SCAN_POLICY_TABLE.md` | Allowed and forbidden scan types | Planning — permanent reference |
| `docs/OPEN_QUESTIONS.md` | Original design questions and their resolutions | Historical — all resolved |

---

## Technical Design

| Document | Purpose | Phase |
|---|---|---|
| `docs/TECHNICAL_DESIGN.md` | System architecture, API design, data model overview | Design |
| `docs/FOLDER_STRUCTURE.md` | Original planned folder structure — **superseded by REPOSITORY_MAP.md** | Historical only |
| `docs/DATABASE_SCHEMA.md` | Database tables, relationships, migration history | Design + reference |
| `docs/API_SPECIFICATION.md` | REST API endpoints, request/response shapes | Design + reference |
| `docs/SAFE_SCAN_RUNNER_DESIGN.md` | 10-step mandatory scan pipeline design rationale | Design — do not modify pipeline without reading |
| `docs/OWNER_FIX_PLAN_DESIGN.md` | Fix Plan card types, display logic, developer instruction format | Design |
| `docs/DATA_RETENTION_POLICY.md` | What data is stored, for how long, and how it is deleted | Compliance reference |

---

## Security

| Document | Purpose | Phase |
|---|---|---|
| `docs/SECURITY_RISKS.md` | Original risk register — SSRF, data minimization, auth | Planning |
| `docs/SECURITY_CONTROLS_DESIGN.md` | How each security control is implemented | Design + reference |
| `docs/SECURITY_NOTES_1_0_1.md` | Security changes introduced in Release 1.0.1 | Release reference |
| `docs/SECURITY_REVIEW_CHECKLIST.md` | Pre-release security review checklist | Release gate |
| `docs/PRE_LAUNCH_COMPREHENSIVE_REVIEW.md` | 8-angle comprehensive review before supervised beta | Pre-launch reference |

---

## Development Setup

| Document | Purpose | When to read |
|---|---|---|
| `docs/LOCAL_SETUP.md` | Environment setup, Docker Compose, database migration | First day of development |
| `docs/ADMIN_UI_SCOPE.md` | Admin panel scope boundaries and read-only constraints | Before touching admin routes |
| `docs/ADMIN_MVP_STATUS.md` | Admin MVP completion status | Historical reference |

---

## Release History

| Document | Purpose | Release |
|---|---|---|
| `docs/FINAL_MVP_CLOSURE_REPORT.md` | MVP closure — what was built, what was deferred | MVP |
| `docs/MVP_READINESS_CHECKLIST.md` | MVP readiness gate checklist | MVP |
| `docs/RC1_REVIEW_REPORT.md` | Release candidate 1 review — blockers and accepted risks | RC1 |
| `docs/SECURITY_NOTES_1_0_1.md` | Security hardening changes (Release 1.0.1) | 1.0.1 |
| `docs/DESIGN_UX_RELEASE_PLAN.md` | Design and UX refresh plan (Release 1.1) | 1.1 planning |
| `docs/DESIGN_UX_RELEASE_REPORT.md` | Design and UX refresh completion report | 1.1 closure |
| `docs/RELEASE_1_1_CLOSURE_REPORT.md` | Release 1.1 closure — what changed, what was deferred | 1.1 closure |
| `docs/RELEASE_PLAN.md` | Living release plan — all releases, status, scope | All releases |

---

## Pre-Launch & Beta Planning

| Document | Purpose | When to use |
|---|---|---|
| `docs/LAUNCH_DECISION_REVIEW.md` | Three-tier classification: Beta Blockers / Pre-Public / Nice-to-Have | Before inviting users |
| `docs/OPERATIONAL_BETA_LAUNCH_GATE.md` | TB1–TB5 manual verification commands — deployer checklist | Before first invitation |
| `docs/BETA_TRIAL_PLAN.md` | Beta trial objectives, cohort plan, success criteria | Beta planning |
| `docs/ENGINEERING_HANDOVER.md` | Engineering handover to founder/deployer | Handover point |

---

## Beta Operations (active during trial)

| Document | Purpose | Who uses it |
|---|---|---|
| `docs/BETA_OPERATING_CYCLE.md` | 18-day cycle structure, phases, stop conditions | Founder |
| `docs/BETA_FOUNDER_PLAYBOOK.md` | Session-by-session observation guide | Founder |
| `docs/BETA_FEEDBACK_TEMPLATE.md` | Per-session structured feedback form | Founder |
| `docs/ISSUE_CLASSIFICATION_GUIDE.md` | 7-class taxonomy for every finding | Founder + Engineering |
| `docs/BETA_PRIORITIZATION_FRAMEWORK.md` | P0–P3 priority framework with examples | Founder + Engineering |

---

## Post-Beta

| Document | Purpose | When to use |
|---|---|---|
| `docs/POST_BETA_RELEASE_WORKFLOW.md` | 8-step path from retrospective to Release 2.0 | After Day 18 |

---

## Quick Reference Tables

| Document | Content |
|---|---|
| `docs/PERMISSIONS_TABLE.md` | Role × Action matrix |
| `docs/SITE_STATUS_TABLE.md` | Site lifecycle states |
| `docs/SCAN_POLICY_TABLE.md` | Allowed / forbidden scan types — permanent policy |
