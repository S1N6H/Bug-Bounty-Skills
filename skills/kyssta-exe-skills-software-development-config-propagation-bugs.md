---
name: config-propagation-bugs
description: "Detect and fix silent data loss from incomplete model serialization, wholesale overwrites, and live-probe replacement of configured values."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [pydantic, fastapi, data-loss, config, debugging, bug-pattern]
    related_skills: [systematic-debugging]
---

# Config Propagation Bugs

## Overview

A recurring bug class in FastAPI/Pydantic applications: API endpoints silently drop config fields because the Pydantic request model doesn't declare them, the transform function naturally omits them, and the endpoint does a wholesale dict overwrite of the persisted config section.

**Symptom:** User sets a config value (by hand-editing config.yaml or via another endpoint), saves unrelated settings through the UI, and the original value silently reverts to its default.

**Root cause:** The request model → transform → overwrite pipeline has no mechanism to preserve fields it doesn't know about.

## The Pattern

```
┌─────────────────────┐
│  Pydantic Model      │  Fields A, B, C declared
│  (API request body)  │  Fields X, Y NOT declared
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Transform /         │  Builds dict from model fields only
│  Normalize function  │  Output: {A, B, C} — no X, Y
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Endpoint handler    │  cfg["section"] = normalized
│  (wholesale overwrite)│  Previous X, Y values: GONE
└─────────────────────┘
```

## Detection

### 1. Find the Pydantic model that receives the config save

```bash
search_files("class.*Payload.*BaseModel", file_glob="*.py")
# or
search_files("class.*Config.*BaseModel", file_glob="*.py")
```

### 2. Find fields in the config template that are NOT in the model

```bash
# What fields does the config have?
search_files('"field_name":', path='config.py', file_glob="*.py")

# What fields does the Pydantic model declare?
search_files("field_name:", path='web_server.py', file_glob="*.py")
```

Compare the two lists. Any config field NOT in the Pydantic model is at risk.

### 3. Find the wholesale overwrite site

```bash
search_files('cfg\\[".*"\\]\\s*=\\s*normalized', file_glob="*.py")
# or
search_files('cfg\\[".*"\\]\\s*=\\s*raw', file_glob="*.py")
# or
search_files('save_config\\(cfg\\)', file_glob="*.py")
```

Look for the pattern: `cfg[section] = result_of_transform` where `result_of_transform` was built solely from the Pydantic model.

### 4. Confirm with standalone reproduction

Write a minimal script — don't rely on the full test suite for initial confirmation:

```python
import os, tempfile
os.environ['HERMES_HOME'] = tempfile.mkdtemp()

from config_module import load_config, save_config
from transform_module import normalize_config

# Seed the field that should be preserved
cfg = load_config()
cfg["section"]["missing_field"] = True
save_config(cfg)

# Simulate what the endpoint does
raw = {"known_field": "value"}  # missing_field not here
normalized = normalize_config(raw)
cfg["section"] = normalized  # wholesale overwrite
save_config(cfg)

# Verify
cfg2 = load_config()
assert cfg2["section"].get("missing_field") is True, "BUG: field silently dropped"
```

## Fix Strategies

### Strategy A: Preserve at the overwrite site (least invasive)

After the transform builds its dict, copy missing fields from the previous config before assigning:

```python
normalized = normalize_config(raw)
_prev = cfg.get("section", {})
for key in ("field_x", "field_y"):
    if key in _prev and key not in normalized:
        normalized[key] = _prev[key]
cfg["section"] = normalized
```

**When to use:** Fields are external to the model by design (debug flags, audit settings, feature toggles the client never sends). The transform function is shared or complex and adding fields there would be intrusive.

### Strategy B: Add fields to the Pydantic model (most correct)

Declare the fields as `Optional` with defaults in the model so they flow through naturally:

```python
class ConfigPayload(BaseModel):
    known_field: str = ""
    missing_field_x: Optional[bool] = None
    missing_field_y: Optional[str] = None
```

Then include them in the `raw` dict before normalization.

**When to use:** The fields are part of the logical config section and clients should eventually send them. Requires updating API docs and client code.

### Strategy C: Merge instead of overwrite

```python
merged = {**cfg.get("section", {}), **normalized}
cfg["section"] = merged
```

**When to use:** Only when the transform dict is a complete representation of what should be saved (i.e., the transform intentionally omits nothing). Usually NOT the right choice — the transform exists specifically to reshape input, so an empty key means "not provided," not "delete."

## Checklist for Code Review

When reviewing any endpoint that saves config:

- [ ] Does the Pydantic model declare ALL fields that exist in the config section?
- [ ] Does the transform function include ALL fields in its output?
- [ ] Does the endpoint use merge semantics (not wholesale overwrite)?
- [ ] Are there regression tests that seed extra fields and assert they survive a save?

## Variant: Live Probe Replaces Configured Values

A subtler form of config data loss: the config YAML is correctly parsed and
the field IS present in memory, but a runtime "live probe" (fetching data from
a remote endpoint) overwrites it before the UI renders.

**Symptom:** User hand-edits `config.yaml` to set a `models:` map on a
`custom_providers` entry. The parsing code correctly reads it, but the Desktop
model picker only shows the top-level `model:` value or a different set.

**Root cause (issue #59560):** In `model_switch.py` Section 4, after
correctly assembling the model list from `model:` + `models:` dict, the code
probes the endpoint's `/models` API. When `api_key` is set and
`discover_models` is not `false`, the probe succeeds and **replaces** the
entire model list:

```python
# model_switch.py lines 2315-2331
should_probe = (
    _can_probe_custom_provider(row_is_current=_grp_is_current)
    and bool(api_url)
    and (bool(api_key) or not grp["models"])  # api_key present → always probe
    and grp.get("discover_models", True)       # True by default
)
if should_probe:
    live_models = fetch_api_models(api_key, api_url, ...)
    if live_models:
        grp["models"] = live_models  # REPLACES configured models
```

**Diagnosis checklist:**
1. Verify config parsing is correct: call `_normalize_custom_provider_entry()`
   and `get_compatible_custom_providers()` — confirm `models` dict is present.
2. Check if probing is the culprit: look at the `should_probe` condition in
   `list_authenticated_providers()` Section 4 (model_switch.py ~line 2315).
   If `api_key` is set and `discover_models` is not false, probing will
   replace configured models.
3. Verify the endpoint's `/models` response: if it doesn't return all
   configured models, the configured subset is lost.

**Fix:** Set `discover_models: false` on the `custom_providers` entry so the
configured `models:` list is preserved regardless of the `/models` endpoint.
This is the intended escape hatch (documented in model_switch.py lines
2290-2308).

**Custom_providers config pipeline (reference):**
```
config.yaml
  → _normalize_custom_provider_entry()          # config.py:4580
  → get_compatible_custom_providers()            # config.py:4814
  → load_picker_context()                        # inventory.py:79
  → build_models_payload()                       # inventory.py:111
  → list_authenticated_providers()               # model_switch.py:1447
    → Section 4: group by endpoint, add models   # model_switch.py:2128
    → Live probe (if should_probe)               # model_switch.py:2315
  → UI renders provider.models                   # model-picker.tsx / ModelPickerDialog.tsx
```

## Historical Example

**Issue #58819:** `MoaConfigPayload` in `hermes_cli/web_server.py` did not declare `save_traces` or `trace_dir`. `normalize_moa_config()` builds a dict from the model fields only. `set_moa_models()` did `cfg["moa"] = normalized`, silently dropping both fields.

**Fix:** After `normalized = normalize_moa_config(raw)`, copy `save_traces` and `trace_dir` from the previous `cfg["moa"]` if they exist and weren't included in the normalized result.

**Issue #59560:** `custom_providers` entry with `models:` dict correctly parsed but overwritten by live `/models` probe. Config pipeline verified intact — `_normalize_custom_provider_entry()` preserves `models` dict, `get_compatible_custom_providers()` passes it through. Root cause is `list_authenticated_providers()` Section 4 probing with `api_key` present, replacing configured models with endpoint response.

**Fix:** User sets `discover_models: false` on the entry. See `references/custom-providers-pipeline.md` for the full tracing guide.

### Variant 2: Live Probe Config Writeback Destroys Metadata on Disk

An even subtler variant: even after the in-memory `grp["models"]` is correctly
handled, a separate **persistent writeback** function replaces the dict-form
`models` in the on-disk `config.yaml`, permanently losing per-model metadata
like `context_length`.

**Problems:**
1. The writeback happens at CLI startup (prewarm), not just when opening the
   picker — so users who never touch `/model` can still lose their metadata.
2. The writeback writes to disk, so the destruction survives restarts.
3. The writeback function uses a flat `list[str]` for the model IDs, so it
   unconditionally replaces any dict-form value.

**Root cause (issue #67841, PR #67878):** `_save_discovered_models_to_config()`
in `hermes_cli/model_switch.py` (added by PR #65652) is called after every
successful `/models` probe. It matches entries by `base_url`, then does:

```python
entry["models"] = model_ids  # model_ids is List[str]
```

When the user's config has `models: {"model-a": {"context_length": 8192}}`,
this replaces the curated mapping with `["model-a", "discovered-b"]`,
destroying `context_length` and any other metadata.

**Detection:** Check `~/.hermes/config.yaml` for a `custom_providers` entry
whose `models:` key was a dict and is now a flat list. Compare git / backup
diffs of the file to confirm when it changed.

**Fix (code):** Add a guard in `_save_discovered_models_to_config()` to skip
dict-form entries:

```python
existing = entry.get("models")
if isinstance(existing, dict):       # ← preserve per-model metadata
    continue
if isinstance(existing, list) and existing == model_ids:
    continue
entry["models"] = model_ids
```

**Fix (config, workaround):** Set `discover_models: false` on the
`custom_providers` entry. This prevents the probe from running, which in turn
prevents the writeback function from being called.

**Timing:** The prewarm trigger chain is:
```
CLI startup
  → prewarm_picker_cache_async()
    → list_authenticated_providers(probe_custom_providers=True)
      → Section 4 probes each custom endpoint
        → fetch_api_models() success
          → _save_discovered_models_to_config(url, model_ids)
            → writes flat list to config.yaml on disk
```

This completes silently a few seconds after the welcome banner appears,
with no visible warning.

**Regression history:**
- PR #65652 added `_save_discovered_models_to_config()` — introduced the bug.
- PR #67878 added the `isinstance(existing, dict)` guard — fixed it.
