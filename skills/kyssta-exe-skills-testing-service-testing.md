---
name: service-testing
description: Integration-test daemon/service systems — background process lifecycle, state cleanup, readiness polling, crash recovery.
---

# Service / Daemon Integration Testing

## When to use

You need to run an integration test against one or more long-running processes (daemon, worker, API server, database, message queue). The system under test has side effects — SQLite, filesystem, UDS socket — that persist across runs.

## Core workflow

The cycle that prevents a rewrite loop:

```
clean state → start dependencies → wait readiness → start SUT → wait readiness → run tests → kill → clean → report
```

**Never** skip to "fix code" before verifying the test cycle. If the test hasn't run yet, the edit is speculative.

## Procedure

### 1. Clean state

```bash
# Kill orphaned processes from prior runs
pkill -9 -f "my-daemon|my-worker" 2>/dev/null

# Remove persistent artifacts (SQLite, sockets, temp files)
rm -f /tmp/my-daemon.sock /var/lib/my-daemon/db.sqlite*
rm -f /tmp/my-worker/memory.db /tmp/my-worker/shared/memory.db
```

**Pitfalls:**
- SQLite WAL (`-shm`, `-wal`) files survive `rm db.sqlite` — delete them explicitly.
- `pkill -9 -f` in a background terminal call returns exit code -9. Ignore it — the processes are dead even though the shell reports a kill signal.
- Named sockets survive abrupt shutdowns. Always `rm -f <socket>` before starting a fresh instance.

### 2. Start dependencies in order

```bash
# Start each dependency as a background process with a watch pattern
# Use the process tool, not terminal(background=true) with pkill
```

Pattern (for Python workers that load models):
```bash
python3 my-worker/src/main.py 2>&1
# Watch for: "listening on" or "ready"
# Allow 15-30s for model download/load
```

### 3. Wait for readiness (poll, don't sleep)

```bash
# Poll every 1-2s, max 30s
for i in $(seq 1 15); do
  sock=$(ls /tmp/my-daemon.sock 2>/dev/null)
  if [ -n "$sock" ]; then break; fi
  sleep 2
done

# Or for HTTP services
for i in $(seq 1 10); do
  out=$(curl -s http://127.0.0.1:PORT/health 2>/dev/null)
  if echo "$out" | python3 -c "..." 2>/dev/null | grep -q ok; then
    echo "READY"
    break
  fi
  sleep 1
done
```

**Pitfalls:**
- Memory/ML workers model-load on startup — can take 20-60s. The socket appears at the END of load, not the start.
- Daemon binds before it's truly ready (DB migrations, seed data). Health endpoint is the real readiness check.

### 4. Start the system under test

Same pattern as dependencies — background with a watch pattern.

### 5. Run the integration test

Prefer a standalone test script (Python or shell) over inline terminal commands. The script should:
- Query endpoints (health, data)
- Execute workflows (create, run, wait)
- Poll for async completion
- Check persistence (DB queries)
- Verify recovery (kill daemon, restart, re-query)

**Test script patterns:**
```python
import subprocess, time, json

def curl(method, path, data=None):
    # returns parsed JSON
def sql(query):
    # returns raw output via sqlite3 CLI

# Each test: print name, run, assert, PASS/FAIL counter
```

### 6. Kill and report

Kill all background processes with `process(action="kill", session_id=...)`. Report PASS/FAIL counts.

## Recovery testing

To test crash durability:

```bash
# 1. Run a workflow
# 2. Kill daemon with signal (SIGKILL = -9)
# 3. Restart daemon (should recover orphaned runs)
# 4. Query health → run status should be the same as before
# 5. Query workflow list → should survive
```

The daemon's startup recovery code polls for `pending`/`running` runs and re-spawns executors. The test must not clean the DB between kill and restart — recovery only works with persistent state.

## Ponytail rules

- No test framework — a single Python/shell script with assert + counter is enough.
- No test fixtures — clean state IS the fixture.
- No test isolation — tests run against real processes, order matters.
- No mocking — if the dependency is hard to start, the test proves you need a better dependency, not a mock.
- When a test fails, diagnose from the failure output — don't rewrite the code speculatively.

## Reference files

<!-- ref to roshi-v0.0.1.md removed for public release -->

## Common failures

| Symptom | Cause |
|---------|-------|
| Curl timeouts | Daemon not started, wrong port, or IPv6 binding |
| `No LLM provider configured` | No `--provider key@model:base` arg |
| `address already in use` | Zombie daemon on the port — kill it |
| `connection refused` on socket | Dependency never created socket — check startup logs |
| Orphaned `running` steps on restart | Migration not applied — check `step_def_id` column exists |
