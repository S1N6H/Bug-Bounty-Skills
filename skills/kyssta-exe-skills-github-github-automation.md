---
name: github-automation
description: "GitHub automation patterns, pitfalls, and workflows beyond the core PR lifecycle."
version: 2.3.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, automation, pitfalls, bug-triage, cron]
    related_skills: [github-pr-workflow, github-auth, github-code-review]
---

# GitHub Automation Patterns

Pitfalls, workarounds, and patterns for automated GitHub workflows (cron jobs, bot PRs, bug triage) that go beyond the core PR lifecycle in `github-pr-workflow`.

## Pitfalls

### 0. Default PR queries scope to `--author @me`, not all contributors

When the user asks "how many PRs do we have open" or "list our PRs", the default `gh pr list` returns **every contributor's** open PRs — not just the user's. Always filter by `--author @me` (or `--author <their-login>`) unless the question is about all-authors on the repo.

```bash
# RIGHT — scoped to the user
gh pr list --author @me --state open

# WRONG — shows all 30+ contributors' PRs mixed together
gh pr list --state open
```

**Pitfall — `--author` vs no filter**: Without `--author`, `gh pr list` returns PRs from ALL authors in the repo. Even with `--limit 200`, a repo with 500+ open PRs returns the 200 most recently created, which may include zero PRs from the target user. Always filter by `--author <user>` when the task is about one person's PRs. (Full stale-cleanup guidance with batch-close workflows is in the "Stale & Duplicate PR Cleanup" section below.)

### 1. Backticks in `gh pr create --body` break shell

Markdown inline code (`` `like this` ``) uses backticks that bash interprets as command substitution. This causes cryptic errors like `command not found` for each backtick-enclosed token.

**Fix:** Write the body to a temp file, then pass `--body-file`:

```bash
cat > /tmp/pr-body.md << 'HEREDOC_END'
## Summary
Fixes the `model.options` endpoint not returning custom provider models.

Closes #1234
HEREDOC_END
gh pr create --title "fix: ..." --body-file /tmp/pr-body.md
```

Use a single-quoted heredoc delimiter (`'HEREDOC_END'`) to prevent all shell expansion. This is strongly preferred over escaping backticks.

### 2. Checking if a bug fix is already on upstream/main

When investigating GitHub issues to determine if they're already fixed, don't just check if a branch exists — verify the fix is actually merged into upstream/main.

The single most reliable check:

```bash
git merge-base --is-ancestor <commit-sha> origin/main && echo "MERGED" || echo "NOT MERGED"
```

**Do NOT** rely on `git log origin/main --oneline --all | grep <issue>` — `--all` includes EVERY ref (local branches, fork remotes), not just origin/main, giving false positives.

### 3. Multi-Branch Fix Audit (Reconciliation)

When auditing a list of fix branches against upstream/main — checking merge status, open PRs, and exact commit SHAs — use this systematic workflow:

**Step 1: Gather commit SHAs**

Check each branch locally, then check the fork remote (branches often live only on the contributor's fork):

```bash
for b in fix-branch-1 fix-branch-2; do
  echo "=== $b ==="
  git log -1 --format="%H %s" "$b" 2>&1 || echo "NOT FOUND locally"
  git log -1 --format="%H %s" "fork/$b" 2>&1 || echo "NOT FOUND on fork"
done
```

**Step 2: Verify merge status**

```bash
for sha in <sha1> <sha2>; do
  git merge-base --is-ancestor "$sha" origin/main && echo "MERGED" || echo "NOT MERGED"
done
```

**Step 3: Find direct PR by branch name**

```bash
gh pr list --head <branch-name> --state all --json number,headRefName,state,title,mergedAt
```

Empty array `[]` means no PR exists under that exact branch name.

**Step 4: Broaden search — find ALL PRs by issue number**

The same bug may have several competing PRs under different branch names. Search by issue number:

```bash
gh pr list --repo <owner>/<repo> --search "#<issue-number>" --state all --json number,title,state,headRefName
```

This surfaces alternative approaches and cherry-pick attempts.

**Step 5: Check alternate versions (v2, clean-, cherry-pick/)**

If alternate branches exist (e.g. `-v2`, `clean-`, `cherry-pick/`), compare them:

```bash
git diff branch-name..branch-name-v2 --stat
git merge-base --is-ancestor <orig-sha> branch-name-v2 && echo "v2 builds on original" || echo "different approach"
gh pr list --head branch-name-v2 --state all --json number,state
```

**Step 6: Check upstream remote**

```bash
for b in branch-1 branch-2; do
  git log -1 --format="%H %s" "upstream/$b" 2>&1 || echo "NOT on upstream"
done
```

**Pitfalls:**
- **`gh pr list --head <branch>` returns `[]` but the fix still has a PR** — the PR may be under a different branch name (e.g. `fix/60089-memory-replace` vs `fix-memory-replace-duplicate-60089`). Always broaden to `gh pr list --search "#<issue>"`.
- **`cherry-pick/` PRs in CLOSED state** (e.g. `cherry-pick/60044`, `cherry-pick/60150`) suggest upstream picked the fix into a different PR or branch. Investigate the closure reason.
- **A branch on the fork remote does NOT mean it's on the upstream remote.** Only the fork has it until a PR is created.
- **Many competing PRs for the same issue** indicate the fix hasn't been finalized. Multiple open PRs for the same issue number is a strong sign nothing has been merged yet.
- **`mergedAt: null` on the PR JSON** means the PR hasn't been merged, even if the branch exists. Cross-check with `merge-base --is-ancestor`.
- **`gh search prs` has a different JSON field set than `gh pr list`.** `gh search prs --json number,state,title` works, but `headRefName` is NOT an available field in search results — use `gh pr list --head` or `gh pr list --search` instead for branch names.
- **Compile results into a table** with columns: branch name, merged? (yes/no/partial), open PR? (number or none), commit SHA of fix. This makes the state clear at a glance.

### 4. Fork-based PR workflow for cron jobs

When running as a cron job that creates PRs on someone else's repo:

1. Fork the repo: `gh repo fork <owner>/<repo> --clone --depth 1`
2. Add upstream remote: `git remote add upstream https://github.com/<owner>/<repo>.git`
3. Fetch upstream: `git fetch upstream main`
4. Create branch from upstream/main: `git checkout -b fix/<description> upstream/main`
5. Make changes, commit
6. Push to the fork (not upstream origin):
   ```bash
   # Push to the fork remote (default: origin after fork clone)
   git push -u origin HEAD
   
   # But if you renamed origin to fork to avoid confusion:
   git remote rename origin fork
   git remote add origin https://github.com/<owner>/<repo>.git
   git push -u fork HEAD
   ```
7. Create PR with the fork's user/org as the head ref:
   ```bash
   # When working from the fork (default remote is origin pointing to fork):
   gh pr create --repo <owner>/<repo> --head <your-username>:<branch> --base main \
     --title "fix: ..." --body "..."
   
   # When the fork is under a different remote name:
   gh pr create --repo <owner>/<repo> --head <your-username>:fix/description --base main \
     --title "fix: ..." --body "..."
   ```

**Pitfall:** The fork remote is usually named `origin` after cloning. If you also need the upstream as `origin` for fetch/pull, rename:
```bash
git remote rename origin fork
git remote add origin https://github.com/<owner>/<repo>.git
```
Then push to `fork` and create PR with `--head your-user:branch-name`.

**Pitfall:** `gh pr create` without `--head` defaults to `--head current-branch` which only works when the branch is on the same repo. For fork-based PRs, `--head USER:BRANCH` is **required**. Omitting it causes a 422 error: `"No commits between <owner>:main and <owner>:<branch>"`.

## Bug Triage Workflow

When scanning GitHub issues for fixable bugs:

1. **Check if already fixed:** Search commit history for the issue number, verify with `git merge-base --is-ancestor`
2. **Check for existing PRs:** `gh pr list --repo <owner>/<repo> --state all --search "<issue-number>"` — use `--state all` (not just `open`) to catch closed/cherry-pick PRs. To catch multiple reference styles, broaden the search query:
   ```bash
   gh pr list --repo <owner>/<repo> --state open --search "fix(#<issue>) OR #<issue> OR issue #<issue>"
   ```
   This catches `fix(#42)`, `Closes #42`, and bare issue references in PR titles.
3. **Pre-filter candidates against existing PRs before starting any fix:** When given a list of bug candidates (e.g. top 10 from a pre-run script), batch-check ALL of them for existing PRs first. This avoids wasted investigation on issues that already have a fix in flight. Loop over all candidates:
   ```bash
   for issue in 60808 60802 60795 60784; do
     echo "=== Issue #${issue} ==="
     gh pr list --repo <owner>/<repo> --state open --search "fix(#${issue}) OR #${issue} OR issue #${issue}" \
       --json number,title,state,headRefName,url
   done
   ```
   Use a broad search query (`"fix(#N) OR #N OR issue #N"`) to catch all referencing styles — `fix(#42)`, `Closes #42`, bare `#42`, and `issue #42` in PR titles. Only investigate candidates that return `[]` (no existing PRs). Prioritize fixes for candidates where no PR exists. Report skipped candidates briefly.

   **Pitfall: The pre-run script's dedup is weaker than `gh pr list --search`.**
   The script typically checks only for PRs formally cross-referenced in the issue's Development section (Linked PRs). This catches PRs whose descriptions say `Fixes #N` or `Closes #N`, but misses PRs that merely mention `#N` in the title or body without being formally linked. In practice, 50-100% of "new" candidates from a script can have existing PRs that a `gh pr list --search` finds. Always treat the script's "new" label as provisional and always run the secondary `gh pr list --search` loop --- even when every single candidate turns out to have a PR, that's a correct signal that nothing new needs fixing, not wasted work.

   **Go deeper: `gh search prs` finds PRs that `gh pr list --search` misses.**
   `gh pr list --search "#N"` only searches PR titles. PRs that reference an issue in the body but not the title can slip through. `gh search prs --repo OWNER/REPO "fixes #N" --json number,state,title` searches across titles, bodies, and comments --- catching PRs that `gh pr list` never surfaces. In one session this tool found 5 open PRs for an issue where `gh pr list --search` found 1.

   **Pitfall: `created_prs.json` cache may be empty despite previous work.**
   If the cache at `~/.hermes/cache/auto-fix-bugs/created_prs.json` is missing, previous runs may still have fix branches on the fork remote. Check for them before creating new branches: `git branch -r | grep auto-fix/issue-N`. If found, these branches have existing fixes that were never PR'd --- either PR them or verify they are superseded.

4. **Assess fixability:**
   - Code changes in Python/TypeScript → likely fixable
   - Hardware-specific (Retina, specific GPU) → skip
   - UI rendering issues → may need investigation
   - Complex networking/recovery → likely too risky for automated fix
   - Already-fixed-on-main → skip

5. **Prioritize:** Simple, clear fixes (config changes, missing entitlements, ANSI enablement) > complex refactors

6. **Deep dive when surface candidates are exhausted:** If the top 10 candidates ALL already have PRs, do NOT simply stop — there is still productive triage work to do:
   - **Cross-reference same-root-cause issues:** For each candidate, read the issue body and compare to the linked PR's description. If the root cause is identical to an already-PR'd issue, add a cross-reference comment on the issue linking to the existing PR. This saves a human triager from re-investigating.
     ```bash
     gh issue comment <issue-num> --body "This is the same underlying bug as #<existing-issue> — PR #<existing-pr> already addresses it."
     gh pr comment <existing-pr> --body "This PR also fixes #<new-issue> (same root cause). Cross-referencing."
     ```
   - If the root cause differs from the existing PR (different symptom, different code path), it's genuinely new — proceed to fix it with its own branch/PR.
   - **Batch-check deeper** — extend the search to 30+ additional bugs for existing PRs using a shell loop:
     ```bash
     gh issue list --repo <owner>/<repo> --label bug --state open --limit 50 --json number | jq -r '.[].number' \
     | while read n; do
       count=$(gh pr list --repo <owner>/<repo> --state all --search "$n" --json number --jq 'length' 2>/dev/null)
       [ "$count" -eq 0 ] && echo "NO PRs for #$n" || echo "Has $count PR(s) for #$n"
     done
     ```
   - Focus on issues without any PRs. Discard vague/empty bugs (no title, no repro steps, purely environmental).
   - Issues with detailed root cause analysis already in the body are high-value targets.
   
   **Pitfall: verify the bug's described code actually exists.** Before attempting a fix, check whether the functions, types, and files mentioned in the issue body exist in the current `upstream/main`. Issues may reference code that was refactored or removed — `tokenSpeedLabel` in a renamed file, a `tokens_per_second` field that was never added, etc. If the described code path doesn't exist, the issue is a feature request or stale, not a fixable bug. Run `git log --all -S "<function-name>"` to verify.

7. **Revert archaeology — re-implementing reverted features:** Sometimes the best fix is re-implementing a feature that was merged and reverted, because the revert fixed one broken path but removed a working capability:
   - Find all commits touching a file to discover revert history:
     ```bash
     git log --oneline --all -- <file>
     ```
   - Look for "Revert" commits following "Merge pull request" commits. Cross-reference the timeline: was the issue filed while the feature was live?
   - Read the original commit to understand what was added and why the revert triggered.
   - The revert is often a blanket removal — the CLI path worked fine but the gateway path was broken (e.g. used `submit_pending()` instead of `_await_gateway_decision()`).
   - Re-implement the feature, fixing the broken path that caused the revert. This is safer than writing from scratch because the working paths were already CI-verified.
   - One-line summary: **the revert fixed one broken path but deleted a working feature — re-implement the feature with the broken path fixed.**

8. **Validate test failures before fixing:** When tests fail in CI or under `pytest -n auto` (xdist parallel), re-run each failing test individually before assuming a real bug:
   - Run `python -m pytest -x -v --tb=long <test_path>::<test_name>` to isolate
   - If the test passes individually, the failure was a **parallel-isolation artifact** (shared state, temp-path races, async fixture conflicts), not a code bug — skip it
   - If the test still fails individually, investigate the code. Use `read_file` + `patch`/`write_file` for fixes, then re-verify
   - Docker/infra test failures (BuildKit missing, daemon not running, network timeout) are environmental — skip unless you can fix the Dockerfile or CI config
   - This prevents wasted effort chasing xdist-ordering bugs and fixture-leak failures

9. **Verify the described code actually exists:** Before attempting a fix described in a GitHub issue, check whether the functions, types, and files mentioned in the issue body exist in the current `upstream/main`. Issues can reference code that was refactored, renamed, or removed between the filing date and now:

   ```bash
   # Check if a function/class exists in the file's current version
   grep -n 'def tokenSpeedLabel' apps/desktop/src/app/shell/statusbar-controls.tsx

   # Check git history for the function to understand if it was renamed/moved
   git log --all -S 'tokenSpeedLabel' --oneline | head -5
   ```

   If the described code path doesn't exist, the issue may be a feature request, stale, or already partially addressed — skip it rather than implementing something that doesn't match the issue's intent. Also check whether an existing PR already addresses it:

   ```bash
   git log --oneline upstream/main --all --grep='#<issue-number>' | head -5
   ```

10. **Verify changes compile before creating the PR:** Before committing and pushing, run a compilation check on every modified file:
   ```bash
   python3 -c "
   import py_compile
   for f in ['path/to/file1.py', 'path/to/file2.py']:
       py_compile.compile(f, doraise=True)
       print(f'{f}: OK')
   "
   ```
   This catches syntax errors and import issues that would cause CI to fail immediately. For TypeScript/JS changes, run `npx tsc --noEmit` on the affected files.

11. **Update tests when the fix changes a data-flow mechanism:** If a fix changes HOW a function delivers data (e.g. source of truth moves from a temp file to a stdout marker, or from an attribute to a method return), the tests that mock the old mechanism must be updated to simulate the new one. Run the affected test suite before committing:
    ```bash
    python3 -m pytest tests/path/to/test_file.py -x -v --tb=short
    ```
    A green run confirms both the fix and test updates are correct. Failing to update tests causes the PR to be blocked by CI despite a correct fix.

12. **Create focused PRs:** One fix per PR (unless multiple issues are trivially related or in the same file). Use a clear commit message referencing the issue number. The PR body should explain WHAT the fix does and WHY the issue was happening.

13. **Error-message-only fix is a valid auto-fix outcome**

When the root cause of a bug is **server-side** — an OAuth provider invalidating tokens early, a rate-limiter changing behavior, a billing classifier acting differently — there is no Hermes-side logic change to make. The correct auto-fix in this case is improving the error message so the user understands what happened and knows what to do next.

**Signals this applies:**
- The error comes from an external API/provider response, not a code path in Hermes
- The stored tokens/credentials look valid but the server rejects them anyway
- A token refresh is attempted but fails with the same server error (server invalidated both access and refresh tokens)
- The existing error message is misleading or only covers one narrow cause

**What to change:**
- Broaden the explanation to cover both the original hypothesis AND the server-side possibility
- Keep the re-auth instructions actionable and syntactically correct — `hermes auth add <provider>` (not bare `hermes auth <provider>`, which is invalid)
- No logic changes, no test changes — just the user-facing message. This is still a valid bug fix: fixing incorrect guidance is fixing a bug.

**Pitfall — wrong re-auth command syntax in error messages:** The correct CLI command to re-authenticate a specific provider is `hermes auth add <provider>` (e.g. `hermes auth add openai-codex`). Do NOT write `hermes auth <provider>` (e.g. `hermes auth openai-codex`) — `hermes auth` without a subcommand runs the interactive auth flow, and `hermes auth openai-codex` produces a syntax error: `argument auth_action: invalid choice: 'openai-codex'`. Always test the command you documented.

## AUTO-FIX-BUGS Cronjob Configuration

The AUTO-FIX-BUGS cronjob runs every 90 minutes against `NousResearch/hermes-agent`. It uses a Python script at `/root/.hermes/scripts/auto-fix-bugs.py` to fetch bug candidates, then the agent picks from them and creates PRs.

### Script flow

1. **Fetch candidates** from three sources:
   - GitHub issues labeled `bug` (default: `--limit 30`)
   - `TODO`/`FIXME`/`BUG`/`XXX` grep hits (capped at 50 lines, deduped via `seen_bugs` cache)
   - Failing `pytest` output (first 100 lines)

2. **Deduplicate** each issue against:
   - Open PRs that reference it (scans up to 200 open PRs)
   - Our own `created_prs.json` cache (issues already fixed in previous runs)
   - Whether the issue itself is already closed
   - **Title-based dedup** (`get_kyssta_open_prs()` + `title_overlaps()`): Fetches all open PRs by `kyssta-exe` and checks word-level overlap (≥60%) against each candidate's title/body. Catches duplicates with no issue number — same CVE bump, same temp-file fix, same config bridge. Runs after other dedup so issue-linked duplicates are caught first.
   - **Closed-PR check**: Before marking a candidate "new", runs `gh pr list --author kyssta-exe --state all --search "#ISSUE_NUMBER"` to see if the same user already submitted a PR (even closed/unmerged) for that issue. Prevents re-creating a fix whose PR was closed without merge.

3. **Output** top N new candidates via stdout and `/tmp/bug_candidates.json` (default: `20`)

### Tuning knobs

The script has three key limits that control how many PRs each run produces:

| Parameter | Location | Default | Effect |
|-----------|----------|---------|--------|
| `--limit` on `gh issue list` | Line ~266 | `30` | How many open bug-labelled issues to scan |
| `new_bugs[:N]` on output | Lines ~346, ~353 | `20` | How many candidates the agent sees per run |
| `--limit` on `gh pr list` (dedup) | Line ~83 | `200` | How many open PRs to scan for dedup references |

To increase PR output: raise the candidate slot (`new_bugs[:N]`) and the issue fetch limit together. Always raise the PR dedup scan proportionally so existing work isn't re-done.

### Cache files

| File | Purpose |
|------|---------|
| `~/.hermes/cache/auto-fix-bugs/created_prs.json` | History of PRs this run created — prevents duplicate PRs for same issue |
| `~/.hermes/cache/auto-fix-bugs/seen_bugs.json` | Seen TODO/FIXME markers — prevents re-emitting the same code-comment bugs |
| `/tmp/bug_candidates.json` | Latest output file the agent reads on each run |

### Usage pattern

When the user asks to "increase PR output" or "fix more bugs":

1. Raise the candidate slot (`new_bugs[:N]`) in the script — this is the most direct control.
2. Raise the issue fetch limit so more raw candidates exist to filter.
3. Raise the PR dedup scan so the new slot doesn't waste effort on already-PR'd issues.
4. Verify via `/tmp/bug_candidates.json` after next run that total_new increased.

Do NOT reset `created_prs.json` in normal operation — it's the memory of what's already been PR'd. Reset only when explicitly clearing the slate.

**Pitfall: the cache may silently get cleared between runs.** If `created_prs.json` is missing or empty, previously created fix branches may still exist on the fork remote. Check `git branch -r | grep "auto-fix/issue-NUMBER"` before recreating work. Also note that `gh search prs --repo "fixes #N"` can find PRs the cache didn't track.

### Agent prompt dedup guard

The cron job's agent prompt includes a **Step 3** that the agent must run BEFORE creating any PR. The step instructs the agent to:

```
gh pr list --repo <owner>/<repo> --author <user> --state open --json title
```

and compare each returned title against what it's about to submit. If any open PR title substantially overlaps (same component prefix, same topic, same fix), the agent skips the candidate. This catches cases the script-level dedup missed:
- A PR was opened while the script was running
- The candidate has no issue number (code-comment/CVE fixes)
- The title overlap function in the script didn't match but the agent can see it clearly

**Pitfall: prompt regeneration can drop this step.** If someone regenerates the prompt from scratch, the dedup step won't be in the default template. It must be explicitly added between the analysis step and the create step (positioned as Step 3 in a 6-step sequence).

## Platform Guards Need Platform Checks

When adding a platform-specific guard (`os.geteuid()`, `sys.platform`, feature-detection), gate it with the platform check first — otherwise it fires on every OS during testing.

**Case in point:** Adding `if os.geteuid() == 0:` to `launchd_install()` without `is_macos()` caused all launchd tests to fail because CI runs as root on Linux. The fix: `if is_macos() and os.geteuid() == 0:` keeps the guard macOS-only.

**Pattern:**
```python
# WRONG — fires on every OS during root-run test CI
if os.geteuid() == 0:
    sys.exit(1)

# RIGHT — only blocks the specific broken path
if is_macos() and os.geteuid() == 0:
    sys.exit(1)
```

This matters most for functions that are:
- Named after a platform (e.g., `launchd_install`, `is_macos`)
- Tested on all OSes in CI (monkeypatched platform checks are common in tests)
- Called from shared code paths where different OSes branch before or after

Tests that monkeypatch platform checks (e.g., `monkeypatch.setattr(module, 'is_macos', lambda: True)`) are fine — but if the guard uses `os.geteuid()` directly without a platform gate, it still breaks on Linux root CI where the test doesn't expect a guard at all.

## Automated PR Quality Standards

When a cron job or agent workflow creates PRs autonomously, each PR must be review-ready — compiles, follows the repo's conventions, and is self-contained. These standards prevent the common rejection patterns observed on high-volume repos (~50 PRs/day) where maintainers triage by checklist.

### 1. Always fill in the repo's PR template

Before composing the PR body, check whether the repo has a template:

```bash
ls -la .github/PULL_REQUEST_TEMPLATE.md .github/PULL_REQUEST_TEMPLATE/ 2>/dev/null || echo "No template found"
```

If found, **fill in every section** — "Type of Change", "Checklist", "How to Test". A half-blank template wastes maintainers' time and signals the PR was not human-reviewed. Template checklist items like "I have added tests" and "I have updated the documentation" should be checked off honestly, not blindly.

If no template exists, use `github-pr-workflow`'s `templates/pr-body-bugfix.md` or `templates/pr-body-feature.md`.

### 2. Check for existing PRs on the same issue before creating

Before starting a new PR, verify no open PR already addresses the same issue:

```bash
COUNT=$(gh pr list --repo <owner>/<repo> --state open --search "<issue-number>" --json number --jq 'length' 2>/dev/null || echo 0)
if [ "$COUNT" -gt 0 ]; then
  echo "WARNING: $COUNT open PR(s) already exist for this issue — skipping"
  gh pr list --repo <owner>/<repo> --state open --search "<issue-number>" --json number,title,headRefName
fi
```

If existing PRs are found, do not create a duplicate:
- If the existing PR looks correct → leave it alone
- If the existing PR is stale or wrong → add a review comment with the fix suggestion instead of creating a competing PR
- If the existing PR is from an earlier run of the **same** cron job → close the older PR with "Superseded by #NEWPR" and create the new one, but only when both are from the same bot

### 3. One fix per PR, one PR per issue

Each PR must fix exactly one issue. A PR whose description says "Fixes #X" but also patches an unrelated function for a separate bug will be blocked until the second fix is extracted.

**Self-review gate before push:**

```bash
git diff origin/main...HEAD --stat
```

Scan every changed file. If any change is unrelated to the primary issue, revert it and open a separate PR. Exception: trivial adjacent cleanups in the same file (comment typos, whitespace next to the real change) may stay — they don't warrant their own PR.

### 4. Regenerate lockfiles after manifest changes

After editing `pyproject.toml`, `Cargo.toml`, `package.json`, `Gemfile`, or any manifest with a lockfile companion (`uv.lock`, `pnpm-lock.yaml`, `Cargo.lock`, `Gemfile.lock`), the lockfile **must** be regenerated and committed. Without it:

- Install commands (`uv sync`, `pnpm install`) still resolve the old versions
- The manifest and lockfile disagree — an immediate CI or reviewer catch

```bash
# After editing pyproject.toml
uv lock
git add pyproject.toml uv.lock
```

If you cannot run the lockfile tool (wrong arch, missing runtime), note it in the PR body and flag the missing lockfile as a reviewer action item.

### 5. SQL correctness: ORDER BY before LIMIT 1

When querying for "the most recent" record, `LIMIT 1` without `ORDER BY` returns an **arbitrary** match — not the latest. This is a recurring source of subtle bugs in automated database patches:

```sql
-- WRONG: picks any historical completed run, even from last year
SELECT 1 FROM task_runs WHERE task_id = ? AND outcome = 'completed' LIMIT 1;

-- RIGHT: scopes to the latest completed run
SELECT id, outcome FROM task_runs
WHERE task_id = ? AND outcome = 'completed'
ORDER BY ended_at DESC LIMIT 1;
```

Always include `ORDER BY <timestamp_col> DESC` when the intent is "most recent." Bare `LIMIT 1` is only correct when any match is equally valid (existence checks against a unique constraint).

### 6. Self-review the full diff before push

Final gate before committing:

```bash
git diff origin/main...HEAD --stat   # summary of files changed
git diff origin/main...HEAD          # full diff
```

Check: Does every changed line belong to this fix? Are there debug prints, commented-out code, or formatting-only changes unrelated to the issue? Is the diff minimal — one fix, one commit, clean?

### 7. Avoid Unicode corruption when using the patch tool

The `patch` tool (Hermes's find-and-replace edit tool) can corrupt non-ASCII Unicode characters. When your `old_string` or `new_string` contains characters outside the ASCII range (e.g. em dashes `—`, accented letters `éçã`, curly quotes `" "`), the tool may convert them into escaped sequences like `\u2014` or produce encoding mismatches.

**Prevention:**
- Keep `old_string` and `new_string` purely ASCII when possible. Replace non-ASCII characters with their ASCII equivalents (e.g. `--` for `—`, straight quotes `"` for curly quotes).
- If you must include a non-ASCII character, verify the diff output immediately after the patch. Run `git diff <file>` to check for unexpected changes in unrelated lines.
- If the patch corrupted a nearby line (e.g. the tool swapped a `—` for `\u2014` in a string literal), fix it with a second targeted patch:
  ```bash
  # Restore original character if corrupted
  patch --path path/to/file \
    --old_string 'tab \\u2014 the rest' \
    --new_string 'tab \u2014 the rest'
  ```
  (Use the actual UTF-8 character in new_string, not the escape sequence.)

**Detection:** After every `patch` call, scan the diff for Python-like escape sequences (`\u2014`, `\xe9`) that appear in places where the original file had human-readable text. These are corruption artifacts.

## Stale & Duplicate PR Cleanup

When a user has accumulated 100+ open PRs (especially from an auto-fix pipeline), run a comprehensive stale sweep — not just duplicate-labeled ones.

### Step 0: Scope to the right author first

**Critical — get this wrong and you'll close other people's PRs.** When the user says "my PRs" or shows you a repo, confirm whether they mean ALL PRs or only theirs. If theirs, filter immediately:

```bash
# Get the true total — NOT just the default 30-page
gh pr list --repo <owner>/<repo> --state open --author <user> --limit 200 --json number --jq 'length'
```

The default `gh pr list` limit is 30 — if the user has 120+ PRs, you silently see only the first 30. `--limit 200` catches everything. After getting the total, sort by creation date to identify the tail:

```bash
gh pr list --repo <owner>/<repo> --state open --author <user> --limit 200 --json number,createdAt | \
  python3 -c "import json,sys; prs=json.load(sys.stdin); prs.sort(key=lambda x:x['createdAt']); print(f'Oldest: {prs[0][\"number\"]} ({prs[0][\"createdAt\"][:10]})'); print(f'Newest: {prs[-1][\"number\"]} ({prs[-1][\"createdAt\"][:10]})')"
```

**Pitfall — `--author` vs no filter**: Without `--author`, `gh pr list` returns PRs from ALL authors in the repo. A `--limit 200` query on a repo with 500+ open PRs returns the 200 most recently created, which may include zero PRs from the target user. Always filter by `--author <user>` when the task is about one person's PRs.

### Step 1: Identify stale PRs (beyond duplicates)

Stale = any PR that has been open for more than ~2 days with no merge activity:

- **No reviews at all** → likely untouched
- **Review asked for changes that were never addressed** → abandoned
- **Multiple versions of the same fix exist** → superseded chains (3+ attempts at the same issue)
- **Self-duplicates** in auto-PR pipelines: same fix, same author, multiple branch names
- **Age > 3 days** with no merge → strong stale signal

```bash
# Quick freshness check
gh pr list --repo <owner>/<repo> --state open --author <user> --limit 200 --json number,createdAt,title,reviews | \
  python3 -c "
import json,sys; prs=json.load(sys.stdin)
for p in prs:
    review_count = len(p.get('reviews',[]))
    print(f'#{p[\"number\"]} ({p[\"createdAt\"][:10]}) reviews={review_count} {p[\"title\"][:50]}')
"
```

**Recognising superseded chains**: The auto-fix pipeline often creates 3+ versions of the same fix (e.g. `fix(acp): honor approvals.timeout` → #63484, #63689, #64030). The newest one is the keeper; the older ones are dead weight. Identify them by matching title keywords (same `(scope):` prefix and same issue number), then close all but the newest.

### Step 2: Batch-close from oldest to newest

When closing 50-100+ PRs, **close from the oldest end first** — this avoids hitting the auto-pipeline as it creates new PRs mid-cleanup:

```bash
# Get all PRs sorted oldest-first, skip the N most recent, close the rest
python3 -c "
import json, subprocess
result = subprocess.run([
    'gh', 'pr', 'list', '--repo', 'owner/repo', '--state', 'open',
    '--author', 'user', '--limit', '200', '--json', 'number,createdAt'
], capture_output=True, text=True)
prs = json.loads(result.stdout)
prs.sort(key=lambda x: x['createdAt'])
total = len(prs)
# Keep the 10 most recent
to_close = prs[:-10]
print(f'Closing {len(to_close)} of {total}...')
for pr in to_close:
    subprocess.run(['gh', 'pr', 'close', str(pr['number']),
        '--repo', 'owner/repo',
        '--comment', 'Stale — oldest open PR, no merge activity for weeks.'],
        capture_output=True, timeout=5)
"
```

**Pitfall — the auto-pipeline keeps creating new PRs during cleanup**: While you close old PRs, the pipeline may create fresh duplicates of just-closed ones (respawn). If you started from the newest end, new PRs appear at the top and you chase a moving target. Starting from the oldest avoids this — you clean the tail while fresh PRs accumulate at the head, which you keep by design.

### Step 3: Verify final state

```bash
gh pr list --repo <owner>/<repo> --state open --author <user> --limit 200 --json number --jq 'length'
```

If the count is still high (30+), there may be a paging issue or more old PRs hidden by the `--limit`. Run a paginated sweep:

```bash
for page in 1 2 3 4 5; do
  gh pr list --repo <owner>/<repo> --state open --author <user> --limit 100 --json number -p $page --jq '.[].number'
done | sort -n | head -3 && echo "..." && wc -l
```

This catches PRs beyond the first 200 by paging through results.

## Duplicate PR Triage

When asked to "close duplicate PRs" or seeing PRs labelled `duplicate`, follow this systematic workflow to identify true duplicates and close them properly.

### Step 1: Find duplicate-labelled PRs

```bash
# List all open PRs with their labels, timestamps, authors
# IMPORTANT: default --limit is 30, use 200+ to see everything
gh pr list --state open --limit 200 --json number,title,headRefName,createdAt,author,labels,url,state,mergeable
```

Scan for the `duplicate` label (description: "This issue or pull request already exists", color: `cfd3d7`).

**Pitfall — default limit hides PRs:** `gh pr list` defaults to **30 results**. If a user/repo has more than 30 open PRs, you silently see only the first page. A user with 60+ PRs means half are invisible without `--limit 200`. Always set an explicit limit for comprehensive sweeps.

**Pitfall — terminal output truncation:** The terminal tool caps output at ~80K chars. A JSON dump of 60+ PRs with label arrays, comment objects, and URLs can exceed this. The array mutilates silently — you see a partial list and think that's all. Mitigations:
- Filter by `--author <user>` to narrow the set before expanding details
- Pass `--json` with only the fields you need in pass 1 (`number,title,labels`); drill into individual PRs with `gh pr view` in pass 2
- Use Python post-processing (`| python3 -c "import json,sys; data=json.load(sys.stdin); print(f'Total: {len(data)}')"`) to confirm you got everything

### Step 2: Verify each duplicate

For each PR with the `duplicate` label, confirm it's a genuine duplicate before closing:

**Check A — Same author, same fix, multiple PRs:**
```bash
# Search for PRs from the same author with similar titles
gh pr list --state open --search "<title-keywords>" --json number,title,createdAt,author
```

If the same author opened 2–3 PRs for the same fix, the later ones are duplicates. Keep the earliest by `createdAt`.

**Check B — Multiple authors racing on the same fix:**
```bash
# Search for related PRs by topic
gh pr list --state all --search "<topic>" --json number,title,state,createdAt,author
```

The PR with the earliest `createdAt` is the original; later ones are duplicates.

**Check C — PR references an issue that already has a fix:**
```bash
gh issue view <issue-number> --json title,state 2>/dev/null
gh pr list --state all --search "#<issue-number>" --json number,title,state
```

If multiple PRs reference the same open issue, the fix hasn't been finalized — the duplicate label may be premature. Investigate further before closing.

**Check D — Questionable label application:**
If a PR has high-quality investigation (binary search, reproduction steps, test results) but is labelled `duplicate`, verify by checking whether the earlier PR actually works. Sometimes the label was applied incorrectly — the earlier PR may be stale, abandoned, or have a different approach. Use `gh pr view <number>` to compare both.

### Step 3: Close duplicates with a clear comment

```bash
# When closing your own PR (author matches authed user)
gh pr close <number> --comment "Closing as duplicate of #<original> (same author, submitted later)."

# When closing someone else's PR (need repo write access)
gh pr close <number> --comment "Closing as duplicate — this fix is already addressed in #<original>."
```

**Comment templates by scenario:**

| Scenario | Comment |
|----------|---------|
| Same author, same fix | "Closing as duplicate of #N (same author, same fix — submitted later)." |
| Same author, 3+ attempts | "Closing as duplicate — you already have #N and #M open for the same fix. Keeping the earliest." |
| Different author, same topic | "Closing as duplicate — this fix is already addressed in #N and #M. Thanks for the investigation though." |
| Already covered by merged PRs | "Closing as duplicate — this is already covered by earlier merged PRs." |

### Step 4: Handle close failures

If `gh pr close` fails, read the error:

```
API call failed: GraphQL: <user> does not have the correct permissions to execute `ClosePullRequest`
```

This means the authed GitHub user is NOT a repo collaborator. A non-collaborator can only close their own PRs. For PRs from other authors, report the results and escalate to a maintainer — don't keep trying.

```bash
# Check what user you're authed as
gh auth status
```

### Pitfalls

**1. A `duplicate` label may be applied incorrectly**

Always verify before closing. Read both PR bodies — the later PR may actually have a better approach than the earlier one it supposedly duplicates.

**2. `gh pr list --head <branch>` returns empty for existing PRs**

The PR may be under a different branch name. Always broaden to `gh pr list --search "#<issue>"` or search by title keywords.

**3. Multiple open PRs for the same issue means the fix isn't finalized**

If 3+ PRs exist for the same issue, maintainers haven't decided which approach to merge. Only close clear same-author self-duplicates in this scenario — don't remove competing valid approaches from different contributors.

**4. Only hash (`#`) references are accepted in `gh pr list --search`**

`gh pr list --search` requires `#<number>` (not bare `<number>`) for issue/PR number searches. For topic searches, use `--search "<topic>"`.

**5. Stale PR state in `gh pr list` after closing**

After `gh pr close` succeeds, a subsequent `gh pr list` may still show the PR as open for up to a few seconds (GitHub cache). If a PR appears open in the list but you just closed it, verify with:

```bash
gh pr view <number> --json state
```

This queries the single-PR endpoint which is always fresh. Don't re-close a PR that already closed — the error is harmless but wastes a round-trip.

**6. Batch close loop for many duplicates (30+)**

When closing many duplicate PRs, parallelize in batches of 6 (the terminal tool supports concurrent `gh pr close` calls). After all batches, run a single verification pass:

```bash
# Count remaining duplicates in one call
gh pr list --state open --author <user> --limit 200 --json number,labels | \
  python3 -c "import json,sys; data=json.load(sys.stdin); dups=[p for p in data if 'duplicate' in [l['name'] for l in p['labels']]]; print(f'{len(dups)} duplicates left'); [print(f'  #{p[\"number\"]}') for p in dups]"
```

If any remain, close them in another batch. Loop until zero. One verify call beats checking between every close batch.

**7. Auto-PR pipeline recreates PRs during cleanup**

Some repos have automated fix bots that spawn new PRs continuously. During a cleanup session, you may close PR #64095 only to see #64128 (same fix, same author) appear minutes later. **Do not chase new arrivals** — they will keep coming. Instead:

- Close from the **oldest end** first. The oldest PRs are stable — they won't be recreated.
- Reserve the newest slots (last 10-15) as a "keep buffer" that you never touch.
- After cleaning the tail, verify count. If it's stable (same count after 5 minutes), the pipeline has caught up.
- If the count keeps rising despite closures, the pipeline outruns manual cleanup — tell the user and stop. Continuing is a losing battle; the pipeline needs a config change, not more closes.

**8. `gh pr list --author <user>` still defaults to 30 results**

Even with `--author`, `gh pr list` silently pages at 30 without an explicit `--limit`. If the user has 120 PRs, `gh pr list --author user` returns only 30. Always add `--limit 200` (or `--limit 100` per page in a loop) for any comprehensive sweep. Verify you got everything with a length check:

```bash
TOTAL=$(gh pr list --repo owner/repo --state open --author user --limit 200 --json number --jq 'length')
echo "Total open: $TOTAL"
# If $TOTAL is exactly 200, you hit the limit ceiling — there may be more


## Multi-Fix Sweep Workflow

When an automated session produces fixes for multiple independent bugs, use this stash-and-select workflow to create separate branches without re-doing work:

```bash
# 1. Make ALL changes in the working tree first (no commits yet).
#    Edit file_a.py, file_b.py, file_c.py using patch / write_file tools.

# 2. Stash everything to get a clean baseline
git stash -- file_a.py file_b.py file_c.py

# 3. Create branch for fix-1, apply only its file, commit
git checkout -b fix/issue-12132-description
git stash pop  # restores ALL working-tree changes
git add file_a.py            # stage ONLY fix-1's file
git commit -m "fix(scope): description (#12132)"
git push origin HEAD
# (file_b.py and file_c.py remain unstaged)

# 4. Go back to main, create branch-2, commit only fix-2's file
git checkout main
git checkout -b fix/issue-62503-description
git add file_b.py
git commit -m "fix(scope): description (#62503)"
git push origin HEAD

# 5. Repeat for fix-3
git checkout main
git checkout -b fix/issue-62549-description
git add file_c.py
git commit -m "fix(scope): description (#62549)"
git push origin HEAD

# Result: three independent branches, each with exactly one fix.
# No branch surgery, no force-push risk. The same working-tree edits
# are partitioned into clean, focused commits.
```

**Pitfall — `git stash` requires explicit file list**: `git stash` without a file list stashes ALL tracked changes including files you want for the next branch. Always pass specific files: `git stash -- file_a.py file_b.py`. Files not listed remain in the working tree and carry across `checkout` operations.

**Pitfall — `git stash pop` restores everything**: Popping restores ALL stashed files into the working tree. After staging only the desired file and committing, the remaining unstaged changes persist. They will follow you to the next branch via `git checkout`. This is the intended behavior — each branch progressively commits one file, leaving the rest for the next branch.

**Pitfall — Pre-existing uncommitted changes from pre-run scripts:** A cron pre-run script may have already applied patches to the working tree. Before creating any branches, always check:

```bash
git diff HEAD --stat   # list all uncommitted changes
```

These may contain fixes for multiple issues mixed together. Do NOT commit them as one blob — use the stash-and-select pattern above to partition them into per-issue branches. First identify which fixes belong to which issue by reading the file content and issue descriptions, then separate them into focused branches.

**Pitfall — `delegate_task()` for bug investigation may never complete:** When dispatching investigation tasks to subagents (e.g. `delegate_task(goal="Investigate bug #N...")`), the subagent may fail to report back within a useful timeframe, or may not report at all. This is especially common when the subagent gets stuck on import errors, missing dependencies, or circular reasoning. Do NOT block waiting for subagent results — continue working on other bugs while they run, and be prepared to investigate yourself if they don't materialize. The most reliable investigation strategy is: read the source files directly with `read_file`/`search_files`, run targeted tests, and trace the code path yourself. Use `delegate_task` only for truly parallelizable research (e.g. searching different files simultaneously), not as a primary investigation strategy.

**Alternative — write the fix files first, then branch per fix:**
If you know all fix branches in advance, create them upfront to avoid the stash entirely:

```bash
git checkout main && git checkout -b fix/issue-a
git checkout main && git checkout -b fix/issue-b
git checkout main && git checkout -b fix/issue-c
# Switch to fix/issue-a, edit, commit. Then fix/issue-b, etc.
```

## Post-PR Notification

When a cron job or automated workflow creates PRs, notify the delivery channel with a structured summary:

### Discord Webhook

```bash
# Build a single JSON payload — the content field must be one string
# with embedded \n line breaks, NOT separate string literals per line.
CONTENT="$(
  cat <<'CONTENTEOF'
**🤖 Auto-Fix PRs — July 8, 2026**

**1. fix(desktop): register /compress command** -> <https://github.com/owner/repo/pull/12345>
  One-line problem description

**2. fix(aux): forward max_tokens to all providers** -> <https://github.com/owner/repo/pull/12346>
  One-line problem description
CONTENTEOF
)"

# Encode the multi-line content as a single JSON string with \n escapes
# using jq for proper JSON encoding (avoids manual escaping issues)
jq -n --arg content "$CONTENT" '{content: $content}' > /tmp/discord_payload.json

curl -s -X POST \
  -H "Content-Type: application/json" \
  -d @/tmp/discord_payload.json \
  https://discord.com/api/webhooks/<WEBHOOK_ID>/<WEBHOOK_TOKEN>

# On success Discord returns HTTP 204 (No Content)

**Key points:**
- Use `@filename` with `-d` to pass the file body — avoids shell escaping issues
- Discord returns HTTP 204 on success (no body)
- Wrap URLs in `<angle brackets>` to prevent Discord from generating broken link previews
- Keep each entry to one line per PR — Discord truncates long messages silently
- Structure: `PR number -> URL` followed by a one-line problem description

**Alternative — one message per PR (simpler, no jq needed):**

When creating 2-3 PRs, posting individual notifications per PR is simpler than building a batch summary:

```bash
curl -H "Content-Type: application/json" \
  -d '{"content":"🔧 **New PR** — Short description\n👉 https://github.com/owner/repo/pull/12345"}' \
  https://discord.com/api/webhooks/<ID>/<TOKEN>
```

This avoids the `cat`+`jq` pipeline entirely. The payload is a single flat JSON string — no escaping issues if you keep the description short and avoid quotes. Post one curl call per PR right after `gh pr create` succeeds.

### Other channels
The same pattern works for Slack webhooks, email (via `hermes send`), or any HTTP endpoint — write the structured message to a file, POST it, and check for 2xx status.
