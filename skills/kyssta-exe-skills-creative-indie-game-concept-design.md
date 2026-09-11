---
name: indie-game-concept-design
description: >-
  Generate original, market-verified indie game concepts for solo AI-assisted
  development. Covers ideation, filtering, Steam API research, and the full
  presentation format for darkly humorous, streamable concepts.
---

# Indie Game Concept Design

Use when the user asks you to **generate original game ideas**, **concept a new indie game**, or **find a gap in the market for a solo dev**. This is a structured creative-research workflow, not a brainstorm.

## Trigger phrases
- "come up with game ideas"
- "indie game concept"
- "generate game concepts"
- "what game should I make"
- "darkly humorous game"
- "solo developer game concept"

## Workflow

### 1. Generate 40+ rough concepts privately

Run against the user's constraints (usually: solo dev, AI-assisted, dark comedy, streamable). Do not show the 40. Write them as one-liners in your scratch space. Target 6-8 viable survivors. Reject on:

- Too similar to existing games (have a hunch? research it)
- Mostly narrative / walking sim
- Too large for one dev (open world, complex MP networking)
- Hard to communicate in one sentence
- Depends on multiplayer being active
- Funny only in description, not in gameplay
- Missing repeatable gameplay loop
- Built around a single scripted joke
- Falls in any "explicitly avoid" category the user listed

### 2. Filter to 8 survivors

Each survivor must have:
- A one-sentence hook (the player action)
- A **signature mechanic** — one physical/systemic interaction that defines the gameplay
- Dark comedy baked into the system, not the writing
- Strong viral clip potential (physics fails, awkward moments, unexpected outcomes)
- Solo-dev scope (3-12 environments, ~10 NPC types, 1-2 complex systems)
- Demo potential: one polished 20-45 min scenario

### 3. Research each survivor

**Primary method — Steam Store API** (use when web_search credits are exhausted):
```bash
# Get game details including description + genres
curl -s "https://store.steampowered.com/api/appdetails?appids=<appid>" \
  -H "User-Agent: Mozilla/5.0" | python3 -c "
import json, sys
data = json.load(sys.stdin)
aid = list(data.keys())[0]
if data[aid]['success']:
    d = data[aid]['data']
    print('NAME:', d.get('name'))
    print('SHORT:', d.get('short_description','')[:400])
    print('TAGS:', [t['description'] for t in d.get('genres',[])])
"

# Search Steam by keyword
curl -sL "https://store.steampowered.com/search/?term=<query>&category1=998" \
  -H "User-Agent: Mozilla/5.0" 2>&1 | \
  grep -oP 'href="https://store.steampowered.com/app/[^"]+"' | head -10
```

**`references/steam-api-research.md`** — full reference with all Steam API endpoints and fallback HTML parsing.

For each concept, build a comparison table:

| Game | Overlap | Difference |
|------|---------|------------|
| [name] (link) | shared elements | mechanical-level distinction |

Score originality 1-10. Discard if originality > 5 or a direct competitor exists.

### 4. Present the final concepts

Each concept gets the full format below. Keep the writing tight — data first, commentary brief.

## Concept template

### [Title]

**Hook:** One sentence — what the player actually does.

**Player fantasy:** The role and why it feels interesting.

**Core loop:** 5-8 step repeatable loop, numbered.

**Signature mechanic:** The one interaction that makes this game recognizable.

**Example scenario:** Complete situation start-to-finish, including how it fails.

**Dark humour:** Where the comedy comes from during gameplay (not from writing).

**Viral moments:** 5 specific clipable/thumbnailable moments.

**Progression:** Upgrades, unlocks, complications, long-term goals.

**Solo scope:** Environments, NPC types, major systems, demo content, what NOT to build.

**Visual direction:** Low-poly retro (PS2/late-2000s) aesthetic note — keep it under 4 lines.

**Competitor table:** Direct and adjacent games with mechanical differences.

**Risk scores (1-10):** Originality, Solo feasibility, Viral potential, Replayability, Development risk, Marketability.

**Verdict:** Prototype immediately / Worth prototyping / Build as second project / Discard.

### 5. Rank and roadmap

Rank top 3. For #1, include:
- 30-minute demo plan
- First scenario walkthrough
- 10 minimum-required mechanics
- ~20 required assets (counted)
- Dev roadmap (prototype → demo → Steam page → playtest → release)
- Short Steam description
- Thumbnail concept
- 3 possible names
- Strongest failure reason
- 7-day fun-test plan

### 6. Game Bible & Production Documentation

Once a concept is chosen and validated, create a **game design bible** — the single source of truth for development. Sections:

- Core identity table (genre, engine, price, playtime, visual style, key emotion)
- Setting & lore (1 paragraph + tone)
- Gameplay loop (7-8 numbered steps)
- Signature mechanic deep-dive (how it works, edge cases, comedy source)
- Progression systems (unlock tree, upgrade economy, rank ladder)
- Event/crisis system (procedural params, difficulty curve)
- NPC roster (+ placeholder voice scripts)
- HUD/UI mockups (ASCII layouts)
- Visual direction (colour palette table, per-environment notes, shader specs)
- Audio direction (music per context, SFX table, voice scripts)
- Demo plan (tutorial + scenarios, timed)
- Dev roadmap (phased)
- Steam page materials (description, trailer opening, thumbnail)
- Risk assessment

**Asset prompts** directory: `assets/prompts/` with one `.md` per category — CHARACTERS, ENVIRONMENTS, VEHICLES, UI_SCREENS, AUDIO, TECHNICAL. Each prompt: purpose, generation prompt (Midjourney/SD/Meshy ready), polygon budget, rig specs, texture size. See `references/game-bible-template.md`.

## Important constraints

- The humour is situational and systemic — deadpan characters in absurd situations, not memes or internet jokes
- The player PHYSICALLY does something — manipulate, operate, construct, destroy, repair, transport, control, experiment
- Not a "normal job but scary" — the job itself creates absurd situations through systems
- Solo dev means ~4-8 hours of content for full release, 20-45 min for demo
- Low-poly retro visuals are a production constraint, not a style choice — chunky characters, visible polygons, simple textures, strong lighting
- Price target: $5-15 on Steam with a free demo
- YAGNI everything that isn't the core loop

## Pitfalls

- **Over-scoping:** Each new job/environment/mechanic doubles the work. The demo should reuse 80% of what the full game uses.
- **Narrative creep:** If you find yourself designing a story rather than a system, stop. The story emerges from systems failing.
- **Physics scope:** Physics-based games are viral but physics engines are rabbit holes. Build the minimal physics that creates comedy — cargo sliding is funny, realistic liquid simulation is not needed.
- **Vanity features:** Don't build character customization, skill trees, crafting, or dialogue trees unless they're the core mechanic.
- **Research laziness:** If you haven't checked Steam for a competing concept, you haven't researched. Use the API — it's free and fast.
