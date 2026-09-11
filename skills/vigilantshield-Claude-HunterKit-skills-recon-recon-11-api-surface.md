---
name: recon-11-api-surface
sequence: recon-11
category: recon
domain: recon
description: "API surface mapping: discover all API endpoints (REST, GraphQL, gRPC, WebSocket, SSE), catalog parameters per endpoint, detect auth requirements, identify hidden/undocumented APIs, GraphQL introspection, WADL discovery, version detection."
wordlist_ref: "wordlists/recon/recon-32-openapi-active-enum/"
---

# Recon 11 Api Surface — Offensive Methodology

## Quick Workflow
1. Discover API base URLs and version paths
2. Find spec files (OpenAPI, Swagger, GraphQL introspection, WADL)
3. Catalog all endpoints, methods, parameters
4. Map auth requirements per endpoint
5. Identify undocumented/hidden API endpoints

---

## Hacker Mindset
**API surface is the new attack surface.** Most modern apps are API-first with a thin client. The API surface is 10x larger than the visible web surface. Undocumented API endpoints are the highest-value targets — they often lack auth, rate limiting, and proper input validation.

---

## Detection

### API Spec Discovery
```bash
# Common spec file paths
spec_paths=(
  "/swagger.json" "/swagger/v1/swagger.json" "/swagger/docs/v1"
  "/api/swagger.json" "/api/docs" "/api/v1/swagger.json"
  "/openapi.json" "/api/openapi.json" "/v1/openapi.json"
  "/api-docs" "/api/v1/api-docs" "/api/documentation"
  "/graphql" "/graphql?query={__schema{types{name}}}"
  "/.well-known/openid-configuration" "/.well-known/oauth-authorization-server"
  "/WADL" "/application.wadl" "/service.wadl"
  "/api/v1/" "/v1/" "/api/v2/" "/api/v3/"
)

for path in "${spec_paths[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com$path")
  [ "$code" != "404" ] && [ "$code" != "403" ] && echo "FOUND: $path -> $code"
done
```

### API Version Detection
```bash
# Probe version endpoints
for version in v1 v2 v3 v4 api beta alpha; do
  for base in "/api/$version" "/$version" "/api/$version/"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com$base")
    [ "$code" != "404" ] && echo "LIVE: $base -> $code"
  done
done
```

### API Methods Discovery
```bash
# For each discovered endpoint, test HTTP methods
# 200/405 means method exists but different behavior
methods=(GET POST PUT PATCH DELETE OPTIONS HEAD)
for method in "${methods[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" -X $method "https://target.com/api/users")
  echo "$method -> $code"
done
```

### GraphQL Introspection
```bash
# If GraphQL endpoint found, test introspection
curl -s "https://target.com/graphql" \
  -H "Content-Type: application/json" \
  -d '{"query":"query{__schema{types{name fields{name}}}}"}' | head -100

# If introspection disabled, try field brute-force
```

### Hidden/Shadow API Discovery
```bash
# APIs are often at these patterns
# /internal/api, /partner/api, /debug/api, /admin/api
# /api/v1/internal, /api/partner, /api/debug

# Fuzz for hidden endpoints
# Common shadow API patterns
for path in internal partner debug admin legacy v3test staging; do
  for base in "/api/$path" "/$path/api" "/api/v1/$path"; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com$base")
    [ "$code" != "404" ] && echo "SHADOW API: $base -> $code"
  done
done
```

### WebSocket Endpoint Discovery
```bash
# Check for WebSocket endpoints
# Common patterns: /ws, /socket, /websocket, /ws/v1, /socket.io
for ws_path in ws socket websocket ws/v1 socket.io /ws /wss; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com/$ws_path")
  [ "$code" != "404" ] && echo "WS: $ws_path -> $code"
done
# Also check for upgrade header in responses
curl -sI https://target.com | grep -i "upgrade\|websocket"
```

### SSE Endpoint Discovery
```bash
# Server-Sent Events endpoints
# Common: /events, /stream, /notifications, /sse
for sse_path in events stream notifications sse live; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com/$sse_path")
  [ "$code" != "404" ] && echo "SSE: $sse_path -> $code"
done
```

---

## Wordlist Invocation
Use recon-05 (openapi-enum) wordlists for path discovery.

**Workflow:**
1. Probe spec file paths on all discovered API base URLs
2. Parse any discovered specs for all endpoints
3. Test each endpoint for hidden methods, params, auth requirements
4. Fuzz for shadow/hidden APIs

**Tools:** curl, jq, httpx, grep

## Chaining
- Discovered undocumented API → no auth → mass data access
- GraphQL introspection enabled → full schema → query exploitation
- Shadow API (v2 on production) → old auth → privilege escalation
- WebSocket API found → WS injection → real-time data manipulation
- Old API version (v1) found → known CVEs → exploitation
- OpenAPI/Swagger spec → all endpoints documented for mapping
