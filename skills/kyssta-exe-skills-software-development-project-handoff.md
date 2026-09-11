---
name: project-handoff
category: software-development
description: Package a project for handoff to another developer or environment — comprehensive handoff document, git repo cleanup, architecture docs, risk analysis, and next-steps roadmap.
trigger: User asks to "hand off", "create a handoff file", "package this up", "put this into git", "make a repo so I can continue on my machine", or similar handover signals. Also triggered at the natural end of a project phase when the deliverable transitions.
---

# Project Handoff

When a project phase completes and the user needs to continue on their own machine, or hand the work to someone else, use this procedure to create a proper handoff package.

## Procedure

### 1. Survey Everything

Read every key file in the project to build a complete mental model:

- **docker-compose.yml / docker-compose.yaml** — service architecture
- **README.md** — existing public docs
- **.env.example** — environment variable inventory
- **.gitignore** — what's excluded
- **All source files** — app.py, models, routes, database layer
- **Config files** — LiteLLM, Nginx, etc.
- **Database schemas** — init scripts
- **Build files** — Dockerfile, requirements.txt, Makefile, package.json
- **Test files** if any exist

### 2. Gather Context from Conversation History

Use `session_search()` to find:

- Original goals and decisions made during the build
- Key trade-offs and why they were chosen
- Any business model/pricing discussions with exact numbers
- User's specific constraints and preferences

### 3. Create HANDOFF.md

The handoff document must cover **all** of these sections (adapt order as appropriate):

```markdown
# [Project Name] — Handoff Document

**Built:** [Date]
**Target:** [What it does]
**Audience:** [Who it's for]
**Model:** [Model used to build it]

## Table of Contents

## 1. What Is [Project]?
One-paragraph elevator pitch and key differentiators.

## 2. Project Structure
File tree showing every directory and key file. Annotate briefly.

## 3. Architecture Overview
ASCII diagram showing the full request flow: user → auth → proxy → providers. Include all services, ports, and data stores.

## 4. Service Architecture (Docker)
Table: Service | Image | Port | Purpose

## 5. [Domain-Specific Section]
For API providers: pricing strategy, model lineup, provider routing.
For SaaS: feature list, user flows.
For CLI tools: command reference.
For libs/packages: API surface overview.

## 6. Business Model & Risk (if applicable)
CRITICAL: User prefers exact dollar scenarios (1/5/10/50 users), not percentages.

| Users Scenario | Revenue | Cost | Fixed | Profit/Loss |
|---|---|---|---|---|

Show worst-case, expected, and best-case.

## 7. [Technical Deep-Dive]
Providers & models, API reference, sub-limit architecture, caching strategy, streaming behavior, etc.

## 8. Setup Guide
Quick start commands, environment variable table (variable, required?, default, notes).

## 9. What's NOT Done Yet
Bulleted action items grouped by priority (Critical / Important / Nice-to-have).
Each item: what it is, where to do it, any dependencies.

## 10. Key Decisions Made
For each major decision: the alternatives considered, the final choice, and the reasoning. This is critical so the next developer doesn't re-litigate settled questions.

## 11. Important Design Notes
Gotchas, design debt, architecture quirks, placeholder values, production concerns.

## 12. Commands Cheat Sheet
Every command someone needs: start, stop, rebuild, test, reset DB, run locally, etc.
```

### 4. Verify Risk Analysis Format

When the user cares about risk/business viability (check memory or user profile):

- Use **exact dollar figures** per user-count scenario (1/5/10/50 users), not percentages
- Show worst-case alongside expected
- Identify breakeven point explicitly
- Call out scenarios where the model loses money

### 5. Clean Up Git

- Check `git status` for uncommitted changes
- Verify `.gitignore` catches secrets (.env, keys, __pycache__)
- Check `git log` to see what's already committed
- Stage everything with `git add -A`
- Write a descriptive commit message covering:
  - What was built (infrastructure, features, frontend)
  - What the handoff includes
  - What's next (action items from "what's NOT done")

### 6. Summary to User

Deliver a concise summary:
- Where the repo lives
- What key artifacts were created
- The top 3 things they need to do on their machine
- One-line per key file explaining what it is

## Pitfalls

- **Don't just write a HANDOFF.md** — also commit everything so the repo is clean on clone. A dirty working tree defeats the purpose of handing off.
- **Don't skip the risk analysis** when the user previously asked about business viability — they expect dollar scenarios, not vague warnings.
- **Don't re-state the README** — HANDOFF.md is for the developer continuing the work, not the end-user. Include architecture trade-offs and design debt that wouldn't go in a public README.
- **Don't commit real secrets** — verify .gitignore catches .env before staging.
- **Don't skip old decisions** — the "Key Decisions" section is what prevents the next person from undoing settled architecture choices.
- **Don't write a novel** — be comprehensive but concise. Use tables and bullet points. The reader needs to understand the project in 10 minutes, not 2 hours.
- **Git log check**: If there's only one commit ("Initial commit"), add detail to the handoff. If there are many, reference the commit history for chronological understanding.

## Reference Files

This skill ships with a concrete example from a real session:
- `references/handoff-example.md` — full Nectar API handoff (API provider SaaS). Use as a structural template for API/SaaS projects. Contains architecture diagram, pricing tables, risk analysis with exact dollar scenarios, and a complete "what's NOT done" section.

## Related Skills

- `codebase-inspection` — for understanding LOC, languages, ratios before writing handoff
- `github-repo-management` — for push to remote, setting up remotes
- `plan` — for writing actionable project plans before building
