---
name: stealth-web-scraping
description: |
  Bypass bot detection and anti-scraping measures when browser automation is
  blocked. Covers CloakBrowser, undetected-chromedriver, and Firecrawl
  self-hosted as the three pillars: stealth browsers, patched drivers, and
  headless scraping-as-a-service.
version: 1.1.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [anti-detection, stealth, scraping, cloaking, bot-bypass, firecrawl]
    category: web
    related_skills: [computer-use, dogfood]
---

# Stealth Web Scraping — Anti-Detection Browser Automation

When standard browser tools (Hermes `browser_*` suite, raw Playwright,
raw Selenium) hit CloudFlare, Imperva, hCaptcha, DataDome, or similar
anti-bot walls, reach for the tools in this skill.

## Before stealth: try `--dump-dom` first

Many sites serve data in the initial JS-rendered DOM but don't have
active anti-bot protection. Running chromium directly with `--dump-dom`
is cheaper and faster than deploying CloakBrowser or Firecrawl:

```bash
chromium-browser --headless --dump-dom --no-sandbox \
  --disable-gpu --virtual-time-budget=5000 "https://site.com/page"
```

`--dump-dom` executes JS and returns the final rendered HTML.
`--virtual-time-budget=5000` waits up to 5s for React/Vue content.
This works when the site doesn't actively block headless browsers.

If `--dump-dom` gets blocked (CloudFlare, CAPTCHA, etc.), fall back
to the tools below.

## Before stealth: try the page's JSON API first

Before deploying CloakBrowser or Firecrawl, check if the page loads
its data from an internal JSON API endpoint. Hitting it with plain curl
is orders of magnitude faster and less fragile than any browser-based
approach. Many sites (Oracle, Steam, product catalogs, pricing tables)
serve structured data via endpoints you can find by inspecting the
page HTML.

See **`references/web-extraction-fallbacks.md`** for the full technique:
DuckDuckGo Lite as a search fallback, finding JSON endpoints in page
source, Wayback Machine for IP-blocked sites, and real-world examples
(Oracle free tier, Steam).

## Before stealth: try the Wayback Machine (web.archive.org)

When a site **IP-blocks your datacenter** (Reddit blocks Oracle Cloud, AWS,
and GCP IP ranges with `"Blocked"` / `403`) and no other approach works,
the Wayback Machine at web.archive.org often has a cached copy. This is
the cheapest possible fallback — no API key, no stealth tools, no rate
limits, works with plain curl.

```bash
# Fetch a page as it appeared on a specific date
curl -sL "https://web.archive.org/web/20250803040502if_/https://example.com/page"
```

Timestamp format: `YYYYMMDDHHMMSS`. The `if_` suffix strips Wayback
Machine's header/frame. Find available snapshots via the CDX API:

```bash
curl -sL "https://web.archive.org/cdx/search/cdx?url=https://example.com/page&output=json"
```

**Limitations:** Only works if the page was crawled; snapshots may be
stale. See **`references/web-extraction-fallbacks.md` §7** for the full
technique with Reddit-specific and CDX API examples.

## Before stealth: try raw Playwright via Node.js

When the Hermes `browser_navigate` / `browser_*` tools fail (timeout,
missing Chromium deps, daemon not starting), raw Playwright from Node.js
is a reliable zero-conf fallback. It installs its own Chromium and works
on the first try:

```bash
cd /tmp && npm install playwright
```

```javascript
const { chromium } = require('playwright');
const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
const page = await browser.newPage();
await page.goto('https://site.com', { timeout: 30000 });
console.log(await page.title());
await browser.close();
```

This bypasses the Hermes browser daemon entirely. Each run is a fresh
Chromium instance. Use this when the Hermes browser tool is down but
the target site has no active anti-bot protection.

## Decision tree

```
Blocked by anti-bot or IP-block?
├─ Before deploying anything: try these first (cheapest → most expensive)
│  ├─ --dump-dom (JS-rendered DOM, no anti-bot)
│  ├─ JSON API endpoint (page's own data source, fastest)
│  ├─ Wayback Machine (datacenter IP-block, deleted content)
│  └─ raw Playwright via Node.js (when Hermes browser tools fail)
├─ Stealth browsers (active anti-bot detection):
│  ├─ CloakBrowser (preferred — source-level patches, Playwright API)
│  └─ undetected-chromedriver (Selenium-based fallback)
├─ Bulk extraction (content only, no interaction):
│  └─ Firecrawl self-hosted (headless scraping + markdown extraction)
└─ Interactive + stealth:
   └─ CloakBrowser or undetected-chromedriver for interaction,
      Firecrawl for bulk content extraction
```

## 1. CloakBrowser (preferred stealth browser)

**What:** Chromium compiled with 59 C++ source-level patches (canvas,
WebGL, audio, fonts, GPU, screen properties). Not a JS injection —
it IS a real patched browser.

**Install:** `pip install cloakbrowser`
**Binary:** Auto-downloads ~200MB on first launch, cached locally.
**API:** Drop-in Playwright replacement — same API, change one import.

### Quick start

```python
from cloakbrowser import launch

browser = launch(headless=True, humanize=True)
page = browser.new_page()
page.goto("https://blocked-site.com")
print(page.title())
browser.close()
```

### Migration from Playwright

```python
# Before:
from playwright.sync_api import sync_playwright
pw = sync_playwright().start()
browser = pw.chromium.launch()

# After:
from cloakbrowser import launch
browser = launch()

# Everything else unchanged — same page.goto(), page.content(), etc.
```

### Key options

| Option | Default | Notes |
|--------|---------|-------|
| `headless` | `True` | Headless mode |
| `humanize` | `False` | Adds realistic interaction timing |
| `CLOAKBROWSER_LICENSE_KEY` env | — | Set for Pro (latest Chromium + patches) |

### Linux font setup

CloakBrowser spoofs Windows fonts. On Linux, install Liberation fonts
(closest free equivalents to Arial/Times/Courier):

```bash
apt-get install -y fonts-liberation
```

Without this, font fingerprinting may reveal Linux. Suppress the
warning with `CLOAKBROWSER_SUPPRESS_FONT_WARNING=1`.

### Tiers

- **Free:** Chromium v146, 58 patches, all platforms
- **Pro ($19/mo):** Latest Chromium (v148+), newest patches, priority support

## 2. undetected-chromedriver (Selenium fallback)

**What:** Patches the chromedriver binary to remove automation
signatures. Bypasses CloudFlare/Imperva/hCaptcha when running from
a residential IP.

**Install:** `pip install undetected-chromedriver`

### Quick start

```python
import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(
    options=options,
    use_subprocess=True,
    browser_executable_path="/snap/bin/chromium",
    driver_executable_path="/path/to/arm64/chromedriver"
)
driver.get("https://blocked-site.com")
print(driver.title)
driver.quit()
```

### ARM64 / aarch64 pitfall (CRITICAL)

The pip package auto-downloads an x86_64 chromedriver. On ARM64
servers (Oracle Cloud, Apple Silicon, etc.) this causes
`OSError: [Errno 8] Exec format error`.

**Fix:** Copy the system's ARM64 chromedriver to a writable path:

```bash
# Find system chromedriver
find /snap /usr -name "chromedriver" -type f 2>/dev/null
# Copy to writable location
cp /snap/chromium/.../chromedriver /root/.local/share/uc-chromedriver/chromedriver
chmod +x /root/.local/share/uc-chromedriver/chromedriver
```

Then pass `driver_executable_path` to `uc.Chrome()`. The library
patches the binary in-place, so the destination MUST be writable
(snap filesystems are read-only — copy first).

### Key notes

- Does NOT hide your IP — datacenter IPs still get flagged
- Headless mode: use `--headless=new` (Chrome 109+)
- `use_subprocess=True` is default since v3.1.6 — safer for multiprocessing
- Python 3.7+ required, Selenium 4.9+ required

## 3. Firecrawl self-hosted (scraping service)

**What:** Self-hosted headless scraping API. Converts URLs to clean
markdown/HTML. Runs Playwright internally with its own anti-detection.

**SDK:** `pip install firecrawl-py`
**Self-hosted:** Docker Compose at the firecrawl repo

### Setup (Docker Compose v2)

```bash
cd /path/to/firecrawl
# MUST use docker compose v2 (v1 does not support ${VAR:+default} syntax)
docker compose up -d --build
# API available at http://localhost:3002
```

**Services:** api, redis, rabbitmq, postgres, playwright-service,
foundationdb (6 containers total)

### Python SDK usage

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_url="http://localhost:3002")  # self-hosted
# or: app = FirecrawlApp(api_key="fc-...")  # cloud

result = app.scrape("https://example.com")
# result is a Document pydantic object, NOT a dict
print(result.metadata.title)
print(result.markdown[:500])
```

### SDK v4 API changes (breaking)

- `app.scrape_url()` was renamed to `app.scrape()` in v4
- Returns `Document` pydantic objects, not dicts
- Access via attributes: `result.metadata.title`, `result.markdown`
- NOT via dict methods: no `result.get("metadata")` or `result["markdown"]`

### Useful endpoints

```python
app.scrape(url)              # Single page to markdown
app.crawl(url)               # Recursive crawl
app.map(url)                 # Sitemap discovery
app.search(query)            # Search + scrape
app.extract(urls)            # Batch extract
```

## Helper module

A unified helper lives at:
`/root/projects/anti-detection-tools/stealth_browser.py`

```python
from stealth_browser import StealthBrowser, stealth_fetch

# Context manager
with StealthBrowser(backend="cloakbrowser") as sb:
    page = sb.goto("https://example.com")
    print(page.title())

# One-shot fetch
title, html = stealth_fetch("https://example.com")
```

## When these tools will NOT help

- **IP reputation matters most.** Even with perfect browser fingerprinting,
  datacenter IPs fail many anti-bot checks. Use residential proxies for
  high-security targets.
- **JavaScript-heavy SPAs** may need interaction (click, scroll) before
  content loads — CloakBrowser or undetected-chromedriver handle this;
  Firecrawl handles it internally.
- **Login-required content** needs session/cookie management in addition
  to anti-detection.

## Pitfalls

1. **ARM64 undetected-chromedriver** always downloads x86_64 binary.
   Always set `driver_executable_path` on ARM64 systems.
2. **Docker Compose v1** fails with firecrawl's `${VAR:+default}` syntax.
   Install docker-compose v2 plugin.
3. **CloakBrowser free tier** is behind Pro (v146 vs v148+). Some sites
   may need the latest patches — upgrade to Pro if needed.
4. **Firecrawl SDK v4** changed `scrape_url()` to `scrape()` and returns
   pydantic objects, not dicts. Do not use `.get()`.
5. **Snap filesystems are read-only** — cannot patch chromedriver in-place.
   Always copy to a writable path first.
6. **DNS resolution failure (`curl: (6)` while dig works).** Use `curl --resolve`
   to bypass the OS resolver. See `references/web-extraction-fallbacks.md` §6
   for the full technique and pitfalls.
7. **Firecrawl API container crash (ECONNREFUSED RabbitMQ).** The API
   container can crash at startup with `connect ECONNREFUSED 172.18.0.6:5672`
   — a transient race condition where the API starts before RabbitMQ is
   ready. The other 5 containers (redis, rabbitmq, postgres, playwright,
   foundationdb) stay up. **Fix:** `docker restart firecrawl-api-1`. Prevent
   recurrence with `docker update --restart unless-stopped firecrawl-api-1`.
   The source directory (`/tmp/firecrawl/`) may be deleted — the cached
   Docker images are enough to restart containers; no rebuild needed.
