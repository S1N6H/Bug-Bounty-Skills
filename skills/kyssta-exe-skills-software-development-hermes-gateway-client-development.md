---
name: hermes-gateway-client-development
description: "Build mobile, desktop, or CLI clients that connect to a remote Hermes Agent (hermes serve) via WebSocket JSON-RPC."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, gateway, websocket, json-rpc, mobile, client]
    related_skills: [hermes-agent, github-repo-management]
---

# Hermes Gateway Client Development

Building a custom client (mobile app, desktop UI, CLI tool) that talks to a remote Hermes Agent via the `hermes serve` backend. This covers the protocol, auth, and platform-specific pitfalls.

> **Core principle**: The client is a thin WebSocket/HTTP consumer. All LLM calls, tools, skills, and memory live on the remote `hermes serve` process. The client never runs an agent itself.

---

## Architecture

```
[Client App]                    [Remote Server: hermes serve]
     │                                  │
     ├── GET  /api/status               │  health + auth detection
     ├── POST /api/auth/login           │  username/password login
     ├── WS   /api/ws?token=...         │  JSON-RPC chat + events
     └── WS   /api/pty?token=...        │  PTY/TUI bridge (optional)
```

- `hermes serve` is the same backend the desktop app (`hermes desktop`) spawns locally, but started headless on a remote machine.
- No Hermes agent runs on the client device.

## Connection Flow

### 1. Discover & Auth

```typescript
// Step 1: Check server status
const status = await fetch(`${backendUrl}/api/status`)
// Response includes:
//   auth_required: bool
//   auth_providers: string[]  // ['nous'] or ['basic']

// Step 2a: Username/password auth
const login = await fetch(`${backendUrl}/api/auth/login`, {
  method: 'POST',
  body: JSON.stringify({ username, password })
})
const token = login.token  // Bearer token for WS

// Step 2b: Session token (pre-set on server)
// Server env: HERMES_DASHBOARD_SESSION_TOKEN=my-token
const token = "my-token"  // Use directly
```

### 2. WebSocket (JSON-RPC)

Connect to `ws://host:9119/api/ws?token=<token>`

**All mobile/desktop clients should use `/api/ws`** — this is the structured JSON-RPC protocol. `/api/pty` is for terminal/PTY emulation (xterm.js) and should NOT be used by native mobile clients.

```typescript
const ws = new WebSocket(`ws://${host}:${port}/api/ws?token=${token}`)

// Request (client → server)
ws.send(JSON.stringify({
  jsonrpc: "2.0",
  id: "r1",
  method: "prompt.submit",
  params: { message: "Hello!", session_id: "..." }
}))

// Response (server → client, for RPC calls)
// → { jsonrpc: "2.0", id: "r1", result: { ... } }

// Event (server → client, no id — streaming)
// → { jsonrpc: "2.0", method: "event", params: { type: "message.delta", payload: { content: "Hi" } } }
```

### Key RPC Methods

| Method | Purpose |
|--------|---------|
| `prompt.submit` | Send a message to the agent |
| `session.create` | Create new conversation |
| `session.list` | List recent sessions |
| `session.resume` | Load session history |
| `session.delete` | Delete a session |
| `session.interrupt` | Stop current turn |
| `model.list` | List available models |
| `command.dispatch` | Execute a slash command (`/model ...`) |
| `clarify.respond` | Answer a clarify prompt |
| `approval.respond` | Approve/deny a dangerous command |

### Stream Events (Server → Client)

| Event | When |
|-------|------|
| `message.delta` | Streaming text chunk |
| `message.complete` | Message finished |
| `tool.start` / `tool.progress` / `tool.complete` | Tool execution lifecycle |
| `clarify.request` | Agent needs clarification |
| `approval.request` | Command needs approval |
| `gateway.ready` | Backend initialized |

Full method catalog at `tui_gateway/server.py` in the hermes-agent repo.

---

## Auth Pitfalls

### ⚠️ Desktop App Shows "Sign in with Nous" Instead of Token/Password Field

The Hermes Desktop app reads `/api/status` → `auth_providers` to decide what login UI to show. If only `["nous"]` is listed, it renders the Nous OAuth button — **no token/password field**.

**Fix**: Register a password provider on startup so `auth_providers` includes `["nous", "password"]`, which makes the desktop app render a username/password form.

In `web_server.py`, add at the top of `_lifespan()`:

```python
from hermes_cli.dashboard_auth import register_provider
from hermes_cli.dashboard_auth.base import DashboardAuthProvider, Session
import hmac, os, time

class _TokenPasswordProvider(DashboardAuthProvider):
    name = "password"
    display_name = "Access Token"
    supports_password = True
    supports_token = True

    def start_login(self, **kw): raise NotImplementedError
    def complete_login(self, **kw): raise NotImplementedError

    def complete_password_login(self, *, username, password):
        token = os.environ.get("HERMES_DASHBOARD_SESSION_TOKEN", "")
        if hmac.compare_digest(username, token) or hmac.compare_digest(password, token):
            return Session(user_id="token-user", email="token@local",
                display_name="Token User", org_id="", provider="password",
                expires_at=int(time.time()) + 86400,
                access_token=token, refresh_token=token)
        raise InvalidCredentialsError()

    def verify_session(self, *, access_token):
        from hermes_cli.web_server import _SESSION_TOKEN
        expected = _SESSION_TOKEN or ""
        if hmac.compare_digest(access_token, expected):
            ...  # same Session as above

    def refresh_session(self, *, refresh_token):
        return self.complete_password_login(username=refresh_token, password=refresh_token)
    def revoke_session(self, **kw): pass

register_provider(_TokenPasswordProvider())
```

**Then restart**: kill the dashboard process and re-launch on the same port.

The `password-login` endpoint requires a `provider` field:
```json
POST /auth/password-login
{"provider": "password", "username": "<token>", "password": "<token>"}
```

On success it returns `{"ok": true, "next": "/"}` with session cookies, after which `?token=` on WS or `Authorization: Bearer` on REST works.

See `references/desktop-auth-provider.md` for the full inline class code.

### ⚠️ WebSocket `?token=` Rejected in Gated Mode

When `hermes serve` binds to a non-loopback address (`--host 0.0.0.0`), the auth gate engages. In this **gated mode**, the WebSocket endpoint **rejects** `?token=<_SESSION_TOKEN>` — it only accepts:

- `?ticket=<single-use-ticket>` — obtained via `POST /api/auth/ws-ticket` (browser SPA flow)
- `?internal=<process-credential>` — for server-spawned children
- `Authorization: Bearer <token>` header (REST endpoints)

**Fix for native mobile clients**: Patch `_ws_auth_reason()` in `web_server.py` to also accept `?token=` in gated mode:

```python
# In hermes_cli/web_server.py, inside _ws_auth_reason() gated block:
token = ws.query_params.get("token", "")
if token:
    if hmac.compare_digest(token.encode(), _SESSION_TOKEN.encode()):
        return None, "token"
```

⚠️ **PATCH THE RIGHT FILE** — Hermes may have multiple copies. Always confirm the installed path before editing:
```bash
python3 -c "import hermes_cli.web_server; print(hermes_cli.web_server.__file__)"
# Expected: /usr/local/lib/hermes-agent/hermes_cli/web_server.py
# NOT a dev checkout like /root/hermes-agent/
```
Patching a dev checkout has no effect because the running `hermes` command imports from the installed copy.

⚠️ **`.env` duplicate entries** — If `~/.hermes/.env` has multiple `HERMES_DASHBOARD_SESSION_TOKEN` lines, python-dotenv uses the **last** value. Clean up duplicates to avoid confusion.

After patching, restart and verify:
```bash
fuser -k 9119/tcp
hermes dashboard --host 0.0.0.0 --port 9119 --skip-build --no-open
```
See `references/websocket-auth.md` for a runnable WS verification script.

This fix is only needed for self-hosted backends where you control the server. For Nous Portal OAuth, use the ticket flow instead.

### Android Cleartext HTTP

Android 9+ blocks plain HTTP (`http://`) by default. If your backend uses HTTP (not HTTPS), add to `AndroidManifest.xml`:

```xml
<application ... android:usesCleartextTraffic="true">
```

For production, either use HTTPS with a valid cert or configure a network security policy that allows cleartext only for specific hosts.

---

## Platform-Specific Notes

### React Native / Expo

- The `@hermes/shared` package in the hermes-agent repo (`apps/shared/src/`) contains `JsonRpcGatewayClient` — directly reusable TypeScript for the WS protocol
- React Native `WebSocket` API does not support custom headers on upgrade; query params (`?token=`) are the only way to pass auth
- Use `expo-secure-store` for token persistence
- Use `zustand` + `@tanstack/react-query` for state management (same as desktop app)

### GitHub Actions APK Build (Expo/React Native)

```yaml
- uses: actions/setup-java@v4
  with:
    distribution: 'temurin'
    java-version: '17'
# JDK 17 required — JDK 21+ has CMake/native build compatibility issues

steps:
  - run: npm ci
  - run: npx tsc --noEmit
  - run: cd android && ./gradlew assembleRelease --no-daemon
```

**Key pitfalls:**
- Gradle first build takes 20-25 minutes on GH runners
- Ensure `ANDROID_HOME` / Android SDK is available (setup-java doesn't provide it — need `expo prebuild` or committed `android/` directory)
- Hermes JS engine compiler (`hermesc`) must be x86_64 binary — ARM64 VPS can't build APKs with native modules

### Release Cleanup

Delete old releases when publishing new APKs to keep the releases page clean:

```bash
# List all releases
gh release list --repo owner/repo

# Delete old releases (keep newest)
for tag in old-tag-1 old-tag-2; do
  gh release delete "$tag" --repo owner/repo --yes --cleanup-tag
done
```

---

## Troubleshooting Checklist

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `CLEARTEXT communication not permitted` | Android blocks HTTP | `android:usesCleartextTraffic="true"` in manifest |
| `WebSocket 403 Forbidden` | Auth gate rejects `?token=` | Patch `_ws_auth_reason()` or use ticket flow |
| Desktop shows "Sign in with Nous" only | Only "nous" in `auth_providers` | Register a `supports_password=True` provider in `_lifespan()` (see ⚠️ Desktop App section) |
| `fetch failed` / connection refused | Server not running or wrong port | `hermes serve --host 0.0.0.0 --port 9119` |
| WebSocket connects but no response | Wrong protocol — using `/api/pty` instead of `/api/ws` | Use `/api/ws` for structured JSON-RPC |
| Gradle build fails on native modules | Wrong JDK version | Use JDK 17 (not 21+) |
| `Hermes compiler error` on ARM64 | `hermesc` is x86_64 only | Build on x86_64 CI runner (GH Actions) |
