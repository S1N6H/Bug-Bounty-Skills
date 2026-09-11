---
name: wordpress-seo
description: "WordPress SEO & GEO audit methodology: structured data validation, blog automation via REST API, local SEO for multi-location businesses, and generative engine optimization (GEO) for AI search engines."
category: web
triggers:
  - WordPress SEO audit
  - structured data validation
  - blog automation WordPress
  - local SEO multi-location
  - GEO generative engine optimization
  - schema.org validation
---

# WordPress SEO & GEO — Audit, Automation, Optimization

A systematic methodology for auditing and optimizing WordPress sites for both traditional search engines (Google/Bing) and generative AI search engines (Google SGE, Perplexity, ChatGPT Search, Bing Copilot).

## 1. On-Page SEO Audit

### Checklist
| Element | How to Check |
|---------|-------------|
| **Canonical URLs** | `curl -s URL | grep -o 'rel="canonical"[^>]*'` |
| **OG Tags** | `curl -s URL | grep -o 'property="og:[^"]*"[^>]*'` |
| **Meta Description** | `curl -s URL | grep -o 'name="description"[^>]*'` |
| **Meta Robots** | `curl -s URL | grep -o 'name="robots"[^>]*'` |
| **Header Structure** | `curl -s URL | grep -o '<h1[^>]*>[^<]*'` |
| **Geo Tags** | `curl -s URL | grep -o 'name="geo[^"]*"[^>]*'` |
| **WordPress Version** | `curl -s URL | grep -o 'name="generator"[^>]*'` |
| **Site Speed Signals** | `curl -s URL | grep -oE 'cdn\.tailwindcss|jquery|font-awesome|unpkg\.com|googleapis'` |

### ⚠️ Schema Validation Pitfall
**NEVER trust grep/awk terminal output for JSON-LD validation.** Terminal display artifacts can make `"https://schema.org"` appear as `"https://***@type"` in the output, falsely suggesting broken markup. Always parse the JSON properly:

```python
# ✅ CORRECT: parse JSON, check @context value
import json, re
blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
for block in blocks:
    data = json.loads(block)
    assert data['@context'] == 'https://schema.org'
```

```bash
# ❌ WRONG: grep can display artifacts
grep -o '"@context":"[^"]*"'  # This is fine, but:
grep 'LocalBusiness'           # Can show @context with display artifacts
```

### Schema Validation Methods
1. **Google Rich Results Test** — POST to `https://validator.schema.org/validate` with `url=<site-url>`
2. **Local JSON parse** — Extract all `<script type="application/ld+json">` blocks and `json.loads()` each
3. **Count blocks** — Every page should have exactly the expected number of schema blocks (Organization + N×LocalBusiness + FAQPage + ItemList + BreadcrumbList + Article/HowTo)

### Media Library Inventory (via WP REST API)

Unlinked images in the media library hurt SEO (unoptimized orphan assets)
but can be gold for finding content gaps. The WP REST API enumerates all
media without crawling every page:

```bash
# List ALL media items (up to 100 per page)
curl -s "https://site.com/wp-json/wp/v2/media?per_page=100&offset=0" \
  | jq '.[] | {title: .title.rendered, url: .source_url, date: .date}'

# Filter to store/location images
curl -s "https://site.com/wp-json/wp/v2/media?per_page=100&search=store" \
  | jq '.[] | .source_url'
```

Use this for:
- **Content inventory** — find uploaded images never linked on any page
- **Store location imagery** — discover storefront photos uploaded but
  not displayed in the frontend
- **SEO gap analysis** — identify orphan media without alt text, captions,
  or page associations

For sites with many media items, paginate with `offset`:
`offset=0`, `offset=100`, `offset=200` etc.

## 2. Technical SEO Checks

### Sitemap
```bash
# Check sitemap availability
curl -o /dev/null -w "%{http_code}" "https://example.com/wp-sitemap.xml"
curl -o /dev/null -w "%{http_code}" "https://example.com/sitemap_index.xml"
# WordPress native: /wp-sitemap.xml
# If only /wp-sitemap.xml works, add redirect:
#   Redirect 301 /sitemap_index.xml /wp-sitemap.xml
```

### Robots.txt
Check for:
- **AI crawler access** — GPTBot, ChatGPT-User, ClaudeBot, PerplexityBot, Google-Extended should be ALLOWED (required for GEO)
- **SEO crawlers** — SemrushBot, AhrefsBot should be ALLOWED or rate-limited, not blocked
- **Correct sitemap URL** — points to the working sitemap

### Meta Robots
WordPress default behavior: **no `<meta name="robots">` tag means `index, follow` is implied**. The `max-image-preview:large` alone (WP 5.7+) is NOT a problem — Google treats absence of `noindex` as index. Only add explicit `index, follow` if troubleshooting.

### Page Speed Red Flags
- Tailwind CSS via CDN (`cdn.tailwindcss.com`) — should be built statically
- Multiple Google scripts (GA4 ×2, GAds, Site Kit, Clarity) — consolidate
- jQuery + jQuery Migrate — heavy, consider vanilla JS
- Leaflet/unpkg map library — lazy-load if possible

## 3. Local SEO (Multi-Location)

### Google Business Profile
For each location:
1. Verify/claim GBP listing
2. Primary category: "Electronics Repair Service", secondary: "Mobile Phone Repair Shop"
3. Services: Screen Repair, Battery Replacement, Charging Port Repair, Water Damage Repair, Data Recovery, Logic Board Repair, Console Repair, MacBook Repair, iPad Repair, Phone Trade-In
4. **Photos:** Storefront (exterior + interior), team, before/after repairs.
   - See `references/google-maps-store-capture.md` for a Playwright-based
     method to capture real storefront photos from Google Maps listings
     (useful for GBP photo audits, populating store directories, or
     competitor research without needing a Places API key).
5. Q&A: populate with 15-20 FAQs
6. Reviews: target 50+ per location
7. GBP posts weekly — promotions, new services, seasonal tips
8. Enable messaging — respond within 24h

### NAP Consistency
Standardize format across ALL platforms:
```
FoneWorld [Location Name]
[Street Address]
[City] [Postcode]
Phone: +44 XX XXXX XXXX
```
Create a single NAP reference document. Ensure identical across:
- Website (footer + location pages)
- GBP listings
- All citations
- Schema markup

### Citation Building Priority
1. Google Business Profile (CRITICAL)
2. Bing Places
3. Yell UK
4. Yelp UK
5. Apple Maps
6. Facebook Business
7. Trustpilot
8. FreeIndex, Cylex UK, 118118, Scoot (MEDIUM)
9. Hotfrog, Thomson Local, CityLocal (LOW)

## 4. Blog Automation via WordPress REST API

### Authentication
```python
import base64
auth = base64.b64encode(f"{username}:{app_password}".encode()).decode()
headers = {"Authorization": f"Basic {auth}"}
```

### Create Media (Upload Image)
```python
headers["Content-Type"] = "image/png"
headers["Content-Disposition"] = f'attachment; filename="{filename}"'
response = requests.post(f"{WP_API}/media", headers=headers, data=image_data)
media_id = response.json()["id"]
```

### Create Post
```python
payload = {
    "title": title,
    "slug": slug,
    "content": content_html,
    "excerpt": excerpt,
    "status": "publish",
    "categories": [cat_ids],
    "tags": [tag_ids],
    "featured_media": media_id,
    "date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
}
response = requests.post(f"{WP_API}/posts", json=payload, headers=headers)
```

### Slug Deduplication
Check if slug exists before creating:
```python
resp = requests.get(f"{WP_API}/posts", params={"slug": slug, "per_page": 1})
if resp.json():
    for i in range(2, 50):
        candidate = f"{base_slug}-{i}"
        check = requests.get(f"{WP_API}/posts", params={"slug": candidate, "per_page": 1})
        if not check.json():
            return candidate
```

### Keyword Injection Strategy
- Maintain a pool of target keywords from Google Ads / search data
- For each keyword, roll ~80% probability to include
- Shuffle selected keywords, weave into natural SEO paragraph before CTA
- Deduplicate keyword pool before selection
- Track which keywords have been used (optional, for rotation)

## 5. GEO (Generative Engine Optimization)

### Why GEO Matters
AI search engines (Google SGE, Perplexity, ChatGPT Search, Bing Copilot) cite sources in AI-generated answers. Being cited = free traffic from zero-click queries.

### GEO Checklist
| Factor | How to Achieve |
|--------|---------------|
| **FAQ Schema** | Add `FAQPage` schema with 6+ Q&As on landing pages |
| **HowTo Schema** | Add `HowTo` schema to all tutorial/blog posts |
| **LocalBusiness Schema** | Valid `@context: "https://schema.org"` for every location |
| **AI Crawler Access** | robots.txt ALLOWS GPTBot, ChatGPT-User, ClaudeBot, PerplexityBot, Google-Extended |
| **Entity Alignment** | Wikipedia entry, Wikidata item, Crunchbase, LinkedIn Company Page |
| **Review Signals** | Trustpilot/review platform with 50+ reviews |
| **Conversational Content** | Q&A format in blog posts, "Quick Answer" callout at top |
| **Authority Signals** | Backlinks from reputable domains, press releases, guest posts |
| **HowTo on Blog Posts** | Step-by-step schema with JSON-LD for every tutorial |

### Knowledge Graph Alignment
- [ ] Same NAP across all platforms
- [ ] Logo in standard format (112×112px minimum)
- [ ] Social profiles linked
- [ ] Website verified with Google Search Console
- [ ] GBP verified and optimized
- [ ] Schema markup validated via Schema.org validator

### Backlink Acquisition
- Press releases for store openings → local news pickup
- Guest posts on tech blogs (MacRumors, 9to5Mac, Android Central)
- "Best [service] in [city]" roundup articles — pitch inclusion
- Shopping centre partnerships → links from supplier pages
- Student discounts → links from university websites
- Local business directories in each city

## 6. Content Strategy

### Pillar/Cluster Model
Create pillar pages for broad topics, then cluster blog posts that link back:

```
Pillar: Phone Screen Repair UK
├── Cluster: How to fix a cracked phone screen
├── Cluster: iPhone screen replacement cost UK 2026
├── Cluster: Samsung screen repair vs replacement
├── Cluster: OLED vs LCD screen replacement
└── Cluster: Why OEM-grade screens matter
```

### Internal Linking
- Every blog post should link to 1-2 relevant service pages
- Use descriptive anchor text (not "click here")
- Existing posts should be retrofitted with internal links via REST API

## 7. Prioritized Action Items

### P0 — This Week (Critical)
1. Fix broken `@context` in ALL LocalBusiness schemas (validate that it says `"https://schema.org"`)
2. Add `index, follow` to meta robots if explicitly needed (WordPress default is fine without it)
3. Fix sitemap 404 — redirect to working sitemap
4. Verify and optimize GBP listings for ALL locations
5. Consolidate duplicate analytics/GA4 properties

### P1 — This Month (Important)
6. Add BreadcrumbList schema to all pages
7. Add HowTo schema to all blog/tutorial posts
8. Implement internal linking strategy
9. Add pricing tables to service pages
10. Build local citations on Yell, Yelp, Bing, Apple Maps
11. Create dedicated pricing pillar page (biggest content gap)
12. Unify NAP formatting across all locations

### P2 — This Quarter (Growth)
13. Implement pillar/cluster content model
14. Create Wikipedia + Wikidata entries
15. Build backlinks through press releases + guest posts
16. Implement blog content calendar (12 weeks)
17. Add author bios to all blog posts
18. Create business services B2B page

## 8. Measurement

### Key KPIs
| KPI | 3-Month | 6-Month | 12-Month |
|-----|---------|---------|----------|
| Google Organic Traffic | +50% | +150% | +300% |
| Keyword Rankings (top 10) | 20 | 50 | 100+ |
| #1 Rankings | 5 | 15 | 25+ |
| GBP Reviews | 250+ | 400+ | 600+ |
| Backlinks | 50 | 150 | 500+ |

### Tools
- Google Search Console — crawl errors, indexing, queries
- Google Analytics 4 — traffic, conversions
- Google PageSpeed Insights — Core Web Vitals
- Ahrefs/Semrush — keyword tracking, backlinks (unblock in robots.txt!)
- Schema.org Validator — validate ALL schema
- Google Rich Results Test — test structured data

### Weekly Routine
- [ ] Check GSC for new issues
- [ ] Monitor top 20 keyword rankings
- [ ] Check GBP insights (views, searches, calls)
- [ ] Respond to new reviews
- [ ] Confirm no crawl errors

### Monthly Routine
- [ ] Publish 4 pillar/cluster content pieces
- [ ] Build 3-5 new backlinks
- [ ] Submit to 2-3 new citation directories
- [ ] Run technical SEO scan
- [ ] Check competitor movements
