---
name: ideate
description: Generate product, venture, and feature ideas then exhaustively validate their uniqueness before proposing them. Covers the full loop from constraints and brainstorming through market research and presentation.
---

# ideate

Generate novel ideas (products, tools, projects, ventures) and systematically verify none already exist before saying a word.

## When to use

- User asks "what should I build?" or "give me an idea"
- Brainstorming a new project, tool, or product
- User says "I want to build something that goes viral / gets stars / helps people"
- Any time you are about to propose a concept, check if it is already built first

## Workflow

### 1. Extract constraints

Before generating anything, get the bounds:

- **Problem scope**: what kind of problem? (developer productivity, real-world impact, climate, finance, health, education, etc.)
- **Target user**: developers? general public? specific niche?
- **Audience breadth**: does this serve ONE group or ALL? (developers + company owners + users = highest viral ceiling; pure dev-tools rarely cross 5K+ stars)
- **Real-world filter**: does this solve a problem non-developers also face? Pure dev-tools rarely cross the viral threshold.
- **Format**: CLI tool? web app? library? dataset? guide? browser extension?
- **Success metric**: GitHub stars? users? revenue? impact?
- **Uniqueness requirement**: does the user care about novelty? (this user does - explicit requirement)
- **Daily-use test**: PRIMARY filter, not secondary. If someone would not use this daily, it will not sustain viral growth. Daily-use beats deep-and-rare every time.

### 2. Generate candidates

Brainstorm specific pain points within the constraints. Prefer:

- **Universal problems** - every developer/human faces this
- **Simple concept** - explainable in one sentence, one GIF demo
- **Daily or weekly use** - high engagement
- **Shareable** - makes a great screenshot/tweet
- **Name as verb** - "just X it" (viral repos tend to work as verbs)

Generate 2-3 strong candidates before moving to validation.

### 3. Exhaustive uniqueness check (MANDATORY - do not skip or half-do)

**Before proposing ANY idea**, verify it does not already exist:

| Step | Action |
|------|--------|
| a. **Name search** | Search the exact name/command |
| b. **Problem search** | Search the problem it solves ("tool that helps you X") — **this catches more than name search** |
| c. **Category search** | Search the category + similar tools |
| d. **Adjacent search** | Search related terms the idea might live under |
| e. **GitHub check** | Check if a popular repo already does this |
| f. **Verify** | Parse results. If anything close exists, the idea fails uniqueness |

**Parallel research (recommended for thoroughness):** Instead of checking one step at a time, fan out independent search angles via `delegate_task` so they run concurrently and you get consolidated findings faster:

```
delegate_task(tasks=[
    {"goal": "Search if X CLI tool exists. Check GitHub, npm, PyPI, and web. Report all competitors found.", "context": "Idea: one-line description of the idea"},
    {"goal": "Search for tools solving the same PROBLEM as X (not by the same name). Check different phrasings of the problem. Report all competitors.", "context": "Problem it solves: the real pain point"},
    {"goal": "Search for tools in the same CATEGORY as X. Look for adjacent solutions. Report any that overlap with this idea.", "context": "Category: what kind of tool this is"},
])
```

Consolidate results. If any subagent found a direct competitor, the idea fails.

**Search technique with local Firecrawl:**
```bash
curl -s http://localhost:3002/v1/search -X POST \
  -H 'Content-Type: application/json' \
  -d '{"query":"your search here"}' | python3 -c "
import sys,json
d=json.load(sys.stdin)
for x in d['data'][:5]:
    print(f'{x[\"title\"]}\n  {x[\"url\"]}\n  {x[\"description\"][:200]}\n')
"
```

Customize the query string and result count per search angle.

**Existence judgment:**
- "Exists in a different form" means NOT unique (e.g., web app exists but you wanted CLI - if the problem is solved, the idea fails)
- "Only on closed-source/paid" -> note the gap, may pass (open-source unique angle)
- "5+ tools do this" -> saturated, move on
- "Nothing found" -> only then proceed

**Critical nuance — search by problem, not by solution name:**
Do not search "cli .env manager" if the idea is ".env manager." Search "sync .env files manage secrets projects" — the real competitors use different naming conventions and duck the name-search. In this session, `dotenv-vault`, `env-vault`, and `brandonwbl/env-vault` were all missed by the initial name-biased search.

**Saturation awareness:** The open-source CLI tool space is 90%+ picked over for obvious ideas. Expect the first 10-15 ideas to already exist. Do not conclude "nothing exists" after 3 searches. Plan for multiple rounds of iteration — extract what made each dead idea close, pivot the angle, search again. This is normal, not discouraging.

**Multi-round iteration:** Each failed idea teaches what's saturated. After 5+ dead ends, stop generating pure-CLI concepts and look at non-obvious formats: datasets, reference docs, browser extensions, single-file web apps, shell scripts, VS Code extensions, GitHub Actions, curated lists.

### Fallback search when web_search tool is unavailable

Search tools (web_search, web_extract) may fail due to credits exhausted, service down, or rate limits. When they do, use the GitHub API directly via curl as a fallback to verify if an idea already exists:

```bash
# Search GitHub repos by keyword — unauthed allows 60 req/hr
curl -s "https://api.github.com/search/repositories?q=CLI+tool+auto+mute+microphone&sort=stars&per_page=5" \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
for r in d.get('items',[])[:5]:
    print(f\"{r['full_name']} ⭐{r['stargazers_count']} - {r.get('description','')}\")
"

# Check if a package name exists on npm
curl -s "https://registry.npmjs.org/-/v1/search?text=your-idea-cli&size=5" \
  | python3 -c "
import json,sys
d=json.load(sys.stdin)
for r in d.get('objects',[]):
    p=r.get('package',{})
    print(f\"{p.get('name','')} - {p.get('description','')}\")
"

# Check PyPI availability (200=exists, 404=available)
curl -s -o /dev/null -w "%{http_code}" "https://pypi.org/simple/package-name/"
```

**API rate limit strategy:** Unauthed GitHub API = 60 requests/hr. If you hit the limit, check via `/rate_limit`, reduce `per_page`, or switch to `gh search repos` if the GitHub CLI is installed. When both web_search AND the GitHub API are unavailable, fall back to `browser_navigate` — the browser does not share the same rate limits.

### 4. Present findings

Format:

```
Checked X, Y, Z. Results: [what exists] | [what doesn't]

## [Idea name]
One-liner...

Why it is unique: ...
Why it trends: ...
Build: language, LOC, rough effort.
```

Show the research done so the user trusts the conclusion. If an idea fails, say why and offer the next candidate.

### 5. Quick prototype (when user wants working code)

When the user explicitly asks for code alongside ideas (e.g. "~100 lines showing the core functionality"), extend the workflow with a prototyping phase:

1. **Build minimal working code** — one file per idea, ~100 lines, ponytail mode (stdlib-first, no over-engineering). Solve the unique core; skip edge cases, error handling, packaging.
2. **One external dependency max** — and only if the core value requires it (audio control, OCR, hardware access). Everything else stdlib or `argparse`.
3. **Verify it runs** — syntax check (`ast.parse`), then `--help` boots, then one functional smoke test:
   ```
   python3 -c "import ast; ast.parse(open('file.py').read())"  # syntax
   python3 file.py --help                                       # boots
   echo '{"test":1}' | python3 file.py                          # functional
   ```
4. **Present code before explanation** — the code IS the pitch. Working prototype beats concept document. Put the file listing at the top, explanation as a brief table.

**Directory layout:** One flat directory, one `.py` per idea, a single README.md explaining the batch:

```
cli-ideas/
├── README.md       # cross-idea table, viral strategy, audience map
├── cashviz.py      # one CLI per file
├── mute-me.py
└── ... (10 files, ~100 lines each)
```

**What to skip:** Packaging, tests (beyond smoke test), error handling for impossible paths, CI, config files, multi-platform support. Add when: the idea gets traction and a user asks for it.

## Pitfalls

- **Do not pitch without checking.** This is the cardinal rule for this user. Even one unverified pitch wastes trust.
- **Do not check one search and stop. Search by problem, not by name.** A search for "env manager CLI" will miss `dotenv-vault` (branded as "dotenv"), `env-vault` (different name), and `brandonwbl/env-vault` (repo-specific). Search the PROBLEM: "sync .env files manage secrets projects" — competitors use different naming conventions. Name-biased searching is the single most common failure mode in this skill.
- **Parallel research beats sequential.** Instead of checking one angle then another, dispatch 2-3 subagents simultaneously (via `delegate_task`) to search different query angles, different tool registries (GitHub, npm, PyPI, crates.io), and deliver consolidated findings. This catches more, faster.
- **"Popular tool" is not the same idea.** If the name is taken but the concept is different, note both.
- **Niche is fine for utility but bad for virality.** If only 1,000 people need it, it will not get 10,000 stars.
- **Do not over-research once found.** If a direct competitor is found on the first or second search, stop and pivot. Over-researching an already-dead idea wastes time. The threshold is lower for disproving than for proving.
- **CLI tool space is ~90% saturated.** After 5+ dead ends on CLI concepts, stop generating CLI ideas and consider non-obvious formats: datasets, curated lists, reference docs, shell scripts, browser extensions, VS Code extensions, GitHub Actions, single-file web apps, config templates that go viral. These formats have less competition and can still hit trending.
- **Brace for 80%+ rejection rate.** In a saturated space (CLI tools, developer productivity), most ideas will exist. This is normal. Document what was taken, pivot, and keep going. The 20% that pass are worth the effort. If the user is getting frustrated by rejections, acknowledge the saturation honestly and switch to a non-CLI format.

## Related skills

- `spike` - technical feasibility validation (can we build it?) - complementary to this skill's market validation
- `plan` - writing implementation plans once an idea is validated
