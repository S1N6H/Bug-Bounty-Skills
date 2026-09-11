---
name: ebay-api-integration
category: devops
description: |
  eBay Trading API integration for bulk listing management, analysis, and automation.
  Covers OAuth token management, parallel GetItem/GetMyeBaySelling calls, CSV export,
  issue detection (missing GTINs, shipping details, SKUs, images), and File Exchange workflows.
tags:
  - ebay
  - trading-api
  - oauth
  - bulk-operations
  - inventory-analysis
  - file-exchange
---

# eBay API Integration

## Overview
Class-level skill for working with eBay's Trading API to manage and analyze listings at scale.
Handles authentication, rate-limiting, parallel requests, and common data-quality issues.

## Prerequisites
- eBay Developer Account (developer.ebay.com)
- Application keys: App ID (Client ID), Cert ID (Client Secret), RuName (Redirect URI)
- User OAuth token (stored in `ebay_tokens.txt`, one per line, `#` for comments)

## Authentication Flow
```bash
# One-time OAuth setup (run once per token)
python get_oauth_token.py
# Opens browser → user consents → token saved to .env
```

**Token format**: `v^1.1#i^1#f^0#I^3#p^3#r^1#t^Ul4xMF82OjRBNjM1RDNGOEZENTc2Q0IzQTYyQUYwMjg0NzMzMTI4XzJfMSNFXjI2MA==`

Store tokens in `ebay_tokens.txt` (one per line, ignore lines starting with `#`).

## Core API Calls

### GetMyeBaySelling (Summary View)
- **Purpose**: Fast fetch of all active/sold/unsold ItemIDs
- **Rate limit**: ~10 calls/sec
- **Returns**: ItemID, Title, Price, Quantity, Site, basic SellingStatus
- **Missing**: SKU, Category, Condition, ItemSpecifics, ePID, UPC/EAN/ISBN, Package details
- **Use**: Pagination (200/page) to collect all ItemIDs
- **Important**: Even when called with AU Site ID (15), GetMyeBaySelling returns listings from ALL marketplaces on the account. Filter by `Item/Site` field, NOT by the Site ID in the request header.
- **Limitation**: Does NOT return detailed fields needed for analysis — requires GetItem calls for full details

### GetItem (Detail View)
- **Purpose**: Full listing details for a single ItemID
- **Rate limit**: ~10 calls/sec (parallelize with ThreadPoolExecutor)
- **Returns**: All fields including SKU, Category, Condition, ItemSpecifics, ShippingPackageDetails, Pictures
- **Cost**: 1 call per listing → 561 listings = 561 calls
- **Note**: Price elements (StartPrice, BuyItNowPrice, CurrentPrice) have currencyID as ATTRIBUTE, not child element

## Parallel Processing Pattern
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_WORKERS = 8
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    future_to_id = {executor.submit(fetch_item, iid, token, auth_mode): iid for iid in item_ids}
    for future in as_completed(future_to_id):
        result = future.result()
        process(result)
```
- 561 listings completes in ~60 seconds with 8 workers
- Add small delay (0.05s) between submissions to avoid bursts

## Common Data Quality Issues (Auto-Detection)

| Priority | Issue | Detection | Impact | Fix Method |
|----------|-------|-----------|--------|------------|
| **🔴 #1** | Missing UPC/EAN/ISBN | `specifics.get("UPC")` empty | Kills search visibility — no catalog linkage, no Best Match boost, no Google Shopping indexing | File Exchange / Bulk Edit |
| **🔴 #2** | Missing ePID | `ProductID` empty | Same as above — eBay can't group with other sellers' identical products | Link to catalog via UI or API |
| **🟡 #3** | Few Images (≤2) | `PictureDetails/PictureURL` count < 3 | Low conversion — eBay algo penalizes, buyers skip. Target 6-12 images | Add via UI/API |
| 🟡 | Few Images (3-5) | count < 6 | Suboptimal but not critical | Add more photos |
| 🟡 | Missing SKU | `SKU` or `CustomLabel` empty | Internal tracking only, no direct search impact | File Exchange |
| 🟡 | Missing Package Weight | `ShippingPackageDetails/WeightMajor` empty | Not needed if offering free shipping. Still helps listing completeness | Bulk Edit shipping |
| 🟡 | Missing Package Dimensions | `PackageLength/Width/Depth` empty | Same as weight | Bulk Edit shipping |
| ⚫ | Out of Stock | `Available Qty == 0` | Can't sell. Either restock or end listing | Restock or end |
| ⚫ | Trading Card Specifics | Category 27501/27502/261328 missing Grade/Grader/Cert | Category-specific requirement | Add item specifics |

**Free shipping impact**: If the store offers free shipping (flat rate, no calculated shipping), weight/dimensions are NOT required for cost calculation. They still help with listing completeness and are needed if using eBay Labels. Can safely deprioritize weight/dim fixes if free shipping is active.

## Sales Recovery Priority (When User Reports Low Sales)

When user says "sales are very low since last 90 days", remediate in this order:

1. **UPC/ePID (product IDs)** — 90%+ of stores miss these. Without them eBay can't link to catalog → no search boost, no "Product Research" grouping, no Google Shopping indexing. This is the single highest-ROI fix. Even generic/matched IDs help.

2. **Images** — If ≥50% of listings have ≤2 images, that's a conversion killer. Target 6-12 photos per listing. Free to add, immediate impact.

3. **Never-sold inventory** — A large % of listings will have 0 lifetime sales. For each:
   - Check if it's in a core category (keep but improve) or a random side category (kill or bundle)
   - Check stock levels: high stock + zero sales = dead inventory eating listing fees
   - Options: kill dead listings, bundle as upsells with best sellers, or discount

4. **Cross-list performance** — US/UK cross-listed items often have 10+ units in stock and 0 sales. Either configure them properly (shipping, pricing) or delist from those sites.

5. **Out of stock items** — 36 of 561 is typical. Restock best sellers first.

## Never-Sold / Zero Seller Analysis

~60% of listings may have 0 lifetime sales. Audit them:

```python
never_sold = [r for r in rows if not r['Sold Qty'] or r['Sold Qty'] == '0']
print(f'{len(never_sold)} of {len(rows)} never sold')
for r in never_sold:
    print(f'{r["Title"][:50]} | ${r["Current Price"]} | {r["Site"]} | {r["Available Qty"]} in stock')
```

Cross-reference with categories and stock levels to decide: keep & improve, kill, or bundle.

## Price Distribution Analysis (for identifying dead weight)

```python
buckets = {'<$10': 0, '$10-25': 0, '$25-50': 0, '$50-100': 0, '$100-200': 0, '$200+': 0}
for r in rows:
    p = float(r['Current Price']) if r['Current Price'] else 0
    if p < 10: buckets['<$10'] += 1
    elif p < 25: buckets['$10-25'] += 1
    ...
```
Use to find price bands with lots of inventory but zero sales — overpriced or no-demand items.

## Trading Card Categories (Require Extra Specifics)
| Category ID | Name |
|-------------|------|
| 27501 | Trading Card Games |
| 27502 | Sports Trading Cards |
| 261328 | CCG Individual Cards |
| 261332 | Sports Cards |
| 261336 | Non-Sport Cards |
| 183454 | Collectible Card Games |

Required specifics: `Professional Grader`, `Grade`, `Certification Number`, `Card Condition`

## Output Files
- `all_listings_analysis.csv` — Full dataset with issue flags
- `listings_with_issues.csv` — Only problematic rows
- `missing_sku.csv` — Listings without SKU
- `out_of_stock.csv` — Active listings with 0 qty
- `trading_cards_analysis.csv` — TC-specific subset

## Internal Data Enrichment Workflow
To update eBay listings with data from internal systems (e.g., Shopify, ERP):

1. **Export eBay data**: Use GetMyeBaySelling/GetItem API or File Exchange "Download Active Inventory" to get current listings with ItemID, Title, etc.
2. **Prepare internal sources**: Ensure CSV/Excel files contain:
   - eBay Item ID (or derivable, like from Product eBay URL)
   - Fields to update (Package Weight, Package Dimensions, etc.)
3. **Normalize identifiers**: 
   - Convert scientific notation (e.g., `1.47E+11` → `147035768999`) via `str(int(float(v)))`
   - Extract Item ID from eBay URLs (see "URL-Based Item ID Extraction" below)
   - Trim whitespace and handle quotes
4. **Create lookup maps**: Build dictionaries from internal sources keyed by normalized Item ID
5. **Merge data**: For each eBay listing:
   - Use existing eBay values if present and valid
   - Fill missing values from internal sources (prioritize sources as needed)
   - Track items still missing data for follow-up
6. **Generate File Exchange CSV**: Format with required columns (Action, ItemID, PackageLength, etc.)
7. **Upload and monitor**: Submit via File Exchange and check for email confirmation

### Audit-First Default
- **IMPORTANT USER PREFERENCE**: By default, run in **audit/validation mode only** — report gaps but do NOT update eBay listings unless explicitly told to update.
- User's words: "dont update anything i will do it myself you just have to check files"
- The deliverable is: a coverage report showing which flagged items have data ready vs which still need work.
- Only proceed to API updates (SetItem, File Exchange upload, ReviseFixedPriceItem) when the user explicitly says "update" or "fix" or "apply".

### URL-Based Item ID Extraction
When CSV exports use scientific notation (e.g., `1.47E+11`) and lose precision, extract the real Item ID from the eBay URL column:

| eBay URL Format | Regex | Example |
|---|---|---|
| `/itm/TITLE-/ITEM_ID` (trailing dash) | `r'/(\d{9,})$'` | `.../Honey-Creamer-/147035768999` → `147035768999` |
| `/itm/TITLE-ID` (no trailing dash) | `r'/itm/.+-(\d{9,})$'` | `.../Honey-Creamer-147035768999` → `147035768999` |

Simplest reliable pattern for both: extract the last group of 9+ digits at end of URL:
```python
import re
def extract_ebay_id(url):
    m = re.search(r'/(\d{9,})$', url)
    return m.group(1) if m else None
```

### Mixed Delimiter Detection
Work files from spreadsheet exports often have mixed delimiters:
```python
with open(filepath, "r") as f:
    first = f.readline()
    delim = "\t" if "\t" in first else ","
rows = list(csv.DictReader(open(filepath, "r"), delimiter=delim))
```
**Common scenario**: `all_products.csv` (eBay API export) is comma-delimited; `single_variant_master.csv` (Shopify/manual export) is tab-delimited. Always auto-detect.

### Coverage Validation / Gap Analysis
Before applying any updates from work files, validate which flagged listings are covered:

**Cross-reference workflow:**
```python
# 1. Load eBay export and build lookup
all_prods = csv.DictReader(open("all_products.csv"))
all_by_id = {r["Item ID"]: r for r in all_prods}
flagged_ids = {r["Item ID"] for r in all_by_id.values()
               if r.get("Missing Weight") == "YES"}

# 2. Load work files (may be TSV!) and extract IDs
work_ids = set()
for filepath in ["single_variant_master.csv", "multi_variant.csv"]:
    with open(filepath) as f:
        first = f.readline()
        delim = "\t" if "\t" in first else ","
    for r in csv.DictReader(open(filepath), delimiter=delim):
        url = r.get("Product eBay URL", "")
        iid = extract_ebay_id(url)
        if iid: work_ids.add(iid)

# 3. Find gaps
covered = flagged_ids & work_ids
uncovered = flagged_ids - work_ids

print(f"Flagged: {len(flagged_ids)}")
print(f"Covered by work files: {len(covered)}")
print(f"Still need data: {len(uncovered)}")
```

**What to report:**
- Total flagged items
- How many have data ready in work files (covered)
- How many still need data (uncovered)
- For uncovered: which have stock > 0 (urgent) vs out of stock (can wait)
- Separate AU items (likely covered) from US/UK cross-lists (likely uncovered)

**Key insight**: Weight/dimensions are **product-level**, not site-level. The same physical product listed on AU, US, and UK sites has identical weight and dimensions. If an AU listing has weight/dims set, its US/UK cross-list should use the same values. The API may show US/UK listings as missing data because cross-list shipping config doesn't auto-populate from the primary listing.

### Multi-Variant Listing Nuance
- Multi-variant listings may have per-variant weights (in `Shopify Variant Weights` column) but still show as flagged on eBay because the listing-level `Package Weight` / `Package Dimensions` are empty.
- eBay requires shipping data at the **listing level** even for multi-variant items. Apply the most common variant's weight (or the largest/heaviest) as the listing-level default.
- Work file columns differ: `multi_variant.csv` has `a_weights` column with format `"MULTI - decide: 1kg, 5kg, 10kg"` and `Shopify Variant Weights` with per-variant mapping. Do NOT confuse the two.
- `unresolved.csv` items have no Shopify match or no weight data available — these need manual resolution.

### Example Field Mapping
| eBay Field | Internal Column | Notes |
|------------|----------------|-------|
| Package Length | `Package Length` or derived | In cm |
| Package Width | `Package Width` | In cm |
| Package Depth | `Package Depth` | In cm |
| Weight Major | `Weight` (kg) | Integer part |
| Weight Minor | `Weight` (kg) | Fractional part * 1000 (grams) |
| Weight Unit | Derived | `Kilograms` or `Grams` |
| Quantity | `Available Qty` or `Quantity` | Current stock |
| Shipping Profile Name | `Shipping Profile` or `Postage Policy` | Existing eBay profile name |

### Handling Identifier Mismatches
- **Scientific notation**: Convert `1.47E+11` to `147035768999` via `'{:.0f}'.format(float(s))`
- **URL extraction**: Use regex `r'/itm/(\d+)'` on `Product eBay URL` column
- **Fallback**: Use `ID` column after normalizing scientific notation
- **Validation**: Ensure resulting ID is 10-13 digits

## Session Artifacts (Example)
*See the workflow above applied to real sessions (Jun–Jul 2026, beekeeping supplies seller — OZ ARMOUR / OZ APIARIST):*

**Run 1 — AU-only (corrected by user)**
- Fetched **561 active listings** via GetMyeBaySelling (3 pages @ 200/page)
- Sequential GetItem processing: **411 AU, 106 US, 41 UK** — ~12 min total (1.3s/item)
- Saved only AU rows to CSV (user corrected: "not only AU u have to save all kind of listings")
- **385 AU listings** had complete weight + dimensions; **26 flagged** (missing both weight AND dimensions)
  - 24/26 flagged were already out of stock; 2 were live with stock (urgent)
- **36 total AU listings out of stock**

**Run 2 — All sites (corrected by user feedback)**
- Same 561 items, saved all 561 to `all_products.csv` with full fields
- Flagged: 169 (all missing BOTH weight AND dimensions)
- 392 complete, 36 out of stock, 133 need fixing (flagged + have stock)

**Cross-Reference Audit (Jul 2026)**  
**Shopify Bulk Match (Jul 2026)**  
- **168/169** missing-weight eBay listings matched to Shopify product data via simple title matching (exact → contains → word-overlap) using `/products.json` bulk API
- **1 unresolved** — obscure book SKU not on Shopify
- See `references/shopify-weight-extraction.md` for matching code

User provided work files: `single_variant_master.csv` (83 items, w/dims), `multi_variant.csv` (31 items, variant weights), `unresolved.csv` (8 items, cannot resolve)
- Key finding: AU flagged items (26) were fully covered by work files, but US/UK cross-lists (140 items) had ZERO coverage
- Weight/dims are product-level — same product across AU/US/UK should have identical shipping data
- Files used mixed delimiters: TSV (single_variant*), CSV (multi_variant, unresolved) — auto-detection essential
- User preference confirmed: audit-only by default, "dont update anything i will do it myself"
- Full analysis documented in `references/coverage-validation-workfiles.md`
- Flagged across all sites: **169** (all missing BOTH weight AND dimensions)
- **392 complete**, **36 out of stock**, **133 need fixing** (flagged + still have stock)
- Cross-site listings (US/UK) overwhelmingly lack shipping details due to different marketplace configs
- User preference: "dont give me countrywise summary overall" — flat overall numbers only
- User preference: "give short concise ansers to the point dont ask me questions" — no questions back, minimal output

**Key pattern**: When sellers miss shipping details on cross-site listings, they almost always miss BOTH weight and dimensions. Prioritize flagged items that still have stock first. Always save ALL sites in the initial export — let the user decide what to filter later.

## File Exchange Integration
For bulk fixes, export template:
```
Seller Hub → Tools → File Exchange → Download Active Inventory
```
Edit CSV → Upload → eBay processes asynchronously (email notification).

## Pitfalls & Workarounds

### 1. GetMyeBaySelling Pagination Bug
- `TotalNumberOfPages` sometimes returns 561 instead of 3 (for 561 items @ 200/page)
- **Fix**: Stop when `items` list is empty OR page > calculated pages

### 2. OAuth vs Auth'n'Auth Detection
- Try `oauth` first (modern), fall back to `authnauth` (legacy)
- `X-EBAY-API-IAF-TOKEN` header for OAuth
- `<RequesterCredentials><eBayAuthToken>` for Auth'n'Auth

### 3. Rate Limit Errors (218050, 21919165)
- Back off exponentially: 10s, 20s, 40s
- Reduce MAX_WORKERS if persistent

### 4. Policy Violation Errors (21920397)
- "Single-use plastic products policy" — listing removed
- Check removed listings via `UnsoldList` or email notifications

### 5. Site ID Mismatch
- Use `SITE_ID = "0"` (US) for GetMyeBaySelling to get all sites
- Filter by `Item/Site` field in response ("Australia", "UK", "US")

### 6. Always Save ALL Sites — Never Filter in the Initial Export
- GetMyeBaySelling returns listings from EVERY marketplace on the account regardless of the Site ID used
- **CRITICAL PITFALL**: Do NOT filter to one site when building the output CSV. Save ALL listings regardless of Site value. The user wants a complete inventory view, not a per-country subset.
- Cross-site (non-primary) listings will almost always lack package weight/dimensions when queried — this is expected and should be flagged, not filtered out
- Include the `Site` column in the CSV so the user can filter later if needed

### 7. User Presentation Preference: Minimalist Direct Answers

- **Style: short, direct, flat numbers, no fluff, zero questions back.** No percentages, no hedging, no questions back. If the user wants elaboration they'll ask.
- **Do NOT ask the user clarifying questions** — if data is missing, state what you have and move on. Never end a response with a question.
- Give **flat counts first** — do NOT break down by country unless explicitly asked.
- Example (DO): "36 out of stock of 561 total"
- Example (DON'T): "Australia: 26/411, US: 100/106, UK: 40/41"
- When asked "best selling products, categories etc" — deliver a clean top-N table and a category breakdown inline. If they follow up with "do we have categories?", they just want a clean list of categories — not another analysis. Match the level they ask at.
- If the user asks for detail, they'll ask. Default to the single-line total.

### 8. XML Namespace Handling
```python
NS = "urn:ebay:apis:eBLBaseComponents"
def tag(name): return f"{{{NS}}}{name}"
# Use: elem.find(tag("ItemID"))
```

### 9. Currency ID on Price Elements
- Price elements have `currencyID` attribute, not child element
- Use `elem.get("currencyID", "")` on StartPrice, BuyItNowPrice, CurrentPrice

## Free Shipping Pricing Strategy (Price Bump Calculator)

When a user asks "how much to increase prices if I switch to free shipping":

1. **Get product weights** from Shopify: `curl -s "https://{store}/products.json?limit=250"` → `variants[].grams`
2. **Estimate shipping cost per product** by weight band (use carrier rates or known patterns):
   - <500g: ~$10-13
   - 500g-1kg: ~$13-16
   - 1-3kg: ~$16-20
   - 3-5kg: ~$20-25
   - 5-10kg: ~$25-30
   - 10-20kg: ~$30-45
   - 20kg+: ~$45-60+ (often courier)
3. **Calculate weighted average shipping cost** across all products (weight by sales velocity)
4. **Recommend bump** = average shipping cost as % of average order value
5. **Tiered option**: free shipping on orders over $X threshold, calculated shipping below it

```python
import json
prods = json.load(open("products.json"))['products']
avg_g = sum(p['variants'][0]['grams'] for p in prods) / len(prods)
est = 13 + max(0, (avg_g - 500) / 1000 * 2)
print(f"Avg {avg_g:.0f}g → ~${est:.0f} shipping")
```

**Key insight**: For stores selling mostly suits ($130-240, 1-3kg), a ~$15-18 bump covers standard shipping for most items. Heavy items (honey tanks, extractors) may need separate handling.

## Quick Start Script
See `scripts/fetch_all_listings.py` — complete parallel analysis in one run.
See `templates/get_all_listings.py` — sequential all-sites export with full fields (price, condition, listing type) and flat summary output. Designed for the user who wants overall numbers, not per-country breakdowns.

## References
- `references/ebay-trading-api-calls.md` — Key call signatures and parameters
- `references/common-error-codes.md` — Error codes and resolutions
- `references/trading-card-categories.md` — Category IDs and required specifics
- `references/file-exchange-workflow.md` — Step-by-step File Exchange guide
- `references/xml-namespace-handling.md` — XML namespace handling tips
- `references/weight-dimension-estimates.md` — Typical weights/dims for eBay items
- `references/internal-data-enrichment.md` — Guide to combining eBay and internal data sources
- `references/api-timing-benchmarks.md` — Real-world timing benchmarks (sequential vs parallel, throughput, site breakdown)
- `references/coverage-validation-workfiles.md` — Cross-referencing seller work files against eBay API export to validate coverage and find gaps
- `references/shopify-weight-extraction.md` — Extracting product weights from Shopify JSON API for cross-site listing enrichment
- `references/shopify-cart-shipping-testing.md` — Adding items to cart via direct cart URL (bypasses bot detection), checking shipping rates, and limitations of modern Shopify checkout APIs
- `references/store-profile-2026-07.md` — Store category/revenue/stock snapshot (Jul 2026, beekeeping supplies). Refresh monthly via `scripts/fetch_all_listings.py`