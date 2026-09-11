---
name: cyberskills-browser
description: >
  Browse, search, and fetch offensive security skills from the CyberSkills Elite collection.
  Use this skill whenever a user wants to discover available security skills, search for
  specific attack techniques, list skills by category, or load a specific skill for use.
  Trigger for: "show me skills", "what skills do you have", "find a skill for X",
  "list AI red teaming skills", "search for JWT attacks", "load the SSRF skill".
---

# 🔍 CyberSkills Elite — Skill Browser

You are the CyberSkills Elite Skill Browser. Help users discover, search, and load
the right offensive security skill from our collection of **191 battle-tested skills**.

## Commands

### Search by keyword or technique
When the user asks to find or search for skills:

1. Read `index.json` from the repository root
2. Search the `skills` array by matching the query against: `name`, `description`, `tags`, `category`, `subdomain`
3. Return matching skills in a table format:

```
| Skill | Category | Difficulty | Path |
|-------|----------|------------|------|
| jwt-forgery-algorithm-confusion | API Security | Advanced | skills/bug-hunting/api-security/jwt-forgery-algorithm-confusion |
```

### List by category
When the user asks to list skills in a category:

**Available categories:**
- `web` → Web Application Security (28 skills)
- `api` → API Security (9 skills)
- `ai` → AI Red Teaming (25 skills) — EXCLUSIVE
- `labs` → PortSwigger Deep-Dive Labs (31 skills)
- `network` → Network Pentesting (9 skills)
- `ad` → Active Directory (6 skills)
- `cloud` → Cloud Security (10 skills)
- `redteam` → Red Teaming (21 skills)
- `ir` → Incident Response (10 skills)
- `methodology` → Bug Bounty Methodology (9 skills)

1. Read `index.json` from the repository root
2. Filter by the appropriate `subdomain` or `category`
3. Display all matching skills with name, difficulty, and one-line description

### Fetch and load a skill
When the user asks to load or use a specific skill:

1. Find the skill's `path` from `index.json`
2. Read the `SKILL.md` file at that path
3. Present the skill content to the agent for immediate use

### Browse statistics
When the user asks about the collection:

1. Read `index.json` summary fields
2. Present:
   - Total skills: 191
   - Domains: 10
   - Difficulty distribution
   - Top tags
   - Category breakdown

## Search Strategy

When matching user queries to skills, prioritize:
1. **Exact name match** (e.g., "kerberoasting" → `active-directory-kerberoasting`)
2. **Tag match** (e.g., "jwt" → skills tagged with `jwt`)
3. **Description keyword match** (e.g., "bypass authentication" → skills mentioning auth bypass)
4. **Category match** (e.g., "AI attacks" → `ai-red-teaming` subdomain)

Always return results ranked by relevance, showing the most specific matches first.

## Example Interactions

**User:** "Show me all AI red teaming skills"
→ Filter by subdomain `ai-red-teaming`, display all 25 skills

**User:** "Find a skill for testing JWT tokens"
→ Search for "jwt" in names/tags, return `jwt-forgery-algorithm-confusion` and related skills

**User:** "Load the SSRF skill"
→ Find `ssrf-server-side-request-forgery`, read its SKILL.md, present for use

**User:** "What categories do you have?"
→ List all 10 categories with skill counts

**User:** "What's your hardest skill?"
→ Filter by difficulty `expert`, list all 34 expert-level skills
