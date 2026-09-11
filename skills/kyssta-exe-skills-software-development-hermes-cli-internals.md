---
name: hermes-cli-internals
description: Hermes CLI architecture patterns — pre-argparse flag handling, environment propagation, profile overrides, and subprocess inheritance.
version: 1
---

# Hermes CLI Internals

Patterns and pitfalls for working with the Hermes CLI architecture, particularly around flag handling, environment propagation, and subprocess launches.

## Pre-Argparse Flag Handling

Hermes uses a **pre-argparse flag consumption pattern** for flags that must affect the entire process before argparse runs.

### Pattern

```python
def _apply_<flag>_override() -> None:
    """Pre-parse <flag> and set environment before imports."""
    argv = sys.argv[1:]
    # Manual scan for the flag, consuming it from argv
    # Set environment variable(s) that affect all downstream code
```

### Why

Some flags must take effect before:
- Module imports that read environment variables
- Argparse parsing (which would be too late for some effects)
- Subprocess launches that need the environment set

### Example: Profile Override

`_apply_profile_override()` in `hermes_cli/main.py:355` handles `-p`/`--profile`:

1. Scans `sys.argv[1:]` manually (before argparse)
2. Extracts profile name from `-p <name>` or `--profile=<name>`
3. Sets `HERMES_HOME` to the profile directory
4. Strips the flag from argv so argparse doesn't see it

This must happen before any code imports `hermes_config` or reads `HERMES_HOME`.

### Pitfall: Subprocess Inheritance

When launching subprocesses (like the desktop app), the environment must be explicitly passed:

```python
env = os.environ.copy()
# Modify env as needed
subprocess.run(cmd, env=env)
```

If the subprocess is an Electron app or other long-lived process, it inherits `HERMES_HOME` and other profile-scoped settings from the parent's environment.

### Pitfall: Desktop App Profile Propagation

The `hermes desktop` command launches an Electron app that should respect the active profile. The profile is set via `HERMES_HOME` in the parent process's environment.

**Issue**: If the desktop app doesn't see the profile, check:
1. Is `HERMES_HOME` set in the parent process before launch?
2. Is the environment explicitly passed to `subprocess.run()`?
3. Does the desktop app read `HERMES_HOME` on startup?

The desktop app (`apps/desktop/src/`) reads `hermes_home` from status RPCs, but the initial `HERMES_HOME` must be set in the environment when the Electron process starts.

## Environment Variable Propagation

### Pattern

```python
def cmd_subprocess(args):
    env = os.environ.copy()
    # Add/override env vars based on args
    if getattr(args, "some_flag", False):
        env["SOME_VAR"] = "value"
    
    subprocess.run([command], env=env)
```

### Key Points

1. **Always copy `os.environ`** — don't start from scratch
2. **Pass `env=` explicitly** — subprocesses don't auto-inherit modified parent env
3. **Set vars before launch** — can't change them after the subprocess starts
4. **Use `with_hermes_node_path()`** for Node.js subprocesses — it handles PATH setup

### Example: Desktop Launch

`cmd_gui()` in `hermes_cli/main.py:5682`:

```python
env = with_hermes_node_path()  # Copies os.environ + adds Node to PATH
if getattr(args, "cwd", None):
    env["HERMES_DESKTOP_CWD"] = str(Path(args.cwd).expanduser().resolve())
# ... more env setup ...
subprocess.run(launch_command, env=env)
```

## Profile Scoping

### Architecture

Profiles live at `~/.hermes/profiles/<name>/` and contain:
- `config.yaml` — profile-specific config
- `.env` — profile-specific credentials
- `skills/` — profile-specific skills
- `sessions/` — profile-specific session history

### Mechanism (Subprocess / Pre-Argparse)

1. User runs `hermes -p <name> <command>`
2. `_apply_profile_override()` sets `HERMES_HOME=~/.hermes/profiles/<name>`
3. All config/credential/session lookups use `HERMES_HOME` as base
4. Subprocesses inherit `HERMES_HOME` via environment

### Mechanism (In-Process / Multiplexed Gateway)

The dashboard and desktop app serve multiple profiles from a single process.
Profile scoping is done via **ContextVars**, not environment mutation:

| Concern | ContextVar Setter | Registered In |
|---|---|---|
| Config/skills/sessions | `set_hermes_home_override(path)` → `get_hermes_home()` | `tui_gateway/server.py`, `tui_gateway/compute_host.py`, `gateway/run.py` |
| Credentials (.env) | `set_secret_scope(build_profile_secret_scope(path))` → `get_secret()` | Same sites + `cron/scheduler.py` |

**Critical rule**: these two ContextVars must ALWAYS be set together. A profile
override that installs the HERMES_HOME but not the secret scope causes
`get_secret()` to fall through to `os.environ` — resolving the LAUNCH profile's
credentials instead of the selected profile's `.env`. See `gateway/run.py`
`_profile_runtime_scope()` for the canonical paired pattern:

```python
home_token = set_hermes_home_override(str(profile_home))
secret_token = set_secret_scope(build_profile_secret_scope(Path(profile_home)))
try:
    yield
finally:
    reset_secret_scope(secret_token)
    reset_hermes_home_override(home_token)
```

### Pitfall: MCP Discovery Gating on Launch Profile

MCP tool discovery runs via a process-global background thread
(`hermes_cli/mcp_startup.py`). If the discovery is gated on the **launch
profile's** config having `mcp_servers` (via `_has_configured_mcp_servers()`
which reads the process home), a launch profile without MCP servers
short-circuits discovery for EVERY profile. Fix: always run discovery and
let `discover_mcp_tools()` handle the empty-config case — the import cost is
a one-time hit.

### Pitfall: tui_gateway Profile-Override Sites

The tui_gateway has five sites where profile-scoped ContextVars must be
installed. Missing any one causes partial profile switching:

1. **compute_host.py `_ensure_server_session`** — agent build time
2. **server.py `_build`** — lazy resume agent build
3. **server.py `_handle_resume_session`** — `_make_agent` scope
4. **server.py `_handle_resume_session`** — `_init_session` scope
5. **server.py `_handle_submit_or_edit`** — per-turn handler

Each must pair `set_hermes_home_override` with `set_secret_scope`. See
issue #67605 / PR #67623 for the original fix.

### Testing

To verify subprocess profile propagation:
```bash
hermes -p test debug share | grep "profile:"
# Should show: profile: test
```

If it shows `profile: default`, the profile override isn't propagating correctly.

## Curated Model List System

The model picker (desktop, TUI, CLI) shows a **curated subset** of each provider's model catalog, not the full live API dump. The curation lives in `_PROVIDER_MODELS` in `hermes_cli/models.py`.

### Architecture

```
Desktop picker → /api/model/options → build_models_payload()
                                          → list_authenticated_providers()
                                              → cached_provider_model_ids()
                                                  → provider_model_ids()
                                                      → _PROVIDER_MODELS fallback
```

### Two-tier model resolution

For each provider, `provider_model_ids()` in `hermes_cli/models.py`:

1. **Live fetch** — calls the provider's API `/v1/models` endpoint (when supported)
2. **Curated fallback** — `_PROVIDER_MODELS[provider_slug]` when the live fetch fails/times out

For Anthropic specifically (lines 2480-2509), the logic **merges** curated + live:

```python
curated = list(_PROVIDER_MODELS.get("anthropic", []))
merged = list(curated)          # curated order first
merged_lower = {m.lower() for m in curated}
for m in live:
    if m.lower() not in merged_lower:
        merged.append(m)        # live-only models appended
return merged
```

This means new models must be added to both the curated `_PROVIDER_MODELS` list and any provider-specific live fetch logic.

### Key files

| File | Purpose |
|-------|---------|
| `hermes_cli/models.py` — `_PROVIDER_MODELS` | Curated model list per provider |
| `hermes_cli/models.py` — `provider_model_ids()` | Live + curated merge for each provider |
| `hermes_cli/models.py` — `cached_provider_model_ids()` | Disk-cached wrapper (1h TTL) |
| `hermes_cli/model_switch.py` — `list_authenticated_providers()` | Builds picker rows from curated + cached data |
| `hermes_cli/inventory.py` — `build_models_payload()` | Assembles the `/api/model/options` response |
| `plugins/model-providers/anthropic/__init__.py` | Anthropic `fetch_models()` (used when credential store finds a key) |

### Common fix pattern

When a model is missing from the desktop/TUI picker but works via CLI:

1. Check if it's in `_PROVIDER_MODELS["provider_slug"]` in `hermes_cli/models.py`
2. If missing, add it (tier-order: flagship > opus > sonnet > haiku, newest first within each tier)
3. If present, the live API fetch may be failing — check the provider's `_fetch_*_models()` function
4. For Nous Portal, also check the remote model catalog at `website/static/api/model-catalog.json`

### Pitfall: stale cache

`cached_provider_model_ids()` has a **1-hour TTL**. After adding a model to the curated list, the user may need to explicitly refresh (`hermes model --refresh` or desktop refresh button) if a stale live-fetch result was cached before the fix.

### Pitfall: model ID format differs by provider

Direct Anthropic IDs are bare (`claude-sonnet-4-6`), while Nous Portal models are provider-prefixed (`anthropic/claude-sonnet-4-6`). When adding to `_PROVIDER_MODELS["anthropic"]`, use bare IDs. When adding to `_PROVIDER_MODELS["nous"]`, use prefixed IDs.

## References

- `hermes_cli/main.py:355` — `_apply_profile_override()` implementation
- `hermes_cli/main.py:5682` — `cmd_gui()` desktop launch with env propagation
- `hermes_cli/_parser.py` — Top-level parser construction
- `apps/desktop/src/hermes.ts` — Desktop app profile handling
- `gateway/run.py:1525-1555` — `_profile_runtime_scope()` canonical paired-ContextVar pattern
- `agent/secret_scope.py` — Secret scope module (ContextVar, get_secret, build_profile_secret_scope)
- `hermes_cli/mcp_startup.py` — MCP discovery startup (bg thread must not gate on launch profile)
- `tui_gateway/compute_host.py:438-461` — Profile override with secret scope at build time
- `tui_gateway/server.py` — All profile-override sites (search for `set_secret_scope`)
