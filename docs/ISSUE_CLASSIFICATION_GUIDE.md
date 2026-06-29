# Issue Classification Guide
## Website Trust & Security Advisor — Release 1.2 Beta

Use this guide to classify every issue observed during the Beta Trial. One issue, one classification. If an issue fits multiple categories, use the highest-severity one.

Classification feeds directly into `BETA_PRIORITIZATION_FRAMEWORK.md`.

---

## Classification Summary

| Class | Stop trial? | Fix during trial? | When to fix |
|---|---|---|---|
| Security Blocker | Immediately | Only after full assessment | Before resuming trial |
| Product Blocker | Suspend affected flow | Yes — P1 | Within 24 hours |
| UX Friction | No | No — unless very widespread | Release 2.0 |
| Bug | No (unless P1) | Only if P1/P2 | Depends on priority |
| Documentation Gap | No | No | Post-trial |
| Feature Request | No | Never during trial | Release 2.0 backlog |
| Out of Scope | No | No | Never (in this product) |

---

## Class 1 — Security Blocker

**Definition:** Any issue that exposes user data, enables unauthorized access, bypasses a security control, or violates the product's privacy contract.

**Decision:** Stop trial. Do not resume until patched, tested, and re-verified.

### Examples

| Issue | Why it's a Security Blocker |
|---|---|
| Trust Score API returns raw HTTP headers from the scanned site | Raw headers may contain server version, internal paths, or tokens |
| IP address of scanned domain appears in the UI or API response | Exposes infrastructure of the scanned site |
| User A can see User B's scan history | Broken owner isolation — data leakage between users |
| SSRF block is not firing: `http://169.254.169.254` returns a scan result | SSRF protection bypassed |
| Admin panel accessible without authentication | Auth control failure |
| Password appears in plaintext in any log, response, or UI | Credential exposure |
| `X-Admin-Key` header value visible in browser DevTools response | Secret leakage |

### What is NOT a Security Blocker

- An error message that says "Scan failed" without technical details → Bug, not Security Blocker
- A domain that gets a higher score than expected → Accuracy issue, not security
- A UI layout issue in RTL mode → UX Friction

---

## Class 2 — Product Blocker

**Definition:** The user cannot complete a core product flow without founder intervention. The product delivers no value when this issue is present.

**Decision:** Do not stop trial, but fix within 24 hours. Suspend only the affected flow if the fix takes longer.

### Core flows that must work

1. Visitor: enter URL → receive Trust Score and Usage Decision
2. Owner: register → login → add site → DNS verify → run scan → view Fix Plan
3. Admin: login → view leads → view analytics

### Examples

| Issue | Why it's a Product Blocker |
|---|---|
| Scan form always returns "error" for all valid URLs | Visitor flow is completely broken |
| Fix Plan does not render (white page or error) | Owner flow delivers no actionable output |
| Registration form submits but account is not created | Owner cannot join |
| DNS verification never completes even after TXT record is added | Owner cannot verify their site |
| Arabic locale shows broken text or untranslated keys | One half of the intended audience cannot use the product |
| "View Scans" button on Sites list goes to a 404 | Owner cannot reach scan history |

### What is NOT a Product Blocker

- DNS verification takes 2 hours instead of 5 minutes → Expected behavior (DNS propagation), not a bug
- User finds Fix Plan cards confusing → UX Friction
- User wants more detail in the guidance → Feature Request

---

## Class 3 — UX Friction

**Definition:** The user completed the flow but experienced confusion, hesitation, or unnecessary effort. The product works correctly but the experience is rough.

**Decision:** Log and classify. Do not fix during trial. Aggregate patterns → Release 2.0.

### Examples

| Issue | Notes |
|---|---|
| User did not notice the trust level badge (low/medium/good/high) | Visual hierarchy issue |
| User did not understand what to do after seeing a "Medium" score | Copy clarity gap in guidance section |
| User confused the "Try again" button with a "Rescan" button | Label ambiguity |
| User expected to see the DNS TXT record value inside the product, not in an email | Owner flow UX gap |
| Fix Plan cards feel too technical for a non-developer site owner | Audience calibration issue |
| Arabic text in Fix Plan feels word-for-word translated, not natural | Translation quality gap |
| Score ring appears small on mobile | Responsive layout gap |
| "Back to Sites" link not visible without scrolling | Navigation hierarchy issue |

### Pattern signal

If the same UX Friction appears in 3+ different sessions independently, escalate it to P2 (Release 2.0 must address it). Do not defer UX issues that universally prevent trust in the result.

---

## Class 4 — Bug

**Definition:** The product behaves differently from its intended and documented behavior. No data is exposed and no core flow is broken, but something doesn't work as designed.

**Decision:** Classify by priority using `BETA_PRIORITIZATION_FRAMEWORK.md`. Fix P2 bugs post-trial. Log P3 bugs for Release 2.0.

### Examples

| Issue | Notes |
|---|---|
| Score ring shows `NaN` for a specific domain edge case | Data handling bug |
| "حاول مجددًا" (Try again) button triggers two fetch requests simultaneously | Race condition |
| PDF report download returns 500 for scan IDs with certain characters | PDF generation bug |
| Date/time in scan history shows UTC instead of local time | Display bug |
| Trust level "good" shows `undefined` instead of the translated label | i18n key bug |
| Login form clears password field when switching to register mode | State management bug |
| Scan result for `http://` URL shows HTTPS check as passed | Logic bug |

### What is NOT a Bug

- Feature the user expected but that was never built → Feature Request
- Result that doesn't match user's expectations about their site → Working as designed (Trust Score reflects public-facing signals only)

---

## Class 5 — Documentation Gap

**Definition:** The product behavior is correct, but the user lacked context to understand it. The information needed is either absent or not surfaced at the right moment.

**Decision:** Document or update in-product copy. Post-trial or very fast during trial if widespread.

### Examples

| Issue | Suggested fix |
|---|---|
| User didn't know they need to add a DNS TXT record to verify ownership | Add tooltip or inline step with TXT record value |
| User thought the Trust Score is a cybersecurity vulnerability scan | Update homepage copy to clarify what is and isn't checked |
| User didn't understand why a score of 72 is "Good" not "Medium" | Add score range explanation near the trust ring |
| User asked "who runs this service?" — no About page or attribution | Add a brief About section or footer attribution |
| User was surprised the Fix Plan doesn't show a severity order | Add "start here" signal to highest-priority issue |
| User expected a notification when their score changes | Explain that manual rescan is required in current version |

---

## Class 6 — Feature Request

**Definition:** The user wants something the product intentionally does not have. The product works correctly; the user wants more.

**Decision:** Log in a Feature Request register. Do not commit to any feature during the trial. All Feature Requests are inputs to Release 2.0 planning, not commitments.

### Examples

| Request | Notes |
|---|---|
| "Can you send me an email when the score drops?" | Notification system — Release 2.0 candidate |
| "Can I see the score history as a chart?" | Trend visualization — Release 2.0 candidate |
| "Can I export the Fix Plan as a task list?" | Export feature — Release 2.0 candidate |
| "Can you scan all my subdomains automatically?" | Bulk scan — out of scope per product philosophy |
| "Can you tell me if there are SQL injection vulnerabilities?" | Offensive scan — permanently out of scope |

### How to respond to Feature Requests during trial

Say: "That's useful feedback — we're collecting all requests for the next version. No commitments yet, but we're listening."  
Do NOT say: "Yes, we'll add that" or "No, that's not possible."

---

## Class 7 — Out of Scope

**Definition:** The request or issue falls outside the product's stated purpose as a Website Trust & Security Advisor. These items should never be built into this product.

**Decision:** Log for visibility. Never add to backlog. Close politely.

### Examples

| Request / Issue | Why it's out of scope |
|---|---|
| "Can you scan for open ports?" | Port scanning is an offensive capability — product philosophy prohibits this |
| "Can you test for XSS vulnerabilities?" | Active exploitation testing — permanently forbidden |
| "Can you download the site's files and check for malware?" | Content scanning — not what this product does |
| "Can you tell me the server's IP address?" | Infrastructure reconnaissance — not surfaced by design |
| "Can you check competitor sites automatically in bulk?" | Bulk scanning without ownership — prohibited |
| "Can you show me the HTTP response headers?" | Raw technical data exposure — product strips this intentionally |

### How to respond to out-of-scope requests during trial

Say: "This product is a Trust Advisor — it shows what a visitor can observe about a site's trustworthiness. It's not designed to perform active security testing. We can point you to tools designed for that purpose."

---

## Classification Decision Tree

```
Is user data exposed or a security control bypassed?
  └─ YES → Security Blocker (stop trial)
  └─ NO ↓

Can the user complete the core flow at all?
  └─ NO → Product Blocker (fix within 24h)
  └─ YES ↓

Did something behave differently from documented/intended behavior?
  └─ YES → Bug (prioritize with framework)
  └─ NO ↓

Did the user lack information to understand correct behavior?
  └─ YES → Documentation Gap
  └─ NO ↓

Did the user complete the flow but with confusion or difficulty?
  └─ YES → UX Friction
  └─ NO ↓

Did the user want something the product doesn't have?
  └─ YES → Feature Request (if in-scope) or Out of Scope
  └─ NO → No issue — log as successful session
```

---

*Related: `BETA_FEEDBACK_TEMPLATE.md` · `BETA_PRIORITIZATION_FRAMEWORK.md`*
