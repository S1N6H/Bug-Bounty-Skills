---
name: go-api-gateway
category: software-development
description: Build production-quality Go-based API gateways, routing proxies, and AI gateway backends. Covers project structure, HTTP middleware, provider adapter patterns, config hot-reload, embedded UIs, and auth.
---

# Go API Gateway Development

Patterns for building Go-based API gateways, particularly LLM routing proxies. Covers the architecture from the houter.lol project.

## Project Structure

```
project/
├── cmd/server/main.go          # Thin entrypoint, middleware wiring
├── internal/
│   ├── api/api.go              # HTTP handlers, config, logging
│   ├── cache/cache.go          # LRU hash-keyed response cache
│   ├── provider/
│   │   ├── provider.go         # Interface + shared HTTP client
│   │   ├── openai.go           # OpenAI adapter
│   │   └── anthropic.go        # Anthropic adapter (format translation)
│   └── router/
│       ├── router.go           # Scoring/routing engine
│       └── router_test.go      # Tests
├── cmd/server/ui/              # Embedded web dashboard (HTML)
├── scripts/                    # Cron scripts (bash)
├── Dockerfile
└── go.mod
```

## Routing Engine Pattern (references/routing-engine.md)

The core differentiator. Keyword-scored conditions with fallback chains.

Key design:
- `router.Rule` = condition string (keywords) + ordered `[]Target` fallback chain
- `router.Router.Route(content)` scores all rules against message content, returns best match or fallback
- `score()` extracts keywords from condition, checks substring match in content, returns 0.0–1.0
- No external deps — pure Go string matching
- `ponytail:` naive keyword matcher, upgrade to semantic/LLM-based when routing quality is measured to be the bottleneck

## Provider Adapter Pattern (references/provider-adapters.md)

One interface, one implementation per provider. Format translation happens in the adapter.

Interface:
```go
type Adapter interface {
    Name() string
    Chat(ctx context.Context, req Request) (*Response, error)
    Models() []string
}
```

Each adapter:
- Takes baseURL + API key + model list in constructor
- Translates internal `Request` → provider's native format
- Calls provider's HTTP API
- Translates response back to internal `Response`
- Shared `doJSON()` helper handles HTTP + JSON round-trip

## Embedded Web Dashboard

Embed the full HTML dashboard in the Go binary with `go:embed`:
```go
//go:embed ui/index.html
var uiFS embed.FS
```
Serve via `http.HandlerFunc`. Dashboard uses Tailwind CSS CDN (no build step) and pulls all data from `/api/*` endpoints.

## Auth Middleware

Simple API key check when `HOUTER_API_KEY` env var is set:
```go
func authMiddleware(key string, next http.Handler) http.Handler {
    if key == "" { return next }
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        if strings.HasPrefix(r.URL.Path, "/v1/") {
            auth := r.Header.Get("Authorization")
            if !strings.HasPrefix(auth, "Bearer ") || strings.TrimPrefix(auth, "Bearer ") != key {
                writeJSON(w, 401, map[string]string{"error": "unauthorized"})
                return
            }
        }
        next.ServeHTTP(w, r)
    })
}
```

## Config Hot-Reload

Store config in memory with `sync.RWMutex`. Serve GET/PUT on `/api/config`. PUT unmarshals new config and rebuilds router/provider registry.

## Pitfalls

- **Don't use `default` as a field name in Go** — it's a keyword. Use `fallback`.
- **go:embed path is relative to source file**, not module root. Put the UI dir inside `cmd/server/`.
- **Format translation is the hardest part.** Anthropic uses `x-api-key` header, OpenAI uses `Authorization: Bearer`. Anthropic has `system` as a separate field, not a message role.
- **Keyword matching is dumb but available.** It works for v0.1. The upgrade path is semantic embedding similarity or a small on-device classifier.
- **Empty state matters.** Every page/chart needs a clear empty state — users trust a system that honestly shows "no data" over one that pretends.
- **Auth should only protect /v1/ routes**, not the dashboard. Users need to see the UI to configure things.
