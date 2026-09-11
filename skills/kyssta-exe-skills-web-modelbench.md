---
name: modelbench
description: Maintain ModelBench (modelbench.lol) — Flask/Docker/PostgreSQL AI model directory. Ingestion pipeline, CSS patching, compare page search, deployment.
---

# ModelBench maintenance

Codebase: `/root/modelhub/`, live at modelbench.lol.  
Docker stack: `web` (gunicorn/Flask), `updater` (scraper loop), `db` (PostgreSQL 17).  
Auto-deploy: `cron/auto_deploy.sh` checks git every 5min → rebuilds on new commits.

## Ingestion pipeline

`scraper.py` > `run_full_update()` runs every 5 min via `cron/update_loop.sh`:

1. `ingest_openrouter()` — `https://openrouter.ai/api/v1/models`, 343 models
2. `ingest_models_dev()` — `https://models.dev/catalog.json`, 247 models  
3. `ingest_huggingface()` — 15 official HF orgs, filters out quant/lab/variants

Models deduped by slug. If a model exists on both OpenRouter and Models.dev, the Models.dev data wins (runs second). Source field tracks origin.

To add a new ingestion source, follow the pattern in `ingest_huggingface()`: create `IngestionRun` + `DataSource` records, use the same error/rollback pattern.

## CSS patching

`/root/modelhub/static/css/style.css` is **all one minified line**. To edit:

1. `read_file(path='style.css', offset=<line>, limit=1)` to grab the exact string
2. `patch()` with the **exact substring** from the file
3. Bump version in `templates/base.html`: `style.css?v=<current+1>`
4. Commit, push, rebuild

## Compare page search

`/root/modelhub/templates/compare.html` — searchable model picker.

- Input `[data-model-search]` → debounced 150ms → `/api/search?q=...`  
- Results rendered as `[data-slug]` divs in `[data-model-results]` container  
- Click handler uses **event delegation** (`r.addEventListener('click', pick)`) not inline onclick — the function lives inside the IIFE closure and inline handlers can't reach it.
- `[data-add-model]` button: disabled initially, enabled on selection. Redirects to `/compare/<slugs...>` on click.
- `/api/search` in `app.py` returns `slug`, `name`, `developer`, `logo` per result.

## Adding a new page

Pattern for standalone marketing/landing pages (no server-side data needed):

1. Create `templates/<name>.html` — self-contained HTML, all CSS inline or single `<link>`. No Jinja needed if page is static.
2. Add route in `app.py`:

   ```python
   @app.get("/page-name")
   def page_name():
       return render_template("page-name.html")
   ```

3. Verify locally before push:

   ```sh
   python3 -c "from app import app; r = app.test_client().get('/page-name'); print(r.status_code, len(r.data)); assert b'Expected Content' in r.data"
   ```

4. Commit, push, rebuild (standard deploy flow).

For pages that DO need DB data, use the `get_session()` / `try:finally: session.close()` pattern from existing routes.

## Branch workflow (experimental features)

For big experiments or design system previews that shouldn't touch `main`:

```sh
cd /root/modelhub
git checkout -b feat/<descriptive-name>
# ... make changes ...
git add -A && git commit -m "<msg>"
git push origin feat/<descriptive-name>
# GitHub prints a PR creation URL after push
```

Branch can be rebuilt separately or used for review without disrupting `main`.

## Commit → Deploy

```sh
cd /root/modelhub
git add -A && git commit -m "<msg>" && git push
docker compose -f docker-compose.yml up -d --build
curl -s https://modelbench.lol/ | head -5   # verify
```

Always verify with `curl`, check JS syntax with `node --check` for template JS, and confirm template renders with `test_client()` for new pages.

## Debugging display / sort issues

Chain to trace when data looks wrong on the live site (no browser needed):

1. **Live HTML** — `curl -sL https://modelbench.lol/path | grep ...` — verify what's actually served
2. **Trace route code** — `filtered_query()` in `app.py` builds the SQL; check sort column + direction
3. **Check DB directly** — `python3 -c "from app import get_session; from database import Model; ..."` to verify raw data
4. **Check template** — `templates/home.html` / `templates/models.html` — verify field rendering (e.g. `m.release_date`)
5. **Verify JS** — `static/js/app.js` — ensure no client-side re-sorting
6. **Docker + git** — `docker logs` / `git log` to confirm running version matches code

Common findings:
- **Sort looks wrong on /models but not homepage** → homepage filters `release_date != ""`, /models doesn't. 646 models with empty dates sort after dated ones in DESC.
- **Data stale** → check `DataSource.last_scraped` in DB; updater runs every 5min.
- **Non-ISO dates** → 8 models have `"2026-01"` (no day) — sorts lexicographically, works fine in DESC.

## Pitfalls

- **`release_date` is a String column** — `Column(String(32), default="")` in `database.py`. Works for ISO dates (`YYYY-MM-DD` sorts lexicographically in correct order), but will NOT work for other formats. If adding date filtering/comparisons, cast to actual date type in the query.
- **Minified CSS**: one line → `patch` with exact substring. Use `read_file` offset/limit to get it.
- **Inline JS in templates**: string literals containing `</script>` break the parser. Use `<\/` or escape properly.
- **JS inside IIFE**: event delegation required — inline `onclick` attributes can't reach IIFE-scoped functions.
- **SQLAlchemy tuple unpacking**: raw `session.query(A, func.max(B), C)` returns `(A, max(B), C)` tuples. Unpack in SELECT column order, not by what seems right from variable names. A `for slug, mname, max_score` on `(model_slug, max_score_float, model_name)` puts the float into `mname` and the string name into `max_score`. So every leaderboard entry's `\"score\"` is a model name string. Sorting crashes when a fallback appends a real float `br.score` — Python 3's `<` refuses str vs float.
- **Docker cache**: `--build` forces rebuild when templates/CSS change (Flask doesn't auto-reload in gunicorn).
- **Auto-deploy race**: auto_deploy.sh rebuilds every 5 min. Manual rebuild is safe, auto-deploy catches next cycle.