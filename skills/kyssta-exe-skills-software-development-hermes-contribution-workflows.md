---
name: hermes-contribution-workflows
title: Hermes Contribution Workflows
description: Git/PR/terminal tool patterns for contributing to the Hermes Agent codebase. Covers fork-PR gotchas, terminal atomicity, and patch-tool pitfalls.
---

# Hermes Contribution Workflows

Tool-usage patterns and gotchas when developing or bugfixing Hermes Agent itself.

## Terminal atomicity

**The terminal/filesystem resets between tool calls.** You cannot modify a file in one `terminal()` call and rely on the change persisting to the next `terminal()` call for `git add`/`git commit` — the working tree resets.

**Fix:** Chain ALL operations that depend on file state in a **single** terminal call:

```bash
cd /tmp/hermes-agent
sed -i '...' some_file.py          # modify
git add some_file.py                # stage
git commit -m "..."                 # commit
git push origin branch-name         # push
```

This applies to `sed`, `patch`, and any other file-modifying command plus the git operations that depend on them. Do NOT split across multiple terminal calls.

## Patch tool pagination pitfall

The `patch` tool (find-and-replace) **may silently not persist** when the target file was previously read with offset/limit pagination. If you see:

```
_warning: "... was last read with offset/limit pagination (partial view). Re-read the whole file before overwriting it."
```

the write is unreliable. **Workarounds** (in order of preference):

1. Re-read the file with `read_file(path=..., offset=1, limit=2000)` (no offset) first, then call `patch` again.
2. Use `sed` in a terminal call instead (see Terminal atomicity above — chain everything in one call).
3. Use `write_file` to write the entire file content (last resort, risk of data loss on large files).

## Investigating a referenced PR

When a user drops a PR number in conversation (e.g. `#6471`, `PR #6471`, `[#6471](lnk)`) — especially a closed/unmerged one — first determine whether the changes are **already in the codebase** before reviewing the PR's proposed diff.

```bash
# 1. Fetch PR metadata (title, state, merged status, timeline)
PR_NUMBER=6471
OWNER_REPO=$(git remote get-url origin | sed -E 's|.*github\\.com[:/]||; s|\\.git$||')
curl -s "https://api.github.com/repos/$OWNER_REPO/pulls/$PR_NUMBER" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'Title: {d[\"title\"]}')
print(f'Author: {d[\"user\"][\"login\"]}')
print(f'State: {d[\"state\"]}')
print(f'Merged: {d[\"merged\"]}')
print(f'Body: {(d.get(\"body\") or \"\")[:500]}')
"

# 2. Get the diff to see what code the PR touched
curl -s "https://api.github.com/repos/$OWNER_REPO/pulls/$PR_NUMBER/files" \
  | python3 -c "
import sys, json
for f in json.load(sys.stdin):
    print(f'--- {f[\"filename\"]} (+{f[\"additions\"]}/-{f[\"deletions\"]}) ---')
    print(f.get('patch', '(no patch available)')[:2000])
"

# 3. Search current codebase for the function/variable the PR touches
# Extract function names, guards, patterns from the diff and search
grep -rn "handle_ctrl_d" . --include="*.py" | head -10

# 4. Compare — is the same effect already achieved?
# The installed code may have a different (superset/better) fix from a later PR.
# Report: applied, partially applied (different form), or still needed.
```

**Key questions:**
- Is the PR merged? → fix likely in main.
- Closed but unmerged? → a superset/better version may have landed independently.
- Search for the exact patterns in current code. Compare: same fix? subset? superset? different approach?
- Check the PR timeline for events — `head_ref_force_pushed` means revisions, `closed` vs `merged` tells the story.

**Ponytail/lazy approach:** Before investing time reviewing a PR's proposed changes, check current code. If the fix is already in place with a better approach, report that in one line and stop. No point reviewing diffs against a version that's already moved past them.

## Fork PR creation with `gh`

When creating a PR from a **fork** (not upstream), `gh pr create` requires the `--head` flag:

```bash
gh pr create --repo upstream-owner/repo \
  --title "fix(area): summary (#12345)" \
  --body "Description..." \
  --base main \
  --head your-fork-username:branch-name
```

Without `--head`, you get:
```
aborted: you must first push the current branch to a remote, or use the --head flag
```

**Tip:** Always use `--head <fork>:<branch>` when the branch is on a fork.

## Bug fix = root cause, not symptom

When fixing a bug, grep every caller of the function you're about to touch. Fix it once where all callers route through — a guard in the shared function is a smaller diff than a guard in every caller.

## Verification

After making a change and pushing the branch, verify via one of:

```bash
# Run lint on the changed file
cd /tmp/hermes-agent && python3 -m py_compile hermes_cli/web_server.py

# Check git diff is clean
git diff --stat

# Confirm the change is on the branch
git log --oneline -1
```
