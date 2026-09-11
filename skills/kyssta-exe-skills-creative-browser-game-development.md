---
name: browser-game-development
description: "Build 2D browser games with Phaser 3 + TypeScript + Vite. Covers project setup, tsconfig for Phaser, procedural texture generation, asset pipeline integration, audio, scene architecture, and CrazyGames HTML5 compliance."
version: 1.0.0
author: Hermes Agent
tags: [phaser, typescript, vite, browser-game, html5, crazygames, tycoon]
related_skills: [free-game-asset-discovery]
---

# Browser Game Development (Phaser 3 + TypeScript + Vite)

Build complete 2D browser games using Phaser 3, TypeScript, and Vite. This skill covers the full pipeline from project setup through CrazyGames submission.

## Triggers

- Building a browser/HTML5 game with Phaser
- User asks to create a tycoon, idle, RPG, or arcade game
- CrazyGames, Poki, Newgrounds, or itch.io game submission
- Converting 3D assets to 2D sprites for Phaser
- Integrating sound effects and music into Phaser games

## Tech Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Engine | Phaser 3.80+ | Lightweight 2D, great for tycoon/UI games |
| Language | TypeScript | Type safety, but needs relaxed config for Phaser |
| Bundler | Vite 5.x | Fast builds, HMR, asset handling |
| Ads | CrazyGames HTML5 SDK | Required for platform |
| Audio | Phaser sound or Howler.js | Cross-browser |
| Save | localStorage / IndexedDB | Offline-first |
| Fonts | Google Fonts or Kenney fonts | TTF/OTF loaded via Phaser |

## Project Setup

### package.json
```json
{
  "name": "game-name",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": { "phaser": "^3.80.1" },
  "devDependencies": { "typescript": "^5.4.5", "vite": "^5.4.5" }
}
```

### tsconfig.json (CRITICAL — Phaser requires relaxed settings)
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "moduleResolution": "bundler",
    "strict": false,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "types": []
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

### vite.config.ts
```typescript
import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  resolve: { alias: { '@': path.resolve(__dirname, 'src') } },
  server: { port: 3000, host: '0.0.0.0' },
  build: {
    target: 'es2020',
    rollupOptions: {
      output: { manualChunks: { phaser: ['phaser'] } },
    },
  },
});
```

### index.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <title>Game Title</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { width: 100%; height: 100%; overflow: hidden; background: #0a0a1a; }
    #game-container { width: 100%; height: 100%; display: flex; justify-content: center; align-items: center; }
    canvas { display: block; }
  </style>
</head>
<body>
  <div id="game-container"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

## Project Structure
```
project/
├── public/
│   └── assets/
│       ├── ui/           # Kenney UI PNGs (buttons, panels)
│       ├── icons/        # game-icons.net PNGs
│       ├── characters/   # Hero/NPC sprites
│       ├── enemies/      # Monster sprites
│       ├── buildings/    # Building sprites
│       ├── items/        # Item icons
│       ├── resources/    # Crafting material icons
│       ├── audio/        # SFX (OGG) + music (MP3)
│       └── fonts/        # TTF font files
├── src/
│   ├── main.ts           # Entry: register scenes, create Phaser.Game
│   ├── config/           # Data definitions (items, enemies, etc.)
│   ├── scenes/           # One class per screen
│   ├── systems/          # Game logic (save, economy, crafting)
│   ├── entities/         # Game objects (customer, hero, monster)
│   └── ui/               # Reusable UI components
├── tsconfig.json
├── vite.config.ts
├── package.json
└── index.html
```

## Key Patterns

### 1. Procedural Texture Generation (BootScene)
Generate placeholder sprites programmatically — the game works immediately without any assets:

```typescript
private generateTextures(): void {
  const g = this.add.graphics();
  g.setVisible(false); // don't render, just generate

  // Colored rectangle
  g.clear();
  g.fillStyle(0xDEB887, 1);
  g.fillRoundedRect(0, 0, 48, 48, 6);
  g.generateTexture('item_wooden_sword', 48, 48);

  // Colored circle
  g.clear();
  g.fillStyle(0x8B4513, 1);
  g.fillCircle(14, 14, 14);
  g.generateTexture('res_wood', 28, 28);

  g.destroy();
}
```

**Pitfall:** `this.make.graphics({ add: false })` fails with Phaser TS types. Use `this.add.graphics()` + `g.setVisible(false)` instead.

### 2. Asset Loading with Fallbacks
Load real assets, fall back to procedural:

```typescript
preload(): void {
  // Try loading real assets
  this.load.image('ui_btn', 'assets/ui/btn_normal.png');
  this.load.audio('sfx_coin', 'assets/audio/handleCoins.ogg');

  // Fallback on error
  this.load.on('loaderror', (file: Phaser.Loader.File) => {
    console.warn('Failed to load:', file.key, '- using fallback');
  });

  // Generate procedural textures as fallbacks
  this.generateTextures();
}
```

### 3. Audio File Naming (Kenney)
Kenney audio uses specific naming patterns:
- UI: `click-a.ogg`, `tap-a.ogg`, `switch-a.ogg`
- RPG: `handleCoins.ogg`, `doorOpen_1.ogg`, `bookOpen.ogg`
- Combat: `impactPunch_heavy_000.ogg`, `impactMetal_heavy_000.ogg`

**Always verify file names exist** before referencing in loader:
```bash
ls public/assets/audio/ | head -20
```

### 4. Scene Architecture
One class per screen, shared state via SaveSystem:

```typescript
// main.ts
gameConfig.scene = [BootScene, ShopScene, DungeonScene, CraftScene];

// ShopScene.ts
export class ShopScene extends Phaser.Scene {
  private saveSystem!: SaveSystem;

  create(): void {
    this.saveSystem = new SaveSystem();
    const state = this.saveSystem.getState();
    // ... use state
  }

  // Navigate to other scenes
  private goToDungeon(): void {
    this.saveSystem.save();
    this.scene.start('DungeonScene');
  }
}
```

### 5. Save System Pattern
```typescript
const SAVE_KEY = 'game_save';

export class SaveSystem {
  private state: GameState;

  constructor() {
    this.state = this.load();
  }

  private load(): GameState {
    try {
      const raw = localStorage.getItem(SAVE_KEY);
      if (raw) {
        const saved = JSON.parse(raw);
        return { ...createNewGameState(), ...saved }; // merge with defaults
      }
    } catch (e) { console.warn('Load failed', e); }
    return createNewGameState();
  }

  save(): void {
    this.state.lastSaveTime = Date.now();
    localStorage.setItem(SAVE_KEY, JSON.stringify(this.state));
  }
}
```

### 6. Sound Effects in Scenes
```typescript
// Play with try/catch in case audio not loaded
try { this.sound.play('sfx_coin', { volume: 0.5 }); } catch(e) {}

// Background music (loop)
const music = this.sound.add('bgm_village', { loop: true, volume: 0.3 });
music.play();
```

### 7. Floating Text Animation
```typescript
private showFloatingGold(x: number, y: number, amount: number): void {
  const text = this.add.text(x, y, `+${amount} 💰`, {
    fontSize: '18px', color: '#FFD700', fontStyle: 'bold',
    stroke: '#000', strokeThickness: 3,
  }).setOrigin(0.5).setDepth(200);

  this.tweens.add({
    targets: text, y: y - 50, alpha: 0,
    duration: 1200, ease: 'Power2',
    onComplete: () => text.destroy(),
  });
}
```

### 8. Navigation Bar Pattern
```typescript
private drawNav(): void {
  this.add.rectangle(GAME_WIDTH/2, GAME_HEIGHT-27, GAME_WIDTH, 50, 0x0d0d22, 0.95);
  const tabs = [
    { label: '🏪 Shop', scene: 'ShopScene', active: true },
    { label: '⚔️ Dungeon', scene: 'DungeonScene' },
  ];
  tabs.forEach((tab, i) => {
    if (!tab.active) {
      bg.on('pointerdown', () => {
        this.saveSystem.save();
        this.scene.start(tab.scene);
      });
    }
  });
}
```

## CrazyGames Compliance

### Requirements
| Requirement | Target |
|-------------|--------|
| Initial download | ≤ 50MB (target 20MB) |
| Total size | ≤ 250MB |
| File count | ≤ 1500 |
| Load time | < 5s on fast connection |
| Playable state | < 30s |
| Console errors | Zero |
| Content rating | PEGI 12 safe |
| Ads | Rewarded only (no forced interstitials before gameplay) |

### Required Files
- `CREDITS.md` — Full attribution for all assets
- `asset_manifest.json` — Machine-readable asset list with licenses
- Credits screen in-game — Required for CC BY assets

### Ad Placement Strategy
| Placement | Trigger | Incentive |
|-----------|---------|-----------|
| Rewarded Video | After boss fight | Double loot |
| Rewarded Video | Craft speed-up | Skip timer |
| Rewarded Video | Offline earnings | 2x gold |
| Rewarded Video | Daily chest | Premium rewards |
| Interstitial | Between chapters | Natural break only |

### Revenue Model (CrazyGames)
- 200-600 DAU needed for $300-500/month
- 3-5 ad views per user per session
- RPM: $3-8 (rewarded), $0.50-2 (interstitial)
- Growth via featuring + cross-platform (Newgrounds, Poki)

## Asset Processing Pipeline

### Step 1: Download (use free-game-asset-discovery skill)
### Step 2: Organize into public/assets/ subdirectories
### Step 3: Process with ImageMagick
```bash
# SVG to PNG (game-icons.net)
convert -background none -density 300 icon.svg -resize 128x128 icon.png

# Resize character textures (KayKit)
convert input.png -resize 256x256 output.png

# Verify audio files
file *.ogg  # Should show "Ogg data"
file *.mp3  # Should show "MPEG ADTS, layer III"
```
### Step 4: Trim unused audio (reduce build size)
```bash
# Keep only files referenced in BootScene loader
KEEP="handleCoins.ogg click-a.ogg tap-a.ogg ..."
for f in *; do echo "$KEEP" | grep -q "$f" || rm "$f"; done
```
### Step 5: Rebuild and verify size
```bash
npx vite build
du -sh dist/
```

## Pitfalls & Gotchas

| Pitfall | Fix |
|---------|-----|
| `strict: true` breaks Phaser imports | Use `strict: false` in tsconfig |
| `this.make.graphics({ add: false })` error | Use `this.add.graphics()` + `setVisible(false)` |
| Phaser types: `Property 'add' does not exist` | These are TS-only errors; Vite/esbuild builds fine |
| `Object.entries` not found | Set `"lib": ["ES2020"]` in tsconfig |
| Kenney audio filenames differ from expected | Always `ls` the audio directory first |
| Build includes all public/ assets | Trim unused files before final build |
| 3D assets (GLB/OBJ) can't be used directly | Convert to 2D sprites via ImageMagick or Blender |
| Vite dev server detected as long process | Use `node ./node_modules/vite/bin/vite.js` directly |
| `npm install` triggers postinstall hooks | Add `--ignore-scripts` flag |
| Canvas black on load | Check `backgroundColor` in game config |

## Testing Checklist

- [ ] `npm run build` succeeds with zero errors
- [ ] `npm run dev` serves game on localhost
- [ ] All scenes navigate correctly
- [ ] Save/load persists across refresh
- [ ] Sound effects play on interactions
- [ ] Background music loops
- [ ] No console errors
- [ ] Total dist/ size under 50MB
- [ ] Credits screen shows all attributions
- [ ] Tutorial guides new players
- [ ] Offline earnings calculate correctly
- [ ] Daily rewards reset properly

## Reference Files

- `references/dungeon-market-tycoon-case-study.md` — Full case study with project structure, asset pipeline, and lessons learned
- `references/phaser-tsconfig-and-asset-processing.md` — TypeScript config gotchas and ImageMagick commands
- `references/game-project-git-setup.md` — Git repo setup, .gitignore, session continuity pattern

## Real-World Application: Dungeon Market Tycoon

This skill was applied to build a complete Phaser 3 + TypeScript + Vite tycoon game during a development session. See references/dungeon-market-tycoon-case-study.md for a detailed case study covering:

- Asset sourcing and processing (Kenney UI, KayKit, game-icons.net, royalty-free audio)
- Build size optimization (8.7 MB final size, well under 50 MB CrazyGames limit)
- Technical decisions (TypeScript config, asset loading patterns, audio trimming)
- Verification checklist applied to the actual build
- Lessons learned and best practices from implementation

The case study demonstrates end-to-end application of this skill from asset acquisition through to a polished, compliant game build ready for distribution.
