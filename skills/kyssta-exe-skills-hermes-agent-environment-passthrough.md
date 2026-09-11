---
name: hermes-agent-environment-passthrough
description: "Ensuring environment variables are correctly passed to Hermes agent terminal backends, especially Daytona."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
tags: [hermes, agent, terminal, environment, daytona, bugfix]
related_skills: []
---

# Hermes Agent Environment Passthrough

## Overview

Skills that declare `required_environment_variables` in their frontmatter need
those vars available in sandboxed execution environments (execute_code, terminal).
By default both sandboxes strip secrets from the child process environment for
security. The `terminal.env_passthrough` config and skill registration mechanism
provide a session-scoped allowlist so skill-declared vars pass through.

Two sources feed the allowlist:
1. **Skill declarations** — when a skill is loaded via `skill_view`, its
   `required_environment_variables` are registered automatically.
2. **User config** — `terminal.env_passthrough` in config.yaml lets users
   explicitly allowlist vars for non-skill use cases.

Both `code_execution_tool.py` and `tools/environments/local.py` consult
`is_env_passthrough` before stripping a variable.

## When to Use

- Adding or modifying a terminal backend that runs commands remotely
- Debugging why a skill's required env vars are missing in the sandbox
- Adding a new backend (Docker, SSH, Modal, Daytona, etc.)

## Architecture

### Key files
- `tools/env_passthrough.py` — The registry: `register_env_passthrough()`,
  `is_env_passthrough()`, `get_all_passthrough()`, `clear_env_passthrough()`.
- `tools/environments/local.py` — Reference implementation. `_make_run_env()`
  builds a sanitized env dict; `_sanitize_subprocess_env()` for non-terminal
  spawns. Both consult `is_env_passthrough()`.
- `tools/environments/daytona.py` — Remote backend. Builds a filtered
  `passthrough_env` dict inline in `_run_bash()` using `is_env_passthrough()`
  to forward user/skill-declared vars to the sandbox.
- `tools/environments/base.py` — `BaseEnvironment` base class.

### How local.py filters env vars

`_make_run_env(env)` merges `os.environ` with `env`, then for each key:
1. Skip `_HERMES_FORCE_*` prefix vars (gateway routing hints).
2. Skip `_is_hermes_internal_secret()` matches (AUXILIARY_*_API_KEY, etc.).
3. Allow if key NOT in `_HERMES_PROVIDER_ENV_BLOCKLIST`, OR if
   `is_env_passthrough(key)` returns True (skill/config passthrough).

`_HERMES_PROVIDER_ENV_BLOCKLIST` is a frozenset built at import time from
the provider registry, tool/messaging config, and a hardcoded set of
known API keys and provider URLs.

### Security constraints (GHSA-rhgp-j443-p4rf)

- `is_env_passthrough()` **cannot** override `_HERMES_PROVIDER_ENV_BLOCKLIST`.
  Passthrough registration for blocklisted vars is rejected.
- `_is_hermes_internal_secret()` catches dynamic patterns (AUXILIARY_*_API_KEY,
  GATEWAY_RELAY_*_SECRET) that the static blocklist can't enumerate.
- `_HERMES_FORCE_*` prefix vars are always stripped (used for gateway routing,
  never for user-facing values).

## How Each Backend Handles env_passthrough

### Local (`tools/environments/local.py`)

The `_run_bash()` method calls `_make_run_env(self.env)` which builds a
filtered env dict and passes it to `subprocess.Popen(env=run_env)`.

### Daytona (`tools/environments/daytona.py`)

The `_run_bash()` method builds a `passthrough_env` dict inline by filtering
`os.environ` through `is_env_passthrough()`, then passes it as `env=` to the
Daytona SDK's `sandbox.process.exec()`:

```python
# Inside _run_bash():
from tools.env_passthrough import is_env_passthrough as _is_passthrough

passthrough_env = {
    k: v for k, v in os.environ.items()
    if _is_passthrough(k)
}

response = sandbox.process.exec(
    shell_cmd,
    timeout=timeout,
    env=passthrough_env if passthrough_env else None,
)
```

This relies on `is_env_passthrough()` already blocking Hermes-managed provider
credentials (OPENAI_API_KEY, ANTHROPIC_TOKEN, etc.) via the provider blocklist
check inside `tools/env_passthrough.py` — see Security constraints below and
GHSA-rhgp-j443-p4rf.

The Daytona SDK's `Process.exec()` accepts `env:` — verified by checking the
method signature in `daytona/_sync/process.py`. The SDK base64-encodes each
value and exports it with `export KEY=$(echo '...' | base64 -d)` before
running the command, so special characters and multi-line values are safe.

### Other backends (Docker, SSH, Modal, Singularity)

Follow the same pattern: build a filtered env dict using the same helpers,
pass it to the underlying exec mechanism. The Daytona implementation is the
canonical example for remote backends.

## Pitfalls

1. **Don't pass `self.env` directly to a remote backend.** `self.env` is the
   raw environment from the base class, NOT the filtered version. Passing it
   unfiltered leaks provider credentials to the remote sandbox.

2. **Don't reuse `_make_run_env` directly for remote backends.** That function
   injects local-only things (PATH augmentation, venv markers, session
   context) that don't apply to a remote sandbox. Build a standalone
   `_build_*_env()` function or an inline dict comprehension that imports
   just the filtering components — both patterns are used in the codebase
   (the Daytona backend uses inline is_env_passthrough filtering).

3. **Compute env at exec time, not init time.** The passthrough registry can
   change during a session (skills register vars dynamically). Building env
   once in `__init__` would miss later registrations.

4. **The Daytona SDK's `Process.exec()` accepts `env=` parameter.** Verify
   this by introspecting the SDK: `inspect.signature(Process.exec)` and
   `get_type_hints(Process.exec)`. Not all SDK methods support env passthrough.

5. **Security: never let passthrough override the provider blocklist.**
   `is_env_passthrough()` is checked AFTER the blocklist membership test,
   so even if a var is registered, it stays blocked. This is by design
   (GHSA-rhgp-j443-p4rf).

## Verification

After applying the fix, test with:
```bash
# config.yaml
terminal:
  backend: daytona
  env_passthrough: [MY_TEST_VAR]

# Terminal
echo "val=${MY_TEST_VAR:-MISSING}"
# Expected: val=hello (not MISSING)
```

Run the test suite:
```bash
pytest tests/tools/test_daytona_environment.py tests/tools/test_env_passthrough.py -v
```

## Related

- `tools/env_passthrough.py` — The passthrough registry module
- `tools/environments/local.py` — Reference implementation of filtering
- `tools/environments/daytona.py` — Remote backend with env passthrough
- [GHSA-rhgp-j443-p4rf](https://github.com/NousResearch/hermes-agent/security/advisories/GHSA-rhgp-j443-p4rf) — Security advisory on passthrough bypass
