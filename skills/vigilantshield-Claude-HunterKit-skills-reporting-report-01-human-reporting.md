---
name: report-01-human-reporting
sequence: report-01
category: reporting
domain: reporting
description: "Human-voice bug bounty report writing. Impact-first reporting, natural tone, real examples, and the art of making triagers want to pay you."
wordlist_ref: ""
---

# Human Report Writing

The difference between a paid and rejected report is rarely the bug itself — it's how you tell the story. Triagers read 50 reports a day. Make yours the one they remember.

## The Golden Rule

Write like you're explaining the bug to a smart friend who's never seen it before.

- No "It was observed that..." — just say what happened
- No "Upon further investigation..." — just say what you found
- No "It is recommended to..." — just say how to fix it

## Report Structure (Short)

**Title**: [Bug Type] in [Location] → [What attacker gets]

Good: `IDOR in /api/users/{id} allows reading any user's PII`
Bad: `Broken Object Level Authorization vulnerability identified in user profile API endpoint`

**Summary**: One paragraph. What's the bug, where is it, why does it matter.

**Steps**: Numbered. Exact requests. Exact responses. Anyone should be able to reproduce.

```
1. Login as User A, get session cookie
2. GET /api/users/456/profile  (note: 456 is not you)
   Cookie: session=abc123
3. Response contains User B's full PII
   {"email":"userb@test.com","ssn":"123-45-6789","dob":"1990-01-01"}
```

**Impact**: What an attacker actually does with this. Be blunt.

"This means anyone can read any user's SSN, date of birth, and email by just changing a number in the URL. No special access needed. 100,000 users affected."

**Remediation**: One sentence fix.

"Check that the requesting user owns the resource before returning data."

## Tone Examples

| Don't Say | Say |
|-----------|-----|
| It was observed that the application lacks proper access controls | The app doesn't check who's asking for data |
| Upon further investigation, it was determined that... | I found that... |
| This vulnerability may potentially allow an attacker to... | An attacker can... |
| It is recommended to implement server-side validation | Check access on the server, not just in the UI |
| The following endpoint was found to be vulnerable | This endpoint leaks data |

## When to Submit vs When to Kill

Submit if:
- You can prove real harm (data access, money loss, account takeover)
- You can reproduce it every time
- The evidence is clean and clear

Kill if:
- It only works in theory
- You need 5 unlikely conditions to align
- You can't actually prove impact

## The One Line That Gets You Paid

Put this in the first paragraph: what the bug does, what data/access it exposes, and why that matters to the business.

> "An IDOR in `/api/orders/{id}` lets any logged-in user view any other user's order history — including customer names, addresses, payment methods, and purchase details for all 500,000 orders."

## Tools


- Text editor
- Burp Suite (for evidence capture)
- Screenshot tool


## Hacker Mindset

**Think like an offensive operator.** Every skill is a lens for finding the gap between what the developer intended and what the system actually enforces. Test boundaries, chain findings, and always set up OOB before firing payloads.


## Chaining & Escalation

Chain this finding with others for higher impact. Combine low-severity findings into critical attack chains. Always think: what's the next step after this works?


## OOB Detection & Blind Confirmation

Use Burp Collaborator or Interactsh for blind detection. Always set up OOB before firing payloads. Time-based: inject sleep(5) and measure response delay.


## Bypass Techniques

| Filter/Block | Bypass |
|-------------|--------|
| WAF/Input validation | Encoding, case variation, alternative syntax |
| Rate limiting | IP rotation via X-Forwarded-For, HTTP/2 multiplex |
| Blacklist | Alternative syntax, polyglot payloads |
| Blacklist bypass | Unicode, double encoding, null bytes |

## Wordlist Invocation

This skill provides methodology guidance. Refer to specific attack skills for wordlist payloads.
