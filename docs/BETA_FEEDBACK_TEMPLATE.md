# Beta Feedback Template
## Website Trust & Security Advisor — Release 1.2

Use this template for every structured feedback session. Fill it in during or immediately after observing a user. One form per session per user.

---

## Feedback Entry

**Date:** _______________  
**Participant ID:** (use a pseudonym — no real names in this file) e.g. V-01, O-02  
**Session number:** (1st, 2nd, etc. with this participant)  
**Observed by:** Founder / async (written by participant)  
**Language used:** Arabic / English / Switched between both

---

## 1. User Type and Scenario

**User type:**
- [ ] Visitor tester (no account — testing URL scan flow only)
- [ ] Owner tester (has account — testing full owner flow)
- [ ] Technical reviewer (reviewing Fix Plan accuracy)

**Scenario assigned:**

> Example: "Enter a URL you own and read the result" or "Register, add your site, complete DNS verification, and view the Fix Plan"

_______________________________________________

---

## 2. What Did the User Try to Do?

Describe in the user's own words or as close as possible:

_______________________________________________

_______________________________________________

---

## 3. What Actually Happened?

Describe the actual product behavior observed (not what should have happened):

_______________________________________________

_______________________________________________

**Outcome:**
- [ ] Completed successfully without help
- [ ] Completed with assistance from founder
- [ ] Partially completed — stopped at: _______________
- [ ] Could not complete — reason: _______________
- [ ] Unexpected error occurred — describe: _______________

---

## 4. Did the User Understand the Result?

### Trust Score (Visitor flow)

- [ ] Understood the score immediately (no explanation needed)
- [ ] Needed one sentence of explanation
- [ ] Required extended explanation
- [ ] Still confused after explanation
- [ ] Did not reach the score

**What did the user say or do when they saw the score?**

_______________________________________________

### Usage Decision / Trust Level Label

- [ ] Understood what "High Trust / Good / Medium / Low" means in context
- [ ] Confused by the label
- [ ] Did not notice the label
- [ ] Asked what they should do with this information

**Did the user understand what action to take after seeing the result?**
- [ ] Yes — they immediately knew what to do next
- [ ] Partially — needed a prompt
- [ ] No — they had no idea what to do next

---

## 5. Did the User Trust the Product?

This is the most important signal. The product is a Trust Advisor — if users don't trust the advisor, the product fails.

**Statements or behaviors that indicate trust:**
- [ ] "I would share this result with my client"
- [ ] "I would use this before visiting an unfamiliar site"
- [ ] "The score feels accurate"
- [ ] "I'd pay for this"

**Statements or behaviors that indicate distrust:**
- [ ] "How do I know this is correct?"
- [ ] "This seems like it's just guessing"
- [ ] "The score doesn't match what I expected"
- [ ] "I wouldn't act on this"

**Overall trust level (founder's assessment):**
- [ ] High — user treated the result as credible without prompting
- [ ] Medium — user accepted the result after seeing the explanation
- [ ] Low — user remained skeptical
- [ ] Unable to assess

**Direct quote from user (if any):**

> _______________________________________________

---

## 6. Fix Plan Observations (Owner Testers Only)

Skip this section for Visitor testers.

**Did the user understand what each Fix Plan card means?**
- [ ] Yes — all cards were clear
- [ ] Partially — some cards were confusing
- [ ] No — cards were not actionable

**Which cards caused confusion?** (check all that apply)
- [ ] No HTTPS
- [ ] Invalid SSL certificate
- [ ] SSL expiring soon
- [ ] Missing HSTS header
- [ ] Weak security headers
- [ ] Bad reputation

**Could the user (or their developer) act on the Fix Plan without additional help?**
- [ ] Yes
- [ ] Probably yes
- [ ] Probably not
- [ ] No

**Fix Plan quote or observation:**

> _______________________________________________

---

## 7. DNS Verification (Owner Testers Only)

Skip this section if the user did not attempt DNS verification.

- [ ] User found the DNS verification step confusing
- [ ] User could not find where to add the TXT record in their DNS provider
- [ ] User waited too long for DNS propagation
- [ ] User completed verification successfully
- [ ] User gave up before completing

**Where did they get stuck?**

_______________________________________________

---

## 8. Language and RTL Experience

**Primary language used:**
- [ ] Arabic (RTL)
- [ ] English (LTR)
- [ ] Switched languages during the session

**Any text that appeared broken, misaligned, or confusing?**
- [ ] No issues observed
- [ ] Minor issue: _______________
- [ ] Significant issue: _______________

---

## 9. Severity Classification

Classify using `ISSUE_CLASSIFICATION_GUIDE.md`. Check the primary classification:

- [ ] Security Blocker — stop trial
- [ ] Product Blocker — user cannot complete core flow
- [ ] UX Friction — user completed flow but with difficulty
- [ ] Bug — unexpected error or broken behavior
- [ ] Documentation Gap — product works but user lacked context
- [ ] Feature Request — user wanted something that doesn't exist
- [ ] No issue — session completed smoothly

**Issue description (if any):**

_______________________________________________

---

## 10. Screenshot or Recording

- [ ] Screenshot attached: _______________
- [ ] Screen recording reference: _______________
- [ ] No visual evidence captured

---

## 11. Urgent Intervention Required?

- [ ] No — log and review at Day 18 retrospective
- [ ] Yes — founder must act within 24 hours
- [ ] Yes — stop trial immediately

**If yes, describe the urgency:**

_______________________________________________

---

## 12. Overall Session Rating

Founder's overall assessment of this session:

- [ ] Excellent — user completed everything, result felt credible, no confusion
- [ ] Good — minor friction, nothing blocking
- [ ] Mixed — core flow worked but significant confusion in places
- [ ] Poor — user could not complete core flow or did not trust result
- [ ] Failed — session exposed a blocking issue

**One sentence summary:**

_______________________________________________

---

*Use `ISSUE_CLASSIFICATION_GUIDE.md` to classify issues. Use `BETA_PRIORITIZATION_FRAMEWORK.md` to assign priority. File completed forms in the feedback tracker.*
