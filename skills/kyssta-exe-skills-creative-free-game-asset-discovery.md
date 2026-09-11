---
name: free-game-asset-discovery
description: Find, verify, and curate free (CC0/public domain) game assets for browser-based games. Covers searching itch.io, Kenney, OpenGameArt, CraftPix; verifying true $0 cost vs "name your own price"; matching assets to game bible specs; and delivering verified asset manifests.
triggers:
  - User needs free game assets (sprites, tilesets, UI, audio) for a game project
  - User provides a game bible / design doc and needs matching assets
  - User says "recheck these are free" or "verify these are CC0"
  - Building a browser/HTML5 game with Phaser, Godot, Unity WebGL, etc.
  - Need asset manifest mapping game entities to verified free files
skills_used:
  - web_search (primary)
  - skill_manage (to save verified manifests as references)
---

## Core Workflow

### 1. Parse Game Bible for Asset Requirements
Extract from the game bible:
- **Perspective**: top-down, side-scroller, isometric, platformer
- **Resolution**: 16×16, 32×32, 64×64, vector
- **Style**: pixel art, vector, hand-drawn
- **Entity list**: player classes, NPCs, monsters, items, UI, tilesets, props, audio
- **License requirement**: CC0 only, or CC-BY acceptable, no-GPL

### 2. Search Primary Free Asset Sources (in priority order)

| Source | URL | Strength | License Filter |
|--------|-----|----------|----------------|
| **Kenney Assets** | `kenney-assets.itch.io` / `kenney.nl/assets` | Complete packs, consistent style, huge variety | All CC0 |
| **KayKit** | `kaylousberg.itch.io` + `github.com/KayKit-Game-Assets` | 3D dungeon/character packs, fully rigged & animated, CC0 | All CC0 |
| **itch.io Free + CC0** | `itch.io/game-assets/free` + `assets-cc0` tags | Largest variety, filter by tags | Use `assets-cc0` tag for guaranteed CC0 |
| **OpenGameArt.org** | `opengameart.org` → CC0 resources | Curated CC0, good characters/tilesets | Filter by CC0 license |
| **CraftPix Freebies** | `craftpix.net/freebies` | Polished free packs | Check each pack's license (some CC-BY) |
| **RGS_Dev** | `rgsdev.itch.io` | Modular characters, tileset templates | All CC0 |
| **game-icons.net** | `game-icons.net` | 4180+ SVG/PNG icons (swords, potions, shields, items, etc.) | CC BY 3.0 (attribution required) |
| **soundimage.org** | `soundimage.org` | Royalty-free fantasy/game music, MP3 + OGG | Royalty-Free (attribution required) |

**Search patterns that work:**
- `site:itch.io "free" "CC0" "16x16" "top down" "character"`
- `site:kenney.nl "tiny dungeon" "rogue" CC0`
- `site:opengameart.org "CC0" "top down" "sprite"`
- `itch.io/game-assets/assets-cc0/tag-<tag>` (e.g., `tag-16x16`, `tag-top-down`, `tag-characters`)

### 2a. game-icons.net Downloads (Individual SVG Icons)

game-icons.net provides 4180+ free SVG icons under CC BY 3.0. Each icon has a unique URL pattern. **Browser tools often timeout on this site — use curl directly.**

**URL pattern:** `https://game-icons.net/icons/ffffff/000000/1x1/{author}/{icon-name}.svg`

**Icon name discovery:**
- Browse by tag: `https://game-icons.net/tags/{tag}.html` (e.g., `blade`, `shield`, `cross`, `plant`)
- Search: `https://game-icons.net/search.html?q={query}`
- Common authors: `lorc`, `delapouite`, `sbed`, `willdabeast`, `skoll`

**Download workflow:**
```bash
# Download a single SVG
curl -sL -o sword.svg "https://game-icons.net/icons/ffffff/000000/1x1/lorc/crossed-swords.svg"

# Batch download (example: fantasy RPG items)
BASE="https://game-icons.net/icons/ffffff/000000/1x1"
declare -A ICONS=(
  ["sword-crossed"]="lorc/crossed-swords"
  ["shield"]="sbed/shield"
  ["potion"]="delapouite/health-potion"
  ["scroll"]="lorc/scroll-unfurled"
  ["torch"]="delapouite/torch"
  ["backpack"]="delapouite/backpack"
)
for name in "${!ICONS[@]}"; do
  curl -sL -o "${name}.svg" "${BASE}/${ICONS[$name]}.svg"
done
```

**Convert SVGs to PNGs (requires ImageMagick):**
```bash
# Install if needed: apt-get install -y imagemagick
for svg in *.svg; do
  png="${svg%.svg}.png"
  convert -background none -density 300 "$svg" -resize 128x128 "$png"
done
# Flags: -background none (transparent bg), -density 300 (sharp rendering), -resize 128x128 (game icon size)
```

**License note:** game-icons.net is CC BY 3.0, NOT CC0. Attribution required: "Icons by [author] from game-icons.net"

### 2b. soundimage.org Downloads (Fantasy/Game Music)

Eric Matyas's soundimage.org offers royalty-free MP3 music for games. **Direct MP3 links work with curl — no login required.**

**Browse pages:**
- `https://soundimage.org/fantasywonder/` — Fantasy 1 (RPG, adventure, ambient)
- `https://soundimage.org/fantasy-2/` — Fantasy 2 (mystery, dragon, menu themes)
- `https://soundimage.org/fantasy-3/` through `fantasy-10/` — More fantasy styles

**Download pattern:** Extract MP3 URLs from page content, then curl:
```bash
curl -sL -o "fantasy-village-theme.mp3" "https://soundimage.org/wp-content/uploads/2014/09/Our-Mountain_v003.mp3"
curl -sL -o "fantasy-magic-theme.mp3" "https://soundimage.org/wp-content/uploads/2023/12/Spells-a-Brewin.mp3"
```

**Verify downloads:** Check file size — valid MP3s are typically 500KB–5MB. Files under 1KB are likely error pages:
```bash
for f in *.mp3; do
  size=$(stat -c%s "$f")
  if [ "$size" -lt 1000 ]; then
    echo "WARNING: $f is only $size bytes — likely a failed download"
    rm "$f"
  fi
done
# Also verify with: file *.mp3  (should show "MPEG ADTS, layer III")
```

**License note:** Royalty-free with attribution: "Music by Eric Matyas, Soundimage.org"

### 2c. Direct kenney.nl Downloads (Preferred for Kenney)

Kenney assets can be downloaded directly from `kenney.nl` without itch.io. The download URL is embedded in the HTML, hidden behind a donation modal. This is **more reliable for scripted downloads** than itch.io's "name your own price" flow.

**Download workflow for kenney.nl assets:**
1. Find the asset page: `https://kenney.nl/assets/<pack-name>` (e.g., `ui-pack`, `rpg-audio`, `impact-sounds`)
2. Extract the direct zip URL:
   ```bash
   curl -sL "https://kenney.nl/assets/<pack-name>" | grep -oP "href='[^']*kenney[^']*\.zip'"
   ```
   Returns something like: `href='https://kenney.nl/media/pages/assets/<pack-name>/<hash>/kenney_<pack-name>.zip'`
3. Download: `curl -L -o kenney_<pack-name>.zip "<extracted-url>"`
4. Extract: `unzip -o kenney_<pack-name>.zip -d <pack-name>/`
5. Assets are typically in `<pack-name>/Audio/` (OGG), `<pack-name>/PNG/` (sprites), or `<pack-name>/Vector/` (SVG)

**Example — downloading 3 packs:**
```bash
# UI Pack (430+ sprites, 6 sounds, 2 fonts)
curl -sL "https://kenney.nl/assets/ui-pack" | grep -oP "href='[^']*kenney[^']*\.zip'" | head -1 | sed "s/href='//;s/'//" | xargs -I{} curl -L -o kenney_ui-pack.zip "{}"

# RPG Audio (54 OGG sounds: footsteps, doors, coins, books, knives)
curl -sL "https://kenney.nl/assets/rpg-audio" | grep -oP "href='[^']*kenney[^']*\.zip'" | head -1 | sed "s/href='//;s/'//" | xargs -I{} curl -L -o kenney_rpg-audio.zip "{}"

# Impact Sounds (132 OGG sounds: impacts, footsteps on various materials)
curl -sL "https://kenney.nl/assets/impact-sounds" | grep -oP "href='[^']*kenney[^']*\.zip'" | head -1 | sed "s/href='//;s/'//" | xargs -I{} curl -L -o kenney_impact-sounds.zip "{}"
```

**All Kenney assets are CC0.** No need to verify $0 — they're always free. The donation prompt is optional.

### 2b. GitHub Repos as Download Source (Preferred for Automation)

Many itch.io CC0 asset creators also publish on GitHub — this is **more reliable for scripted downloads** than itch.io's "Name your own price" flow:

| Creator | itch.io | GitHub Org | Notes |
|---------|---------|------------|-------|
| **KayKit** | `kaylousberg.itch.io/*` | `github.com/KayKit-Game-Assets/*-1.0` | 3D dungeon, characters, animations, forest, etc. |
| **Kenney** | `kenney-assets.itch.io` | `github.com/KenneyNL` | Some packs mirrored |
| **RGS_Dev** | `rgsdev.itch.io` | Check individual repos | Modular characters |

**Download workflow for GitHub repos:**
1. Search: `site:github.com "KayKit" OR "kenney" <pack-name>`
2. Download zip: `curl -L -o <name>.zip "https://github.com/<org>/<repo>/archive/refs/heads/main.zip"`
3. Extract: `unzip -q <name>.zip`
4. Assets are typically in `addons/<pack_name>/Assets/` or `addons/<pack_name>/Characters/`

**Verify CC0 license:** Check for `LICENSE.txt` in the repo root or assets directory — should reference CC0 1.0 Universal.

### 3. Verify True $0 Cost (Critical Step)

**Red flags — NOT actually free:**
- "Name your own price" **without** confirmation that $0 works → **ALWAYS TEST** by visiting the page
- "Free" in title but price shown on itch.io page ($2, $3, $5)
- "Free with account" / "Free for Patreon supporters"
- Discounted price shown (e.g., "-50% $5") = **NOT FREE**

**Green flags — VERIFIED FREE:**
- itch.io page shows "Download Now → Name your own price" → enter $0 → download works
- Explicit "CC0" or "Public Domain" in description
- Kenney assets (all CC0, "name your own price" = $0 works)
- RGS_Dev packs (explicit "Free CC0" in title)
- bobddadoo Monster Starter Pack (free download)
- Soulbit Free 16×16 Icons (free)
- Free Pixel Gear by Henry Software (free)

**Verification command:** Visit the itch.io page → click "Download Now" → enter 0 → confirm download starts.

### 4. Match Assets to Game Bible Entities

Create a mapping table:
| Game Entity | Required Spec | Verified Asset Pack | License | Download Link |
|-------------|---------------|---------------------|---------|---------------|
| Player Knight | 16×16, 4-dir, animated | Kenney Roguelike Characters | CC0 | kenney-assets.itch.io/roguelike-characters |
| Green Slime | 16×16, animated idle/walk/attack | bobddadoo Monster Starter Pack | Free | bobddadoo.itch.io/monster-starter-pack |
| Shop Interior | 16×16, top-down tileset | Old Shop Tile Set (GabrielaTot) + Kenney Tiny Town | Free + CC0 | itch.io search + kenney-assets.itch.io |

### 5. Deliver Verified Asset Manifest

Output format:
```markdown
## ✅ VERIFIED FREE Assets for [Game Name]

### KayKit 3D Assets (Downloaded 2026-07-06)

**Note:** These are 3D assets (GLB/OBJ) — for 2D Phaser use, they need sprite sheet conversion or can be used as reference art for 2D variants.

### KayKit Dungeon Remastered
| Pack | License | Source | Verified |
|------|---------|--------|----------|
| Dungeon Remastered 1.0 | **CC0 1.0 Universal** | [GitHub](https://github.com/KayKit-Game-Assets/KayKit-Dungeon-Remastered-1.0) | ✅ |

**622 files (18MB):** 203 GLB models, 208 OBJ models, 1 texture atlas (1024×1024)
- Walls (32), Floors (34), Stairs (8), Banners (42), Props (67), Barriers (15), Other (21)

### KayKit Adventurers Character Pack
| Pack | License | Source | Verified |
|------|---------|--------|----------|
| Adventurers Character Pack 2.0 | **CC0 1.0 Universal** | [GitHub](https://github.com/KayKit-Game-Assets/KayKit-Character-Pack-Adventures-1.0) | ✅ |

**72 files (19MB):** 5 character models + 27 accessory models
- Characters (GLB): Barbarian, Knight, Mage, Rogue, Rogue_Hooded (fully rigged & animated)
- Accessories (GLTF): arrows, axes, crossbows, daggers, shields, swords, staffs, wands, spellbooks, mugs, quivers, smokebombs

### Download Location
All KayKit assets saved to: `/root/dungeon-market-tycoon/assets/raw/kaykit/`

---

## Tier 1: Foundation Packs (2D Assets - Download First)
| Pack | Creator | Platform | License | Direct Link | Verified $0 |
|------|---------|----------|---------|-------------|-------------|

### By Category (Heroes, Monsters, Items, UI, Tilesets, Audio)
...

### ⚠️ Assets Removed (Not Actually Free)
| Asset | Why Removed |
|-------|-------------|

### Download Script / Phaser Manifest (optional)
```

---

## Parallel Delegation Pattern (Recommended for Multi-Source Downloads)

When downloading from 3+ sources, dispatch parallel subagents to cut wall-clock time:

```
delegate_task(tasks=[
  { goal: "Download KayKit packs from GitHub to /path/raw/kaykit/", role: "leaf" },
  { goal: "Download Kenney packs from kenney.nl to /path/raw/kenney/", role: "leaf" },
  { goal: "Download icons from game-icons.net + audio to /path/raw/icons/ and /path/raw/audio/", role: "leaf" },
])
```

Each subagent gets its own terminal session, works independently, and returns a summary with file counts and paths. The parent agent continues building/polishing the game while downloads run in background.

**Why this works well:** Asset downloads are I/O-bound and independent. Parallelizing avoids blocking the main agent for minutes. The subagent summaries tell you exactly what landed.

**Post-download verification:**
```bash
find /path/raw/ -type f | wc -l          # total files
du -sh /path/raw/                         # total size
find /path/raw/ -name "*.png" | wc -l    # count PNGs
find /path/raw/ -name "*.wav" -o -name "*.ogg" | wc -l  # count audio
```

---

## Pitfalls & Gotchas

| Pitfall | Prevention |
|---------|------------|
| **"Name your own price" ≠ free** | Always verify $0 download works before listing |
| **Discounted paid assets in "free" search** | Filter by `assets-cc0` tag on itch.io, not just `free` tag |
| **CC-BY assets mixed in** | Check license field; user asked for CC0 only |
| **Inconsistent resolutions** | Note resolution per pack; warn if mixing 16×16 and 32×32 |
| **Missing animations** | Verify animation frames exist (idle, walk, attack, hit, die) |
| **Kenney packs scattered across pages** | Use "All-in-1" preview page to see all packs at once |
| **CraftPix requires attribution sometimes** | Check each pack; prefer Kenney/OpenGameArt for pure CC0 |
| **Vector vs pixel art mismatch** | Confirm style matches game bible (pixel art for this user) |
| **3D assets for 2D games** | KayKit and similar packs are 3D (GLB/OBJ). For 2D games (Phaser, etc.), note they need sprite sheet conversion or use as reference art. Check ASSET_MANIFEST.md in download directory for format details. |
| **GitHub repo structure** | Assets are typically deep: addons/pack/Assets/gltf/. Don't assume files are at repo root. |
| **Failed downloads disguised as valid files** | Some sites return HTML error pages with 200 status. Always validate: check file size (MP3s <1KB are suspicious), run `file` command to verify type, compare against expected format. |
| **Browser tools timeout on game-icons.net / soundimage.org** | Use `curl` directly instead. The URL patterns are documented in sections 2a and 2b above. |

---

## Verification Checklist (Run Before Delivery)

- [ ] Every listed asset visited on itch.io/source page
- [ ] $0 download confirmed working (or explicit CC0 statement)
- [ ] Resolution matches game bible (16×16 for this project)
- [ ] Perspective matches (top-down for this project)
- [ ] Animation frames verified for characters/monsters
- [ ] License confirmed CC0 or public domain
- [ ] Direct download links provided (not search pages)
- [ ] "Not free" assets explicitly called out in removal section
- [ ] For 3D packs: note format (GLB/OBJ) and that conversion may be needed for 2D games

---

## Reference Files

- `references/verified-free-asset-sources.md` — Master list of verified free sources with direct links
- `references/dungeon-market-tycoon-asset-manifest.md` — Example manifest for this game
- `references/asset-download-verification.md` — Process for verifying true $0/CC0 downloads
- `templates/asset-manifest-template.md` — Reusable template for new games