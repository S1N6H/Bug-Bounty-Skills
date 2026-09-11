---
name: devtools-01-chrome-devtools-mcp
sequence: devtools-01
category: devtools
domain: devtools
description: "Chrome DevTools MCP server — official browser automation from Chrome DevTools team. 46k+ GitHub stars. Install: npx -y chrome-devtools-mcp@latest. Tools: navigation, click/fill/hover, network inspection, console capture, performance tracing, heap snapshots, screenshots, and Lighthouse audits. Use for XSS verification, SSRF confirmation, OAuth interception, CSP inspection, and SPA endpoint discovery."
wordlist_ref: ""
---

# Chrome DevTools MCP

Official MCP server from the Chrome DevTools team for agentic browser control and debugging.

GitHub: https://github.com/ChromeDevTools/chrome-devtools-mcp (46,000+ ⭐)

## Quick Install

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

Slim mode (basic browsing only):
```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest", "--slim", "--headless"]
    }
  }
}
```

## Tools Overview

| Category | Tools | Use Case |
|----------|-------|----------|
| **Navigation** | navigate_page, new_page, close_page, list_pages, select_page, wait_for | Browse targets, manage tabs |
| **Input** | click, fill, fill_form, drag, hover, press_key, type_text, upload_file | Interact with forms, buttons |
| **Network** | list_network_requests, get_network_request | Inspect API calls, auth flows |
| **Debugging** | take_screenshot, take_snapshot, evaluate_script, list_console_messages, get_console_message | Verify XSS, capture PoC |
| **Performance** | performance_start_trace, performance_stop_trace, performance_analyze_insight, lighthouse_audit | Lighthouse audits, load perf |
| **Memory** | take_heapsnapshot, compare_heapsnapshots, get_heapsnapshot_* | Memory leak analysis |
| **Emulation** | emulate, resize_page | Mobile testing, network throttle |
| **Extensions** | install_extension, list_extensions, uninstall_extension | Browser extension testing |

## Bug Bounty Usage

### XSS Verification
1. `navigate_page` to vulnerable URL with payload
2. `take_snapshot` to see if script executed
3. `list_console_messages` to check for errors/proof
4. `take_screenshot` for evidence

### SSRF Confirmation
1. `navigate_page` to target with SSRF payload
2. `list_network_requests` to check for callbacks
3. Inspect request/response details via `get_network_request`

### OAuth/SSO Flow Interception
1. `navigate_page` through OAuth flow
2. `list_network_requests` to capture authorization codes, tokens
3. Inspect redirect_uri handling

### CSP/Header Inspection
1. `navigate_page` to target
2. `get_network_request` to inspect response headers
3. Check for CSP, HSTS, X-Frame-Options

### SPA Endpoint Discovery
1. Navigate through SPA application
2. `list_network_requests` to discover API calls
3. Extract hidden endpoints from network traffic

## Configuration

| Flag | Purpose |
|------|---------|
| `--headless` | Run without visible browser window |
| `--slim` | Only navigation + screenshot tools |
| `--channel=canary` | Use Chrome Canary |
| `--isolated` | Temporary profile, cleaned on close |
| `--browser-url=http://127.0.0.1:9222` | Connect to running Chrome |
| `--auto-connect` | Auto-connect to local Chrome 144+ |
| `--no-usage-statistics` | Opt-out of telemetry |
| `--experimental-vision` | Enable coordinate-based click_at(x,y) |

## Prerequisites

- Node.js LTS
- Google Chrome (stable or newer)
- `npx` (ships with npm)
