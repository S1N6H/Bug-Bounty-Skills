---
name: web-app-seo
description: SEO for custom web applications (Flask, Django, FastAPI) — structured data, meta tags, URL restructuring, competitor research, and schema markup patterns for directory/listing/data sites. Not for CMS-based sites (use wordpress-seo).
trigger: |
  User asks to improve search ranking, add structured data, or audit a web app's SEO
  User asks about schema.org JSON-LD for a data-driven website
  User asks to add Open Graph / Twitter Card meta tags
  User wants to research competitor SEO for similar sites
  User is restructuring URLs for SEO benefit
---

# Web App SEO — Custom Application SEO

## Class-level concepts

This skill covers SEO for **custom-built web applications** (Flask, Django, FastAPI, etc.) — not WordPress/CMS sites (use `wordpress-seo` for those). The focus is on structured data, meta tags, URL structure, and competitor research for directory/listing/data-intensive sites.

## 1. JSON-LD Structured Data

### Key Schema Types for Directory / Benchmark Sites

| Schema Type | Where | When |
|-------------|-------|------|
| `SoftwareApplication` | Model/detail pages | AI models, software tools, any digital product |
| `BreadcrumbList` | All pages with breadcrumbs | Navigation hierarchy |
| `FAQPage` | Detail pages | Implicit Q&A on the page (capabilities, pricing, availability) |
| `WebSite` | Homepage | Site-wide, sets search action |
| `Organization` | Homepage | Brand identity |
| `DataCatalog` | Listing pages | When the page lists/searchable entries |
| `Product` | Detail pages | Physical products with pricing |
| `TechArticle` | Blog/methodology pages | Technical content |

### Injection Pattern (Flask/Jinja)

```html
{% block head %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "SoftwareApplication",
      "name": "{{model.name}}",
      "applicationCategory": "AI Model",
      "description": "{{model.description or ''}}",
      "author": {"@type": "Organization", "name": "{{model.developer}}"},
      "offers": {"@type": "Offer", "price": "{{model.price_prompt}}", "priceCurrency": "USD"}
    },
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Models", "item": "{{request.url_root}}models"},
        {"@type": "ListItem", "position": 2, "name": "{{model.developer}}"}
      ]
    },
    {
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question", "name": "What capabilities does {{model.name}} support?",
          "acceptedAnswer": {"@type": "Answer", "text": "{{model.name}} supports {{model.multimodal}} input/output modalities, reasoning, and tool calling."}
        }
      ]
    }
  ]
}
</script>
{% endblock %}
```

Use `@graph` to bundle multiple schemas in one script tag.

### FAQ Schema Tips
- Look for implicit Q&A on the page (specs tables, comparison summaries, capability lists)
- 3–4 questions is sufficient per page
- Questions should be natural search queries users would type
- Common patterns: "What is X?", "How much does X cost?", "Where can I use X?", "Is X available?"

## 2. Open Graph / Twitter Card Tags

### Base Template Pattern (Jinja block inheritance)

```html
<!-- base.html: defaults -->
<meta property="og:title" content="{% block og_title %}Default Title{% endblock %}">
<meta property="og:description" content="{% block og_description %}Default description{% endblock %}">
<meta property="og:type" content="website">
<meta property="og:url" content="{{ request.url }}">
<meta property="og:image" content="{% block og_image %}{{ url_for('static', filename='default-og.png', _external=True) }}{% endblock %}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{% block twitter_title %}{% block og_title %}{% endblock %}{% endblock %}">

<!-- model.html: per-page override -->
{% block og_title %}{{model.name}} — {{config.APP_NAME}}{% endblock %}
{% block og_description %}{{model.description or default_description}}{% endblock %}
```

### Required OG Tags
- `og:title` — page title (50-60 chars)
- `og:description` — page summary (max 160 chars)
- `og:type` — `website` for most pages, `article` for blog
- `og:url` — canonical URL with `{{ request.url }}`
- `og:image` — shareable preview image (1200×630 recommended)
- `twitter:card` — `summary_large_image`

### Additional Optimization
- `og:locale` for non-English sites
- `og:site_name` — brand name
- Preconnect for external image hosts: `<link rel="preconnect" href="https://cdn.example.com">`

## 3. URL Restructuring for SEO

### Clean URL Principles
- **Fewer path segments**: `/openai/gpt-5.6-sol` > `/models/openai/gpt-5.6-sol`
- **Semantic hierarchy**: Provider/Model is more descriptive than just /model-id
- **Dashes, not underscores**: `gpt-5.6-sol` not `gpt_5_6_sol`
- **301 redirect old → new**: Always preserve old URLs with permanent redirects
- **Update sitemap immediately** after URL changes

### Route Ordering (Flask)
When adding a catch-all route `/<path:slug>` for models/pages, register it LAST in the file to avoid shadowing specific routes:

```python
# Specific routes first (in order of specificity)
@app.get("/models")
@app.get("/providers")
@app.get("/compare")
# ...other specific routes...

# Catch-all model/detail route LAST
@app.get("/<path:slug>")
def detail_page(slug):
    ...
```

### Multi-item / Compare / List URLs

When URLs represent multiple items whose slugs contain `/`, use a clean path format instead of query strings:

```
/compare/openai~gpt-5.6-sol+openai~gpt-5.6-luna
```

- Replace `/` in each slug with `~` (path-safe); join with `+`
- Flask: `@app.get("/compare/<path:rest>")` → `rest.split("+")` → replace `~` with `/`
- Backward compat with old `?models=slug1,slug2` links via `urlModels` fallback in JS
- Client-side: `location.href = '/compare/' + slugs.map(s => s.replace('/', '~')).join('+')`
- Parsing: `pathname.match(/^\/compare\/(.+)/)` → split `+` → replace `~` with `/`
- Google gets keyword-bearing path segments instead of query params

### When restructuring URLs
1. Update ALL internal links across templates and JS
2. Update sitemap.xml to emit new URLs
3. Add 301 redirects from old URLs to new ones
4. Update `/go` or smart-redirect routes to use new URL format
5. Update canonical URL references
6. Rebuild + deploy immediately

## 4. Competitor SEO Research

### What to Check (per competitor site)
1. **Page title + meta description** — pattern, keywords, length
2. **JSON-LD schema** — view page source, grep `ld+json` or `schema.org`
3. **Open Graph tags** — grep `og:` in page source
4. **URL structure** — clean? Hierarchical? Flat?
5. **H1/H2 hierarchy** — logical structure?
6. **Breadcrumbs** — visible? Structured?
7. **Canonical URLs** — present? Self-referencing?
8. **Image alt text** — empty or descriptive?
9. **Sitemap.xml** — URL count, changefreq, lastmod
10. **Internal linking** — model ↔ provider ↔ benchmark cross-links
11. **robots.txt** — blocking anything important?
12. **Framework** — SSR or client-side render?

### Tools
- `curl -s URL | grep` — quick checks for schema, OG tags, headers
- `web_extract` — page content + title
- Delegate parallel research tasks for different sites
- Local firecrawl (if available) for JS-rendered pages
- Google Rich Results Test / Schema.org Validator for validation

## 5. GEO (Generative Engine Optimization)

> GEO optimizes content for AI assistants (ChatGPT, Gemini, Perplexity, Claude) that extract and cite web content in answers. It's distinct from traditional SEO but shares the same structured data foundation.

### Key GEO Principles

1. **FAQPage schema is the primary GEO signal.** When an AI answers "How much does X cost?", it prefers pages with FAQ markup containing that exact question. Every detail page with implicit Q&A should have FAQPage schema with 3-4 natural questions.

2. **Don't block AI crawlers in robots.txt.** Specifically allow:
   ```
   User-agent: GPTBot
   Allow: /
   
   User-agent: Google-Extended
   Allow: /
   
   User-agent: ChatGPT-User
   Allow: /
   ```

3. **Clear, factual, source-linked content.** AI extractors prefer pages that cite verifiable sources. Benchmarks, prices, and specs should point to a real URL — invented data lowers citation confidence.

4. **Open Graph / structured data → AI previews.** When users share links in ChatGPT or Perplexity, the OG title/description/image is what renders. Good OG tags directly improve AI answer quality.

5. **WebSite + SearchAction schema** enables AI search features in supported assistants.

6. **BreadcrumbList helps AI understand page hierarchy** in relation to the rest of the site.

### Homepage FAQ builds brand authority for AI answers

Adding FAQPage schema to the homepage with questions like "What is [site name]?", "Is [site name] free?", "Where does [site name] get its data?" directly feeds AI assistants (ChatGPT, Perplexity) when users ask about the site itself. This is distinct from model/detail-page FAQs which answer questions about the product.

```html
{% block head %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is Your Site?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Your Site is a free, independent directory of [thing]. All data is source-linked and verified."
      }
    },
    {
      "@type": "Question",
      "name": "Is Your Site free?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Yes. Your Site does not require an account, subscription, or payment. Data is publicly accessible."
      }
    }
  ]
}
</script>
{% endblock %}
```
### What GEO Does NOT Require
- Blog posts or news articles (AI extracts from structured data, not narrative)
- Natural language optimization (structured data + tables > prose for factual queries)
- Social media presence

### Verification
```bash
# Check all structured data on a page
curl -s https://yoursite.com/page | grep -oE '<script type="application/ld\+json">.*?</script>'
# Verify FAQ schema is extractable
curl -s https://yoursite.com/model | python3 -c "import sys,json,re; [print(json.loads(m.groups()[0]).get('@type')) for m in re.finditer(r'ld\+json\>(.*?)</', open(0).read(), re.DOTALL)]"
```

## 6. Quick Wins Checklist (Priority Order)

1. **JSON-LD schema** — SoftwareApplication + BreadcrumbList (30 min, highest impact)
2. **OG/Twitter tags** — base template + per-page overrides (15 min)
3. **Image alt text** — descriptive alt on all `<img>` tags (5 min)
4. **preconnect hints** — external resource domains (5 min)
5. **Clean URLs** — remove unnecessary path segments (30 min)
6. **FAQ schema** — extract implicit Q&A from page content (20 min) — *also GEO*
7. **WebSite + Organization schema on homepage** — enables Sitelinks Search Box + brand entity (10 min) — *also GEO*
8. **Check robots.txt doesn't block AI crawlers** — GPTBot, Google-Extended, ChatGPT-User (2 min) — *GEO*
9. **Blog/changelog article pages** — individual URLs for fresh content (30 min)
10. **Dynamic OG images** — server-generated per-page OG images (hours, low priority)

## 7. Verification

After deployment, verify with:
```bash
curl -s https://yoursite.com/page | grep -E 'ld+json|schema\.org|og:|twitter:'
curl -s https://yoursite.com/sitemap.xml | grep -c '<loc>'
```

## Pitfalls
- Don't put JSON-LD in `<body>` — must be in `<head>` for Google Rich Results
- Don't use `@graph` if you only have one schema type
- OG image must be absolute URL (include `_external=True` in Flask `url_for`)
- Don't block Google-Extended in robots.txt if you want AI search citations
- After URL changes, wait for Google to recrawl — use Search Console URL Inspection to expedite
- Always test with both `og:` and `twitter:` — some platforms only read one
- Server-side rendered (SSR) is critical for SEO — avoid client-only rendering for public pages
