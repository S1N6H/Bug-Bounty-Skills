---
name: indie-game-research
description: Verify indie game concept originality via Steam API + itch.io deep search. No web_search credits? Use curl directly against Steam's API. Keep a findings log so next re-check is delta-only.
tags: [steam, itch, game-research, competitor-analysis, market-validation]
---

# Indie Game Market Research

Validate an indie game concept by checking if anything mechanically similar already exists on Steam, itch.io, or the broader market.

## When to use

- User asks "check if any game like this exists"
- Before committing to prototype a new game concept
- Periodically re-validating an existing concept (new games launch weekly)

## Research methodology

### 1. Search Steam API directly (no browser, no web_search credits)

Steam's store search API is free and returns JSON. Much faster than scraping HTML.

```bash
# Keyword search
curl -s "https://store.steampowered.com/api/storesearch/?term=hearse+funeral&cc=US&l=en" \
  -H "User-Agent: Mozilla/5.0"

# Get full game details by app ID
curl -s "https://store.steampowered.com/api/appdetails?appids=4159710" \
  -H "User-Agent: Mozilla/5.0"
```

The storesearch API returns `items[]` with `name`, `id`, `price`, `short_description`. The appdetails API gives genres, tags, developers, release date, full description.

**Pitfall:** The storesearch API is shallow — it may not return all relevant results for niche terms. For thoroughness, also scrape the HTML search page:

```bash
# Get app IDs from HTML (more comprehensive)
curl -s "https://store.steampowered.com/search/?term=cargo+physics&category1=998" \
  -H "User-Agent: Mozilla/5.0" | grep -oP 'data-ds-appid="[^"]+"'
```

### 2. Search strategy per concept

For each concept, run at least these search categories:

- **Exact premise**: "hearse delivery", "dimensional breach sealing"
- **Core mechanic**: "cargo physics", "input lag", "chain physics"
- **Theme + genre combo**: "funeral comedy", "tow truck recovery physics"
- **Adjacent games from prior research**: re-verify they haven't pivoted or added features

### 3. Evaluate each result

For each result, determine:
- Does the **core mechanic** match? (not just theme)
- Is the **genre** the same? (racing vs physics puzzle vs management sim)
- Is the **tone** similar? (serious sim vs dark comedy)
- Has it **launched or changed** since your last research?

A game sharing a theme (hearse, funeral, breach) but different mechanics is **not a competitor**. Document why, so the user can see the reasoning.

### 4. Save findings as reference

Write results to a reference file under the concept name so re-checks are delta-only:
- `references/<concept-name>.md` — all games found, overlap analysis, verdict
- On re-check, compare new results against the reference to spot changes

### 5. Check itch.io as secondary source

itch.io requires JS rendering, so curl won't work reliably. Alternative approaches:
- Use `site:itch.io <keywords>` in web_search (when credits available)
- Browse manually for critical concepts
- itch.io is more volatile — a smaller game-jam project here is less concerning than a Steam competitor

## Verdict phrasing

For each concept, deliver a clear verdict:

> **Concept X: CLEAR.** Closest match was [Game Y] but it's [genre/tone difference]. No direct competitor.

Or if concerning:

> **Concept X: RISK.** [Game Y] shares [mechanic]. Key differences: [differences]. Monitor if [scenario where it pivots].

## Reference format

```
# Concept: FINAL RUN
Last checked: 2026-10-13

## Results
| Game | App ID | Genre | Overlap | Why not competitor |
|------|--------|-------|---------|-------------------|
| Hearse Hero | 4159710 | Arcade Racing | Hearse theme | Crazy Taxi clone, no cargo physics or will delivery |
| My Funeral Home | 1214870 | Business Sim | Funeral theme | Management sim, no physics-based delivery gameplay |

## Verdict
CLEAR. No direct competitor.
```

## Pitfalls

- **Storesearch API is limited**: returns ~20 results max. Use HTML scraping for broader results.
- **Same name, different game**: "Death Delivery" has TWO entries on Steam — one horror, one FPS. Always check the appdetails to confirm.
- **"Coming soon" games change**: Re-check unreleased games before committing to a concept. A game in development might pivot toward your space.
- **Don't confuse theme with mechanic**: A hearse in a racing game ≠ a hearse delivery physics game. The mechanic is what matters.
- **Price/Free is not reliable**: The API price field sometimes shows defaults. Check the Steam page directly for accuracy.
