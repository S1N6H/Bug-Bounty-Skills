---
name: hermes-mobile-development
description: "Build native mobile clients (iOS/Android) that connect remotely to a Hermes Agent backend via WebSocket JSON-RPC."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mobile, react-native, expo, android, websocket, json-rpc, hermes-client, dashboard-api, icons]
    related_skills: [hermes-agent]
---

# Hermes Mobile Client Development

Building a mobile app that connects to a Hermes Agent backend running on another machine. The mobile app is a **thin client** — it connects to `hermes serve` via WebSocket JSON-RPC and never runs the agent locally.

## Architecture

```
Phone (React Native + Expo)          Remote Server (hermes serve)
┌─────────────────────────────┐       ┌──────────────────────────────┐
│  GatewayClient (WS client)  │  WS   │  /api/ws (JSON-RPC)          │
│  Dashboard REST API client  │ HTTP  │  /api/model/info             │
│  Zustand stores             │───────│  /api/analytics/models       │
│  React Native UI            │       │  /api/model/options          │
│  expo-secure-store (tokens) │       │  /api/status                 │
└─────────────────────────────┘       │  AIAgent + Tools + Memory   │
                                      └──────────────────────────────┘
```

### The Backend: `hermes serve`

On the remote machine, the user runs:
```bash
hermes serve --host 0.0.0.0 --port 9119
```

This starts a headless FastAPI server. The desktop app spawns this locally; mobile connects to it remotely.

### Key Endpoints

| Endpoint | Purpose | Auth |
|----------|---------|------|
| `GET /api/status` | Server info, auth status, gateway state | Public |
| `POST /api/auth/login` | Login (username/password) | Public |
| `WS /api/ws?token=...` | JSON-RPC chat WebSocket | Token via ?token= |
| `GET /api/model/info` | Current main model + capabilities | Public (in public_paths) |
| `GET /api/model/options` | Available providers + models | Gated |
| `GET /api/model/auxiliary` | Auxiliary task config | Gated |
| `GET /api/model/moa` | Mixture of Agents config | Gated |
| `GET /api/analytics/models` | Per-model usage analytics | Gated |
| `POST /api/model/set` | Change active model | Requires token |

## Authentication & WebSocket Connection

### Auth Gate Modes

`hermes serve` has three auth modes determined by the bind address:

1. **Loopback** (`--host 127.0.0.1`): `?token=<_SESSION_TOKEN>` accepted on WS. Auto-generated or set via `HERMES_DASHBOARD_SESSION_TOKEN` env var. Only loopback clients allowed.
2. **Insecure** (`--host 0.0.0.0 --insecure`): Same as loopback but any peer allowed. **Deprecated.**
3. **Gated** (non-loopback bind without --insecure): Auth gate engages. Only `?ticket=<single-use>` or `?internal=<process-credential>` accepted. **`?token=` is rejected by default.**

### For Native Mobile Clients

Since React Native WebSocket cannot set custom HTTP headers (Authorization, X-Hermes-Session-Token), the `?token=` query parameter is needed. This requires **patching the server** to accept `?token=` in gated mode (see reference `server-auth-gate-patch.md`).

**For HTTP REST dashboard endpoints** (model info, analytics, aux config), the same `X-Hermes-Session-Token` header works — but only if you also patch the server's `_require_token()` function to accept it in gated mode (see reference `server-auth-gate-patch.md#rest-api-auth-patch`).

**Alternatively**, add the needed endpoints to `PUBLIC_API_PATHS` in `dashboard_auth/public_paths.py` to bypass auth entirely (only safe for read-only data).

### Setting the Session Token

```bash
export HERMES_DASHBOARD_SESSION_TOKEN=your-token-here
hermes serve --host 0.0.0.0 --port 9119
```

The token is read at process start. Must be passed via environment variable.

## WS JSON-RPC Protocol

### Connection
```
ws://host:9119/api/ws?token=<session_token>
```

### Request → Response (JSON-RPC 2.0)
```json
→ {"jsonrpc":"2.0","id":1,"method":"prompt.submit","params":{"message":"Hello"}}
← {"jsonrpc":"2.0","result":{...},"id":1}
```

### Methods

| Method | Purpose |
|--------|---------|
| `prompt.submit` | Send a message (streams events back) |
| `session.create` | Create new session |
| `session.list` | List recent sessions |
| `session.resume` | Load session history |
| `session.delete` | Delete sessions |
| `session.history` | Get full message history |
| `session.steer` | Inject message mid-turn |
| `session.interrupt` | Stop current turn |
| `session.compress` | Compress context |
| `model.list` | List models |
| `config.get` / `config.set` | Read/write config |
| `command.dispatch` | Execute slash command (/model, /clear, etc.) |
| `commands.catalog` | List available slash commands |
| `status` | Get server status |
| `clarify.respond` | Answer clarification prompt |
| `approval.respond` | Approve/deny dangerous command |

### Events Streamed Back

| Event | When |
|-------|------|
| `gateway.ready` | Connection established |
| `message.delta` | Streaming text chunk |
| `message.complete` | Message finished |
| `tool.start` | Tool started |
| `tool.progress` | Tool progress update |
| `tool.complete` | Tool finished |
| `clarify.request` | Agent needs clarification |
| `approval.request` | Command needs approval |
| `sudo.request` | Sudo access needed |
| `secret.request` | Secret needed |

### Key Implementation Detail: Auto-Finalize Streaming Content

The RPC `prompt.submit` may resolve before `message.complete` fires. Always add a fallback after the RPC resolves that waits ~500ms and finalizes any remaining streaming content into a message:

```typescript
await client.request('prompt.submit', { message: content, session_id })
await new Promise(r => setTimeout(r, 500))
const state = get()
if (state.isStreaming && state.streamingContent) {
  // Finalize assistant message from streaming content
}
```

## WebSocket Close Codes

| Code | Meaning |
|------|---------|
| 4401 | Authentication failed — bad session token |
| 4403 | Access denied — server rejected connection |
| 1006 | Connection dropped — network/firewall blocking WS |

## REST Dashboard API Client Pattern

For dashboard features, create a REST API client that uses the session token:

```typescript
import { useConnectionStore } from '../stores/connection'

function fetchApi<T>(path: string): Promise<T> {
  const baseUrl = useConnectionStore.getState().backendUrl.replace(/\/+$/, '')
  const token = useConnectionStore.getState().token
  const headers: Record<string, string> = {}
  if (token) headers['X-Hermes-Session-Token'] = token
  return fetch(`${baseUrl}${path}`, { headers }).then(r => {
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    return r.json()
  })
}
```

Key endpoints for dashboard features:

| Path | Data |
|------|------|
| `/api/model/info` | Current model, provider, capabilities |
| `/api/model/options` | All providers with their model lists |
| `/api/model/auxiliary` | Auxiliary task definitions |
| `/api/model/moa` | Mixture of Agents config |
| `/api/analytics/models?days=30` | Per-model analytics (sessions, tokens, costs) |
| `/api/status` | Gateway status, version, active sessions |

## Android-Specific Configuration

### Cleartext Traffic
Android 9+ blocks plain HTTP by default. Add to `AndroidManifest.xml`:
```xml
<application android:usesCleartextTraffic="true" ...>
```
This applies to both HTTP fetch calls AND WebSocket connections.

### WebSocket on React Native
- React Native uses OkHttp for WebSocket on Android
- Cannot set custom HTTP headers on WebSocket upgrade
- Must use `?token=` query parameter instead
- WS to raw IP addresses may be blocked on some mobile carriers

## UI / UX Preferences

### Icon Library: @expo/vector-icons / Ionicons
Use `@expo/vector-icons` (Ionicons) for all icons — **never use emoji characters** (☰, ⚙, 👁, 🙈, etc.). Emoji rendering varies by platform and looks unprofessional. Always import from `react-native`:

```typescript
import { Ionicons } from '@expo/vector-icons'
// Usage: <Ionicons name="menu" size={22} color="#fff" />
```

Common icon mappings:

| Purpose | Ionicon Name |
|---------|-------------|
| Menu / hamburger | `menu` |
| Settings | `settings-outline` / `settings` |
| Chat | `chatbubble-outline` / `chatbubble` |
| Dashboard | `bar-chart-outline` / `bar-chart` |
| Eye (show) | `eye` |
| Eye (hide) | `eye-off` |
| Key | `key` / `key-outline` |
| Flash / connect | `flash` |
| Star (main model) | `star` |
| Grid (aux tasks) | `grid` |
| Network (MOA) | `git-network` |
| Server | `server` |
| Cube (models) | `cube` |
| Apps (model grid) | `apps` |
| Analytics | `analytics` |
| Refresh | `refresh` |

### Keyboard Handling
Wrap chat screens in `KeyboardAvoidingView` at the root level (not just the composer):
```tsx
<KeyboardAvoidingView
  style={{ flex: 1 }}
  behavior={Platform.OS === 'ios' ? 'padding' : undefined}
  keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
>
  {/* Full screen content */}
</KeyboardAvoidingView>
```

### Token / Password Visibility Toggle
Always provide eye/eye-off toggle for masked inputs:
```tsx
const [visible, setVisible] = React.useState(false)
<TextInput secureTextEntry={!visible} />
<TouchableOpacity onPress={() => setVisible(!visible)}>
  <Ionicons name={visible ? 'eye-off' : 'eye'} size={20} />
</TouchableOpacity>
```

## Common Pitfalls

1. **WS connects locally but not from phone**: Mobile carrier or corporate proxy blocking WebSocket upgrades on non-standard ports. Try WiFi vs mobile data, or use a Cloudflare tunnel / ngrok for `wss://`.
2. **`?token=` gets 403 on gated server**: The server must be patched to accept `?token=` in gated mode (see `server-auth-gate-patch.md` reference).
3. **REST endpoints return 401 even with token**: In gated mode, `_require_token()` short-circuits to check `request.state.session` only — patch it to also check `_has_valid_session_token()`.
4. **"Hermes vundefined"**: Server status returns `version` field, not `agent_version`.
5. **CLEARTEXT communication not permitted**: Add `android:usesCleartextTraffic="true"` to manifest.
6. **WebSocket connection timeout**: Increase connect timeout to 30s for mobile networks. Check firewall rules.
7. **"Connection failed" with no detail**: Capture WebSocket close codes (`event.code`) for proper diagnosis (4401=bad token, 1006=network issue).

## GitHub CI/CD for APK

```yaml
# Key workflow steps:
- Setup Node.js + Java 17
- npm ci
- npx tsc --noEmit
- npx expo prebuild --platform android
- cd android && ./gradlew assembleRelease --no-daemon
- gh release create <tag> --prerelease <apk>
```

- APK output: `android/app/build/outputs/apk/release/app-release.apk`
- Upload directly to GitHub Releases (not artifact storage — quota limits)
- Clean old releases: `gh release delete <tag> --yes --cleanup-tag`
