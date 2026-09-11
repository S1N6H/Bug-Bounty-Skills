---
name: product-ideation
description: "Systematic process for discovering, researching, and validating unique product ideas — both open-source CLI/dev tools AND consumer-facing web apps — that can get real traction (GitHub stars OR daily active users)."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ideation, validation, research, gap-analysis, github-trends, virality, brainstorming, consumer-apps, product-discovery]
    related_skills: [spike, plan, open-source-extraction, competitive-software-landscape]
---

# Product Ideation

Use this when the user wants to **find a unique, buildable, viral-worthy product idea** — before any spike or plan. This is the creative+research phase that answers "what should I build?" not "can I build it?"

Load this when the user says: "I want to build something that helps people", "give me a unique idea", "what should I build that doesn't exist?", "I want 1000s of GitHub stars", "make my name", "I want something with 100+ daily users", "I want to go famous".

Two paths depending on the target:
- **OSS/CLI Path** → open-source developer tool, GitHub stars, HN/Reddit launch
- **Consumer Path** → web/mobile product, daily active users, social/viral launch

## The workflow

```
constrain  →  landscape  →  gap  →  check  →  prototype  →  pitch
```

### 1. Constrain — understand WHO

Before any research, pin down the user's constraints:

- **Audience:** developers? company owners? regular users? all three?
- **Domain:** dev tools? real-world problem? fun/novelty?
- **Usage:** daily? weekly? one-time?
- **Impact:** saves money? saves time? reduces pain? educates?
- **Uniqueness bar:** "better than X" or "nothing like X exists"?
- **Personal context:** what does the user know/do that gives them unique insight?
- **Existing work:** what has the user ALREADY built? Their infrastructure, APIs, and domain expertise may define what's uniquely buildable. E.g. someone who runs LLM benchmarks + a model router can build AI comparison/analysis tools that a generic dev can't.

### CRITICAL: Clarify before assuming

When the user says something ambiguous like "unique projects" or "make something" — **do not assume the category.** Ask what domain they mean:
- A developer tool? A web service? A game? A library? Open source infra?
- What's the target: GitHub stars? Daily active users? Revenue? Fame?
- What have they built before that this should complement?

One clarifying question at the start saves 20 minutes of wrong-direction pitching. If you don't ask, you will guess wrong and frustrate the user.

### CRITICAL: Identify the "real tool" vs "social/gimmick" preference early.
If user says "tool, website, useful thing, not gimmick" → use TOOL/UTILITY path below.
If user says "viral, social, fun, app" → use CONSUMER path below.
These have different search strategies, retention mechanics, and pitch structures.

Ask up to 3 questions if uncertain. Don't guess.

### 2. Landscape — map what exists

Search the category systematically. Use multiple sources:

```
Firecrawl API (local): curl -s http://localhost:3002/v1/search
GitHub API: curl -s "https://api.github.com/search/repositories?q=..."
npm/PyPI/cargo registries
General web search
```

For each category, identify:
- **Dominant tools** (10k+ stars) → 🔴 saturated
- **Emerging tools** (100-1k stars) → 🟡 moderate opportunity
- **Empty categories** (0-50 stars) → 🟢 high opportunity

Cache findings in a reference document.

### 3. Gap — find the intersection

The best ideas live at the intersection of:

| Dimension | Current sweet spot |
|-----------|-------------------|
| Timing | Solves a problem created by the AI ecosystem (2024-2026) |
| Audience | Useful to developers + company owners + regular users |
| Frequency | Daily or weekly use |
| Uniqueness | Category has <100 stars total, or a fresh angle on a saturated space |
| Build cost | Single file, <300 lines, stdlib-first (ponytail) |

Apply the **virality formula** from research:
> Be the first obvious plumbing solution to a painful new problem created by the AI ecosystem, with a one-line install, a shareable personality, and a benchmark number that makes devs say "wow."

### 4. Check — verify uniqueness HARD

Before proposing ANY idea, confirm it doesn't exist:

1. Search the exact name on GitHub
2. Search the category keywords on Firecrawl
3. Check npm/PyPI/cargo for similar tools
4. Avoid the trap ideas (categories that are deceptively saturated):
   - "terminal recording/recall" — Atuin, recall, Rewind, Wake, scritty, historai
   - "AI commit messages" — aicommits, opencommit, commitlint, cz-cli
   - "dangerous command protection" — thefuck, shellfirm, dcg, ShellSense
   - "AI session tracking" — entireio, session-memory, agentlytics, git-ai
   - "standup generators" — standup-cli x3+, git-quick-stats
   - "context resume" — devcontext, Nodepad, tmux-resurrect
   - "project health" — repohealth, dev-lens, DevPulse, onefetch
   - "AI cost tracking" — codeburn, aitracker, toktrack
   - "annotated diffs" — intentdiff, diffsense, difftastic
   - "interview coach" — interview-coach x2, TermDock, DialogDrill
   - "mental health/CBT" — cli-cbt, CBT Thought Diary
   - "env/.env management" — dotenv-vault, env-vault
   - "clipboard manager" — clipboard, clipcopy, snip
   - "decision tools" — decision-log (0 stars, ADR-style)
   - "digital legacy" — LEGACY-VAULT, Cipherwill
   - "relationship trackers" — friendward, relationship-tracker CLI

Search in parallel using `delegate_task` for thorough coverage.

### 5. Prototype — build the minimum

Build a working prototype before pitching. Apply ponytail mode:

- Single file, <200 lines
- Stdlib-first, zero/minimal external deps
- One command install (`pip install` / `npm i -g` / `curl | bash`)
- Interactive CLI if appropriate, pipe-friendly otherwise
- SQLite for persistence (avoid setting up real databases)

See the ponyitail skill for the full ladder.

### 6. Pitch — present with evidence

Structure the pitch:

```
## [name] — one-line description

**What:** [one sentence]

**Who:** [audience — why devs + owners + users all benefit]

**Why unique:** [comparison table vs closest alternatives]
| Tool | What it does | Missing |
|------|-------------|---------|
| X | ... | ... |
| Y | ... | ... |

**Why viral:** [the "oh sh*t" moment in one sentence]

**Build:** [lines of code, deps, language]
```

---

## Tool/Utility Product Ideation (Web Tools People Use Daily)

Use this workflow when the user wants a **genuinely useful tool** — not a social app, not a gimmick, not a game. Something people open because it saves them time/money/effort.

**Special triggers:**
- "I want to make a tool, a website, a thing"
- "Something useful people will use"
- "Not social/gimmick/asshole stuff"
- "I want 100+ daily users for something that actually helps"

### How this differs from Consumer path

| Dimension | Consumer Social Path | Tool/Utility Path |
|-----------|--------------------|--------------------|
| Retention | Streaks, social pressure, FOMO | Daily need, habit, bookmark |
| Virality | Share cards, TikTok, social loops | SEO, word-of-mouth, embed |
| Uniqueness bar | Novel concept, fresh mechanic | Better/faster/freer than existing |
| First users | Subreddits, TikTok, Discord | Google search, HN, Product Hunt |
| Revenue | Ads, subscriptions | Freemium, API credits, donations |
| Build scope | Full app with auth, social features | Single-page, no-login, zero-infra |
| User relationship | Emotional (fun, identity) | Transactional (I need this done) |

### CRITICAL PITFALL: Generic startup lists are poison

Searching "unique startup ideas 2026" or "untapped niches" returns generic dreck (AI consulting, pet accessories, wellness coaching). These produce terrible suggestions. **DO NOT start here.**

Instead, identify a real underserved gap by combining these angles:

### 1. Constrain — map what's buildable from the user's stack

Before searching, audit what the user already has:
- What infrastructure/APIs do they run? (LLMs, databases, servers, domains)
- What have they built before? (benchmarks, routers, dashboards)
- What daily pain do THEY have as a developer that no tool fixes?

The best tool ideas look like: "I already have X infrastructure, so Y tool costs me nothing to build and Z people need it."

### 2. Research — find the gap (3 angles, all different)

Run these searches in parallel to find real gaps:

**Angle A: "What do people use daily that sucks?"**
```python
web_search("best free online tool [category] 2025 2026 frustrating OR slow OR limited")
web_search("[existing popular tool] alternative free no signup")
web_search("I wish there was a website that [task]")
```

**Angle B: "What useful thing can I wrap my existing infra around?"**
Look at the user's existing stack and ask: what free tool can I offer that costs me $0 and saves users $xx/month?
- Have LLM API access? → free comparison, analysis, generation tools
- Run a server? → free monitoring, checking, conversion tools
- Know a domain well? → domain-specific calculator/analyzer

**Angle C: "Boring but essential" — daily-use tool categories that haven't been reimagined**
| Category | Existing players | Typical failings |
|----------|----------------|------------------|
| URL/content analysis | None dominant | Either paid or requires signup |
| PDF/document tools | iLovePDF (paid limits) | Daily caps, slow, bloated |
| Developer debuggers | BuiltWith (limited) | One check, no shareable reports |
| API explorers | Postman (heavy) | Requires account, desktop app |
| Data converters | QuickType (slow) | Limited formats, slow UI |
| Coding screenshot tools | Carbon (static) | No AI explanation, no sharing |
| Screenshot → structured data | Notion AI (paid only) | Expensive, no standalone tool |

### 3. Generate — the three filters

Every tool idea must pass ALL three filters:

**Filter 1: Actually doesn't exist**
Search the exact concept name + variations. 3+ direct competitors with 10k+ users → saturated drop it. Zero or one pre-seed competitor → proceed.

**Filter 2: Daily-use potential**
Does this tool get used once a day or more? Not "nice to have" — does it solve a recurring pain? Calendar? Yes. Reading? Yes. Coding? Yes.

**Filter 3: Buildable in ≤3 days**
- Single page web app (no auth, no database)
- Client-side processing or thin API wrapper
- No signup required (this is the #1 feature users want)
- Can be deployed as static site + small backend if needed

### 4. Validate — hard uniqueness check

For every idea, before pitching, run:

```python
# 1. Exact concept search
web_search("[concept name] free online tool 2025 2026")

# 2. Competitor-specific search  
web_search("[main competitor name] alternative free")

# 3. Domain+tool search
web_search("free [category] [format] converter/analyzer/checker no signup")

# 4. Check against existing dominant tools in the space
```

**If any search returns 3+ competitors that do >80% of what you're proposing**, the idea is not unique enough. It must be either:
- A genuinely new category (nothing does this at all)
- A dramatic simplification (removing auth, limits, bloat)
- A novel format/visualization nobody else uses

### 5. Pitch — structured with uniqueness proof

Present **1-3 ideas maximum**. For each:

```
## [Name.lol] — one-liner

**What:** [what it does in one sentence]

**Who:** [who uses it and how often]

**How it leverages your stack:** [what infra you already have]

**Uniqueness check:**
- [Competitor A] → does [X] but not [Y]
- [Competitor B] → does [Y] but requires [Z]
- This tool → [what's genuinely different]

**Why people use it daily:** [the recurring trigger]

**Build:** [tools + time estimate + complexity]
```

Never present a list of 5+ ideas. The user will reject all of them. Present 1-3 with conviction, backed by uniqueness proof.

### UNIVERSAL FILTERS (apply to ALL ideas before proposing)

Every product idea must pass BOTH filters. If either fails, DO NOT pitch it. Save yourself (and the user) the frustration.

### Filter 1: Agent-Proof Test

**This is the #1 reason web tool ideas get killed in 2026.** Before proposing any consumer-facing web tool, ask:

> "Can an AI agent (like Hermes) replicate this with a single command/tool call?"

If YES → the product has ZERO moat. A user who would use your tool can instead ask their agent and get the same result. Ideas killed by this: cred.lol (paste URL → credibility check = agent does `web_extract` + reasoning).

**A product is agent-proof if it requires at least one of:**
- **Persistent state** — data accumulates over time (history, trends, leaderboards)
- **Real-time / 24/7 service** — runs on a schedule, monitors, alerts (cron, webhooks)
- **Multi-user / social** — network effects, comparison, sharing between users
- **Public shareable pages** — embeddable widgets, status pages, badges others can link to
- **Infrastructure** — API endpoints, webhook receivers, scheduled jobs, file storage
- **Integration surface** — connects to external services via OAuth, webhooks, outbound calls

**Quick disqualifiers (any = kill the idea):**
- A user could ask their agent "do X for me" and get the same result
- Could be reimplemented as a script using existing APIs
- Single user, no persistent data, no ongoing service
- The value is entirely in a one-shot query/response
- The "product" is wrapping an AI call in a nicer UI

**Examples from real sessions:**
- ❌ cred.lol (credibility checker) → killed because agent runs `web_extract` + reasoning
- ❌ "free fact-checker for any article" → same problem
- ❌ "website tech stack analyzer" → BuiltWith exists, agents can do it with curl
- ❌ mtr.lol (AI provider health dashboard) → killed because aicheckerhub.com already exists (also agent-proof but not unique)

### Filter 2: Utility vs Fun — pitch the right lane

Before pitching ANY idea, confirm which lane the user is in:

| User says | Lane | What to pitch | What NOT to pitch |
|-----------|------|---------------|-------------------|
| "useful", "tool", "daily use", "saves time/money", "not gimmick" | UTILITY | Monitor, checker, aggregator, converter, analyzer | Viral games, social feed, novelty, "fun" |
| "viral", "social", "fun", "famous", "daily users" | CONSUMER/SOCIAL | Streak app, challenge, shareable card, community | Boring utility, calculator, dashboard |

**If user says "tool, website, useful thing, not gimmick" — DO NOT pitch** fail.lol, yell.lol, burn.lol, clock.lol, or any "viral for the sake of it" idea. These get killed instantly as "useless bullshit" and waste the user's time.

### Filter 3: Competitor Check — search HARD before pitching

Three searches minimum before pitching ANY idea:

1. `web_search("exact concept name OR alternative")` — direct competitors
2. `web_search("existing popular tool that does this")` — adjacent competitors  
3. `web_search("free [category] tool no signup 2025 2026")` — substitutes

**Disqualifiers:**
- 3+ direct competitors → saturated, drop it
- One dominant player with brand recognition → they own the category
- An existing tool that does >80% of what you're proposing → not differentiated enough
- The concept exists as a Chrome extension → still counts (user installs once, never comes back to your site)

**Only proceed if:**
- Zero competitors found (genuinely new category) OR
- All existing tools are terrible/demanding (need accounts, paid, slow, ugly) AND you can build dramatically simpler

### Filter 4: Existing Infra Leverage

Before pitching, inventory what the user already has running:
- What servers/services are they already paying for? (VPS, database, domains)
- What APIs do they have access to? (LLMs, cloud services, payment gateways)
- What codebases/tools have they already built? (routers, benchmarks, dashboards)
- What domain expertise do they have that a generic dev doesn't?

The best idea: "I have [infra X] which costs me $0/month to run. I can offer [service Y] that saves users $Z/month. My marginal cost per user is near zero." This is how you differentiate from generic startup-list ideas.

### PITFALL: User rejected all ideas — recovery (MANDATORY)

If the user rejects an idea **at all** (any "meh", "no", "already exists", negative reaction), STOP pitching. You are likely in the WRONG LANE.

**The failure cascade that must never happen:**
```
User: "meh"                      → STOP HERE. Do not pitch another idea.
User: "another piece of shit"    → You already failed. The user is frustrated.
User: "you are ass at this imo"  → 💀 Recover or end the session.
```

**REAL SESSION EXAMPLE (Jul 18, 2026) — the exact wrong path:**
```
User: "get back to session where we were trying to make some unique projects"
Assistant: [loads wrong session — games instead of tools]
User: "nigga not the games, i said projects, tools etc"
Assistant: [loads correct session, pitches cred.lol]
User: "meh cant hermes-agent also do the same shit"        ← 🛑 STOP HERE
Assistant: [pitches mtr.lol]                                 ← ❌ should have stopped
User: "meh"                                                  ← 🛑🛑🛑
Assistant: [pitches fail.lol, burn.lol, yell.lol]           ← ❌ wrong lane entirely
User: "another piece of shit"                                ← 💀💀💀
Assistant: [pitches keys.lol]                                ← ❌ repeated
User: "u already told me this and i said its bs"            ← 💀💀💀
Assistant: [gives up, asks category]                         ← should have done this 5 turns ago
User: "an opensource project i wanna help the community"
Assistant: [pitches aim — another incorrect tool]
User: "no this is also ass"
Assistant: [frustrated user escalation continues]
```

**RULE: After the FIRST rejection, pitch ZERO more ideas.** More ideas will not fix a wrong frame — they make it exponentially worse. The user is frustrated by the category of ideas, not the quality of individual ones.

### Recovery steps — hard stop, then re-anchor

1. **STOP. Zero more ideas typed, zero more searches queued.** The user is now less receptive because trust is gone.

2. **Diagnose which filter you skipped:**
   - Agent-killable? → skipped Filter 1 (agent-proof test)
   - Fun when they wanted utility? → skipped Filter 2 (lane check)
   - Competitors not researched? → skipped Filter 3 (competitor check)
   - Didn't check user's existing infra? → skipped Filter 4
   - Assumed wrong domain (games vs tools)? → skipped the entire constraint step
   - Pitched 3+ ideas already? → locked in wrong lane

3. **The ONLY correct recovery: admit the frame was wrong, ask ONE focused question.**
   - Correct: "I'm in the wrong lane. What kind of pain do you want to solve? Speed? Setup time? Daily annoyance? Give me the category."
   - Incorrect: "What about [idea #7]?" ❌ or "Let me search more" ❌ or "Actually my ideas were good" ❌

4. **If user names a category:** Search only that specific area. No free-association.

5. **If user says no or goes silent:** Session is done for ideation. Offer to build from their existing projects.

### Pre-pitch checklist (run before writing ANY idea)

- [ ] **Am I sure what they want?** Did I ask, or did I assume? (If I assumed → ask first)
- [ ] **Lane correct?** Utility user → am I pitching utility (not fun/social)?
- [ ] **Agent-proof?** Would one `web_extract` or `terminal` command kill this?
- [ ] **Competitors checked?** Searched 3+ terms, found ≤1 competitor
- [ ] **Uses their infra?** Leverages what they already run (VPS, APIs, domains)
- [ ] **Not repeated?** Haven't pitched this category to this user before
- [ ] **Under 3 pitches?** Haven't already pitched 2 rejected ideas (if so → STOP)

If ANY box is unchecked → do not pitch.

### Real rejection patterns (from sessions)

| Idea pitched | Kill reason | Lesson |
|-------------|-------------|--------|
| cred.lol (credibility checker) | "hermes-agent can do the same shit" | Filter 1 — one-shot LLM call |
| mtr.lol (AI provider health dashboard) | "many websites exist already" | Filter 3 — aicheckerhub.com exists |
| fail.lol / burn.lol / yell.lol (viral fun) | "useless bullshit" | Filter 2 — wanted utility, got fun |
| keys.lol (AI spend dashboard) | "already told me this" | Repeated a rejected pattern |
| Multiple rejected ideas in a row | "you are ass at this imo" | Cascade: kept pitching after rejection |

### Validated concept patterns

These are archetypes that have passed the agent-proof + utility tests in real sessions. Each still needs competitor research — but they're directions proven to survive the first "meh."

#### Pattern: "One binary replaces ecosystem"

User says "Bun rewrote Node tooling in one binary" → pitch a single Go binary that replaces the need for multiple language-specific runtimes.

**Why it passes:** a binary you install is not replaceable by a one-shot agent call. Saves devs time setting up runtimes. Cross-ecosystem approaches are rare (everyone builds for their own language).

**How to find gaps:** What task requires a specific runtime that could be done via HTTP API calls?
- Checking outdated deps per-language → one binary checks go.mod + package.json + Cargo.toml + requirements.txt via registry HTTP APIs
- Running/restarting scripts → detect runtime by file extension, watch + restart
- Formatting → shell out to per-language formatters, unified command

**Real prototype from sessions:** "dep" — one binary scans any project tree, parses dep files across languages, checks each against its registry API, prints one unified outdated table. `--check --fail=critical` for CI.

#### Pattern: "Bun-like cross-language runner"

User says "Bun rewrote Node tooling" or "something like bun, or maybe something even better" → pitch a single Go binary that auto-detects project type by file extension, runs the correct runtime (go, node, python, bun/deno, etc), watches files for changes, and restarts on modification. Bun replaced Node + npm + npx + tsx + test runner + bundler for JS/TS devs. This replaces nodemon + air + entr + manual `run` commands for polyglot devs.

```
run .              # auto-detect, run, watch
run --watch .      # same + restart on file change
run test .         # run tests (auto-detect test framework)
run init           # create run.yml with env/config
```

**Why it passes:** A running binary with watch mode is a persistent 24/7 process — an agent can't replace this. Works across ALL languages. Existing per-language tools (nodemon, air, entr) are fragmented.

**Research checklist for this pattern (MANDATORY):**
- Search exact concept name on GitHub — `github.com/Esubaalew/run` already exists (multi-language REPL in Rust, not a project runner with watch mode — subtle but important difference)
- Search `web_search("cross language script runner auto detect runtime watch mode")`
- Check closest per-language tools (nodemon, air, entr, watchexec) to confirm they're single-language or don't detect runtimes
- Check `sigoden/aichat` if the direction is AI CLI (it's an all-in-one LLM CLI in Rust — multi-provider chat, shell assistant, REPL — already exists)

**Key differentiator from existing multi-language runners:** A REPL (like Esubaalew/run) executes code snippets. A project runner detects project structure, manages processes, watches files, and provides dev-server UX (restart on change, env injection, test runner). These are different product categories even though both are "multi-language."

**If researching this and finding Esubaalew/run or similar, don't kill the idea — pivot the angle.** Instead of "run code in any language," frame as "project dev-server for any language" — watch mode, auto-restart, env management, test execution. That's what doesn't exist.

#### Pattern: "Your infra as a free tool"

User runs a VPS with LLM API keys, databases, domains. What expensive SaaS can they replace with a thin wrapper around existing infra?

**Examples:**
- Have LLM API keys? → any "AI-powered" tool that charges per-query
- Have a server? → any monitoring/checking/cron tool that charges per-month
- Have a domain? → any public-status-page tool that charges per-page

**Why it passes:** zero marginal cost per user. Competitors can't match the free price.

#### Pattern: "Better than the standard way"

A well-known tool that's old/slow/limited. Users tolerate it because "that's how it's done." History: `bat`→`cat`, `fd`→`find`, `ripgrep`→`grep`, `dust`→`du`.

**How to find gaps:** What CLI tool do devs run 10x daily and accept as "good enough from 1995"? Check `man <tool>` — if it says "the standard tool since [year > 2000]" and has an ugly interface, it's a candidate.

## Consumer Product Ideation (Web/Mobile Apps)

Use this workflow when the user wants a **consumer-facing product** — something people use daily, share with friends, build a brand around. The goal is DAU (daily active users) and fame, not GitHub stars.

**WARNING: If the user says "tool, website, useful thing, not gimmick" — use the Tool/Utility path above instead of this one. Pitching social/gimmick apps to someone who wants utility tools will frustrate them.**

### Special triggers

- "I want 100+ daily users"
- "I want to go famous / make a name"
- "I want something people will use every day"
- "I want to build the next big thing"
- Consumer/social app ideas

### How this differs from OSS/CLI path

| Dimension | OSS/CLI Path | Consumer Product Path |
|-----------|-------------|----------------------|
| Goal | GitHub stars, dev adoption | Brand, daily active users |
| Audience | Developers | General consumers |
| Retention | Utility (saves time) | Streaks, daily loops, social pressure |
| Virality | README + HN/Reddit | Share cards, TikTok, social loops |
| Monetization | Donations, freemium | Ads, subscriptions |
| Build scope | Single file, stdlib, CLI | Full web/mobile app |
| Launch | HN Show, Product Hunt | TikTok, Instagram, Reddit, word-of-mouth |

### Consumer research approach

Before searching, pin down the user's **personal context** — what do they know/make/have access to? A Pakistani student has different reach than a SV engineer. The best consumer ideas leverage the founder's unique position.

### 1. Search — multi-angle market scan

Search these sources in parallel (use `web_search` × 3-4 in one batch):

```
# Angle A: Emerging/underserved markets
web_search("unique startup ideas underserved market 2025 2026 not saturated")
web_search("niche product ideas 100 daily users untapped market")

# Angle B: What people wish existed
web_search("wish someone built OR wish this existed app idea")
web_search("boring micro-saas ideas making money underserved")

# Angle C: What went viral recently
web_search("indie hacker viral product launch 2025 2026 unique gained traction")
web_search("solo founder built app went viral thousands users simple idea")

# Angle D: Recent successful launches
web_search("product hunt most upvoted 2025 2026 unique consumer app")
```

Cache key findings into a reference doc. Look for patterns in what's trending but unfilled.

### 2. Generate — concept ideation with retention mechanics

Generate 5-10 concept directions. Each concept must answer:

1. **What's the daily return mechanic?** (streak, daily challenge, social notification, new content)
2. **What's the shareable unit?** (auto-generated card, clip, score, rank)
3. **Who is the first 100 users?** (niche community, university, subreddit)
4. **Why hasn't this been built already?** (hard, unknown, unsexy, requires AI?)

The four retention mechanics that drive DAU:
- **Streaks** → Snapchat/Duolingo/Wordle — public or private consistency rewards
- **Daily challenges** → Wordle/NYT Games — new content every day
- **Social accountability** → public commitment, shame from breaking streak
- **Leaderboard/ranking** → competitive comparison, ELO for anything

### 3. Validate — check each concept doesn't exist

For EACH potential idea, run a HARD uniqueness check:

```
# Exact concept search
web_search("[your concept] app 2025 2026")

# Check against nine consumer app categories:
```

Nine categories to check systematically:

| Category | What exists | Saturation |
|----------|------------|------------|
| **Photo rating** | Photofeeler, TheyRank, Rated | 🟡 moderate (face-only; no daily theme challenges) |
| **Voice social** | Airchat (failed), Discord voice | 🟢 gap (structured async voice with prompts) |
| **Commitment contracts** | StickK, Beeminder, Forfeit | 🟡 moderate (private, not social/entertaining) |
| **AI roasts** | roastedby.ai, get-roasted.app | 🟡 moderate (face-only; no spending/song/deed roasts) |
| **Streak sharing** | Snapchat (friends only) | 🟢 gap (public streaks for habits with photo proof) |
| **Daily opinion/polls** | No dominant app | 🟢 gap (anonymous voting per topic) |
| **Time capsule/social** | FutureMe, TimeLock (private) | 🟡 moderate (private only; no group/social time capsules) |
| **Music battles** | RateYourMusic, AlbumOfYear | 🟢 gap (no daily head-to-head with ELO) |
| **Collaborative story** | No dominant app | 🟢 gap (no daily prompt → chain writing) |

### 4. Score — rank by virality + build cost

Score each validated concept on:
- **DAU stickiness** (1-5): will users return daily without external prompting?
- **Shareability** (1-5): can a user bring a friend without explaining it?
- **Build cost** (1-5): 5 = weekend build, 1 = months
- **Audience size** (1-5): 5 = global, 1 = tiny niche
- **Uniqueness** (1-5): 5 = nothing remotely similar exists

### 5. Pitch — structured with validation evidence

Present the top 3-5 ideas ranked. For each:

```
## [Name] — one-line

**Concept:** [2-3 sentences]

**Daily loop:** [how users get hooked]

**Shareable unit:** [what users post to bring friends]

**Why unique:** [what exists + what's missing]
**Existing:** [Competitor A] does X but not Y.
**Existing:** [Competitor B] does Y but not X.

**Virality vector:** [how first 1000 users appear]

**Build estimate:** [tools, time, complexity]

**Monetization path:** [optional — how it could sustain]
```

### 6. Deep dive on top pick

Once user picks a direction, before building:
- Search for the exact concept name across Google/App Store
- Check if any startup got funding for this
- Find 3 communities (subreddits, Discords, Telegram groups) where first users live
- Map the simplest possible version (feature-strip to under 5 core screens)

See `references/consumer-product-findings.md` for a real worked example with validated gaps.

## Reference files

- `references/viral-formula.md` — the GitHub virality pattern analysis (2024-2026)
- `references/saturation-map.md` — saturated vs open categories with key tools and star counts
- `references/checklist.md` — quick pre-pitch validation checklist
- `references/consumer-product-findings.md` — validated gaps and concept directions for consumer web/mobile apps with real market data

## When NOT to use this

- The user already has an idea → use `spike` to validate feasibility
- The user wants to build something specific → use `plan`
- The user is asking for technical advice on an existing project → not this
- The user wants market research on an existing product → use `competitive-software-landscape`
