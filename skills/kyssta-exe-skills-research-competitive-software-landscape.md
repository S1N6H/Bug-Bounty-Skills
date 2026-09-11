---
name: competitive-software-landscape
category: research
description: Systematic multi-registry research of open-source tools and products across categories — GitHub star queries, npm/PyPI/cargo fallback, and saturation scoring.
trigger: User asks to search, compare, audit, map, or list software tools across categories.
---

# Competitive Software Landscape Research

Systematic research of open-source tools/products across categories — star counts, registry presence, saturation assessment.

## Process

### 0. Tool availability check (try these first)
When possible, start with `web_search()` and `web_extract()` — they're fastest for fetching READMEs and docs. **But** they depend on Firecrawl credits, which may run out. This skill documents the fallback chain.

### 1. Parallel registry sweep (single terminal call)
For N independent categories, batch all queries in one `terminal()` call:

```bash
echo "=== Category A ==="
curl -s "https://api.github.com/search/repositories?q=KEYWORD+stars:>500&sort=stars&order=desc&per_page=5" | python3 -c "import json,sys; [print(f'  {r[\"full_name\"]} ⭐{r[\"stargazers_count\"]} — {(r.get(\"description\") or \"\")[:80]}') for r in json.load(sys.stdin).get('items',[])]"
echo "=== Category B ==="
# ... same pattern
```

### 2. Specific known-tool lookups
After broad search, verify known names via direct repo endpoint:
```bash
curl -s "https://api.github.com/repos/OWNER/REPO" | python3 -c "
import json,sys
d=json.load(sys.stdin)
print('Stars:', d.get('stargazers_count','?'))
print('Desc:', d.get('description',''))
print('Lang:', d.get('language',''))
print('License:', d.get('license',{}).get('spdx_id',''))
print('Topics:', d.get('topics',[]))
print('Open Issues:', d.get('open_issues_count','?'))
"
```

### 3. Fetch detailed project info from READMEs
Once you have the repo list, fetch READMEs to extract features, architecture, and unique selling points:

```bash
# Try main, then master branch
curl -sL https://raw.githubusercontent.com/OWNER/REPO/main/README.md | head -500
# Fallback:
curl -sL https://raw.githubusercontent.com/OWNER/REPO/master/README.md | head -500
```

For structured extraction, pipe README content into Python and extract sections by heading markers. Use the README content to build:
- Feature tables
- Architecture descriptions
- Supported provider lists
- Deployment options
- Comparison matrices

### 4. Multi-registry fallback
When GitHub API hits rate limit or misses tools:
- `npm search KEYWORD` — Node ecosystem
- `pip3 index list` or `pip3 index versions PKG` — Python
- `cargo search KEYWORD` — Rust

### 5. Web search fallback (when Firecrawl is down / out of credits)
Firecrawl (used by `web_search` and `web_extract`) may fail with "Payment Required: Insufficient credits". Fall back to the **DuckDuckGo Python SDK**, but note it may silently return empty results (rate-limited/blocked):

```bash
pip install duckduckgo-search
python3 -c "
from duckduckgo_search import DDGS
with DDGS() as ddgs:
    results = list(ddgs.text('YOUR QUERY HERE', max_results=5))
    for r in results:
        print(r['title'], '|', r['href'], '|', r['body'][:200])
"
```

If DuckDuckGo returns `[]` (empty), try alternative queries or skip directly to step 7 (browser fallback).

Note: `duckduckgo-search` emits a RuntimeWarning about being renamed to `ddgs` — ignore it, the API still works.

### 6. Direct web documentation extraction (when web_extract fails)
For project documentation sites, `web_extract` uses the same Firecrawl pool as `web_search`. When it's down, use `curl` directly:

```bash
# Fetch docs pages — often render text well enough for extraction
curl -sL "https://docs.example.com/page" | python3 -c "
import sys, re
html = sys.stdin.read()
text = re.sub(r'<[^>]+>', ' ', html)
text = re.sub(r'\s+', ' ', text)
for kw in ['feature', 'routing', 'load balanc', 'guardrail', 'key manag']:
    idx = text.lower().find(kw)
    if idx >= 0:
        print(f'--- {kw} ---')
        print(text[max(0,idx-100):idx+300], end='\\n\\n')
"
```

This works for static docs but poorly for JS-rendered SPAs. When curl extracts garbage, use the browser tool.

### 7. Browser tool (last resort for JS-rendered pages)
When READMEs and curl extractions are insufficient (SPA docs sites):

```python
from hermes_tools import browser_navigate, browser_snapshot, browser_vision
browser_navigate(url="https://docs.example.com/features")
snapshot = browser_snapshot(full=True)      # full text tree
vision = browser_vision(question="Features listed?")  # visual fallback
```

Use sparingly — slower than curl, more context consumed. Reserve for JS-heavy pages.

### 6. Compile with comparative scoring
Per-category report: top tools with star counts, short description, language, license.

For deep comparisons (like multiple LLM gateways), build a comprehensive document with:
- **Overview Matrix** — stars, language, type, deployment, license
- **Per-tool deep dives** — how it works, all features, what it's good at, what it lacks, unique features
- **Comparative Summary** — side-by-side feature table, performance comparison
- **Decision Matrix** — which tool to use when (by user profile: individual dev, small team, startup, enterprise)

## Pitfalls

- GitHub unauthenticated API: **60 req/hr**. Batch aggressively in one call. When exhausted, switch to npm/PyPI/cargo or general knowledge.
- GitHub search API returns different results than browsing github.com — use direct repo lookups for known tools.
- Star counts drift — note the check date in output.
- npm/PyPI/cargo results don't guarantee CLI suitability — verify each individually.
- **Firecrawl credit exhaustion**: `web_search` and `web_extract` will both fail with "Payment Required" when credits run out. This blocks both search and content extraction. The DuckDuckGo SDK and direct `raw.githubusercontent.com` curl calls are your independent fallbacks — they don't share the same credit pool.
- **DuckDuckGo rate limiting**: May return empty results (`[]`) silently. Try different query formulations, or use the browser tool to navigate directly to known URLs.
- **raw.githubusercontent.com** only works for repos that have a default branch (main or master). For others, try the API's `/repos/OWNER/REPO/readme` endpoint (returns base64-encoded content).
- **DuckDuckGo SDK can silently return `[]`** — the `duckduckgo-search` package can return empty results without error when rate-limited. Always check result length and have a fallback ready (direct curl or browser tool). This is NOT the same as a genuine "no results" for the query.
- **Direct curl to docs pages** often works for static documentation but fails for JS-rendered SPAs (React docs sites, Docusaurus with client-side rendering). Use the browser tool in those cases — but note it's significantly slower.
