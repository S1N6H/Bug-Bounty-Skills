---
name: hermes-client-development
description: >-
  Build custom clients (mobile, desktop, web, CLI, IDE plugins) that connect
  to a remote Hermes Agent via its JSON-RPC WebSocket protocol. Covers the
  hermes serve backend, auth flows, the tui_gateway protocol, and the
  @hermes/shared TypeScript client library.
version: 2.0.0
author: Hermes Agent
tags:
  - hermes
  - gateway
  - websocket
  - json-rpc
  - client
  - protocol
  - integration
  - mobile
  - desktop
  - app-development
related_skills:
  - hermes-agent
  - gateway-adapter-development
---

# Hermes Client Development

Build custom frontends that connect to a running `hermes serve` backend — the same headless server the desktop app and web dashboard use. The client never runs Hermes itself; it's a thin WebSocket+JSON-RPC consumer.

## When to use this skill

- Building a **mobile app** (React Native / Flutter) that chats with a remote Hermes
- Building a **custom desktop client** (Tauri, Electron, SwiftUI, etc.)
- Building an **IDE plugin** that speaks the tui_gateway protocol directly instead of ACP
- Building a **web-based custom chat UI** that connects to `hermes serve`
- Writing a **scripted client** (Python, Rust, Go) that drives Hermes programmatically

## When NOT to use this skill

- You want to embed the full Hermes agent in-process → import `run_agent.AIAgent` directly
- Your IDE already supports ACP → use `hermes acp` instead
- You want an OpenAI-compatible HTTP endpoint → use the API server (`API_SERVER_ENABLED=true`, port 8642)
- You want to write a new gateway platform adapter → use `gateway-adapter-development` skill

## Architecture: hermes serve

The remote machine runs:

```bash
# Install web extras (one-time)
uv pip install -e ".[web]"

# Start headless backend
hermes serve --host 0.0.0.0 --port 9119
```

This single FastAPI process serves:

| Endpoint | Type | Purpose |
|----------|------|---------|
| `GET /api/status` | REST | Server info, auth requirements, gateway state |
| `POST /api/auth/login` | REST | Login (username/password) → session token |
| `WS /api/ws?token=<token>` | WebSocket | JSON-RPC chat protocol |
| `WS /api/pty?token=<token>` | WebSocket | PTY/TUI bridge (xterm.js) — **NOT** needed for custom clients |
| `GET /api/health` | REST | Health check |
| `GET /api/sessions` | REST | Session listing (token-gated) |
| `POST /v1/chat/completions` | HTTP | OpenAI-compatible API (port 8642, requires `API_SERVER_ENABLED=true`) |

## Connection Flow

```
1. DISCOVERY
   GET /api/status
   → { agent_version, auth_required, auth_providers, gateway_running }

2. AUTH (choose one)
   a) Username/Password: POST /api/auth/login {username, password} → {token}
   b) Static Token:     Set HERMES_DASHBOARD_SESSION_TOKEN on backend, use directly
   c) OAuth:            Browser-based flow via Nous Portal (hermes dashboard register)

3. CONNECT
   new WebSocket("ws://<host>:9119/api/ws?token=<session_token>")

4. CHAT (JSON-RPC over WebSocket)
   → {"jsonrpc": "2.0", "method": "prompt.submit", "params": {...}, "id": 1}
   ← {"jsonrpc": "2.0", "method": "message.delta", "params": {...}}
   ← {"jsonrpc": "2.0", "method": "tool.start", "params": {...}}
   ← {"jsonrpc": "2.0", "result": {...}, "id": 1}
```

## Auth Details

### Auth Provider Detection

`GET /api/status` returns:

```json
{
  "auth_required": true,
  "auth_providers": ["basic"],
  "auth_methods": {
    "basic": {"has_username": true},
    "oauth": {"provider": "nous"}
  }
}
```

- `["basic"]` → username/password form
- `["oauth"]` → OAuth browser flow
- `auth_required: false` → no auth (loopback only)

### Username/Password

Set on the backend's `~/.hermes/.env`:

```bash
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=strong-password
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)  # stable across restarts
```

Login: `POST /api/auth/login` with JSON body `{username, password}` → `{token, token_type: "bearer"}`

### Static Token

Set on the backend's `~/.hermes/.env`:

```bash
HERMES_DASHBOARD_SESSION_TOKEN=my-static-token
```

Use directly as the WebSocket `?token=` query param. No login needed.

### Stable Sessions (important)

Without `HERMES_DASHBOARD_BASIC_AUTH_SECRET`, the token-signing key is regenerated per boot — all sessions expire on restart. Always set this for production use.

## WebSocket Protocol: The @hermes/shared Library

The Hermes repo has a **framework-agnostic TypeScript library** at `apps/shared/src/` that handles:

- `JsonRpcGatewayClient` — full WS client with pending-call dispatch, event handlers, reconnect
- `resolveGatewayWsUrl()` — constructs the WS URL with base path, scheme, auth token
- `buildHermesWebSocketUrl()` — one builder for all WS endpoints (`/api/ws`, `/api/pty`, `/api/events`)
- `GatewayReauthRequiredError` — handles expired OAuth tickets vs long-lived tokens

**This library can be imported directly** into React Native, web, or Node.js projects:

```bash
# From the hermes-agent repo root, link it
npm install  # workspace links apps/shared

# In your project
import { JsonRpcGatewayClient } from "@hermes/shared";
```

For non-TypeScript clients (Flutter, Kotlin, Swift), see the reference file `references/json-rpc-protocol.md` for the full wire format.

## Key Implementation Patterns

### Chat Loop

```typescript
// 1. Create or resume a session
const { session_id } = await client.call("session.create");

// 2. Listen for streaming events
client.on("message.delta", (params) => {
  appendToMessage(params.content);
});
client.on("tool.start", (params) => {
  showToolCall(params.name, params.id);
});
client.on("tool.complete", (params) => {
  hideToolCall(params.id);
});
client.on("clarify.request", (params) => {
  showClarifyModal(params.id, params.question, params.options);
});

// 3. Submit a prompt
client.call("prompt.submit", { message: "Hello!", session_id });
```

### Reconnection Strategy

- On WS close: exponential backoff (1s → 2s → 4s → ... → 30s max)
- Queue outgoing messages during reconnect
- Flush queue on successful reconnect
- After 5 consecutive failures, surface "connection lost" with manual retry
- Clear queue on manual disconnect

### Session Management

| Action | RPC Call |
|--------|----------|
| Create | `session.create` |
| List | `session.list` (with `limit`, `offset`) |
| Resume | `session.resume` (loads history) |
| History | `session.history` (full transcript) |
| Delete | `session.delete` |
| Rename | `session.title` (auto-generate) |
| Interrupt | `session.interrupt` (stop the current turn) |

## Pitfalls

- **DO NOT use `/api/pty` for chat clients.** That endpoint is for xterm.js terminal rendering (binary ANSI output). Use `/api/ws` for structured JSON-RPC.
- **Token storage must be encrypted.** Use `expo-secure-store` (React Native), Keychain (iOS), or EncryptedSharedPreferences (Android). Never store plaintext.
- **WebSocket URL must use `ws://` or `wss://`** based on whether the backend is behind TLS. Local/Tailscale → `ws://`. Public HTTPS → `wss://`.
- **Mid-session model switches reset prompt caching.** Switching model in `prompt.submit` costs full re-read of conversation on next turn.
- **The profile-scoped `/api/ws?profile=<name>`** parameter exists — pass it to target a specific Hermes profile on the backend.
- **Auth gate auto-engages on non-loopback bind.** You CANNOT skip auth when `--host` is `0.0.0.0`. Only `127.0.0.1` bypasses auth.
- **punycode polyfill (React Native/Expo):** `react-native-markdown-display` depends on `markdown-it`, which imports Node.js's `punycode` module. Node 22+ removed it. Fix: `npm install punycode@2.3.1` as a direct dependency. Without this, Metro bundling fails with "Unable to resolve module punycode".
- **ARM64 NDK limitation:** The Android NDK ships x86_64 host binaries only. You CANNOT build native Android code on ARM64 Linux (Apple Silicon, ARM64 VPS) without qemu-user. GitHub Actions runners (x86_64) work fine. If you must build on ARM64, set `hermesEnabled=false` in `android/gradle.properties` to skip the Hermes bytecode compiler (also x86_64-only), but CMake native modules (expo-modules-core, react-native-screens) will still fail. Use x86_64 CI runners.
- **GitHub Actions artifact storage quota:** Free-tier GH accounts have limited artifact storage (~500MB). Uploading APKs can hit this quickly. Instead of `actions/upload-artifact`, use `gh release create --files <apk>` which uses Release storage (separate, much larger quota).
- **Connection UX flow:** Always implement this startup sequence: (1) check saved connection → (2) GET /api/status to detect auth provider → (3) show appropriate login form → (4) authenticate → (5) WS connect → (6) proceed to main UI. Show server info before asking for credentials so the user knows the server is reachable.
- **expo-file-system v57+ API change:** The newer expo-file-system uses a class-based API (`Paths.cache`, `File`, `DownloadTask`) instead of the old `FileSystem.cacheDirectory` and `FileSystem.createDownloadResumable()`. For downloads: `const task = new DownloadTask(url, new File(Paths.cache, 'file.apk'), {}); const result = await task.downloadAsync();`. Progress tracking uses `task.addListener('progress', handler)` not the old callback style.
- **expo-intent-launcher for APK installs:** On Android, after downloading an APK with expo-file-system, install it via `IntentLauncher.startActivityAsync('android.intent.action.INSTALL_PACKAGE', { data: contentUri, flags: 1 })`. The content URI is obtained via `ExpoFileSystem.getContentUriAsync(fileUri)`.
- **Auto-update via GitHub Releases:** Fetch `GET https://api.github.com/repos/<owner>/<repo>/releases/latest`, compare semver, prompt user. Download APK using `DownloadTask`, install using `IntentLauncher`. Track skipped versions in AsyncStorage.

## Reference Files

- `references/json-rpc-protocol.md` — full method catalog, event catalog, payload schemas
- `references/connection-flow.md` — detailed sequence diagram and endpoint reference
- `references/react-native-expo.md` — React Native (Expo) mobile app porting guide: project structure, theme system, tab navigation architecture, auto-update checker, GitHub Actions CI/CD for APK builds, common pitfalls

## See Also

- `hermes-agent` skill — installing, configuring, and running Hermes (the backend side)
- `gateway-adapter-development` skill — writing server-side platform adapters (different concern)
- Official docs: https://hermes-agent.nousresearch.com/docs/developer-guide/programmatic-integration
