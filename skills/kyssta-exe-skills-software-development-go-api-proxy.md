---
name: go-api-proxy
description: Build Go-based API proxy/gateway services with embedded web UIs, provider adapters, routing engines, and auth middleware.
triggers:
  - Build an API proxy or gateway in Go
  - Create a multi-provider LLM router
  - Embed a web dashboard in a Go binary
  - User says "make it clean" or "this is nowhere near production"
---

# Go API Proxy / Gateway

Production-quality Go API proxies with embedded web UIs. One binary. Zero runtime deps.

## Project Structure

```
project/
├── cmd/project/main.go          # entrypoint only
├── internal/
│   ├── router/                  # decision engine
│   │   ├── router.go
│   │   └── router_test.go
│   ├── provider/                # upstream API adapters
│   │   ├── provider.go          # Adapter interface
│   │   ├── openai.go
│   │   └── anthropic.go
│   ├── cache/                   # LRU + hash-key cache
│   │   └── cache.go
│   └── api/                     # HTTP handlers + config types
│       └── api.go
├── cmd/project/ui/index.html    # embedded dashboard
├── go.mod
└── Dockerfile
```

## UI Rules

- **One file.** HTML + CSS variables + vanilla JS. No build step. No Tailwind CDN (cramped layouts, class soup).
- **No mock data. Ever.** Every number from backend. Empty states say "No data yet." Hardcoded percentages, trend arrows, mini-charts, fake user profiles, fake workspace IDs, fake plan tiers — all of these get called out immediately. Real data or empty state. Nothing in between.
- **SVG icons only.** No emojis. (User will call out emojis in a dark dashboard.)
- **Dark theme.** Use CSS variables: `--bg`, `--surface`, `--border`, `--text`, `--muted`, `--accent`. Example: `:root{--bg:#09090b;--surface:#18181b;--border:#27272a;--text:#fafafa;--muted:#a1a1aa;--accent:#6366f1}`
- **Real-time via setInterval.** WebSocket is overkill for dashboards.
- **Row hover on tables.** `tr:hover td` — zero JS, looks polished.
- **No "plans" or tiers.** No Pro/Enterprise/Business references. No fake usage stats. No "Plan:" labels.
- **Complex dashboards in one file.** Every UI feature (metric cards, live tables, bar charts, flow diagrams) lives in that single HTML. JS fetches from `/api/*` endpoints and renders via innerHTML + template literals. This scales to ~500 lines of JS without needing a framework.
- **CSS-only mockup matching.** A visual design reference — colored bars, mini charts, dark theme, hexagon logos, status dots — is all CSS. SVG icons inline. No image assets, no font imports beyond the CDN.
- **Settings pages are CRUD forms, not JSON editors.** Every list (providers, routes, models, API keys) needs: inline edit fields, Add button at section header, Delete button per row. Use proper form inputs (text, password for secrets, select). JSON textarea is a debug tool, not a user-facing interface.

## Quality Gates

A proxy that gets called out as "far from production" usually fails one of these:

1. **Streaming works.** If `/v1/chat/completions` doesn't stream, every real client (Cursor, Claude Code, OpenAI SDK) blocks waiting for the full response. Implement the raw SSE proxy pattern before anything else.
2. **No mock data anywhere.** Fake trend arrows, fake usage numbers, fake user profiles — all of these erode trust. Every number on the dashboard must trace back to a backend API call.
3. **Auth gates the proxy.** `HOUTER_API_KEY` env var. Without it, every `/v1/*` endpoint is public.
4. **Errors are JSON.** No raw Go error dumps. Every error response has `{"error":"message"}` format.
5. **Config hot-reloads.** Editing config.json restarts the proxy's routing state without a process restart.

## Provider Adapter Pattern

```go
type Adapter interface {
    Name() string
    Chat(ctx context.Context, req Request) (*Response, error)
    Models() []string
}
```

One adapter per provider. Registry maps name → adapter. No switch-on-type at routing time.

### Streaming (SSE Proxy)

Streaming is the gate — everything else is cosmetic until streaming works. Clients expect SSE from `/v1/chat/completions` with `stream: true`.

**Lazy implementation:** Don't change the adapter interface. In the Chat handler, check `req.Stream`. If true, make a direct HTTP POST to the provider with `stream: true` and pipe the response body line-by-line to the client as SSE. This bypasses the adapter entirely and works for any OpenAI-compatible provider.

```go
// In api.go Chat handler, after routing:
if req.Stream {
    s.streamChat(w, r, tgt, req, res.Rule, start)
    return
}

// streamChat makes a raw HTTP streaming call:
// 1. Marshal body with stream:true
// 2. POST to provider's /chat/completions with Bearer auth
// 3. Set response headers: Content-Type: text/event-stream, Cache-Control: no-cache
// 4. bufio.Scan upstream response body, write each line as "line\n\n"
// 5. Flush after each line via http.Flusher
// 6. Send "data: [DONE]\n\n" on completion
```

SSE headers: `Content-Type: text/event-stream`, `Cache-Control: no-cache`, `Connection: keep-alive`. Stream terminates on `data: [DONE]` or connection drop.

**Skipped:** Anthropic streaming format translator (different SSE schema). Add when Anthropic is a streaming target.

## Routing Engine

The routing engine evaluates conditions against request content and returns an ordered fallback chain. The keyword scoring approach works without any external dependencies:

```go
type Router struct {
    rules    []Rule
    fallback []Target
}

func (r *Router) Route(content string) Result
```

Rules have a `Condition` (space-separated keywords) and ordered `Targets` (provider/model pairs). The scorer extracts meaningful keywords from the condition, counts how many appear in the content, and returns a 0.0–1.0 score. The highest-scoring rule wins; its targets are tried in order.

### Routing Strategies

Extend rules with a `Strategy` field to support different routing modes:

```go
type Rule struct {
    Name      string   `json:"name"`
    Condition string   `json:"condition"`
    Strategy  string   `json:"strategy"` // "", "keyword", "round-robin
}
```

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `"keyword"` (default) | Score conditions against content | Intent-based routing |
| `"round-robin"` | Always matches (score=1.0), rotates target order | Load distribution |

**Round-robin implementation:** Add a `rrIndexes map[string]int` + `sync.Mutex` to the Router struct. In `Route()`, check winning rule's strategy. For round-robin, cycle index via key `"rr:" + rule.Name`, then rotate: `rotated[i] = targets[(idx+i)%len(targets)]`.

**ponytail:** Keyword + round-robin cover 90% of cases. "cost-optimized" routing needs per-model cost data from middleware — wire when a CostCalculator exists and a user asks for cheapest-provider fallback.

### Token Compression

Reduce token usage 15-40% on tool-calling workloads by compressing messages before upstream dispatch:

```go
func Compress(messages []provider.Message, maxToolLen int) []provider.Message
```

**Lazy implementation:** Strip consecutive whitespace, truncate tool-role messages >2000 chars. Wire in the Chat handler BEFORE routing:

```go
req.Messages = router.Compress(req.Messages, 2000)
```

**ponytail:** Basic compression only. RTK/Caveman-style function-signature compression needs AST parsing per language (Go, Python, JS, TS, Rust — each needs its own node walker). Add when tool-call-heavy workloads emerge and measurements show >30% token waste on tool output.

**Upgrade path:** Replace keyword scorer with a small LLM (3-8B) for semantic matching when keyword overlap is insufficient. The Router interface doesn't change — only the `score()` function.

## Auth

Auth key from `HOUTER_API_KEY` env var. Protects `/v1/*` routes only. Dashboard stays public. No auth = no config → auth disabled.

## Config

JSON with env var overrides. `HOUTER_KEY_<name>` and `HOUTER_URL_<name>` for secrets.

## What Not To Do

- **No Next.js/Vite/React.** More complexity, no benefit for a dashboard that ships inside a Go binary.
- **No mockup data.** Real data or empty states. Mockups are design references, not data sources.
- **No fake tiers/plans.** No "Pro Plan", no "ws_..." workspace IDs, no imaginary billing.

## Pitfalls

- **go:embed paths are source-relative.** If main.go is in `cmd/project/`, embed path is `ui/index.html`. Keep UI inside the cmd directory.
- **Tailwind CDN has no @apply.** Use inline classes or `<style>` blocks with standard CSS.
- **Tailwind CDN produces cramped layouts when over-stacked.** When you see "the UI/UX is so ass" after a Tailwind build, the issue is usually: (1) too many utility classes fighting each other, (2) tight spacing (p-3 instead of p-6), (3) no design tokens. **Escape hatch:** switch to pure CSS with CSS variables (`--bg`, `--surface`, `--accent`, `--border`, `--text`, `--muted`). Define a design system in `:root`, use `var(--token)` everywhere, add hover effects with `transition: all .15s`. This produces cleaner, more maintainable dashboards than 50 Tailwind classes per element. Example: `.metric{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px;transition:transform .15s,box-shadow .15s}.metric:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.3)}` is cleaner than `class="bg-surface border border-border rounded-xl p-5 hover:-translate-y-0.5 hover:shadow-2xl transition-all"`.
- **Vet errors are normal cross-file.** `go vet` runs per-file and can't see types in sibling package files.
- **Config writes to disk.** Ensure the process user has write permission on the config path.
- **Don't over-engineer env var lookup.** If you need testability, inject a `func(string) string` field on the Server struct and set it in `New()`. Don't build a chain of `SetEnvLookup()` + `init()` + `lookupEnvFallback()` — it's three layers of indirection for `os.Getenv`. If there's only one real implementation, just call it directly in `ApplyEnvOverrides`. Testability via injection is fine; function-pointer gymnastics with fallbacks that return "" is not.
- **Stray heredoc artifacts in embedded files.** When writing UI HTML via shell heredoc (`cat > file << 'EOF'`), the closing delimiter (e.g., `EOF`, `UIEOF`) can end up in the file if the write is interrupted or the delimiter is on a separate line from expected. Always verify embedded files don't have trailing artifacts after build.
- **Table column alignment in JS template literals.** When rendering rows via `.map()` + template literals, every `<td>` must match its corresponding `<th>` position. Misalignment (provider name in model column, model path in latency column) is the #1 visual bug. Count columns: if `<th>` count is N, every `<tr>` must have exactly N `<td>` elements in matching order. Use the mockup's exact column sequence as the source of truth, not the order your data comes in.
- **Mock data violation is a recurring bug — even with explicit rules.** The skill says "no mock data" but agents STILL hardcode reference data. **Explicit rule:** Even when matching a mockup image with specific numbers (e.g., "612ms latency", "99.35% success rate", "$0.72/1K tokens"), do NOT hardcode those numbers in the UI. The mockup is a visual reference for layout/colors/typography/spacing — not data. Real backend data or empty states only. If the backend returns no data, show "—" or "No data yet" — not fake numbers. The user will call out mock data immediately, every time. There is no "but it looks better with data" justification.
- **Competitive feature parity.** When a user says "continue the plan" and a competitive research document exists, the plan means matching ALL differentiating features from the research — not just basic CRUD. For LLM routers: LiteLLM virtual keys with budgets, Portkey guardrails, 9Router free provider directory, OmniRoute multi-platform. Check the research doc's feature matrix before shipping. Basic routing + dashboard is the floor, not the ceiling.
- **Quick-add provider presets (9Router pattern).** For any multi-provider system, ship one-click setup for the top 4-5 providers. Hardcode the known base URLs and model lists; user only enters their API key. Example: `quickAddProvider('openai')` → auto-fills `https://api.openai.com/v1`, models `gpt-4o,gpt-4o-mini,gpt-4-turbo`, user types key. This is the difference between "easy onboarding" and "go read API docs first". Store presets as a JS object keyed by provider name.
- **Visual fallback chain diagrams (OmniRouter pattern).** When routes have ordered fallback targets, render them as horizontal flow diagrams — not just text pills. First target highlighted with accent background (primary), subsequent targets in muted background with arrow icons between them. Labels: "Primary" for first, implicit fallback for rest. This makes the routing logic immediately comprehensible without reading config. Use flexbox + inline SVG arrows, no library needed.
- **Settings pages need CRUD forms, not JSON editors.** When building settings/config UI for lists (providers, routes, models, API keys), never ship a raw JSON textarea as the primary interface. Users expect: (1) inline edit fields for each item, (2) "Add" button at section header, (3) "Delete" button per row. Use proper form inputs (text, password for secrets, select dropdowns). JSON editor is a debug tool, not a user-facing settings page. Example: providers list needs name/baseURL/apiKey fields with edit + delete, not `{"providers": [...]}` textarea. If user says "proper settings" or "we can't add/edit/remove", they're rejecting the JSON textarea approach.

## Related

- [defensive-programming](skill:defensive-programming) — input validation at trust boundaries.
