---
name: modelhub-dashboard
description: ModelHub AI Model Benchmark Dashboard - operations, data refresh, and management
category: hermes
---

# ModelHub Dashboard (ModelBench)

AI Model Benchmark Dashboard at `/root/modelhub/` — comprehensive model comparison with real benchmarks, pricing, speed, and capability scores. **Completely free — no auth, no upsells, no pro tiers.**

Domains: **https://modelbench.lol** (primary), **https://model.kyssta.lol** (secondary)

## Design Principles (this user)

- **No upsells or paywalls** — everything free, no signup, no pro tiers
- **No fake social proof** — no GitHub star counts, no fabricated metrics
- **Do what's asked, don't argue** — user says data is in a rendered web page, use `--dump-dom`. Don't say "I checked the API and it's not there" — when they insist on a method, just do it.
- **Terse delivery, no explanations** — fix the bug, push, give the summary. No design notes, no justifications, no back-and-forth about what might be wrong.
- **Minimal nav** — remove dead/unused nav items. Pricing tab removed (page still at `/pricing`)
- **SVG-only icons** — inline `<svg>` elements (`.section-icon` class), never emojis
- **No decorative icons on interactive elements** — rejected SVG copy icon on slugs. Plain text click-to-copy without any icon
- **Slug tight under title** — `h1{margin:0}; .model-slug{margin:2px 0 6px}`
- **Cost calculator hidden when no offerings** — wrap in `{% if offerings %}`
- **Provider stars** — models.dev generic star SVGs for unknown brands were rejected then accepted. Keep them.
- **Dark mode provider logos** — `filter: brightness(0) invert(1)` on all `.provider* img` classes including `.provider-hero img`
- **Clean professional UI** — responsive tables, live search, benchmark bars

## Architecture (Docker Compose + PostgreSQL)

| Service | Image | Role |
|---------|-------|------|
| **db** | postgres:17-alpine | PostgreSQL, internal port 5432 |
| **web** | modelhub-web | Flask 3.1 + Gunicorn on :5050 |
| **updater** | modelhub-updater | Runs `cron/update_loop.sh` every 300s — scrapes OpenRouter + Models.dev + HuggingFace |

As of Jul 14, 2026: **910+ models, 3 healthy sources** (OpenRouter, Models.dev, HuggingFace), 60+ providers, ~1.7k benchmark results.

## Quick Commands

```bash
cd /root/modelhub
docker compose up -d --build                                # rebuild + restart
docker compose build --no-cache web && docker compose up -d web  # fast code-only rebuild
docker compose exec web python scraper.py                    # force data refresh
docker compose exec db psql -U modelbench -d modelbench       # direct DB queries
docker compose logs updater                                   # check scraper status
```

## Auto-Deploy (Cron)

`/etc/cron.d/modelhub-autodeploy` checks GitHub every 5 min. If new commits found, pulls and rebuilds. Remove by deleting the file.

## Provider Logos: Stars for Unknown Brands

46/60 providers have no real brand icon at models.dev — they return a generic **star/sparkle SVG**. `REAL_LOGOS` whitelist in `app.py` controls which get real icons. All others fall through to models.dev's star fallback (user prefers stars over blank space).

Dark mode: `filter: brightness(0) invert(1)` on all `.provider* img` selectors including `.provider-hero img`.

## UX Preferences

- **No emojis** in UI — inline SVG `<svg class="section-icon">` instead
- **Slug tight under title** — `h1{margin:0}`, `.model-slug{margin:2px 0 6px}`
- **Copy slug on click** — plain `<code>` with `onclick`, NO copy icon
- **Cost calculator hidden** when no offerings — wrapped in `{% if offerings %}`
- **Benchmark bars show actual score out of 100** — not relative to leader
- **"Not reported" fallback** for speed/latency when data unavailable

## Key Patterns (see references/)

| Pattern | Reference file |
|---------|---------------|
| Speed/TPS scraping via `--dump-dom` | `references/speed-scraping.md` |
| Domain + Nginx + Certbot setup | `references/domain-deployment.md` |
| Benchmark bars + compare | `references/benchmark-bars-compare.md` |
| OpenRouter API null handling | `references/openrouter-api-scraping.md` |
| HuggingFace ingestion filter rules | `references/huggingface-ingestion.md` |
    # Ensure current model always visible
    if slug not in seen:
        current = session.query(BenchmarkResult, Model.name).join(...).filter(
            BenchmarkResult.model_slug == slug,
            BenchmarkResult.benchmark_name == bname).first()
        if current:
            br, mname = current
            entries.append({"name": mname or slug, "slug": slug,
                "score": br.score, "is_current": True})
            entries.sort(key=lambda e: e["score"], reverse=True)
    if entries:
        benchmark_leaderboards[bname] = entries
```

### Template pattern (`templates/model.html`)

```html
<div class="benchmark-chart">
  <div class="benchmark-chart-header">
    <strong>Intelligence Index</strong>
    <small>vs top 8 models</small>
  </div>
  <div class="benchmark-bars">
    {% for e in entries %}
    <div class="benchmark-bar-row {{'current' if e.is_current}}">
      <span class="benchmark-bar-label">{{e.name|truncate(42)}}</span>
      <div class="benchmark-bar-track">
        <div class="benchmark-bar-fill" style="width:{{'%d'|format(e.score if e.score <= 100 else 100)}}%"></div>
      </div>
      <span class="benchmark-bar-score">{{'%.1f'|format(e.score)}}</span>
    </div>
    {% endfor %}
  </div>
</div>
```

### CSS for bars (`static/css/style.css`)

```css
.benchmark-chart-header{display:flex;align-items:baseline;gap:12px;margin-bottom:12px}
.benchmark-bars{display:flex;flex-direction:column;gap:6px}
.benchmark-bar-row{display:grid;grid-template-columns:170px 1fr 52px;align-items:center;gap:12px;padding:4px 0}
.benchmark-bar-row.current{background:color-mix(in srgb,var(--brand) 6%,transparent);margin:0 -12px;padding:4px 12px;border-radius:6px}
.benchmark-bar-label{font-size:12px;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.benchmark-bar-row.current .benchmark-bar-label{color:var(--brand)}
.benchmark-bar-track{height:16px;background:var(--raised);border-radius:8px;overflow:hidden}
.benchmark-bar-fill{height:100%;background:var(--brand);border-radius:8px;min-width:4px;transition:width .4s ease}
.benchmark-bar-row.current .benchmark-bar-fill{background:linear-gradient(90deg,var(--brand),var(--brand2))}
.benchmark-bar-score{font-size:12px;font-weight:700;text-align:right;color:var(--muted)}
.benchmark-bar-row.current .benchmark-bar-score{color:var(--brand)}
```

## Leaderboard Page (Default: Intelligence)

The `/leaderboards/<category>` route now supports **benchmark-based sorting** via `BenchmarkResult` table, not just Model columns:

```python
@app.get("/leaderboards/<category>")
def leaderboard(category):
    bench_names = {"intelligence", "coding", "agentic"}
    if category in bench_names:
        label = f"{category.title()} Index"
        results = session.query(BenchmarkResult, Model).join(
            Model, Model.slug == BenchmarkResult.model_slug
        ).filter(BenchmarkResult.benchmark_name == label
        ).order_by(desc(BenchmarkResult.score)).limit(100).all()
        models = [(br.score, m) for br, m in results]
    else:
        # cost/context/recent — query Model columns directly
        ...
```

Template has tabs: Intelligence (default), Coding, Agentic, Recent, Lowest cost, Largest context. Score column appears only for benchmark categories.

## Search Autocomplete + Smart Redirect

Two search mechanisms work together on the homepage:

1. **Autocomplete dropdown** — as-you-type suggestions from `/api/search`
2. **Smart form redirect** (`/go` endpoint) — when user presses Enter, redirects to exact model page if one matches, otherwise to filtered /models list

### Smart redirect endpoint (`app.py`)

```python
@app.route("/go", methods=["GET", "POST"])
def go_search():
    q = (request.args.get("q") or request.form.get("q") or "").strip()
    if not q:
        return redirect("/models")
    session = get_session()
    try:
        like = f"%{q}%"
        # Exact slug match
        model = session.query(Model.slug).filter(Model.slug.ilike(q)).first()
        if model:
            return redirect(f"/{model.slug}")
        # Exact name match
        model = session.query(Model.slug).filter(Model.name.ilike(q)).first()
        if model:
            return redirect(f"/{model.slug}")
        # Fuzzy slug/name — partial queries like "gpt-5.6" → "openai/gpt-5.6-sol"
        model = session.query(Model.slug).filter(Model.slug.ilike(like)).first()
        if model:
            return redirect(f"/{model.slug}")
        model = session.query(Model.slug).filter(Model.name.ilike(like)).first()
        if model:
            return redirect(f"/{model.slug}")
        return redirect(f"/models?q={quote(q)}")
    finally:
        session.close()
```

The homepage form submits to `/go` (GET method) so pressing Enter triggers this smart routing. The JS autocomplete dropdown links to `/{slug}` (clean URLs).

### API endpoint (`app.py`)

```python
@app.get("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    if not q or len(q) < 1:
        return jsonify({"results": []})
    session = get_session()
    try:
        like = f"%{q}%"
        results = session.query(Model.slug, Model.name, Model.developer).filter(
            or_(Model.slug.ilike(like), Model.name.ilike(like), Model.developer.ilike(like))
        ).order_by(Model.release_date.desc().nullslast()).limit(10).all()
        return jsonify({"results": [
            {"slug": r[0], "name": r[1], "developer": r[2]} for r in results
        ]})
    finally:
        session.close()
```

### JavaScript (`static/js/app.js`)

Creates a dropdown `<div class="search-dropdown">` appended to the form on page load. On input (200ms debounce), fetches `/api/search?q=...` and renders results as clickable links:

```javascript
function setupSearchAutocomplete(form) {
  let input = form.querySelector('input[name="q"]');
  let dropdown = document.createElement('div');
  dropdown.className = 'search-dropdown'; dropdown.style.display = 'none';
  form.appendChild(dropdown);
  let timer;
  input.addEventListener('input', () => {
    clearTimeout(timer);
    let q = input.value.trim();
    if (q.length < 2) { dropdown.style.display = 'none'; return; }
    timer = setTimeout(async () => {
      let r = await fetch('/api/search?q=' + encodeURIComponent(q));
      let d = await r.json();
      dropdown.innerHTML = d.results.map(r =>
        '<a class="search-result" href="/' + encodeURIComponent(r.slug) + '">' +
        '<span class="search-name">' + escapeHtml(r.name) + '</span>' +
        '<span class="search-dev">' + escapeHtml(r.developer) + '</span>' +
        '<span class="search-slug">' + escapeHtml(r.slug) + '</span></a>'
      ).join('');
      dropdown.style.display = 'block';
    }, 200);
  });
  input.addEventListener('blur', () => setTimeout(() => dropdown.style.display = 'none', 200));
}
setupSearchAutocomplete($('.hero-search'));
setupSearchAutocomplete($('.filters'));  // models page filter form
```

### CSS for dropdown (`static/css/style.css`)

```css
.search-dropdown {
  position: absolute; top: 100%; left: 0; right: 0;
  background: var(--surface); border: 1px solid var(--line); border-top: 0;
  box-shadow: var(--shadow); z-index: 50; max-height: 360px; overflow-y: auto;
  border-radius: 0 0 10px 10px;
}
.search-dropdown .search-result {
  display: grid; grid-template-columns: 1fr auto; gap: 4px 12px;
  padding: 10px 14px; border-top: 1px solid var(--line); align-items: center;
}
.search-dropdown .search-name { font-weight: 600; grid-column: 1; }
.search-dropdown .search-dev { font-size: 11px; color: var(--muted); grid-column: 1; }
.search-dropdown .search-slug { font-size: 11px; color: var(--brand); grid-row: 1/3; grid-column: 2; text-align: right; }
.hero-search { border-radius: 10px; }
.hero-search:focus-within { border-bottom-left-radius: 0; border-bottom-right-radius: 0; }
```

Note: the form hosting the dropdown must have `position: relative` (set by JS for `.filters`, already present for `.hero-search`).

## CSV Export

```python
@app.get("/api/v1/export.csv")
def api_export_csv():
    session = get_session()
    models = session.query(Model).order_by(Model.slug).all()
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["slug", "name", "developer", "context_length", "max_output_tokens", "modality",
        "input_price_per_million", "output_price_per_million",
        "intelligence_score", "coding_score", "agentic_score", "release_date", "source"])
    for m in models:
        w.writerow([m.slug, m.name, ...])
    return Response(out.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=modelbench.csv"})
```

## Compare Page Model Picker (Searchable)

Replaced the 910-option `<select>` with a search-as-you-type input that hits `/api/search?q=...`. The select was sending 910 `<option>` elements on every page load (heavy markup); the search input sends zero until the user types.

### Template (`templates/compare.html`)

```html
<div class="compare-search">
  <input type="search" data-model-search placeholder="Search models…" autocomplete="off">
  <div class="search-dropdown" data-model-results style="display:none"></div>
</div>
<button class="button primary" data-add-model disabled>Add model</button>
```

The search input is positioned relative to the dropdown (`position:relative` on `.compare-search`). Results show logo + name + developer from the API response.

### API (`/api/search`)

Returns `logo` field alongside `slug`, `name`, `developer`:

```python
@app.get("/api/search")
def api_search():
    ...
    return jsonify({"results": [{"slug": r[0], "name": r[1], "developer": r[2],
        "logo": logo_url(r[2])} for r in results]})
```

### JS Behavior

Debounced search on input (150ms). Click outside closes dropdown. Add model button appends slug to URL path and navigates.

### CSS

```css
.compare-search{position:relative;flex:1;min-width:200px}
.compare-search .search-dropdown{position:absolute;top:100%;left:0;right:0;...}
.compare-search .search-result{display:flex;align-items:center;gap:8px;padding:9px 12px;cursor:pointer}
.compare-search .search-result img{width:18px;height:18px;flex:0 0 18px}
```

## Trailing Slash 404 Fix

Flask is strict about trailing slashes. `/compare` and `/compare/` are different routes. When JS removes all models, it navigates to `/compare/` which hits no route. Fix: stack both decorators:

```python
@app.get("/compare")
@app.get("/compare/")
@app.get("/compare/<path:rest>")
def compare(rest=""):
    ...
```

## Route Registration Order

The catch-all `@app.get("/<path:slug>")` must be registered **last**. Flask registers routes in definition order — model detail route should be the last `@app.get(...)` in the file, otherwise it shadows `/compare`, `/go`, `/models`, etc.

## Compare Page Benchmark Integration

The `/compare` route (`app.py`) fetches all `BenchmarkResult` rows for compared models and groups them by benchmark name:

```python
results = session.query(BenchmarkResult).filter(
    BenchmarkResult.model_slug.in_(slugs)
).order_by(BenchmarkResult.benchmark_name).all()
grouped = {}
for r in results:
    key = r.benchmark_name
    if key not in grouped:
        grouped[key] = {"name": key, "metric": r.metric, "scores": {}}
    grouped[key]["scores"][r.model_slug] = r.score
benchmark_rows = sorted(grouped.values(), key=lambda x: x["name"])
```

The template iterates `benchmark_rows` and displays each model's score or "—" for missing data. Section headers use inline SVG icons (`.section-icon` class) — never emojis. Example SVG icon for the Benchmarks section:

```html
<svg class="section-icon" viewBox="0 0 24 24" width="16" height="16">
  <path d="M4 19V9m6 10V5m6 14v-7m4 7H2"/>
</svg>
```

CSS for section icons:
```css
.section-icon{display:inline;vertical-align:middle;margin-right:6px;color:var(--muted)}
```

## Sitemap & SEO

Dynamic sitemap at `/sitemap.xml`:
- Static pages (/, /models, /providers, /benchmarks, /compare, /pricing, /changes, /methodology, /api/docs, /privacy) with `changefreq` and `priority`
- All 505 model pages with `lastmod` date
- All 60+ provider pages
- ~3,382 lines, ~105KB

```python
@app.get("/sitemap.xml")
def sitemap_xml():
    session = get_session()
    urls = []
    # Add static pages
    for path, changefreq, priority in pages:
        urls.append(f"""  <url><loc>https://model.kyssta.lol{path}</loc>
    <changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>""")
    # Add model pages — clean URLs like /openai/gpt-5.6-sol (no /models/ prefix)
    for slug, updated in session.query(Model.slug, Model.updated_at).all():
        lastmod = updated.strftime("%Y-%m-%d") if updated else ""
        urls.append(f"""  <url><loc>https://model.kyssta.lol/{slug}</loc>
    <lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq><priority>0.6</priority></url>""")
    # Add provider pages
    for (dev,) in session.query(Model.developer).distinct().all():
        slug = dev.lower().replace(" ", "-")
        urls.append(f"""  <url><loc>https://model.kyssta.lol/providers/{slug}</loc>
    <changefreq>weekly</changefreq><priority>0.5</priority></url>""")
    return Response(xml, mimetype="application/xml")
```

robots.txt at `/robots.txt`:
```
User-agent: *
Sitemap: https://model.kyssta.lol/sitemap.xml
Allow: /
```

Note: Flask view function names must NOT collide — Gunicorn's endpoint registry uses function names as endpoint identifiers. If you see `AssertionError: View function mapping is overwriting an existing endpoint function`, rename the function (e.g. `sitemap_xml` instead of `sitemap`, `robots_txt` instead of `robots`).

## VPS + Domain Setup (Nginx + Certbot)

Already running at **model.kyssta.lol** behind Nginx reverse proxy. See `references/domain-deployment.md` for the full setup recipe with exact Nginx config and Certbot commands.

Steps:
1. Point DNS A record to server IP
2. Create Nginx site config (port 80 only initially — no SSL lines)
3. Enable site: `ln -sf /etc/nginx/sites-available/domain /etc/nginx/sites-enabled/; systemctl reload nginx`
4. Run `certbot --nginx -d domain --agree-tos --email you@domain.com` — auto-provisions SSL + rewrites config
5. Verify the final Nginx config has both 443 SSL and 80→301 redirect server blocks
6. SSL auto-renewal timer is automatically set by Certbot

## Provider Logo Handling (Stars for Unknown Brands)

Models.dev returns **generic star/sparkle placeholder SVGs** for unknown providers (46 out of 60). The user initially rejected these but later decided to **keep the stars** — they prefer seeing a star over a blank/transparent space. A `REAL_LOGOS` whitelist in `app.py` controls which providers show actual brand icons; all others fall through to models.dev's default star SVG:

```python
REAL_LOGOS = {
    "alibaba qwen", "anthropic", "cohere", "deepseek", "google", "inception",
    "meta", "minimax", "nvidia", "openai", "openrouter", "perplexity",
    "poolside", "xai", "x-ai", "xiaomi",
    "meta-llama", "qwen", "alibaba",
}
```

The `logo_url()` function checks this set. Providers NOT in `REAL_LOGOS` use models.dev's fallback URL, which returns a star/sparkle SVG:

```python
def logo_url(name):
    key = name.lower()
    slug = PROVIDER_ICONS.get(key)
    if slug and key in REAL_LOGOS:
        return f"https://models.dev/logos/labs/{slug}.svg"
    if key in REAL_LOGOS:
        return f"https://models.dev/logos/{key.replace(' ', '-').replace('(', '').replace(')', '')}.svg"
    # ponytail: models.dev fallback returns star SVGs for unknown brands — user prefers stars
    return f"https://models.dev/logos/{key.replace(' ', '-').replace('(', '').replace(')', '')}.svg"
```

### Dark Mode — Invert Logos to White

Provider logos are typically dark-colored SVGs. In dark mode, they must be inverted to white:

```css
[data-theme=dark] .provider img,\n[data-theme=dark] .provider-grid img,\n[data-theme=dark] .provider-mark img,\n[data-theme=dark] .provider-card>img,\n[data-theme=dark] .provider-hero img {\n  filter: brightness(0) invert(1);\n}\n```

Add new providers to `REAL_LOGOS` whenever a real brand icon becomes available. Check by downloading the SVG and looking for the star pattern (`M9.8132 15.9038L9 18.75`).

## HuggingFace Ingestion

`scraper.py` has an `ingest_huggingface()` function that queries 15 official HF orgs for models not already in the DB. Imported **403 models** on first run; subsequent runs find 0 new ones (slug-deduplicated):

- **Orgs**: meta-llama, google, microsoft, mistralai, CohereForAI, Qwen, deepseek-ai, nvidia, stabilityai, upstage, ai21labs, bigcode, ibm-granite, 01-ai, x-ai
- **Filtering**: only text-generation / image-text-to-text / text-to-image / any-to-any pipelines. Skips quantized (GGUF/AWQ/GPTQ), mobile/ONNX ports, experimental lab projects, low-download models, and fine-tune variants.
- **Strict thresholds**: `downloads < 100 AND likes < 5` filters out experimental stuff. Aggressive exclude patterns (`DSpark|DFlash|AgentWorld|Lab-|forcedaligner`) block non-base-model variants.
- **Existing check**: only adds models whose `slug` isn't in the DB yet. Updates sparse fields (name, developer, context_length, open_source) for existing models when HF has richer data.
- **First run imported 403 new models** (from 15 orgs × 3 pages each). Subsequent runs find 0 since all are already in DB.

Location in code: `ingest_huggingface()` called in `run_full_update()` after OpenRouter and Models.dev scrapes. New `DataSource` record "HuggingFace" is created on first run. Uses same `IngestionRun` pattern for error tracking.

## Table Column Widths

The `.model-table` uses `table-layout:fixed`. Without explicit widths, the Creator column stretches to fill remaining space, pushing the compact Modalities column right and creating visual gap:

```css
.model-table th:nth-child(2){width:16%}  /* Creator column */
```

Bump CSS version in `base.html` (`style.css?v=N`) when modifying style.css — browsers cache aggressively. Nginx doesn't add `Cache-Control: no-cache` to static files served via `sendfile` so the query param is the only cache-bust.

## Modality Icon Sizing

Modality icons in the table (`/models`, `/compare`) are 24×24px boxes with 14×14px SVGs inside. The text "T" icon uses 13px font. These were reduced from 25×25 / 15×15 / 14px on user request (~5% shrinkage). The `.modality-icons` flex container has a 5px gap. Colors per modality:

- Text: blue (`#38bdf8`)
- Image: green (`#4ade80`)
- Audio: purple (`#c084fc`)
- Video: amber (`#fbbf24`)
- File: gray (`#94a3b8`)

All icons get `opacity:.35` when inactive, `opacity:1` with `.active`.

## Benchmark Dedup (Overlapping Fix)

### Model Page (`app.py`)

Same benchmark name can appear from multiple sources (OpenRouter artificial_analysis + Models.dev) or with different harness values (Codex, Mini-SWE-Agent, Cursor CLI). Fix: dedup by `(benchmark_name, metric)` keeping highest score:

```python
seen = {}
for row in result_rows:
    key = (row.benchmark_name, row.metric)
    if key not in seen or row.score > seen[key].score:
        seen[key] = row
result_rows = list(seen.values())
```

### Leaderboard Query

Previously filtered `BenchmarkResult.harness == ""` which skipped all benchmarks with named harnesses. Replaced with `GROUP BY model_slug, name` + `MAX(score)` per model, so each model appears once per benchmark with its best score. Removes the `harness = ''` restriction entirely.

SQL pattern:
```python
top_results = session.query(
    BenchmarkResult.model_slug,
    func.max(BenchmarkResult.score).label('max_score'),
    Model.name,
).join(
    Model, Model.slug == BenchmarkResult.model_slug
).filter(
    BenchmarkResult.benchmark_name == bname,
).group_by(
    BenchmarkResult.model_slug, Model.name
).order_by(
    desc('max_score')
).limit(7).all()
```

## Table Scrollbar Fix

The `.table-shell` wrapper uses `overflow-x:auto` (not `overflow:auto`) and tables have no `min-width` constraint. This prevents vertical scrollbars from appearing and lets tables shrink to fit the viewport width:

```css
.table-shell{background:var(--surface);border:1px solid var(--line);overflow-x:auto;...}
table{width:100%;border-collapse:collapse}
```

The `min-width:800px` was removed from the `table` rule. Tables that genuinely need scrolling on narrow viewports get a horizontal scrollbar only (`overflow-x:auto`).

## Performance / Speed Card

Model pages show a "Performance" sidebar panel with Throughput and Latency. The scraper at `cron/scrape_speed.py` uses `chromium-browser --headless --dump-dom` to get JS-rendered speed data from OpenRouter's web pages (their API doesn't return it). See `references/speed-scraping.md` for the full technique including batch scraping all 505 models and importing results back into PostgreSQL.

## Modality Icons

Model pages and compare page show input/output modality icons (Text, Image, Audio, Video, File) using `_modality_icons.html` template macro. Inline SVGs with `.modality-icon` CSS class. Active/inactive states controlled by `.active` class. Colors per modality: Text=blue, Image=green, Audio=purple, Video=amber, File=gray. Only renders for models with metadata_json modalities from OpenRouter.

## Model Page UX Preferences

- Slug sits tight under title: `h1{margin:0}`, `.model-slug{margin:2px 0 6px}`
- Copy on click: `onclick="navigator.clipboard.writeText(...)"` — NO icon, plain `<code>` element
- Cost calculator wrapped in `{% if offerings %}` — hidden entirely when no offers
- Performance card always shown (handles "Not reported" gracefully)
- Badges: Source-linked status, family tag, open/closed weights, release date
- Provider pricing table uses `offer.provider_id` for logo URLs on the `img` tag (not `provider_icon()` function — those are developer names, not provider IDs)

## API Endpoints (with ?fields)

- `GET /api/models` — List all models (search, filter, sort, paginate). Supports `?fields=slug,name,speed_tps,intelligence_score` to return only specified fields. All available field keys: `slug`, `name`, `developer`, `description`, `context_length`, `max_output_tokens`, `modalities`, `release_date`, `open_weights`, `input_price_per_million`, `output_price_per_million`, `cached_input_price_per_million`, `speed_tps`, `intelligence_score`, `coding_score`, `agentic_score`, `benchmark_data`, `source`, `verification_status`.
- `GET /api/models/<path:slug>` — Single model details
- `GET /api/leaderboard` — Top models by category
- `GET /api/stats` — Aggregate statistics
- `GET /api/providers` — All providers with pricing ranges
- `GET /api/search?q=<query>` — Quick search/autocomplete
- `GET /api/sources` — Data source scrape status
- `POST /api/update` — Trigger manual data refresh

## Pitfalls & Patterns

### Flask Route Slugs with Slashes
Model slugs contain `/` (e.g. `anthropic/claude-fable-5`). Use `<path:slug>` converter in Flask routes. Both template routes and API routes need this.

### Catch-All Route Must Be Registered Last
Clean URLs like `/openai/gpt-5.6-sol` use a catch-all route `@app.get("/<path:slug>")`. This route MUST be defined **after all other routes** (e.g. just before `@app.after_request`). If registered early, it shadows `/compare`, `/go`, `/models`, and every other route.

### Trailing Slash 404 on URL-Built Routes
When the compare page builds URL from JS (`/compare/` after removing all models), the trailing slash hits no route — Flask doesn't match `/compare/` to `/compare` or `/compare/<path:rest>`. Fix: add an explicit `@app.get("/compare/")` decorator on the same handler. Same applies to any route that can be navigated to with a trailing slash via JS URL construction.

Implementation: three decorators on the same function:
```python
@app.get("/compare")
@app.get("/compare/")
@app.get("/compare/<path:rest>")
def compare(rest=""):
    ...
```

Implementation: keep the main route decorator at the top (old path → 301 redirect), copy the function body to a new catch-all route at the bottom of the file. Both old (`/models/<slug>`) and new (`/<slug>`) paths coexist — old redirects 301 to clean URL.

### Jinja2 Filter Syntax
Filters registered via `@app.template_filter('name')` use pipe syntax: `{{ value|filter_name }}`.

### Jinja2 Conditional Pitfall (IF inside expressions)
Don't put Jinja2 `if/else` logic inside `{{` expression markers. This DOES NOT WORK:
```
${{offer.cost.input|price}} if offer.cost.input is defined else '—'}}
```
Jinja2 will render `$<price_value> if offer.cost.input is defined else '—'` as literal text — the `if/else` is not evaluated, it's just printed.

Use `{% %}` statement blocks instead:
```
{% if offer.cost.input is defined %}${{offer.cost.input|price}}{% else %}—{% endif %}
```
This also applies to attribute-only checks like `offer.cost.input is defined`. When the value could be 0, use the Jinja2 `is defined` test (not truthiness like `{% if offer.cost.input %}` which would hide `$0` prices).

### Flask Endpoint Naming Conflicts
Flask uses the **Python function name** as the endpoint identifier. Two route functions cannot share the same name even if they serve different paths. If you get `AssertionError: View function mapping is overwriting an existing endpoint function`, rename one of the functions (e.g. `def robots_txt():` for `/robots.txt`).

### Required Imports for New Routes
When adding endpoints that use `redirect()` with query parameters, `Response()`, or file IO, remember the imports:
- `from urllib.parse import quote` — for URL-encoding query params in `redirect(f"/path?q={quote(q)}")`
- `import csv, io` — for CSV export responses
- `from flask import Response` — for raw XML/text responses (sitemap, robots.txt)

### Bar charts: scores out of 100, not relative to leader

Bar width = raw score capped at 100 (`{{'%d'|format(e.score if e.score <= 100 else 100)}}%`). Do NOT compute `score / max_score * 100` — that makes bars show relative ranking, not actual performance. The user explicitly rejected relative bars.

### speed_tps scraping via chromium

Run on host where chromium-browser is installed:
```bash
cd /root/modelhub && python3 cron/scrape_speed.py
```
See `references/speed-scraping.md` for full technique. The script uses `--dump-dom` to get JS-rendered speed data since OpenRouter's API returns null for all throughput fields. 3 models parallel via ThreadPoolExecutor, ~22 min for all 505.

### Imports checklist for new routes

- `from urllib.parse import quote` → URL-encoding query params in redirects
- `import csv, io` → CSV export responses  
- `from werkzeug.middleware.proxy_fix import ProxyFix` → HTTPS behind Nginx
- `from flask import Response` → raw XML/text responses (sitemap, robots.txt)

-
When editing Python/template files after a `docker compose up -d --build`, the `COPY . .` layer may be **cached** and not pick up the changes. Symptoms: new routes return 502, template changes don't appear. Fix:
```bash
docker compose build --no-cache && docker compose up -d
```
Or rebuild just the affected service:
```bash
docker compose build --no-cache web && docker compose up -d web
```

### SQLAlchemy Query Column Order Must Match For-Loop Unpacking

When building benchmark leaderboards via `session.query(a, b, c).group_by(...)`:

```python
top_results = session.query(
    BenchmarkResult.model_slug,        # position 0
    func.max(BenchmarkResult.score).label('max_score'),  # position 1
    Model.name,                        # position 2
).join(…).filter(…).group_by(…).order_by(desc('max_score')).limit(7).all()

for model_slug, max_score, mname in top_results:
    #        ^position 0  ^position 1  ^position 2
```

The **for-loop variable order must exactly match the `.query()` column order** — SQLAlchemy returns tuples in the order you specify, not by label name. Swapping `mname` and `max_score` silently puts a float in the name slot and a string in the score slot, crashing the template with `TypeError: object of type 'float' has no len()` when `|truncate(42)` is applied. The same swap causes `'<' not supported between instances of 'str' and 'float'` on the sort line.

Fix: match variable names to positions. Remove the `slug_or_ms = ...` guard from the old broken unpacking — it was compensating for the wrong column ending up in the wrong variable, not for actual type uncertainty.

### Old Cron Job Still Active?
The old `c7bf189ac4a7` cron job (daily SQLite-based update via cron/update_data.sh) is **obsolete** — the Docker updater service handles continuous data refresh every 5 minutes. Remove via `cronjob(action='remove', job_id='c7bf189ac4a7')`.

## Auto-Deploy from GitHub

A system cron job checks for upstream changes every 5 minutes and auto-deploys:

```bash
# /etc/cron.d/modelhub-autodeploy
*/5 * * * * root /root/modelhub/cron/auto_deploy.sh
```

The script (`cron/auto_deploy.sh`):
```bash
cd /root/modelhub
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
### Cost Calculator: Read Prices Fresh from Select on Every Calculation

Don't cache provider prices in `.dataset.*` and read them later — `modelCost()` reads prices from `$('[data-offer-select] option:checked')?.dataset.*` fresh each call, falling back to `box.dataset.*` only if no select exists. Wire `input` event (not `change`). One function, no `offerCost()`.

### OUT/IN Price Column (Tables)

Home page and model directory merge Input/Output prices into one "OUT/IN" column to save space: `$2.500/$15.000`. Decrement `colspan` by 1 on empty-state rows when merging.

### OpenRouter API Null Handling pick up `app.py`/`scraper.py`/template/JS/CSS changes without `--no-cache`\n- After starting, verify with `curl http://localhost:5050/health`
- The `updater` container auto-runs every 5 minutes — no manual cron needed
- To rebuild after a `git pull`: `docker compose up -d --build` (use `--no-cache` if python files changed)

### Health Check
```bash
curl https://model.kyssta.lol/health
# Returns: {"service":"ModelBench","status":"ok"}
```
