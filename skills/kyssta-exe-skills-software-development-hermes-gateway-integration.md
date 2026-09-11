---
name: hermes-gateway-integration
description: "Build clients that connect to Hermes Agent via the tui_gateway JSON-RPC WebSocket protocol — mobile apps, web clients, custom UIs, and automations that drive a remote Hermes backend."
version: 1.0.0
author: Hermes Agent
metadata:
  hermes:
    tags: [hermes, gateway, websocket, json-rpc, mobile, client, integration, protocol]
    related_skills: [hermes-agent]
---

# Hermes Gateway Integration

Guide for building clients that connect to a Hermes Agent backend remotely using the tui_gateway JSON-RPC WebSocket protocol. The same protocol the Hermes desktop app and web dashboard chat tab use.

**Core principle: the client is a thin WebSocket client.** No agent runs on the client device. The heavy lifting (LLM, tools, skills, memory) happens on the remote `hermes serve` backend.

## Architecture

```
Client (React Native, Web, CLI, etc.)          Remote Server
┌────────────────────────────┐                ┌──────────────────────┐
│  JsonRpcGatewayClient      │  WebSocket     │  hermes serve        │
│  (JSON-RPC over WS)        │───────────────▶│  /api/ws             │
│                            │                │  /api/auth/login     │
│  Auth: token/password      │                │  /api/status         │
│  Events: message.delta,    │                │                      │
│  tool.start/complete,      │                │  AIAgent + Tools     │
│  clarify/approval.request  │                │  + Skills + Memory   │
└────────────────────────────┘                └──────────────────────┘
```

## Backend Setup

On the remote machine, run:

```bash
hermes serve --host 0.0.0.0 --port 9119
```

This starts a headless FastAPI server. When bound to a non-loopback address, auth is automatically required.

### Auth Configuration

Two providers:

**Username/Password** (trusted networks only):
```bash
cat >> ~/.hermes/.env <<'EOF'
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=strong-password
HERMES_DASHBOARD_BASIC_AUTH_SECRET=$(openssl rand -base64 32)
EOF
```

**OAuth (Nous Portal)** (public/VPS backends):
```bash
hermes dashboard register
```

### Required Extras
The `[web]` extra must be installed for `hermes serve`:
```bash
cd ~/.hermes/hermes-agent && uv pip install -e ".[web]"
```
The `[pty]` extra is for the browser TUI (not needed for JSON-RPC chat clients).

## Client Connection Flow

1. **GET /api/status** → detect server version, auth providers, gateway state
2. **Authenticate** → obtain session token:
   - Username/password: `POST /api/auth/login` with `{username, password}` → `{token}`
   - Static token: use `HERMES_DASHBOARD_SESSION_TOKEN` from backend .env
3. **WebSocket connect** → `ws://host:port/api/ws?token=<token>`
4. **JSON-RPC** → send requests, receive streaming events
5. **Reconnect** on disconnect with exponential backoff (1s → 2s → 4s → ... → 30s)

### Token Storage
Store tokens in encrypted storage (e.g. `expo-secure-store` on mobile, `Keychain` on desktop). Never persist in plain text or logs.

## JSON-RPC Protocol

The tui_gateway speaks JSON-RPC 2.0 over WebSocket. Full method/event catalog in `references/json-rpc-protocol.md`.

### Common Methods

| Method | Purpose |
|--------|---------|
| `prompt.submit` | Send a message to the agent (returns streaming events) |
| `session.create` | Create a new conversation session |
| `session.list` | List recent sessions |
| `session.resume` | Load a session's history |
| `session.delete` | Delete a session |
| `session.interrupt` | Stop the current turn |
| `command.dispatch` | Execute a slash command (/model, /clear, etc.) |
| `clarify.respond` | Answer a clarification prompt |
| `approval.respond` | Approve/deny a dangerous command |

### Common Events (Server→Client)

| Event | Payload | When |
|-------|---------|------|
| `message.delta` | `{content, session_id}` | Streaming text chunk |
| `tool.start` | `{id, name, args}` | Tool execution started |
| `tool.complete` | `{id, name, result}` | Tool finished |
| `clarify.request` | `{id, question, options}` | Agent needs input |
| `approval.request` | `{id, command, message}` | Dangerous command needs OK |

### Key Implementation Details

- **Streaming**: `message.delta` events arrive in sequence. Accumulate the `content` field and display incrementally. A trailing cursor/blinking indicator signals "more coming".
- **Tool calls**: `tool.start` → tool name/status shown → `tool.complete` → result summarized. Mobile clients should show a compact inline card, not full tool output.
- **Interrupts**: `clarify.request`, `approval.request`, `sudo.request`, `secret.request` all require a response before the agent continues. Show as native modal sheets on mobile.
- **Connection state**: Track `idle → connecting → open → closed → error`. Show persistent indicator. Auto-reconnect on closed/error.

## Auth Endpoint Discovery

```
GET /api/status
→ {
    "agent_version": "0.18.2",
    "auth_required": true,
    "auth_providers": ["basic"],
    "gateway_running": true,
    "active_sessions": 2
  }
```

Use this to detect which auth provider to show the user (password form vs OAuth button).

## WebSocket URL Construction

For a backend at `http://host:9119`:
```
ws://host:9119/api/ws?token=<session_token>
```

For HTTPS backends:
```
wss://host:9119/api/ws?token=<session_token>
```

## Platform Plugin vs Standalone Client

Two ways to wire a new platform into Hermes. Choose based on what you're building:

| Dimension | Platform Plugin (`~/.hermes/plugins/<name>/`) | Standalone Bridge Client |
|-----------|-----------------------------------------------|--------------------------|
| **Architecture** | Subclass of `BasePlatformAdapter`, lives inside the gateway process | External daemon, connects to `hermes serve` over WS JSON-RPC |
| **Door to door** | ~500 lines (adapter + bridge subprocess) | ~300 lines (full WS client + session mgmt) |
| **Features** | Sessions, slash commands, auth, cron delivery, tool events in chat, clarify/approval — all free from the gateway | Everything you build yourself — raw `prompt.submit` + event handlers |
| **State management** | Gateway handles per-user sessions, thread tracking, message batching | You manage `session_id` mapping, reconnect state, message queue |
| **When to use** | A **messaging platform** (Discord, Telegram, Minecraft, IRC, etc.) — users chat with the bot | A **custom UI/automation** (mobile app, web dashboard, game overlay, telemetry display) — anything that isn't a multi-user chat surface |

**Rule of thumb:** If people will talk to the bot from the platform itself (chat messages, DMs, group channels), write a plugin. If the user interacts through a separate UI/dashboard that you control, write a standalone client.

## Platform Plugin Pattern

A Hermes platform plugin lives at `~/.hermes/plugins/<name>/` and is auto-discovered by `discover_plugins()`.

### Minimum file structure

```
~/.hermes/plugins/<name>/
├── plugin.yaml         # Metadata + env var definitions
├── __init__.py         # `from .adapter import register`
└── adapter.py          # Adapter class + register(ctx)
```

### The adapter.py skeleton

```python
from gateway.platforms.base import BasePlatformAdapter, SendResult, MessageEvent, MessageType
from gateway.config import Platform

class MyAdapter(BasePlatformAdapter):
    def __init__(self, config, **kwargs):
        # Dynamic enum value — Platform._missing_() handles plugin names
        platform = Platform("my_platform")
        super().__init__(config=config, platform=platform)
        # Parse config.extra + env vars
        self.host = config.extra.get("host") or os.getenv("MY_HOST", "")

    async def connect(self, *, is_reconnect=False) -> bool:
        self._mark_connected()
        return True

    async def disconnect(self):
        pass

    async def send(self, chat_id, content, reply_to=None, metadata=None, **kwargs) -> SendResult:
        # SIGNATURE: must match BasePlatformAdapter.send(self, chat_id, content, reply_to, metadata)
        # The parameter is `content`, NOT `text` — using `text` causes TypeError at runtime
        # Chunk at platform limit if needed
        return SendResult(True)

    async def send_private_notice(self, chat_id, user_id, content,
                                  reply_to=None, metadata=None) -> SendResult:
        """Called for tool progress / notices when notice_delivery=private.
        Override to send via platform's private message mechanism (/tell, DM, etc.).
        Default falls back to public send()."""
        return await self.send(chat_id, content, reply_to, metadata)

    async def send_typing(self, chat_id):
        # Use only ASCII-safe text — emoji/unicode can kick bots on strict servers
        pass

    async def get_chat_info(self, chat_id) -> dict:
        return {"name": chat_id, "type": "dm", "chat_id": chat_id}

    async def _on_inbound(self, user, text):
        source = self.build_source(
            chat_id=user.lower(), chat_name=user,
            chat_type="dm", user_id=user.lower(), user_name=user,
        )
        event = MessageEvent(text=text, source=source, message_type=MessageType.TEXT)
        await self.handle_message(event)

def check_requirements() -> bool:
    return True

def _env_enablement() -> dict | None:
    if os.getenv("MY_ENABLED", "").lower() not in ("true", "1", "yes"):
        return None
    # Set notice_delivery=private to route tool progress through
    # send_private_notice() instead of public send()
    return {
        "extra": {
            "host": os.getenv("MY_HOST", ""),
            "notice_delivery": os.getenv("MY_NOTICE_DELIVERY", "public"),
        },
        "home_channel": None,
    }

def register(ctx):
    ctx.register_platform(
        name="my_platform", label="My Platform",
        adapter_factory=lambda cfg: MyAdapter(cfg),
        check_fn=check_requirements,
        required_env=["MY_ENABLED", "MY_HOST"],
        env_enablement_fn=_env_enablement,
        allowed_users_env="MY_ALLOWED_USERS",
        allow_all_env="MY_ALLOW_ALL_USERS",
        max_message_length=256,
        emoji="📡", pii_safe=True,
        platform_hint="You are on My Platform. Plain text only.",
    )
```

### Subprocess bridge pattern (platforms with non-Python SDKs)

When the platform's SDK is Node.js (Mineflayer, whatsapp-web.js, etc.) or another language:

1. The Python adapter spawns a subprocess running the platform SDK
2. The subprocess runs an HTTP server on a local port (e.g. `/health`, `/messages`, `/send`)
3. Python polls `GET /messages` for inbound events
4. Python `POST /send` for outbound messages
5. The bridge's stderr goes to `~/.hermes/logs/<platform>-bridge.log`

```
Python Adapter                          Node.js Bridge
  subprocess.Popen ───────────────────►  http server :PORT
  poll GET /messages ◄────────────────  chat events queue
  POST /send ─────────────────────────► bot.chat(text)
  check GET /health ◄─────────────────  {status, players}
```

Full implementation: `references/subprocess-bridge-pattern.md`

## Reference: Shared Client Library

The Hermes agent repo (`apps/shared/src/`) contains a framework-agnostic `JsonRpcGatewayClient` class that handles:
- WebSocket connection with configurable timeout (default 15s)
- JSON-RPC request/response routing with per-request timeout (default 120s)
- Event dispatch with typed event names
- Connection state tracking (idle/connecting/open/closed/error)
- Request ID generation with configurable prefix

This can be ported directly into any TypeScript client (React Native, React, Node.js).

Files to port:
- `apps/shared/src/json-rpc-gateway.ts` — the client class
- `apps/shared/src/websocket-url.ts` — URL builder utilities
- `apps/shared/src/index.ts` — exports

## Pitfalls

### Gateway (server-side) pitfalls

- **`send()` parameter is `content`, not `text`**: The base class signature is `send(self, chat_id, content, reply_to=None, metadata=None)`. Using `text` as the parameter name causes `TypeError: missing 1 required positional argument: 'text'` at runtime because the gateway calls it as `send(chat_id=..., content=...)`.
- **Subprocess stdout PIPE must be read or redirected**: When spawning a Node.js bridge with `stdout=subprocess.PIPE`, the pipe buffer fills (~64KB) and Node.js blocks — no chat events, no movement, nothing. Always redirect stdout to a log file (`stdout=log_fh, stderr=subprocess.STDOUT`) or read it periodically. The bridge's `console.log()` / `process.stdout.write()` output will block if the pipe isn't drained.
- **`platform_hint` is taken literally by the LLM**: If the hint says "you can use § codes for formatting", the LLM will use them — even if the server rejects them as illegal characters. Keep the hint conservative: "Plain text only. No markdown, no formatting codes."
- **`send_typing` emoji can kick bots**: Minecraft and other strict servers reject non-ASCII characters. `🤔 Thinking...` becomes "Illegal characters in chat" → disconnect. Use plain ASCII text like `"Thinking..."`.
- **`notice_delivery` controls tool progress routing**: Set `notice_delivery: private` in the extra config to route tool progress through `send_private_notice()`. Otherwise notices go to public `send()`.
- **Prefix should be optional, not a gate**: If you set a command prefix (e.g. `$` for `$new`), don't skip messages that don't have it. Strip the prefix when present, but forward all messages. Users should be able to both chat normally and use commands.
- **`max_message_length` must be set**: Pass it to `ctx.register_platform(max_message_length=N)`. The gateway uses it for the default chunk size. Missing it means no chunking, and messages > platform limit get truncated or rejected.

### Client-side pitfalls

- **WebSocket not HTTP**: Don't use standard HTTP fetch for real-time chat. The `/api/ws` WebSocket is the only path that gets streaming deltas and tool events.
- **No xterm/PTY needed**: Mobile clients should use `/api/ws` (structured JSON-RPC), NOT `/api/pty` (which is for xterm.js terminal emulation in the browser dashboard).
- **Reconnect on mobile**: Mobile networks drop WebSocket connections frequently. Always implement auto-reconnect with exponential backoff and message queue.
- **Auth token rotation**: OAuth tokens may expire. Handle `401`/reauth gracefully by catching WS close codes and triggering re-login.
- **punycode polyfill**: In React Native/Expo, `markdown-it` imports `punycode` (removed in Node.js 22). Install `punycode@2.3.1` as a direct dependency to fix Metro bundler errors.
- **ARM64 vs x86_64 builds**: Android NDK toolchains are x86_64 only. Building on ARM64 Linux (Apple Silicon, ARM64 VPS) requires either qemu-user, prebuilt ARM64 NDK, or skipping native modules. GitHub Actions runners (x86_64) work without issues.
- **GitHub Actions artifact storage**: Free-tier accounts have limited artifact storage. Use `gh release create --files <apk>` instead of `actions/upload-artifact` to upload APKs to Releases (separate quota).

## Standalone Bridge Clients

For building a **headless daemon** that bridges an external platform (Minecraft,
IRC, game servers, telemetry dashboards) to Hermes via the WebSocket JSON-RPC
protocol — without React Native, Electron, or a web UI. The client is a thin
relay: connect to `hermes serve`, forward inbound messages as `prompt.submit`,
stream `message.delta`/`message.complete` events back to the external platform.

Typical stack: **Node.js + platform SDK** (e.g. Mineflayer for Minecraft).

```
External Platform    Node.js Bridge Daemon          Hermes Backend
                    ┌─────────────────────┐
Platform SDK ◄─────►│  PlatformClient     │         hermes serve
(native protocol)  │  + SessionManager   │◄──WS──► :9119
                   │  + HermesClient     │        JSON-RPC
                   └─────────────────────┘
```

Key differences from mobile/web clients:
- No user-facing UI — runs as a daemon/service alongside `hermes serve`
- Platform message limits (Minecraft 256 chars, IRC 512 bytes) → chunking
- No typing indicators on many platforms → wait for `message.complete`
- Per-user session mapping persisted to JSON file

Full guide and code snippets: `references/standalone-bridge-client.md`

## See Also

- `references/json-rpc-protocol.md` — Full method catalog and event reference
- `references/standalone-bridge-client.md` — Headless daemon bridge pattern (Minecraft, IRC, game servers)
- `references/subprocess-bridge-pattern.md` — Python adapter spawning a Node.js/etc subprocess for platforms without Python SDKs
- `references/plugin-debugging-checklist.md` — Debugging checklist for common plugin failures (send signature, pipe blocking, illegal characters, regex escapes, platform hint gotchas)
- `skill_view(name="hermes-agent")` — General Hermes Agent setup and configuration
- [Hermes Gateway docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/gateway)
- [Programmatic Integration docs](https://hermes-agent.nousresearch.com/docs/developer-guide/programmatic-integration)
