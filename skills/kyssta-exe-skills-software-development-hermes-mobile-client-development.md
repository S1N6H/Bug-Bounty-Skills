---
name: hermes-mobile-client-development
description: "Building native mobile clients (React Native / Expo) that connect to a remote Hermes Agent gateway via WebSocket JSON-RPC."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [darwin, linux]
metadata:
  hermes:
    tags: [hermes, mobile, react-native, expo, websocket, gateway, android]
    related_skills: [hermes-agent]
---

# Hermes Mobile Client Development

How to build a React Native (Expo) app that connects to a remote `hermes serve` backend — same pattern as the Electron desktop app.

## Architecture

```
Phone (React Native / Expo)
  └── GatewayClient (ported from @hermes/shared)
       └── WebSocket /api/ws?token=<session_token>
            └── hermes serve (Python FastAPI)
                 └── tui_gateway JSON-RPC
                      └── AIAgent core
```

The mobile app is a **thin client** — no Hermes agent runs on the phone. It connects to an existing `hermes serve` process running on a remote machine (VPS, home server, etc.).

## Protocol: tui_gateway JSON-RPC

The same protocol the TUI, desktop app, and web dashboard chat use.

**Connect:** `ws://<host>:9119/api/ws?token=<session_token>`

**Methods (request → response):**
| Method | Purpose |
|--------|---------|
| `prompt.submit` | Send a message, receive streaming deltas |
| `session.create` / `.list` / `.resume` / `.delete` | Session CRUD |
| `session.history` | Get full conversation history |
| `command.dispatch` | Execute a slash command (e.g. `/model`) |
| `model.list` / `model.switch` | Model management |
| `clarify.respond` / `approval.respond` | Handle human-in-the-loop interrupts |
| `status` | Get server info |

**Events received (server → client):**
`message.delta`, `message.complete`, `tool.start`, `tool.progress`, `tool.complete`, `clarify.request`, `approval.request`, `sudo.request`, `secret.request`

## WebSocket Auth: The Critical Detail

`hermes serve` bound to a non-loopback IP engages auth-gate mode. The `/api/ws` endpoint then accepts credentials in this order:

1. `?internal=<process-credential>` — server-spawned children only
2. `?ticket=<single-use>` — browser SPA (minted via POST /api/auth/ws-ticket)
3. `?token=<_SESSION_TOKEN>` — **EXPLICITLY REJECTED in gated mode** (line ~14320)

This means a React Native WebSocket client sending `?token=` will get **403 Forbidden** by default. The fix is to patch `_ws_auth_reason()` in `hermes_cli/web_server.py` to also accept `?token=` in gated mode — see `references/hermes-ws-auth-patch.md`.

**Alternative:** Use username/password auth (POST /api/auth/login → get a session cookie), or set up OAuth (Nous Portal). The session token approach is simplest for testing.

## Key Libraries for Mobile App

| Layer | Library |
|-------|---------|
| Framework | React Native (Expo) |
| State | Zustand |
| WebSocket | Native WebSocket (wrapped in GatewayClient) |
| Secure storage | expo-secure-store |
| Async storage | @react-native-async-storage/async-storage |
| File system | expo-file-system (v57+: File, Directory, Paths, DownloadTask) |
| Intent launcher | expo-intent-launcher |
| Image picker | expo-image-picker |
| Notifications | expo-notifications |
| Markdown | react-native-markdown-display (+ punycode polyfill for Node 22+) |
| Icons | @expo/vector-icons (Ionicons) — use proper icons throughout, never emoji text for UI elements |

## UI & UX Conventions

### Icons: always use Ionicons, never emoji text

Use `@expo/vector-icons` Ionicons for ALL interface elements. Never use emoji characters (☰, ⚙, 👁, 🙈, 💬, etc.) as icons — they render inconsistently across platforms and look unprofessional.

```tsx
import { Ionicons } from '@expo/vector-icons'

// ✅ RIGHT
<Ionicons name="menu" size={22} color={theme.colors.textPrimary} />
<Ionicons name="eye" size={20} color={theme.colors.textSecondary} />
<Ionicons name="eye-off" size={20} color={theme.colors.textSecondary} />

// ❌ WRONG
<Text>☰</Text>
<Text>👁</Text>
```

Common icons map:
| Element | Ionicons name |
|---------|---------------|
| Menu/hamburger | `menu` |
| Chat tab | `chatbubble` / `chatbubble-outline` |
| Dashboard tab | `bar-chart` / `bar-chart-outline` |
| Settings tab | `settings` / `settings-outline` |
| Eye (show) | `eye` |
| Eye (hidden) | `eye-off` |
| Key/auth | `key` / `key-outline` |
| Send | `flash` |
| Close | `close` |
| Delete | `trash-outline` |
| Streaming | `pulse` |

### Password/Token input with visibility toggle

Both password and session token fields should have an inline eye/eye-off toggle so users can verify what they typed. Wrap the `TextInput` in a `View` with `flexDirection: 'row'` and place the toggle button at the trailing edge. Use `secureTextEntry={!visible}` with a `visible` boolean state.

### Keyboard handling on iOS

Wrap the entire screen (not just the composer) in `KeyboardAvoidingView`:

```tsx
<KeyboardAvoidingView
  style={{ flex: 1 }}
  behavior={Platform.OS === 'ios' ? 'padding' : undefined}
  keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
>
  {/* screen content — header, messages, composer */}
</KeyboardAvoidingView>
```

On iOS, `behavior='padding'` with a 90px offset accounts for the header+status bar. On Android, avoid `behavior='height'` — it causes layout jumps. Let Android handle it natively with `android:windowSoftInputMode="adjustResize"` (default in Expo).

## State Management Pattern

```
ConnectionStore (Zustand)        ChatStore (Zustand)
  ├─ backendUrl                    ├─ sessions
  ├─ token                         ├─ messages
  ├─ connectionState               ├─ isStreaming
  ├─ serverStatus                  ├─ streamingContent
  ├─ client (GatewayClient)        ├─ currentToolCalls
  ├─ connect() / disconnect()      ├─ sendMessage()
  └─ reconnect()                   └─ loadSessionHistory()
```

- `GatewayClient` is a singleton managed by ConnectionStore
- `useGatewayEvents()` hook wires GatewayClient events → ChatStore actions
- Reconnection uses exponential backoff (1s → 2s → 4s → ... → 30s max)

## CI/CD for APK Builds

GitHub Actions workflow builds on `ubuntu-latest` (x86_64):

```yaml
- name: Setup Java (JDK 17)
  uses: actions/setup-java@v4
  with:
    distribution: 'temurin'
    java-version: '17'

- run: cd android && ./gradlew assembleRelease --no-daemon

# Enable Hermes on CI (x86_64 hermesc)
- run: sed -i 's/hermesEnabled=false/hermesEnabled=true/' android/gradle.properties

# Upload directly to release (not artifact storage — quota limits)
- run: gh release create "$TAG" --prerelease "$APK_NAME.apk"
```

**ARM64 gotchas:** Android NDK + CMake + Hermes compiler are x86_64-only. Gradle native builds (expo-modules-core, react-native-screens) fail on ARM64. Always build APKs on x86_64 runners or use EAS Build.

## App Structure

```
app/                  # Expo Router pages
  (tabs)/
    chat.tsx          # Chat tab
    dashboard.tsx     # Dashboard tab (status, sessions)
    settings.tsx      # Settings tab (connection, themes)
  connect.tsx         # Connection setup screen
  _layout.tsx         # Auth gate + theme provider
src/
  lib/
    gateway-client.ts # Port of @hermes/shared JsonRpcGatewayClient
    websocket-url.ts  # WS URL builder (buildChatWsUrl, etc.)
    auth.ts           # loginWithPassword, checkServerStatus
    update-checker.ts # GitHub releases auto-update
  stores/
    connection.ts     # Zustand — connection + client
    chat.ts           # Zustand — messages + sessions + streaming
  hooks/
    useGateway.ts     # Wires events → stores, auto-reconnect
  components/
    chat/MessageList.tsx, Composer.tsx, SessionSwitcher.tsx
    ui/Themed.tsx     # ThemedView, ThemedButton, StatusBadge, etc.
  screens/
    ConnectScreen.tsx, ChatScreen.tsx, DashboardScreen.tsx, SettingsScreen.tsx
  theme/
    themes.ts         # 7 themes (Midnight, Teal, Ember, Mono, Cyberpunk, Rosé, Nous Blue)
    ThemeProvider.tsx # Context + persistence to AsyncStorage
```

## Versioning

```json
// app.json and package.json
{
  "version": "0.0.1",
  "android": { "versionCode": 1 }
}
```

Each CI build creates a release `v<version>-YYYYMMDD-<short_sha>` with `HermesMobile-v<version>.apk`.

## Pitfalls

- **punycode module**: `markdown-it` (used by react-native-markdown-display) imports `punycode`, removed in Node 22+. Add `npm install punycode@2.3.1`.
- **expo-file-system v57+ API changed**: Uses `File`, `Directory`, `Paths`, `DownloadTask` classes instead of old `FileSystem.cacheDirectory`. Check the API before using migration guides.
- **GitHub Actions artifact storage**: Has quota limits. Use `gh release create` to upload APKs directly to releases instead of `actions/upload-artifact`.
- **JS bundle fails on Metro**: Check import paths for asset references. Metro resolves relative to file location, not project root. Error `Unable to resolve module ../assets/icon.png` means the path is wrong.
- **WS auth in gated mode**: `?token=` is rejected by default. Patch `_ws_auth_reason()` or use ticket-based auth.
- **Android cleartext HTTP**: Android 9+ blocks plain HTTP. Add `android:usesCleartextTraffic="true"` to `<application>` in `android/app/src/main/AndroidManifest.xml` when connecting to self-hosted HTTP backends.
- **ARM64 build failures**: Android NDK + CMake + Hermes compiler are x86_64-only. Gradle native builds (expo-modules-core, react-native-screens) fail on ARM64. Always build APKs on x86_64 runners (GitHub Actions) or use EAS Build.
- **Server version field**: `GET /api/status` returns `version` (not `agent_version`). The status type must include both fields: `version?: string; agent_version?: string`.
- **Streaming responses not finalizing**: The `prompt.submit` RPC response may arrive before `message.complete` event. Add a fallback in `sendMessage()` that waits ~500ms after the RPC resolves and finalizes any pending `streamingContent` into a message.
- **WebSocket close codes**: React Native WebSocket `onclose` event includes `code` and `reason`. Map common codes to human-readable errors: 4401=bad token, 4403=access denied, 1006=connection dropped (network/firewall likely blocking WS upgrades).
- **Auth provider auto-detect**: The server returns `auth_providers: ['nous']` (OAuth), not `['oauth']`. When auto-detecting auth mode, check for both `['nous', 'oauth'].includes(p.toLowerCase())`.
