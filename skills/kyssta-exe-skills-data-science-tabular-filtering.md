---
name: tabular-filtering
description: Filter tabular data (CSV, Excel) by string columns with fuzzy/partial matching, not just exact substring. Covers prefix/root matching, spelling variants, false-positive filtering, and independent vs exclusive area counts.
tags:
  - excel
  - csv
  - filtering
  - data-cleaning
  - fuzzy-matching
  - openpyxl
  - address-matching
---

# Tabular Data Filtering (Fuzzy String Matching)

When a user uploads a spreadsheet and asks you to filter rows where a column
contains one of several terms (addresses, names, categories), **naive
substring matching misses many valid rows**. Real-world data has:

- Spacing variants (`baghbanpura` vs `baghban pura` vs `baghban pora`)
- Prefix/root truncation (`darogha` instead of `daroghawala`)
- Typos (`salamatpurra`, `baghbanura`, `daroghahwala`)
- Compound addresses (`SHALIMAR TOWN BAGHBANPURA` — belongs to both areas)

## Matching Strategy (from most to least strict)

| Strategy | Example | When to use |
|---|---|---|
| **Exact substring** | `"baghbanpura" in addr` | Clean data, single canonical spelling |
| **Space variants** | `"baghban pura" in addr or "baghbanpura" in addr` | Catch space/no-space differences |
| **Prefix/root match** | `"baghban" in addr` | Catch all baghban* variants (pura, pura, pora, pu) |
| **Root + qualifier** | `"singhpura" in addr or "singh pura" in addr` | Avoid false positives like "singh" as surname |

## Key Pitfalls

### 1. Prefix matching can be TOO broad

`"mint" in addr` catches:
- "pakistan mint" ✓
- "akhri mint stop" ✗ (a bus stop name, not residence area)
- "mint colony" ✗ (different locality)
- "mintgumri road" ✗ (different area)

**Fix**: match the full area name or pair with another signal:
```python
if "pakistan mint" in a or "pak mint" in a:  # right
if "mint" in a:                               # wrong — too broad
```

### 2. Disjoint areas with overlapping names

`"darogha" in addr` catches:
- "daroghawala" ✓
- "kacha darogha" ✗ (different locality)
- "darogha" as part of a person's name/surname ✗

**Fix**: filter out known false positives:
```python
if ("daroghawala" in a or "darogha wala" in a) and "kacha darogha" not in a:
```

### 3. "Madina" is a common word

`"madina" in addr` matches "Madina Colony" but also "Madina Chowk",
"Madina Street", "Madina Town", "Al-Madina Furniture" — all different
locations.

**Fix**: match the full compound `"madina colony" in addr`.

### 4. Student appears in multiple areas

Some addresses mention multiple areas (e.g. "SHALIMAR TOWN BAGHBANPURA").
Decide upfront:

- **Independent counting** — one student can belong to N areas. Top-level
  total will be higher than student count.
- **Priority ordering** — first-match-wins per area list. Use when each
  student needs exactly one bucket.
- **First-match with broader-list** — put more specific/contained areas
  first, broader parent areas last.

## Implementation Template

```python
import openpyxl
from openpyxl import Workbook

path = "data.xlsx"
wb = openpyxl.load_workbook(path, read_only=True)
sheet = wb.active
headers = [c.value for c in next(sheet.iter_rows())]
col_idx = headers.index("Adress")  # or whoever the target column is

def match_areas(addr):
    """Return list of areas matched. Each address can match multiple."""
    a = addr.lower()
    matched = []
    
    # Specific area first to avoid broader `baghban` stealing it
    if "shalimar town" in a:
        matched.append("Shalimar Town")
    
    # Root prefix match for variants: baghbanpura, baghban pura, etc.
    if "baghban" in a:
        matched.append("Baghbanpura")
    
    # etc.
    return matched

counts = Counter()
results = []  # (area, row_data)

for row in sheet.iter_rows(values_only=True):
    addr = str(row[col_idx] or "")
    for area in match_areas(addr):
        counts[area] += 1
        results.append((area, list(row)))
```

## Writing the Output File

When asked for "the file", write a new `.xlsx` with:

1. A `Matched Area` column prefixed to show which area triggered inclusion
2. Each area-student pair on its own row (if independent counting)
3. OR one row per student with the primary area (if priority ordering)

## Verification

After generating the filtered file, always run a quick sanity check:

```python
# Per-area breakdown
for area in sorted(counts):
    print(f"{area}: {counts[area]}")

# Check for obvious false positives
# e.g., print a few raw addresses from each area to eyeball
```
