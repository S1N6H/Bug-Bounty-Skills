---
name: defensive-programming
description: "Defensive programming practices to prevent bugs and increase code resilience"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [programming, best-practices, defensive-coding, software-engineering]
related_skills: [systematic-debugging, test-driven-development, requesting-code-review]
---

# Defensive Programming

Defensive programming is an approach to software design intended to ensure the continuing function of a piece of software under unforeseen circumstances. It emphasizes robustness and the ability to handle unexpected inputs or conditions gracefully.

## Core Principles

### 1. Validate All Inputs
Never trust input data, whether from users, APIs, files, or other systems. Always validate:
- Type checking (is it the expected type?)
- Range checking (is it within valid bounds?)
- Format checking (does it match expected patterns?)
- Presence checking (is it present when required?)

### 2. Assume Things Will Go Wrong
Design for failure modes:
- What happens if a file doesn't exist?
- What happens if a network call fails?
- What happens if memory allocation fails?
- What happens if the input is malformed?

### 3. Fail Fast, Fail Loud
When you detect an error condition:
- Fail immediately rather than continuing in an inconsistent state
- Provide clear, actionable error messages
- Log sufficient context for debugging

### 4. Make Invalid States Unrepresentable
Use type systems and data structures to prevent invalid states:
- Use specific types instead of primitives when possible
- Use enums for limited sets of values
- Use optionals/maybe types for values that might be absent

## Specific Practices Learned in This Session

### Verify API Filtering Works Before Presenting Comparisons

When an API endpoint accepts date range (or other filtering) parameters, **do not assume all returned fields are actually filtered by those parameters**. What looks like a time-windowed query may return cumulative/unfiltered data for some fields.

**Signals that filtering is broken:**
- Querying with different ranges (e.g., "Today" vs "Last 7 days") returns identical values for certain fields
- An extreme range like `startDate=2020-01-01` returns the same as `startDate=today` for some fields but different values for others
- The "total" or "cumulative" label is implicit — the API doesn't warn you it's not filtering

**Detection recipe:**
1. Send the same query with **three different ranges**: narrow (today), medium (last 7 days), and extreme (e.g., 5 years ago → today)
2. Compare each field across all three responses
3. Fields that return identical values across all ranges are **cumulative / not date-filtered**
4. Fields that change proportionally to range width are **properly windowed**

**Example (from FoneWorld CRM `/api/financials`):**
```
Today:     leads=4   spend=79.04  impressions=30019   ← different leads
7d:        leads=94  spend=79.04  impressions=30019   ← same spend/imps
2020→now:  leads=1025 spend=79.04 impressions=30019   ← still same
```
Conclusion: `total_leads` is properly windowed; `total_spend`, `total_impressions`, `total_clicks`, `total_reach` are cumulative/lifetime values that ignore the date filter.

**What to do about it:**
- **Never** present the same cumulative number under different window labels (1d vs 3d vs 7d) — that's misleading
- Show cumulative fields once as a snapshot with a clear label (e.g., "Meta Ads (Cumulative)")
- Break down only the properly-filtered fields by time window
- If derived metrics (CPR = spend/leads) mix a cumulative numerator with a windowed denominator, note the caveat explicitly

**When building automated reports from APIs, always include a one-time verification step** that checks whether filtering parameters actually affect each returned field. Document which fields are filtered vs cumulative in a comment or config so future developers aren't confused by identical numbers across windows.

### JSON Parsing Validation
When parsing JSON or similar structured data:
1. Always check the parsed result's type before using it
2. Don't assume JSON objects are dictionaries - they could be arrays, strings, numbers, etc.
3. Handle single-element arrays appropriately if they represent the expected structure
4. Provide sensible defaults for malformed or unexpected input

**Example (from fixing sanitize_tool_call_arguments):**
```python
try:
    parsed = json.loads(arguments)
    if not isinstance(parsed, dict):
        # Handle non-dict cases appropriately
        if isinstance(parsed, list) and len(parsed) == 1 and isinstance(parsed[0], dict):
            # Unwrap single-element list containing a dict
            parsed = parsed[0]
        else:
            # Not a dict or suitable list: treat as corrupt
            raise ValueError("Arguments must be a JSON object")
    # If we unwrapped, re-serialize to ensure canonical form
    if isinstance(parsed, dict) and parsed is not json.loads(arguments):
        function["arguments"] = json.dumps(parsed)
except (json.JSONDecodeError, ValueError):
    # Handle corrupt JSON
    function["arguments"] = "{}"
```

### Defensive Dictionary Access
When accessing nested dictionary values:
1. Always check if intermediate values exist and are of the expected type
2. Never assume that `dict.get("key")` returns a dict when you plan to call `.get()` on it
3. Provide default values at each level to prevent AttributeError

**Example (from fixing _category in learning_graph.py):**
```python
def _category(fm: dict[str, Any], skill_md: Path) -> str:
    # Defensive check: ensure fm is actually a dict before calling .get()
    if not isinstance(fm, dict):
        fm = {}
    cat = fm.get("category") or _hermes_meta(fm).get("category")
    # ... rest of function
```

Or alternatively, using safe chaining:
```python
# Instead of: fm.get("metadata", {}).get("hermes", {})
# Do:
meta = fm.get("metadata")
if isinstance(meta, dict):
    hermes = meta.get("hermes", {})
    if isinstance(hermes, dict):
        # safe to use hermes
    else:
        hermes = {}
else:
    hermes = {}
```

hermes = {}\n\n### URL-Decode HTTP Header Values Before Using as File Paths\n\nWhen extracting values from HTTP headers — especially `Content-Disposition` filenames or redirect URL paths — always URL-decode them with `urllib.parse.unquote()` before using the value as a filesystem path component. Percent-encoded non-ASCII characters expand 3-9× in length (each byte becomes `%XX`), which can push a path past Windows MAX_PATH (260 chars) even though the original filename was reasonable.\n\n**Pattern**: Code that extracts a value from an HTTP header or URL and uses it directly as a filename without decoding.\n\n**Example** (from `plugins/platforms/wecom/adapter.py:832-842`):\n```python\n# BUG: Returns percent-encoded value like \"%E4%B8%AD%E6%96%87.txt\"\ndef _guess_filename(url, content_disposition, content_type):\n    if content_disposition:\n        match = re.search(r'filename=\"?([^\";]+)\"?', content_disposition)\n        if match:\n            return match.group(1)  # Still encoded!\n```\n\n**Fix**: Always call `unquote()` on values from HTTP headers or URLs before using them as filenames:\n```python\nfrom urllib.parse import unquote\n\nreturn unquote(match.group(1))       # Content-Disposition\n# Also for URL-path fallbacks:\nPath(unquote(urlparse(url).path)).name  # Decode URL path too\n```\n\n**What can go wrong without this**:\n- **Windows MAX_PATH violation**: A 30-character Chinese filename becomes ~200+ chars when percent-encoded, exceeding 260-char limit and causing `write_bytes()` to fail\n- **Garbled cache names**: Cache files stored with encoded names are harder to inspect and debug\n- **Inconsistent behavior**: Same file with ASCII name works, non-ASCII name fails silently\n\n**Detection**: When a file upload/download works for ASCII filenames but fails for non-ASCII (especially multi-byte languages like Chinese, Japanese, Korean), check whether the filename extracted from HTTP headers is still percent-encoded before being written to the filesystem.\n\n**Affected sources to always decode**:\n| Source | Example | Decode function |\n|--------|---------|----------------|\n| `Content-Disposition: filename=\"...\"` | `%E4%B8%AD%E6%96%87.txt` | `unquote()` |\n| `Content-Disposition: filename*=UTF-8''...` | `UTF-8''%E4%B8%AD%E6%96%87.txt` | `unquote()` after stripping `UTF-8''` |\n| URL path segment | `urlparse(url).path` | `unquote()` |\n| URL query parameter | `urlparse(url).query` → `parse_qs()` | Already decoded by `parse_qs()` |\n\n**Note**: `urlparse()` does NOT decode percent-encoding — it only splits the URL into components. If you use `urlparse(url).path` as a filename, you must also call `unquote()`.\n\n## When to Apply These Practices

Apply defensive programming especially when:
- Processing external input (user data, API responses, file contents)
- Working with dynamically typed data (JSON, YAML, configuration)
- Integrating with third-party services or libraries
- Writing utility functions that others will call
- Handling data that may have come from unreliable sources

## Benefits

- Fewer production bugs and crashes
- Better error messages that aid debugging
- Increased system stability and reliability
- Easier maintenance and refactoring
- Improved security (many vulnerabilities stem from improper input validation)

## Presentation-Ready Code Quality

Before presenting any code to the user (not just before commit), verify it meets minimum quality standards. Presenting half-baked code wastes the user's time and erodes trust.

**Hard gates before showing code:**
1. **Compiles cleanly** — `go build ./cmd/...` (or equivalent) returns zero errors
2. **Tests pass** — `go test ./...` (or equivalent) is green
3. **Lint clean** — `go vet ./...` (or equivalent) has no new issues
4. **No cross-file type errors** — if vet warns about undefined types across files but "it'll compile when bundled," FIX the actual issue, don't paper over it

**Architecture gates for new projects:**
- Use standard project layout (`cmd/`, `internal/`, `pkg/`) — not monolithic `package main`
- Define interfaces and types before implementations
- Use `go:embed` for static assets instead of inline constants
- Write package-level tests alongside the first implementation
- No half-baked prototypes — the first version shown should feel production-adjacent

**Go-specific checklist for new projects:**
```
houter/
├── cmd/houter/main.go     # thin entrypoint
├── internal/
│   ├── router/            # core logic
│   ├── provider/          # interface + implementations
│   ├── cache/             # supporting infrastructure
│   └── api/               # HTTP handlers
├── ui/                    # static assets (embedded via go:embed)
├── go.mod
└── Dockerfile
```

**When a user says "this is not clean / 100x away from X":**
The problem is almost never missing features — it's low code quality. Stop adding features and fix the architecture. Identify the specific quality gaps (cross-file errors, inline-everything, no tests, wrong project layout) and fix those before adding anything new.

**Principle:** The first version you show establishes the quality baseline. Always present code that feels like v1, not v0.1.

### Full-Change Delivery: Don't Ship Half the Fix

When you update a feature, URL, command, path, or script name that appears in multiple files, the bug you ship isn't in the code you changed — it's in the documentation and installers pointing to the old version.

**Before committing any change:**
1. **Search before you ship.** `grep -rn "old-string" .` across the whole project, including docs/, install scripts, CI configs. Update EVERY occurrence, not just the one in front of you.
2. **Cross-platform verification.** Linux-only testing is not done. Reason through macOS and Windows behavior explicitly:
   - Windows: no `sh`, no `git` on PATH by default, no `make`, different line endings
   - PowerShell: native cmdlets (`Invoke-WebRequest`, `Expand-Archive`) over external commands
   - If you say "works on Windows" → the install.ps1 path is required, not the install.sh that runs in Git Bash
3. **README is not the only doc.** `README.md`, `docs/index.md`, `docs/install.md` all serve as entry points. The install command appears in all of them. Updating one but not the others is the most common "almost done" failure pattern.
4. **Install scripts are application code.** `install.sh` (POSIX sh), `install.ps1` (PowerShell) — same review, same testing. Edge cases (missing git, wrong Rust toolchain, PATH not persisted after install) ARE the real bugs, not obscure paths.

**Detection recipe:** After your change, run: `grep -rn "raw\.githubusercontent" .` or `grep -rn "install\." .` — every result should use the NEW URL. If any still point to the old one, you're not done. Same for any renamed command, path, or feature.

**Pitfall:** "I fixed the README" → But `docs/index.md` still has the old command. The README is the first thing people see on GitHub; `docs/index.md` is the first thing on GitHub Pages. Both must be updated. The install script is what actually runs — it must also be updated.

## Related Practices

- **Input validation** at system boundaries
- **Type hints** and static analysis (where available)
- **Unit testing** with edge cases and invalid inputs
- **Code reviews** focused on defensive practices
- **Static analysis tools** that catch common mistakes

## Anti-Patterns to Avoid

- Assuming parsed JSON is always an object/dictionary
- Chaining `.get()` calls without checking intermediate types
- Using broad exception handlers that mask programming errors
- Continuing execution after detecting corrupt or invalid state
- Providing unclear error messages that don't help users fix problems

### Sanitizer False Positives: Empty Collection Removal

Sanitization code often strips data it considers "no data" — but empty collections (`[]`, `{}`, `""`) are valid explicit values, not absence. When a sanitizer removes them, downstream consumers may see `null` instead of the intended empty value.

**Pattern**: Code that removes empty lists/dicts/strings as "no data" when they are actually valid explicit values.

**Example** (from `tools/schema_sanitizer.py:328-334`):
```python
# BUG: Removes required:[] (empty array) which is valid JSON Schema
if out.get("type") == "object" and isinstance(out.get("required"), list):
    props = out.get("properties") or {}
    valid = [r for r in out["required"] if isinstance(r, str) and r in props]
    if not valid:  # ← Empty list is falsy, so required:[] is deleted
        out.pop("required", None)
```

**Fix**: Distinguish between absent, present-but-empty, and present-but-malformed:
```python
if out.get("type") == "object" and isinstance(out.get("required"), list):
    props = out.get("properties") or {}
    valid = [r for r in out["required"] if isinstance(r, str) and r in props]
    if len(valid) != len(out["required"]):  # Only act if entries were pruned
        if valid:
            out["required"] = valid
        else:
            out.pop("required", None)
```

**When writing sanitizer code, always distinguish between:**
- **Absent** (key not present) → may need a default
- **Present but empty** (`[]`, `{}`, `""`) → valid explicit value, preserve it
- **Present but malformed** (wrong type, invalid content) → sanitize/fix

See `hermes-bugfixes` skill reference `references/schema_sanitizer_required_pruning_bug.md` for the full analysis.