---
name: delivery
category: productivity
description: Shipping project deliverables — install scripts, documentation, multi-platform support, CI/CD. Before declaring done, verify the full chain end-to-end.
---

# Delivery — shipping project work

Class of work: writing READMEs, install scripts, CI configs, docs, and infrastructure that users interact with BEFORE they run your code.

## Ladder

Same as ponytail, but with one extra rung added at the bottom:

1. **Does this need to exist at all?** (YAGNI)
2. **Already in this codebase?**
3. **Stdlib does it?**
4. **Native platform feature covers it?**
5. **Already-installed dependency solves it?**
6. **Can it be one line?**
7. **Minimum code.**

## Pitfalls (learned the hard way)

### Verify the full chain before declaring done
After writing an install script, doc URL, or config file, verify it works end-to-end:
- `curl -I <url>` to check the file resolves (200, not 404)
- Run the install command in a clean environment (or at least confirm the URL returns the content you expect)
- Check ALL platforms the doc claims to support — if you say Windows, test the Windows path

### REPLACE placeholders
If you reference a URL (raw.githubusercontent.com, docs URL, API endpoint) in a doc or script, verify it exists immediately after pushing. A 404 is not "the CDN is slow" — it's a bug.

### Docs are code
README.md, docs/install.md, and every file the user will see deserve the same verification as source code. If you update one doc file, search for all others that reference the same thing and update those too.

### Multi-platform
- `install.sh` = Linux/macOS
- `install.ps1` = Windows (PowerShell)
- Both must be mentioned in the same quick-start section
- Default install URL must resolve for BOTH before you say "done"

### Private repo trap
raw.githubusercontent.com requires public repos. If the repo is private, every install script URL in every doc returns 404. Always check repo visibility before writing install docs.

## Sequence

1. Write all files (install scripts, docs, CI configs)
2. Commit and push
3. **Verify** — curl every URL referenced in docs, check they 200
4. Check repo visibility — public? If private, all raw URLs break
5. Check all platforms — if you said Windows, validate the .ps1 path
6. Only then declare done
