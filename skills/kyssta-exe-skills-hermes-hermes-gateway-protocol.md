---
name: hermes-gateway-protocol
description: "Build custom clients against the Hermes tui_gateway JSON-RPC protocol — remote connection, WebSocket transport, auth, and the @hermes/shared client library."
version: 1.0.0
author: agent
license: MIT
---

# Hermes Gateway Protocol

This skill covers the **external protocol** Hermes exposes for remote clients — the `hermes serve` backend, its WebSocket JSON-RPC API, auth flows, and how to build a custom client against it. This is what the Electron desktop app, the web dashboard chat tab, and any third-party client (mobile app, CLI tool, web UI) use to talk to a running Hermes agent on another machine.

**The mobile app does NOT run Hermes locally.** It connects to `hermes serve` on a remote host, same as the desktop app does in remote mode.

## Quick Overview

```
Remote Server (hermes serve --host 0.0.0.0 --port 9119)
├── GET  /api/status          — Server info, auth requirements, gateway state
├── POST /api/auth/login      — Username/password login → session token
├── WS   /api/ws?token=...    — JSON-RPC chat (primary protocol for custom clients)
├── WS   /api/pty?token=...   — PTY terminal bridge (for xterm.js TUI — NOT needed on mobile)
└── (optional) POST /v1/chat/completions  — OpenAI-compatible HTTP API (port 8642)
```

## Starting the Backend

On the remote machine (VPS, home server, Tailscale node):

```bash
# Install the web extra (FastAPI + Uvicorn)
cd ~/.hermes/hermes-agent && uv pip install -e ".[web]"

# Set auth credentials in ~/.hermes/.env
cat >> ~/.hermes/.env <<'EOF'
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=strong-password
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
EOF
chmod 600 ~/.hermes/.env

# Start the backend
hermes serve --host 0.0.0.0 --port 9119
```

The auth gate **automatically engages** when binding to a non-loopback address. Three auth providers:
- **basic** — username/password (set in `.env`, use for trusted networks)
- **oauth** — Nous Portal OAuth (use for public-internet exposure)
- **token** — static `HERMES_DASHBOARD_SESSION_TOKEN` (for programmatic clients)

## Auth Flow

### 1. Check server status
```
GET /api/status
→ {
    "agent_version": "0.18.2",
    "auth_required": true,
    "auth_providers": ["basic"],
    "gateway_running": true,
    "active_sessions": 2,
    "auth_methods": {
      "basic": {"has_username": true}
    }
  }
```

### 2. Login (username/password)
```
POST /api/auth/login
Content-Type: application/json
{"username": "admin", "password": "strong-password"}

→ {"token": "eyJ...", "token_type": "bearer"}
```

### 3. Connect WebSocket
```
new WebSocket("ws://host:9119/api/ws?token=eyJ...")
```

Tokens persist across restarts when `HERMES_DASHBOARD_BASIC_AUTH_SECRET` is a stable value (otherwise the signing key regenerates per boot).

## JSON-RPC Protocol

The `/api/ws` endpoint speaks **newline-delimited JSON-RPC 2.0** over a single persistent WebSocket.

### Request format (client → server)
```json
{"jsonrpc": "2.0", "id": "r1", "method": "prompt.submit", "params": {"message": "Hello"}}
```

### Response format (server → client)
RPC response:
```json
{"jsonrpc": "2.0", "id": "r1", "result": {"session_id": "abc123"}}
```

Error:
```json
{"jsonrpc": "2.0", "id": "r1", "error": {"code": -1, "message": "Something went wrong"}}
```

### Event stream (server → client, no `id` field)
```json
{"jsonrpc": "2.0", "method": "event", "params": {"type": "message.delta", "payload": {"content": "Hello", "session_id": "abc123"}}}
```

### Method catalog

| Method | Params | Returns | Purpose |
|--------|--------|---------|---------|
| `prompt.submit` | `{message, session_id?}` | Stream of events | Send a message to the agent |
| `prompt.background` | `{message, session_id?}` | Stream of events | Background prompt (non-blocking) |
| `session.create` | `{}` | `{session_id, title}` | Create a new session |
| `session.list` | `{limit?, offset?}` | `{sessions: [...]}` | List saved sessions |
| `session.resume` | `{session_id}` | `{history: [...]}` | Resume an existing session |
| `session.close` | `{session_id}` | `{ok: true}` | Close an active session |
| `session.delete` | `{session_id}` | `{ok: true}` | Delete a session |
| `session.history` | `{session_id}` | `{messages: [...]}` | Get full message history |
| `session.title` | `{session_id}` | `{title}` | Generate/refresh title |
| `session.steer` | `{session_id, message}` | Stream of events | Inject message mid-turn |
| `session.interrupt` | `{session_id}` | `{ok: true}` | Stop current turn |
| `session.compress` | `{session_id}` | `{ok: true}` | Compress context |
| `session.branch` | `{session_id}` | `{new_session_id}` | Fork a session |
| `session.status` | `{session_id}` | `{status, usage}` | Session status |
| `session.usage` | `{session_id}` | `{token_count}` | Token usage |
| `session.active_list` | `{}` | `{sessions: [...]}` | Currently open sessions |
| `session.activate` | `{session_id}` | `{ok: true}` | Switch active session |
| `model.list` | `{}` | `{models: [...]}` | Available models |
| `config.get` | `{key?}` | `{config}` | Read config |
| `config.set` | `{key, value}` | `{ok: true}` | Write config |
| `command.dispatch` | `{command}` | Stream of events | Run a slash command |
| `commands.catalog` | `{}` | `{commands: [...]}` | List slash commands |
| `clarify.respond` | `{id, response}` | Continues turn | Answer clarify prompt |
| `approval.respond` | `{id, approved}` | `{ok: true}` | Approve/deny command |
| `sudo.respond` | `{id, password}` | `{ok: true}` | Send sudo password |
| `secret.respond` | `{id, value}` | `{ok: true}` | Supply a secret |
| `delegation.status` | `{}` | `{agents: [...]}` | List subagents |
| `subagent.interrupt` | `{id}` | `{ok: true}` | Stop a subagent |
| `reload.mcp` | `{}` | `{ok: true}` | Reload MCP servers |
| `reload.env` | `{}` | `{ok: true}` | Reload environment |
| `terminal.resize` | `{cols, rows}` | `{ok: true}` | Resize PTY |
| `clipboard.paste` | `{}` | `{text}` | Get clipboard |
| `image.attach` | `{path}` | `{ok: true}` | Attach image |

Full up-to-date catalog: `tui_gateway/server.py` in the hermes-agent source.

### Events streamed back

| Event | Payload | When |
|-------|---------|------|
| `gateway.ready` | `{}` | Backend ready |
| `session.info` | `{session_id, status}` | Session state change |
| `message.start` | `{session_id}` | Assistant started responding |
| `message.delta` | `{content, session_id}` | Streaming text chunk |
| `message.complete` | `{session_id, usage?}` | Message finished |
| `thinking.delta` | `{content, session_id}` | Thinking/reasoning chunk |
| `reasoning.delta` | `{content, session_id}` | Reasoning trace chunk |
| `tool.start` | `{id, name, args, session_id}` | Tool started |
| `tool.progress` | `{id, name, status, session_id}` | Tool progress update |
| `tool.complete` | `{id, name, result, summary?, session_id}` | Tool finished |
| `tool.generating` | `{id, name, session_id}` | Tool generating output |
| `status.update` | `{session_id, status}` | Session status change |
| `clarify.request` | `{id, question, options?, session_id}` | Agent needs clarification |
| `approval.request` | `{id, command, message?, session_id}` | Dangerous command needs approval |
| `sudo.request` | `{id, command, session_id}` | Sudo password needed |
| `secret.request` | `{id, key, prompt?, session_id}` | Secret/credential needed |
| `background.complete` | `{session_id}` | Background task done |
| `error` | `{message, code?, session_id}` | Error occurred |
| `skin.changed` | `{skin, session_id}` | Theme changed |

## Building a WebSocket Client

### Core client pattern (port from @hermes/shared)

The `@hermes/shared` TypeScript package (`apps/shared/src/`) contains the reference `JsonRpcGatewayClient` class. Key design:

1. **Connect** — open WebSocket, wait for `open` event with timeout (default 15s)
2. **Request** — assign an ID, store `{resolve, reject, timer}` in a pending map, send JSON
3. **Response handling** — match incoming `id` to pending call, resolve/reject
4. **Event handling** — frames without `id` but with `method: "event"` and `params.type` dispatch to registered handlers
5. **Disconnect** — reject all pending calls, fire state change
6. **Reconnect** — exponential backoff 1s → 2s → 4s → ... → 30s cap

```typescript
// Minimal example
const ws = new WebSocket("ws://host:9119/api/ws?token=xxx")
const pending = new Map()
let id = 0

ws.onmessage = (msg) => {
  const frame = JSON.parse(msg.data)
  if (frame.id && pending.has(frame.id)) {
    const { resolve, reject, timer } = pending.get(frame.id)
    clearTimeout(timer)
    if (frame.error) reject(new Error(frame.error.message))
    else resolve(frame.result)
  } else if (frame.method === "event" && frame.params?.type) {
    dispatchEvent(frame.params)
  }
}

function call(method, params = {}) {
  const requestId = `r${++id}`
  return new Promise((resolve, reject) => {
    pending.set(requestId, { resolve, reject, timer: setTimeout(() => reject(new Error("timeout")), 120000) })
    ws.send(JSON.stringify({ jsonrpc: "2.0", id: requestId, method, params }))
  })
}
```

### WebSocket URL construction
```
ws://host:port/api/ws?token=<session_token>
wss://host:port/api/ws?token=<session_token>   # if HTTPS
```

Optionally: `?profile=<profile_name>` to target a specific Hermes profile on the backend.

## Remote Connection Setup (End-to-End)

### On the backend:
```bash
# Start the server
hermes serve --host 0.0.0.0 --port 9119
# Keep it running: systemd, tmux, screen, or docker
```

### On the client (any platform):
1. `GET /api/status` — discover auth requirements
2. `POST /api/auth/login` — authenticate (or use pre-set token)
3. Save token to secure storage
4. Open `WebSocket` to `/api/ws?token=<token>`
5. Chat via `prompt.submit`, handle events via `onmessage`

### Auth config on backend:
```bash
# Username/password (trusted networks)
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=<pw>
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)

# Static token (programmatic clients)
HERMES_DASHBOARD_SESSION_TOKEN=my-token

# OAuth (public internet — requires hermes dashboard register)
# Run: hermes dashboard register --redirect-uri https://your-domain.com/auth/callback
```

## API Server (Alternative: OpenAI-Compatible HTTP)

The gateway can also serve an OpenAI-compatible HTTP API on port 8642:

```bash
# Enable in ~/.hermes/.env
API_SERVER_ENABLED=true
API_SERVER_KEY=my-api-key
```

Endpoints:
- `POST /v1/chat/completions` — streaming SSE chat completions
- `POST /v1/responses` — stateful responses API
- `GET /v1/models` — list models
- `POST /v1/runs` — long-running sessions
- `GET /v1/runs/{id}/events` — SSE lifecycle events

Best for: OpenAI-compatible frontends (Open WebUI, LobeChat, LibreChat).
Not as feature-rich as JSON-RPC WebSocket (no real-time tool events, no interrupt handling).

## Pitfalls

- **`hermes serve` is required.** The desktop app's local backend and the remote backend are the same `hermes serve` process. A running `hermes gateway` is NOT enough — the messaging gateway is a separate process.
- **Auth gate engages automatically on non-loopback bind.** `--host 0.0.0.0` always requires auth. Use `--host 127.0.0.1` + Tailscale for trusted-network-only access without auth.
- **Token signing key regenerates per boot without `HERMES_DASHBOARD_BASIC_AUTH_SECRET`.** Set a stable random value to keep sessions alive across restarts.
- **WebSocket close codes matter.** The desktop app has close-code triage for error reporting. Expect 4401 for auth failure, 1011 for internal error.
- **The `@hermes/shared` library is framework-agnostic TypeScript.** It works in React Native, web, and Node.js — no DOM dependency. Import directly from `apps/shared/src/`.
- **For mobile: use `/api/ws`, NOT `/api/pty`.** The PTY endpoint is for xterm.js terminal rendering. Mobile apps should use the structured JSON-RPC protocol.

## Verification

After starting `hermes serve`, verify the backend is reachable:

```bash
# Check status
curl -s http://127.0.0.1:9119/api/status | jq .

# Login (if using basic auth)
curl -s -X POST http://127.0.0.1:9119/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "test"}' | jq .

# The mobile app/desktop app now connects via WebSocket
```

## References

- `references/gateway-protocol-reference.md` — Full method/event catalog with payload schemas
- `references/react-native-port.md` — Porting guide for React Native (Expo) clients: stack choices, Metro bundler issues, expo-file-system v57+ API, GitHub Actions CI/CD patterns, Hermes bytecode on ARM64, auto-update via releases, theme porting
