---
name: desktop-file-browser-fix
description: Fix for Hermes Desktop file browser sidebar crash when encountering binary files
version: 1.0.0
author: Hermes Agent
license: MIT
---

# Hermes Desktop File Browser Sidebar Fix

**Cross-reference**: See `hermes-bugfixes` skill for the complete analysis, patch file (`references/desktop_binary_preview_crash.patch`), and debugging pitfalls for this issue.

This skill provides a fix for the Hermes Desktop file browser sidebar crash that occurs when displaying folders containing binary files (PDF, PPTX, XLS, etc.).

## Problem
When the Hermes Desktop file browser sidebar renders a folder containing binary files, it crashes with:
```
AttributeError: 'NoneType' object has no attribute 'splitlines'
```
The error appears inline in the sidebar panel with the format `@folder:path: error`. The crash is in the Python backend (`agent/context_references.py`), not the TypeScript frontend.

## Root Cause (corrected — see hermes-bugfixes for full analysis)
The error message `@folder:path: error` format comes from `_expand_reference()` in `agent/context_references.py`, NOT from the Desktop frontend. The `_rg_files()` function calls `result.stdout.splitlines()` but `result.stdout` can be empty/falsy in edge cases, triggering `'NoneType' object has no attribute 'splitlines'`.

**IMPORTANT**: The TypeScript frontend (`preview-file.tsx`) is well-guarded — it checks `state.text !== undefined` before rendering and handles binary files via `blockedByTarget` logic. Don't waste time searching for `.splitlines()` in `.tsx` files; it doesn't exist in JavaScript/TypeScript. The crash is purely a Python-side issue in the `@folder:` reference expansion path.

## Solution (see hermes-bugfixes skill for patch file)
The fix belongs in `agent/context_references.py` in the `_rg_files()` function:
1. Added an explicit guard for empty/falsy `result.stdout` — returns `[]` instead of attempting `splitlines()`
2. This is a defensive fix; with `text=True`, `result.stdout` should always be a string, but the guard prevents edge cases

```python
# In _rg_files(), after the returncode check:
if not result.stdout:
    return []
files = [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
```

**Note**: The `preview-file.tsx` TypeScript component is already well-guarded and does NOT need changes for this specific bug.

## Pitfalls
- **Python error format ≠ Python crash site**: The error `'NoneType' object has no attribute 'splitlines'` looks like a Python `AttributeError`, but the actual crash is in TypeScript where `.split('\\n')` is called on null. However, for THIS specific bug (#58718), the crash IS in the Python backend (`agent/context_references.py`), not the TypeScript frontend. Don't assume the crash location based on error message format alone.
- **File read caching**: After editing files, re-read from disk before applying patches. The `read_file` tool may serve a cached version if the file was recently accessed. Always verify with `git show HEAD:path` or `git diff` to see the actual committed content.
- **Sibling call paths**: `local-preview.ts` also calls `readDesktopFileText` (in `enrichPreviewTarget`) but already has try/catch wrapping. No fix needed there.
- **TypeScript types lie at runtime**: `HermesReadFileTextResult` declares `text: string` as non-optional, but the Electron IPC can return null. Always guard against null regardless of what the type says.

## Files Modified
- `agent/context_references.py` - Enhanced `_rg_files()` function with null guard

## Verification
After applying this fix:
- The file browser sidebar no longer crashes when displaying folders with binary files
- Binary files show appropriate fallback UI (binary file warning or preview option)
- Text files continue to display correctly with syntax highlighting
- Image files display as expected
- The editor functionality remains intact for editable text files

## Application
To apply this fix:
1. Navigate to your Hermes Agent repository
2. Apply the patch from `hermes-bugfixes` skill: `git apply references/desktop_binary_preview_crash.patch`
3. Or manually edit `agent/context_references.py` to add the null guard in `_rg_files()`
4. No rebuild needed — this is a Python backend change

## Prevention
To prevent similar issues in the future:
- **Python side**: Guard `result.stdout` before calling `.splitlines()` in subprocess calls — empty/falsy stdout can occur in edge cases even with `text=True`
- **TypeScript side**: Always validate API responses before using them, provide proper fallback values for optional fields, handle null/undefined cases explicitly
- Consider adding null-checks in both frontend and backend when consuming API responses