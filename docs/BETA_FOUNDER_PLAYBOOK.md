# Beta Founder Playbook
## Website Trust & Security Advisor — Release 1.2

**Who this is for:** The founder conducting the supervised beta trial  
**Purpose:** Practical, session-by-session guidance — what to do, what to say, what to watch for, and when to stop

---

## Before Inviting the First User

### Confirm the gate is closed

Before sending any invitation, confirm every item in `OPERATIONAL_BETA_LAUNCH_GATE.md §5` is checked. If even one item is unchecked, do not invite anyone.

### Prepare your monitoring setup

Open two browser tabs before each session:
1. **Backend logs** — `docker compose logs -f backend` or your log viewer
2. **The product** — `https://<trial-domain>` — be ready to use it as the user would

Know how to read these events in the logs:
- `scan.completed` — successful scan
- `scan.failed` — unexpected error (note the reason)
- `rate_limit.ip.exceeded` — guest rate limit fired
- `rate_limit.domain.exceeded` — domain rate limit fired
- `auth.login.failed` — failed login attempt

### Prepare the feedback form

Have `BETA_FEEDBACK_TEMPLATE.md` open before each session. Fill it in during the session, not after — memory fades within an hour.

### Prepare the invitation message

Each invitation should include:
1. What the product does (one sentence)
2. What you're asking the user to do (specific scenario)
3. What to do if something breaks (direct contact method)
4. A clear note: "This is a private trial — please don't share the URL"
5. No promises about features, timelines, or pricing

**Invitation message template:**

> Hi [Name],
>
> I'd like to invite you to try a tool I've been building: a Website Trust Advisor that helps you understand how trustworthy a website appears to a visitor, and what fixes would improve its score.
>
> I'm running a small private trial with a few people I trust to give honest feedback. This is not a public product yet.
>
> What I'd like you to do: [specific scenario — e.g., "Enter a URL you want to check and tell me what you think of the result" or "Register, add your domain, and walk through the Fix Plan"]
>
> If anything breaks or confuses you: [contact method]
>
> Please keep the URL private — do not share it or post it anywhere.
>
> Thank you.

---

## During Each Session

### Observation, not demonstration

Your job during a session is to watch, not to explain. Resist the urge to guide the user through the product. Let them get stuck. Let them be confused. That confusion is the data.

**Do:**
- Say "what would you do next?" when they pause
- Say "what were you expecting to happen?" when something surprises them
- Say "what does this score tell you?" to probe understanding
- Take notes in the feedback template in real time

**Don't:**
- Say "click here" or "scroll down"
- Explain what the Trust Score means before they react to it
- Defend the product when the user is confused
- Promise that the confusion will be fixed
- Ask leading questions like "Wasn't that straightforward?"

### The most important question to ask

> "If you had to explain what this score means to a colleague in one sentence, what would you say?"

This tells you whether the Trust Signal is working. If the user cannot answer this question, the signal is failing regardless of how beautiful the UI is.

### Secondary questions by user type

**Visitor testers:**
- "Would you use this score to decide whether to visit an unfamiliar website?"
- "What would make you trust this score more?"
- "What do you think is being checked?"

**Owner testers:**
- "Could your developer implement the fix in the Fix Plan without calling you?"
- "Does this score reflect how your site actually is?"
- "What's the most useful thing on this page?"

**Technical reviewer:**
- "Is the Fix Plan technically accurate?"
- "Would a developer understand the 'How' section without Googling?"
- "Is anything in the Fix Plan dangerous or incorrect?"

### Red flags to watch for (log immediately)

| Signal | What it might mean |
|---|---|
| User refreshes the page multiple times | Flow is broken or confusing |
| User opens DevTools | They're trying to understand what's happening under the hood (may indicate confusion or distrust) |
| User says "so is this a security scanner?" | Product positioning failure — they expect offensive capabilities |
| User tries to enter `http://localhost` | Testing the SSRF block (expected from technical users; confirm it blocks correctly) |
| Error message appears in the browser | Bug — screenshot and log it |
| User cannot complete DNS verification | Friction in the Owner flow |
| Any raw technical data appears in the result | Potential data minimization failure — treat as P0 candidate |

---

## After Each Session

### Immediately (within 30 minutes)

1. Complete the `BETA_FEEDBACK_TEMPLATE.md` entry while memory is fresh
2. Assign a preliminary classification using `ISSUE_CLASSIFICATION_GUIDE.md`
3. Add any issues to the Priority Register from `BETA_PRIORITIZATION_FRAMEWORK.md`
4. If any issue is P0 or potentially P0 — stop and investigate before the next session

### Daily (end of each trial day)

1. Review the Priority Register
2. Check: has any P2 issue appeared 3+ times? → Elevate to P2 confirmed
3. Check backend error logs for anything the user didn't mention
4. If error rate is elevated: identify cause before the next day begins
5. Note any pattern emerging across sessions (even if no single issue hits P2 threshold)

### At the end of the trial (Day 18)

Follow `POST_BETA_RELEASE_WORKFLOW.md` from Step 1.

---

## What Not to Promise During the Trial

During sessions or follow-up conversations, never promise:

| What users often ask | What not to say |
|---|---|
| "Will you add [feature]?" | "Yes, we'll add that" |
| "When will this be public?" | A specific date |
| "How much will this cost?" | Any price or "it'll be free" |
| "Can you check [out-of-scope capability]?" | "We're working on it" |
| "Will my score improve if I fix X?" | A specific score prediction |
| "Can I invite my team?" | "Sure" (this is an invitation-only trial) |

**What to say instead:**
- "That's useful to know — I'm collecting all of this for the next version"
- "I'm not ready to share timelines yet"
- "That's a great question and I don't have an answer yet"
- "This product is focused on the trust signals a visitor can observe — it's not a security scanner"

---

## How to Keep the Product as an Advisor, Not a Scanner

The product's value is in being a **trusted judgment tool**, not a vulnerability scanner. Every interaction with a beta tester is an opportunity to reinforce or undermine this positioning.

### Reinforce it by:
- Describing the score as "what a visitor would conclude about this site's trustworthiness"
- Describing the Fix Plan as "what a site owner can do to appear more trustworthy"
- Saying "we check public-facing signals" rather than "we scan for vulnerabilities"
- Never using words like "exploit," "attack surface," "penetration test," or "hack"

### Undermine it by:
- Promising to add port scanning or XSS testing
- Saying the product finds "all" security issues
- Claiming the score reflects internal security posture (it reflects public-facing signals only)
- Suggesting users scan sites they don't own for security purposes

If a user treats the product as an attack tool, stop the session, clarify the product's purpose, and decide whether to continue the trial with that user.

---

## When to Stop the Trial Immediately

Stop all sessions and suspend the trial without waiting for confirmation if:

1. **Any raw technical data is visible** — IP addresses, HTTP headers, file paths, server names in any API response or UI element
2. **Any user reports seeing another user's data** — even if you can't reproduce it immediately
3. **Auth is bypassed** — a user is logged in to someone else's account, or reaches `/sites` without logging in
4. **You suspect a security researcher is probing the system** — take it seriously, not as a compliment

For anything else, you can continue the session and investigate afterward.

**Stopping procedure:**
1. End active sessions politely: "I need to look into something before we continue — I'll be in touch"
2. Do not say "there's a security issue" — say "I need to check something on my end"
3. Investigate in a copy of the logs immediately
4. If the issue is confirmed P0: do not resume until patched, tested, and re-verified in staging
5. Notify all active beta participants when the trial resumes (brief, honest message: "I found an issue and fixed it")

---

## Quick Reference Card

**Start of each session:**
- [ ] Logs open in terminal
- [ ] Feedback template open
- [ ] Session is observation-only — no guidance unless user is completely stuck

**During session:**
- [ ] "What would you do next?" when user pauses
- [ ] "What were you expecting?" when user is surprised
- [ ] Log every hesitation, confusion, and error

**After session:**
- [ ] Complete feedback template within 30 minutes
- [ ] Assign classification and priority
- [ ] Check logs for backend errors
- [ ] Is anything P0? → Investigate before next session

**Daily:**
- [ ] Review full Priority Register
- [ ] Any P2 hitting 3+ sessions? → Confirm as P2
- [ ] Error rate acceptable? (< 1% of scan requests)

**Day 18:**
- [ ] Follow `POST_BETA_RELEASE_WORKFLOW.md`

---

*Related: `BETA_OPERATING_CYCLE.md` · `BETA_FEEDBACK_TEMPLATE.md` · `ISSUE_CLASSIFICATION_GUIDE.md` · `BETA_PRIORITIZATION_FRAMEWORK.md` · `POST_BETA_RELEASE_WORKFLOW.md`*
