---
name: open-source-extraction
description: Extract specific packages from large open-source monorepos and adapt them for standalone use. Covers dependency mapping, stripping cloud/infra deps, creating shim packages, and iterative build fixing.
---

# Open Source Code Extraction

Extract packages from large open-source monorepos and adapt them to standalone use.

## When to Use

- User wants to reuse specific UI/dashboard/app code from a large project
- Extracting from an enterprise monorepo (20+ packages, deep dependency chains)
- Need to strip cloud/infrastructure dependencies (SST, Cloudflare, AWS)
- Porting server-side frameworks (Next.js, SolidStart) to client-side SPAs

## Technique

### 1. Clone Repository

```bash
# Shallow clone saves time/space
git clone --depth 1 --single-branch --branch <branch> <repo-url> <target-dir>
```

### 2. Map Dependency Tree

- Read root `package.json` for workspace definitions and catalog
- Identify packages the target depends on (internal `workspace:*` deps)
- Check each package's `package.json` for internal deps
- Build full dependency chain: `target → internal-pkg1 → internal-pkg2 → ...`

### 3. Create Workspace Structure

Create a clean monorepo for the extracted code:

```
nectar-v2/
├── package.json          # Root workspace config
├── bunfig.toml           # (if using Bun) [workspace] catalog = true
├── packages/
│   ├── target-package/   # The main thing user wants
│   ├── dep-pkg-a/        # Internal dependency packages
│   └── shim-pkg/         # Stub packages for missing deps
└── HANDOFF.md            # Documentation of what's adapted
```

**Root package.json workspace pattern:**

```json
{
  "workspaces": {
    "packages": [
      "packages/shim-packages",
      "packages/ui",
      "packages/console/*"
    ]
  }
}
```

### 4. Strip Cloud/Infrastructure Dependencies

Common infra deps to replace:

| Original | Replacement |
|----------|-------------|
| `sst` (SST/Ion) | Simple env-based Resource proxy |
| `@cloudflare/*` | Remove or stub |
| `@aws-sdk/*` | Remove or stub |
| `@planetscale/database` | Replace with standard postgres |
| `stripe` | Keep but make optional |
| `nitro` (SSR engine) | Remove (use SPA mode) |

**Pattern for Resource adapter (SST replacement):**

```typescript
// Resource adapter - reads from env vars
export const Resource = new Proxy({}, {
  get(_target, prop) {
    return new Proxy({}, {
      get(_inner, subProp) {
        const key = `${prop}_${subProp}`.toUpperCase()
        if (prop === "App" && subProp === "stage") return "development"
        return process.env[key] || null
      },
    })
  },
}) as Record<string, any>
```

### 5. Handle Server-Side Frameworks

When extracting from SolidStart/Next.js/etc., convert to client-side SPA:

**SolidStart → Vite + SolidJS SPA:**

1. Replace `FileRoutes` with manual `Route` definitions
2. Create `@solidjs/start` shim with stub exports
3. Rewrite `"use server"` functions as API calls
4. Replace `createAsync`/`useAction`/`useSubmission` with direct calls
5. Create `index.html` entry point
6. Configure Vite with aliases for the shim — **each subpath must be aliased separately** because Vite resolves `@solidjs/start`, `@solidjs/start/server`, and `@solidjs/start/client` independently:

```typescript
// vite.config.ts
import { defineConfig } from "vite"
import solidPlugin from "vite-plugin-solid"
import path from "path"

const shim = path.resolve(__dirname, "../../solidjs-start-shim/src")

export default defineConfig({
  plugins: [solidPlugin()],
  resolve: {
    alias: {
      "@solidjs/start": shim,
      "@solidjs/start/server": path.join(shim, "server.ts"),
      "@solidjs/start/client": path.join(shim, "client.ts"),
      "@solidjs/start/router": path.join(shim, "router.ts"),
      "@solidjs/start/http": path.join(shim, "http.ts"),
    },
  },
})
```

**⚠️ VITE SUBPATH ALIAS TRAP** — Each subpath (`@solidjs/start/server`, `@solidjs/start/client`, `@solidjs/start/router`, `@solidjs/start/http`) MUST be aliased individually in `vite.config.ts`. Vite does NOT resolve `@framework/x` through the base `@framework` alias — it searches npm for the literal string `@solidjs/start/server`. Missing even one subpath causes an opaque `Rollup failed to resolve import` error with zero indication of how to fix it. The shim package must export each subpath from its own file in `package.json`'s `exports` field.

This same pattern applies to any server-side framework that has subpath imports — Vite won't resolve them through the base package alias alone.

**SolidStart shim package:**

```json
{
  "name": "@solidjs/start",
  "version": "0.0.0-shim",
  "private": true,
  "exports": {
    ".": "./src/index.ts",
    "./server": "./src/server.ts",
    "./client": "./src/client.ts",
    "./router": "./src/router.ts",
    "./http": "./src/http.ts"
  }
}
```

### 6. Resolve Catalog Dependencies

Many monorepos use Bun/Yarn catalogs for shared versions. Replace `catalog:` references with explicit versions:

```python
# Python script to convert catalog: to explicit versions
catalog = {
    "@kobalte/core": "0.13.11",
    "solid-js": "1.9.10",
    # ... (read from original root package.json catalog)
}
# Iterate packages, replace "catalog:" -> explicit version
```

### 7. Iterative Build Fixing

Common Vite build errors and fixes:

| Error | Fix |
|-------|-----|
| `"X is not exported by __vite-browser-external"` | Remove `node:*` imports from browser code or make browser-safe |
| `failed to resolve "extends"` | Install missing `@tsconfig/*` packages |
| `failed to resolve "package-name"` | Add missing npm dep or create shim |
| `"use server" directive` | Remove directive, convert to regular async function |
| `Module externalized for browser` | Rewrite to not use Node.js APIs |
| `"AsyncLocalStorage" is not exported by "__vite-browser-external"` | Replace `import { AsyncLocalStorage } from "node:async_hooks"` with a simple closure-based store (no Node imports): `function create<T>() { let store: T; return { use() { if (!store) throw Error(); return store }, provide(v, fn) { const prev = store; store = v; try { return fn() } finally { store = prev } } } }` |

### 8. Document Everything

Create a `HANDOFF.md` with:

- What was extracted and what builds
- What was adapted/changed from original
- API endpoints the SPA needs
- What the user needs to implement
- Step-by-step "what to do next" for the user

## Complete Rebranding (Post-Extraction)

After extraction, the user will want **full ownership** — no traces of the original project name/brand anywhere.

### Phase 1: Name Research

Before touching code, verify the name is actually available — **domain checks alone are not enough**. You need a two-pass conflict check:

**Pass 1 — Domain availability:**
```bash
for domain in proposedname.com proposedname.dev proposedname.org proposedname.so; do
  if host "$domain" 2>/dev/null | grep -q "not found\\|NXDOMAIN"; then echo "✅ $domain"; fi
done
```

**Pass 2 — Product category conflicts:**
Search for the name being used in the same product space (AI coding tools, developer platforms, API providers):
```
web_search(query="\"ProposedName\" AI coding OR developer platform OR API provider")
web_search(query="ProposedName site:github.com")
```

⛔ **Naming reality for agentic coding tools (2026):** Names with "Code" suffix are nearly ALL registered as either a product, GitHub project, or parked domain. Verified taken: OpenCode, ForgeCode, NovaCode, CoreCode, ShiftCode, DriftCode, BladeCode, PrimeCode, RidgeCode, ArcCode, FluxCode, ApexCode, EdgeCode. Short single-word names (Spire, Corvus, Adept, Verve, Beam, Motif) face heavy competition too — most are already claimed by adjacent developer tools, AI platforms, or programming languages.

✅ **Names that tested available** (sample, verify at time of use):
- motif.com — not a coding tool (UNIX toolkit from 90s + construction startup)
- comb.com — not in developer tools
- vigor.so — not in AI coding
- zealous (uncommon) — less competition

**User style preferences** — When naming, some users want real English words (like Stripe, Vercel), not obscure/invented names. If they reject suggestions, probe: real word vs made-up, short vs longer, what vibe. 

**Cheap domain reality** — Most `.com` short English words are premium/owned (check via RDAP, not just DNS). After-sale domains ($500+) are a non-starter for most users. Options:
- `.so` TLD (~$10/yr) has many short real words still available (vigor.so, knoll.so, brook.so, comb.so, quay.so, etc.)
- `.dev` TLD (Google-managed) has some availability
- Always check actual registration status via `curl -s "https://rdap.nic.so/domain/$domain"` (for .so) or the relevant registry RDAP, NOT via DNS lookup (parked domains resolve)

**Product category conflict search** — Required before suggesting a name, not optional:
```

### Phase 2: Mass Text Replacement

**Two-pass approach** — mandatory to avoid breaking package imports:

```bash
# PASS 1: Replace project name everywhere (WILL over-replace package names)
grep -rl "OldName\\|oldname" --include="*.tsx" --include="*.ts" --include="*.css" \
  --exclude-dir=node_modules . | while read f; do
  sed -i 's/OldName/NewName/g; s/oldname/newname/g' "$f"
done

# PASS 2: Revert package-scoped names (@old-org/pkg must stay @old-org/pkg)
grep -rl "@NewName-org" --include="*.tsx" --include="*.ts" --include="*.css" . | \
  while read f; do
  sed -i 's/@NewName-org/@OldName-org/g' "$f"
done
```

**⚠️ THE PACKAGE NAME TRAP** — npm-style package names (`@opencode-ai/*`, `@org/*`) are workspace resolution keys. Changing them breaks `bun install` and every import. The two-pass approach is non-negotiable.

### Phase 3: i18n Batch Rebranding

Projects often have 15+ locale files. Process all at once:

```bash
for f in packages/*/src/i18n/*.ts packages/*/src/i18n/*.tsx; do
  [ -f "$f" ] && sed -i 's/OldName/NewName/g; s/oldname/newname/g' "$f"
done
```

### Phase 4: Asset File Renaming

Brand asset files (logos, images, videos, posters) have the original project name in their filenames. Rename on disk — binary files `sed` can't touch:

```bash
# Top-level asset directory
cd packages/console/app/src/asset
for f in oldname-* oldname.*; do
  [ -f "$f" ] && mv "$f" "$(echo "$f" | sed 's/^oldname-/newname-/')"
done

# Nested directories (brand/, lander/, etc.)
cd lander && for f in oldname-*; do
  [ -f "$f" ] && mv "$f" "$(echo "$f" | sed 's/^oldname-/newname-/')"
done

cd ../brand && for f in oldname-* preview-oldname-*; do
  [ -f "$f" ] && mv "$f" "$(echo "$f" | sed 's/^oldname-/newname-/; s/^preview-oldname-/preview-newname-/')"
done
```

### Phase 5: SVG Logo Creation (Fallback When Image Gen Unavailable)

Create all brand SVGs from scratch using a **hexagonal tech-logo pattern**:

```svg
<!-- Core logo mark -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="none">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#BRAND-PRIMARY"/>
      <stop offset="100%" stop-color="#BRAND-SECONDARY"/>
    </linearGradient>
  </defs>
  <!-- Hexagon background -->
  <polygon points="128,16 232,72 232,184 128,240 24,184 24,72" fill="url(#g)"/>
  <!-- Inner cutout -->
  <polygon points="128,46 208,88 208,168 128,210 48,168 48,88" fill="#BG-COLOR"/>
  <!-- Brand drop/diamond -->
  <path d="M128 70 C... " fill="url(#g)"/>
  <ellipse cx="120" cy="120" rx="8" ry="12" fill="white" opacity="0.3"/>
</svg>
```

Generate all variants in one batch:

```python
svgs = {
    f"{asset_dir}/logo.svg": "<svg>icon only</svg>",
    f"{asset_dir}/zen-ornate-dark.svg": "<svg>logo + wordmark dark</svg>",
    f"{asset_dir}/zen-ornate-light.svg": "<svg>logo + wordmark light</svg>",
    f"{asset_dir}/go-ornate-dark.svg": "<svg>logo + 'Go' dark</svg>",
    f"{asset_dir}/go-ornate-light.svg": "<svg>logo + 'Go' light</svg>",
    f"{asset_dir}/lander/logo-dark.svg": "<svg>lander logo dark</svg>",
    f"{asset_dir}/lander/logo-light.svg": "<svg>lander logo light</svg>",
    f"{asset_dir}/lander/wordmark-dark.svg": "<svg>text wordmark dark</svg>",
    f"{asset_dir}/lander/wordmark-light.svg": "<svg>text wordmark light</svg>",
    # brand/ variants, favicon, etc.
}
for path, content in svgs.items():
    write_file(path=path, content=content)
print(f"Created {len(svgs)} SVG logos")
```

Use `<text font-family=\"system-ui\">` for wordmarks — no font loading needed.

### Phase 6: Favicon

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" fill="none">
  <defs><linearGradient id="f" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#PRIMARY"/><stop offset="100%" stop-color="#SECONDARY"/>
  </linearGradient></defs>
  <rect width="96" height="96" rx="20" fill="url(#f)"/>
  <path d="M30 48... " fill="#BG"/>
  <ellipse cx="42" cy="42" rx="6" ry="9" fill="white" opacity="0.3"/>
</svg>
```

Update the favicon component & `site.webmanifest` with the new name.

### Phase 7: Theme File

```json
{
  "name": "BrandName",
  "dark": true,
  "theme": {
    "primary": "#PRIMARY",
    "secondary": "#SECONDARY",
    "accent": "#ACCENT",
    "background": "#BG-DARK",
    "backgroundPanel": "#PANEL",
    "text": "#FOREGROUND",
    "textMuted": "#MUTED",
    ...
  }
}
```

Place in the theme directory and verify the theme registry imports it.

### Phase 8: Metadata Files

| File | What to change |
|------|---------------|
| `packages/<app>/public/theme.json` | `name`, `short_name`, `theme_color` |
| `packages/<app>/index.html` | `<title>`, meta tags |
| `packages/<app>/src/component/favicon.tsx` | Icon refs, `apple-mobile-web-app-title` |
| `packages/ui/src/assets/favicon/site.webmanifest` | `name`, `short_name` |
| Social share images | Rename on disk (`social-share.png`, etc.) |

### Phase 9: Verification

```bash
# Check for remaining old-name traces in source
grep -r "OldName\|oldname" packages/ --include="*.tsx" --include="*.ts" --include="*.css" \
  --exclude-dir=node_modules | grep -v "@OldName-org"

# Check for old-name asset files still on disk
find packages/ -name "*oldname*" -type f | head -10

# Check the built dist for leaked old names
grep -r "OldName" packages/<target>/dist/ --include="*.html" --include="*.js" 2>/dev/null | head -5

# Verify the build still works
cd <workspace> && bun install && bun run --cwd packages/<target> build
```

### Complete Rebranding Checklist

```
☐ Research name availability (domains + product category search)
☐ Mass text replacement (two-pass sed: global then revert package scopes)
☐ i18n batch rebranding (all locale files)
☐ Rename asset files on disk (SVG, PNG, MP4, ZIP in brand/ and lander/)
☐ Create new SVG logos (icon + wordmark + favicon + all variants)
☐ Create brand theme JSON for UI system
☐ Update favicon component and site.webmanifest
☐ Update index.html title and meta tags
☐ Update public/theme.json
☐ Remove/replace old brand assets zip
☐ Rebuild and verify no old name leaks into dist
```

## Pitfalls (Rebranding-Specific)

- **`sed` over-replacement** — The #1 mistake. Package names like `@old-org/pkg` will be broken. Always use two-pass: replace global, then revert package-scoped.
- **Binary files can't be `sed`'d** — PNGs, MP4s, ZIPs keep old filenames. Use `mv` to rename on disk.
- **Missing theme JSONs** — `default-themes.ts` may import `./themes/brandname.json` but the file may not exist in your extracted copy. Always create it.
- **Import vs filename mismatch** — After `sed` renames `import x from "old-video.mp4"` to `import x from "new-video.mp4"`, the actual file still has the old name. Either rename the file or fix the import.
- **Package.json `name` field** — The `name` is the workspace resolution key. Changing it requires updating ALL `workspace:*` references. Leave as `@old-org/*` until the user explicitly asks to rename packages.
- **Social preview images** — Easy to miss. Check for `social-share*.png` files in asset directories and the `public/` folder.\n- **Dist/ contains leaked old names** — After any text replacement, check `grep -r "OldName" dist/ --include="*.html" --include="*.js"` to catch hardcoded strings the bundler inlined.

## Pitfalls

- **Don't copy everything at first** — Start with the minimum packages and add more as needed
- **Check if packages actually resolve on npm** — Some catalog entries (`@typescript/native-preview`, custom registry packages) may not exist publicly
- **Shallow clone** saves disk space but you lose git history — fine for extraction
- **Server routes in SPA** — exfiltrate to your own backend; don't try to keep them in the SPA bundle
- **`@solidjs/start` custom URLs** — the pinned pr.new URLs may be gone; always shim
- **Auth/session code** — the heaviest dependency on server-side framework; always needs rewriting
- **`sed` over-replacement** — always protect npm package names with a two-pass approach
- **Missing theme files** — if a theme JSON is imported but doesn't exist on disk, create it
- **Binary files can't be sed'd** — rename them on disk separately
- **Vite ignores lazy imports** — removing a route from the router stops Vite from resolving its imports
- **Don't suggest premium/after-sale domains** — most .com short English words are parked/premium ($500+). Check actual availability via RDAP (`curl -s "https://rdap.verisign.com/com/v1/domain/$domain"`) not DNS. If the user gets frustrated with bad suggestions, they'll tell you — listen for "cheap" / "premium" / "after-sale". Fall back to .so, .dev, or less common TLDs.
- **Bun workspace + catalog resolution edge case** — When a catalog entry points to a URL (`"https://pkg.pr.new/@solidjs/start@dfb2020"`), bun will try to fetch it. If the URL is dead, the install fails. Always replace such entries with a workspace shim or explicit npm version.

## Reference Files

- `references/browser-safe-context.md` — How to replace `AsyncLocalStorage` with a browser-safe closure when extracting server code to a SPA.
- `references/opencode-architecture.md` — Deep architecture of the OpenCode codebase: package layout, free model pipeline, provider integration system, CLI build pipeline, key overrides, and what to change for a fork. Essential when forking or rebranding OpenCode as a standalone coding agent CLI.

## Verification

```bash
# After all fixes:
cd <workspace-root>
bun install          # Should succeed
bun run --cwd packages/<target> build  # Should succeed
ls packages/<target>/dist/  # Should have index.html + JS chunks

# Verify no remains of original brand:
grep -r "OriginalName" packages/<target>/src/ --include="*.tsx" --include="*.ts" | grep -v node_modules | grep -v "@Original-org"
grep -r "original-name" packages/<target>/dist/ --include="*.html" --include="*.js" 2>/dev/null | head -5
```
