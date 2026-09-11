---
name: debugging-patterns
description: "Concrete debugging tactics for error classification, library API verification, and multi-location bug fixes. Supplements systematic-debugging with pattern-level techniques."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [debugging, error-handling, classification, tracing, patterns]
    related_skills: [systematic-debugging, defensive-programming, config-propagation-bugs]
---

# Debugging Patterns

Concrete tactics that recur across debugging sessions. These slot into Phase 1 (Root Cause) and Phase 4 (Implementation) of the [systematic-debugging](skill:systematic-debugging) skill.

## Trace Classification Pipelines Top-to-Bottom

Error classifiers with priority-ordered guard clauses need **exact tracing** before concluding an error won't match. A single error message can match multiple patterns at different priority levels — the first match wins, so you must trace from the top.

**Steps:**

1. Extract the error's status code, type, body dict, and error code.
2. Build the combined `error_msg` the same way the classifier does (`str(error).lower()` + body message).
3. Read each guard clause in order — check every `if` or `elif` before the one you expect to fire. One earlier clause may intercept the error with a broader pattern.
4. Check **excluded patterns** — some guard clauses explicitly skip certain values (e.g., `if p != "invalid_request_error"`). The exclusion may or may not apply to your error.
5. If the error reaches the expected bucket but still isn't handled, the issue is in the *consumer* of the classification, not the classifier itself.

**Common gotcha:** A status-code-based classifier (like `_classify_by_status`) only runs when `status_code is not None`. If the error loses its status code during propagation, it falls through to message-pattern matching, which may produce a different (and wrong) classification.

**Descriptive vs. Signal Keywords:** When an error classifier has a broad override gate (e.g. `"input token" in error_lower`), check whether the keyword is a **signal** (the error IS about that condition) or a **description** (the error mentions the concept as part of its arithmetic but is actually about something else). For example:

- The vLLM format `"your prompt contains at least N input tokens"` mentions `"input token"` *descriptively* — it's explaining the total count, not saying the input is too long.
- The same format also says `"reduce the length of the input prompt OR the number of requested output tokens"` — offering a choice, not signaling input overflow.

**Fix:** When a well-known error format uses descriptive keywords that trigger a broad override, add an exact-format exception before the broad override rather than broadening the override further:

```python
# Known output-cap format that descriptively mentions input
vllm_style = (
    "maximum context length" in error_lower
    and "requested" in error_lower
    and "output tokens" in error_lower
    and "prompt contains" in error_lower
)
return (not input_overflow_signal) or vllm_style
```

## Check Library API Support Before Assuming

When a fix depends on whether a third-party constructor or function supports a parameter, verify it directly instead of reading docs or guessing:

```python
import inspect
import some_library
print(inspect.signature(some_library.SomeClass.__init__))
```

This reveals the exact parameter names, defaults, and types the installed version supports. Useful when:
- The library is behind a lazy import and the source isn't immediately visible.
- Different library versions have different signatures.
- You're connecting to a new API for the first time and the docs are stale or ambiguous.

If the library isn't importable in the current environment, fall back to reading the installed package's source at its `site-packages` path.

## Rewrite-Loop Trap Detection

**Signal:** Build compiles (0 errors) but agent keeps editing. Multiple independent reviewers converge on "stop editing, run the test."

**Root cause:** Editing feels like progress; testing feels like waiting. The compiler is not the arbiter — the test is.

**Protocol when build is green:**
1. Stop editing — close the patch/write tool
2. Kill zombies — clean processes, sockets, DB files
3. Start system — launch the actual processes
4. Run e2e test — the integration test, not unit tests
5. Read output — the test reveals what's actually broken

**Heuristic:** If >2 edits since last green build without running the test → you're in the trap. Close the file and execute.

*Mirror of `references/rewrite-loop-trap.md`*

## Stale-Binary Test Regression

**Symptom:** Test fails with a regression in a module that hasn't been touched. The same test passed in a prior run. Build compiles cleanly.

**Root cause chain:**
1. Previous test run left a daemon process listening on the service port
2. New daemon failed to bind (`Address already in use (os error 98)`)
3. Test HTTP requests were served by the OLD daemon process (stale binary)
4. The old binary was from before the latest changes, so the "fixed" bug still manifests

**Diagnosis:** Check the daemon's startup log in the background process output. If the output contains `Error: Address already in use` or `error 98`, the new binary never bound — the test ran against a zombie.

**Fix protocol (clean step):**
```bash
kill -9 $(pgrep -f "target/debug/<name>") 2>/dev/null
kill -9 $(pgrep -f "python3.*<worker>") 2>/dev/null
sleep 2
ss -tlnp | grep <port> || echo "port free"
rm -f <socket> <db-file>*   # also remove -wal and -shm
```

Then start fresh and test.

**Prevention:** Before any test run, issue a targeted kill against the exact process pattern (not a broad `pkill -f` that kills the shell running the test). Verify the port is released with `ss -tlnp` before starting the service. Remove WAL/SHM files alongside the DB, or SQLite may replay stale transactions on restart.

**Common companion:** This pattern often appears alongside the "Rewrite-Loop Trap" (many edits since last clean test run). The edit loop produces correct changes, but the stale binary never exercised them. Kill + restart is the omitted step.

## Reference Convergence as a Stop Signal

When multiple independent reviewers (MoA reference agents, a user repeating the same instruction, or tool output with identical errors in different formats) converge with identical advice, treat that convergence as a **blocking signal** — execute before writing another line, not after.

Signals to recognize:
- Four reference agents with the same verdict → don't re-analyze, execute
- Tool errors with identical root cause in different parameter variations → read the error once, fix the root
- User repeating "stop doing X" → the correction is confirmed, no need for a third confirmation attempt

## Rust Async UDS Patterns

See `references/rust-async-uds-patterns.md` for:
- `tokio::net::UnixStream` has no `set_read_timeout` — wrap reads in `tokio::time::timeout()`
- JSON framing over UDS (4-byte BE length prefix recipe)
- MemoryClient idempotency: check-before-INSERT pattern
- Verify step: `Value::is_null()` not `as_str()` for JSON outputs
- Migration safety: `pragma_table_info` runtime check before `ALTER TABLE ADD COLUMN`

---

## Find All Affected Locations for the Same Fix

When a bug pattern (missing parameter, wrong default, dropped field) is found in one location, assume it exists in sibling callers until proven otherwise.

```python
search_files("ClassName(", path="src/", file_glob="*.py")
search_files("function_name(", path="src/", file_glob="*.py")
```

Inspect each result. Fixing only the path the issue number names leaves other callers still broken. The same root cause may manifest in 2+ files, each needing the same fix.

## When a Tight Loop Can't Be Built

Sometimes reproduction requires a specific environment, hardware, or service account you don't have (WSL2, macOS, Windows, a cloud provider API key). In that case:

1. **Read the code** end-to-end — trace the data flow from the entry point to the failure site. The root cause is often visible without runtime execution.
2. **Look for existing tests** that exercise the same code path. They may reveal how the code behaves under different conditions or flag a gap in coverage.
3. **Check if the error message matches known patterns** in the codebase's error classification or retry logic.
4. **Default to "requires that environment to verify"** — do not ship a speculative untestable fix. Note the skipped issue and why, and move on.

## `AttributeError: 'read-only'` from `abc.abstractmethod` + `__slots__`

When you encounter `AttributeError: 'ClassName' object attribute 'attr' is read-only` and the attribute is a regular method (not a property), suspect a CPython interaction between `abc.abstractmethod` and `__slots__`.

**Root cause:** On Python 3.11 (fixed in 3.12+), when a parent class defines an `@abc.abstractmethod` and the concrete child class uses `__slots__`, the overridden method becomes a read-only attribute on instances. The opaque error gives no stack trace hinting at the real cause.

**Steps to isolate:**

1. **Verify the error message is from CPython internals**, not a custom `__setattr__`. The format `'ClassName' object attribute 'attr' is read-only` is CPython's `type_setattro` output when a data descriptor (abstractmethod) without a setter is assigned on a slots-class instance. Custom `__setattr__` methods produce different messages.

2. **Check the MRO for both `abc.ABC` and `__slots__`** in the same inheritance chain. The issue requires a parent with `@abc.abstractmethod` AND a child with non-empty `__slots__`:
   ```python
   for cls in SomeClass.__mro__:
       if '__slots__' in cls.__dict__:
           print(f'{cls.__name__} __slots__ = {cls.__dict__["__slots__"]}')
   ```

3. **Test attribute settability directly** to confirm:
   ```python
   try:
       obj.some_method = 'test'
       print('Settable — no conflict')
   except AttributeError as e:
       print(f'Read-only: {e}')
   ```

4. **Test with different Python interpreter**, not just different library versions — the bug is Python-version-specific (3.11 vs 3.12+), not library-version-specific.

5. **Fix pattern** (never change the third-party library):
   - Detect the `AttributeError` by message pattern and convert it to a clear error with guidance (upgrade Python or pin the library version that avoids the slots layout).

## Preserve Pre-Normalization Values

When a value is normalized (provider name, path, URL, identifier) before being stored or passed to another component, the original unnormalized value is often needed later for lookup or display. If the normalization is destructive (the normalized form loses information), preserve the original alongside it.

**Pattern:** Store the pre-normalization value on the object before calling the normalization step:

```python
# Before normalization
original = value

# Normalize
normalized = normalize(value)
obj.field = normalized

# Preserve original for downstream consumers
obj._original_field = original
```

This is especially relevant for persist/restore flows where the stored value is later used to look up an entry in a config or registry that uses the original key.

## Non-UTF-8 Output From Child Processes (Rust)

**Symptom:** `BufReader::lines()` or equivalent UTF-8-strict line reader returns `"stream did not contain valid UTF-8"` or similar `io::Error` when reading stdout/stderr from a subprocess on a non-English system locale.

**Root cause:** `BufReader::lines()` (tokio/std) and similar APIs (`read_line` returning `String`) require strict UTF-8. On Windows with non-English locales, PowerShell and other tools emit output using the system code page (e.g. Windows-1252, Shift-JIS) rather than UTF-8. The same can happen on Linux when LANG is set to a non-UTF-8 locale.

**Fix pattern:** Replace `.lines()` with byte-level `read_until(b'\n')` + `String::from_utf8_lossy()`:

```rust
use tokio::io::AsyncBufRead;
use std::io::BufReader;

async fn read_lossy_line<R: AsyncBufRead + Unpin>(
    reader: &mut R,
) -> std::io::Result<Option<String>> {
    let mut buf = Vec::new();
    let n = reader.read_until(b'\n', &mut buf).await?;
    if n == 0 {
        return Ok(None);
    }
    // Strip trailing \n or \r\n (BufReader::lines() behaviour).
    if buf.ends_with(b"\n") {
        buf.pop();
        if buf.ends_with(b"\r") {
            buf.pop();
        }
    }
    Ok(Some(String::from_utf8_lossy(&buf).into_owned()))
}
```

Then use in your select loop:
```rust
let mut reader = BufReader::new(child.stdout.take().unwrap());
loop {
    tokio::select! {
        line = read_lossy_line(&mut reader) => { ... }
    }
}
```

`from_utf8_lossy` replaces invalid byte sequences with U+FFFD (replacement character) instead of aborting. The output is human-readable even if slightly garbled, which is acceptable for logging/display and far better than a crash.

**Applicability:** Any Rust asynchronous reader that must handle process output from non-UTF-8-safe environments. Also applies to synchronous `BufRead::read_line` — wrap with `read_to_end` + `from_utf8_lossy` instead.

## UI "Already Focused" Guard Mismatch Across Route Changes

**Symptom:** In a sidebar+detail-view UI (desktop app, web dashboard), clicking the **most recently selected item** from a different view/tab does nothing — the UI stays on the current page. Clicking any *other* item works normally.

**Root cause:** A guard function like `focusExisting(itemId)` checks whether `itemId === $selectedItemId` at the **data level** (the store holds the id). If the IDs match, the guard returns `true` to prevent re-selection — but it only performs a UI-level action like `revealPane()` or `focusTab()` that assumes the correct view is already displayed. When the user switched to a different page/tab first, `revealPane()` doesn't change the route, so the UI stays on the wrong page.

**Fix pattern:** Before trusting an "already focused" guard, verify the current UI actually shows that view:

```typescript
// Before the guard function decision point:
onSelectItem: itemId => {
  if (!focusExisting(itemId)) {
    // Not already shown → navigate
    navigate(itemRoute(itemId))
  } else if (appViewForPath(location.pathname) !== 'chat') {
    // Guard says "already focused" but we're on a different view
    // — force the route change (#66875, #66880)
    navigate(itemRoute(itemId))
  }
}
```

**Broader principle:** Guard functions that short-circuit a navigation/focus action must verify the **whole precondition** — not just that the data matches, but that the current UI context (route, view, tab) actually displays the data. A stale route check is the most common missing precondition.

**Pattern variants:**
- Sidebar sessions in a chat app where the guard exists in a session-store function and the view is determined by the router
- Tab-based UIs where `selectTab(id)` returns early if `id === activeTabId` but the user is on a different pane
- Item selection stores where `$selectedId` persists across route changes

## Electron/Chromium: `preventDefault()` on Focus Events Breaks Clicks

When an interactive element (button, link) wrapped in a Radix UI `<Tooltip>` (or similar overlay component) becomes unclickable in Electron/Chromium, suspect a focus-event handler calling `event.preventDefault()`.

**Root cause:** In Electron and Chromium-based environments, calling `preventDefault()` on a `focus` event prevents the subsequent `click` event from firing on the same element. This is a platform-specific quirk — it does not happen in all browsers, but it reliably breaks clicks in Electron apps.

**Symptom pattern:**
- Buttons wrapped in `<Tip>` or `<Tooltip>` components stop responding to clicks
- The buttons appear interactive (hover states work) but clicks produce no response
- The issue appears after a tooltip-related fix that added `preventDefault()` to focus handlers
- CLI/non-desktop paths work fine (they don't use Electron)

**Diagnosis:**
1. Search for `preventDefault()` calls in focus event handlers near the broken element
2. Check if the element is wrapped in a tooltip/overlay component
3. Look for recent commits that added focus-event suppression logic

**Fix pattern:** Instead of `preventDefault()` on the focus event, use a context-based approach:

```tsx
// BAD: breaks clicks in Electron
onFocus={event => {
  if (!isKeyboardFocus(event)) {
    event.preventDefault() // ❌ prevents subsequent click
  }
}}

// GOOD: use context-based state
const suppressRef = React.useRef(false)

// In trigger:
onFocus={event => {
  if (!isKeyboardFocus(event)) {
    suppressRef.current = true // ✅ mark for suppression
  }
}}

// In overlay root:
onOpenChange={open => {
  if (suppressRef.current && open) {
    suppressRef.current = false
    return // suppress the open
  }
  suppressRef.current = false
  onOpenChange?.(open)
}}
```

**Broader principle:** Focus event handlers in Electron/Chromium must be careful about `preventDefault()`. If you need to suppress a side effect (tooltip open, menu open, etc.), use state-based suppression rather than event cancellation. Test in Electron, not just browser — the quirk is Electron-specific.
