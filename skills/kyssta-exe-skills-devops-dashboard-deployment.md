---
name: dashboard-deployment
description: "Deploy the Hermes web dashboard behind Nginx with Let's Encrypt SSL and Nous OAuth authentication."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [dashboard, nginx, ssl, oauth, self-hosting, production]
    related_skills: [hermes-agent, hermes-gateway]
---

# Dashboard Deployment

Deploy the Hermes web dashboard (`hermes dashboard`) on a public domain with HTTPS and Nous OAuth authentication.

## Scope

- Nginx reverse proxy configuration
- Let's Encrypt SSL via Certbot
- Nous Portal OAuth registration
- Systemd service for persistence
- Production hardening
- Related localhost service deployments that use the same systemd + Nginx + TLS pattern, such as LiteLLM/OpenAI-compatible proxy services; see `references/litellm-openai-proxy-deployment.md`

When the user says to clone/fork something "here" and expose it on a domain, interpret that as a request for a working local deployment unless they explicitly ask for planning only. Clone it, start it, put it behind Nginx/TLS, and verify public-domain behavior with real health and API calls.

When the user says to "rebrand everything" or wants a "new UI" for a proxy service, consider building a custom lightweight HTML dashboard served directly from Nginx rather than patching the existing frontend. This is faster, cleaner, and more maintainable for personal use. See `references/kasellm-custom-dashboard-pattern.md`.

## Quick Start

```bash
# 1. Register with Nous Portal
hermes dashboard register --redirect-uri https://your.domain.com/auth/callback

# 2. Install Nginx + Certbot
apt-get update && apt-get install -y nginx certbot python3-certbot-nginx

# 3. Configure Nginx (see templates/nginx.conf)

# 4. Obtain SSL cert
certbot --nginx -d your.domain.com --non-interactive --agree-tos --email admin@your.domain.com

# 5. Start dashboard
hermes dashboard --host 127.0.0.1 --port 9119 --skip-build &
```

## Architecture

```
Internet (HTTPS)
    │
    ▼
Nginx :443 (SSL termination, Let's Encrypt)
    │
    ▼
Nginx :80 → 301 redirect to HTTPS
    │
    ▼
Hermes Dashboard :9119 (HTTP, localhost only)
```

## Files

| File | Purpose |
|------|---------|
| `templates/nginx.conf` | Nginx site config template |
| `templates/systemd.service` | Systemd unit file |
| `scripts/verify-deployment.sh` | Post-deployment health checks |
| `references/gateway-coupled-dashboard-service.md` | User systemd pattern for making the dashboard start/restart with the Hermes gateway, including public-domain Host header and OAuth verification notes |
| `references/litellm-openai-proxy-deployment.md` | Runbook for cloning/running a LiteLLM or OpenAI-compatible local proxy, exposing it on a domain with Nginx/Let's Encrypt, and wiring it into Hermes as a custom provider |
| `references/litellm-admin-ui-unusual-port-runbook.md` | Pitfalls and verification for LiteLLM Admin UI on unusual HTTPS ports: preserving `Host: domain:port`, dashboard backend routes, building UI assets, PostgreSQL/Prisma setup, and diagnosing HTML-instead-of-JSON login errors |
| `references/litellm-deployment-pitfalls.md` | UI_USERNAME/UI_PASSWORD env vars for dashboard login, env secret recovery from running processes, Hermes provider URL updates, env file duplication traps |
| `references/kasellm-custom-dashboard-pattern.md` | Building a lightweight custom HTML dashboard to replace LiteLLM's React/Next.js UI — single-file, no build step, served by Nginx |
| `references/litellm-smart-routing-config.md` | LiteLLM model routing with auto-fallback: multiple backends per model name, simple-shuffle, retries, cooldown |

## Prerequisites

- Domain pointing to server (A/AAAA record)
- Ports 80, 443 open on firewall
- `sudo` access
- Hermes installed and configured

## Step-by-Step

### 0. If the dashboard must follow the gateway lifecycle

When the user expects “restart the gateway” to also bring the dashboard back, install the dashboard as a user systemd unit and couple it to `hermes-gateway.service` with both:

```ini
PartOf=hermes-gateway.service
[Install]
WantedBy=default.target hermes-gateway.service
```

See `references/gateway-coupled-dashboard-service.md` for a full known-good unit, Host-header pitfall, OAuth registration, and verification commands.

### 1. Register Dashboard

```bash
hermes dashboard register --redirect-uri https://your.domain.com/auth/callback
```

Writes to `~/.hermes/.env`:
```bash
HERMES_DASHBOARD_OAUTH_CLIENT_ID=agent:...
HERMES_DASHBOARD_PUBLIC_URL=https://your.domain.com
```

### 2. Configure Nginx

Use `templates/nginx.conf`, replace `your.domain.com`.

Enable:
```bash
ln -sf /etc/nginx/sites-available/your.domain.com /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl start nginx
```

### 3. Get SSL Certificate

```bash
certbot --nginx -d your.domain.com --non-interactive --agree-tos --email admin@your.domain.com
```

Auto-renewal via `certbot.timer` (systemd).

### 4. Start Dashboard

```bash
# Foreground test
hermes dashboard --host 127.0.0.1 --port 9119 --skip-build

# Production (with systemd)
systemctl enable --now hermes-dashboard
```

### 5. Verify

```bash
./scripts/verify-deployment.sh your.domain.com
```

### 6. Visual verification with browser (always do this)

After deploying, take screenshots of every page/tab to verify data loads correctly:

```bash
cd /tmp && npm install playwright
node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  page.on('response', r => { if (r.status() >= 400) console.log('ERR', r.status(), r.url()); });
  await page.goto('https://domain/ui/', { timeout: 30000 });
  // Fill auth if login modal appears
  const input = await page.\$('input');
  if (input) {
    const key = require('fs').readFileSync('/path/to/env', 'utf8').match(/LITELLM_MASTER_KEY=(.+)/)[1].trim();
    await input.fill(key);
    await page.\$('button').then(b => b?.click());
  }
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '/tmp/overview.png', fullPage: true });
  // Click through tabs
  for (const name of ['Models', 'Quick Start', 'Settings']) {
    const tabs = await page.\$\$('nav button, [role=tab]');
    for (const t of tabs) { if ((await t.textContent()).includes(name)) { await t.click(); break; } }
    await page.waitForTimeout(2000);
    await page.screenshot({ path: '/tmp/' + name.toLowerCase() + '.png' });
  }
  await browser.close();
})();
"
```

Then use `vision_analyze` on each screenshot — look for red error text, missing data, or broken layouts. Fix any issues before declaring the deployment done.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| 502 Bad Gateway | `systemctl status hermes-dashboard`, port 9119 listening |
| SSL error | `certbot renew --dry-run` |
| OAuth redirect mismatch | `HERMES_DASHBOARD_PUBLIC_URL` matches domain exactly |
| Dashboard not loading | `hermes dashboard --status`, Nginx error logs |
| LiteLLM UI on unusual port redirects to bare domain/443 | Preserve the original port with `proxy_set_header Host $http_host;` plus `X-Forwarded-Host $http_host` and `X-Forwarded-Port $server_port`; see `references/litellm-admin-ui-unusual-port-runbook.md` |
| LiteLLM Admin UI shows `Unexpected token '<' ... is not valid JSON` | A dashboard API route is returning an Nginx HTML 404. Proxy `/v2/login`, `/litellm/.well-known/litellm-ui-config`, and other dashboard backend routes to LiteLLM; verify wrong login returns `401 application/json`, not `404 text/html` |
| LiteLLM Admin UI login accepts master key but returns DB/auth error | The Admin UI needs `DATABASE_URL` and Prisma schema/client setup to mint UI session keys. Set up Postgres, run `python -m prisma generate --schema=litellm/proxy/schema.prisma` and `python -m prisma db push --schema=litellm/proxy/schema.prisma --accept-data-loss` |
| LiteLLM `/ui` returns 500 for missing `_experimental/out` | Build `ui/litellm-dashboard` with `npm ci && npm run build`, then copy `out/` to `litellm/proxy/_experimental/out/` and restart the service |
| LiteLLM UI shows old branding after patching `ui/litellm-dashboard/out/` | **CRITICAL**: The proxy serves from `litellm/proxy/_experimental/out/`, NOT `ui/litellm-dashboard/out/`. Patch `_experimental/out/` instead. See `references/litellm-unusual-ports-and-ui.md` |
| Need to rebrand LiteLLM UI without rebuilding | `find _experimental/out -type f \( -name "*.html" -o -name "*.js" -o -name "*.txt" \) -exec sed -i 's/OldBrand/NewBrand/g' {} +` — works on minified JS and RSC payloads |
| Need dark mode in LiteLLM UI without rebuilding | Inject `dark-mode.css` + `dark-toggle.js` into `_experimental/out/_next/static/chunks/`, then `sed -i 's\|</head>\|<script src="/litellm-asset-prefix/_next/static/chunks/dark-toggle.js"></script></head>\|'` all HTML files. See `references/litellm-unusual-ports-and-ui.md` |
| Custom dashboard 403 Forbidden | Fix file permissions: `chmod 644 /var/www/custom/index.html && chmod 755 /var/www/custom/` |
| Custom dashboard 500 / doubled filename | Nginx `alias` pitfall: use `alias /var/www/custom/;` (directory), NOT `alias /var/www/custom/index.html;` (file). The `location /ui/` with `alias /path/file.html` produces `/path/file.htmlindex.html` |
| LiteLLM UI login fails with "Invalid credentials" | Add `UI_USERNAME` and `UI_PASSWORD` to env file. The `/v2/login` endpoint (what the UI calls) uses these, NOT the master key. See `references/litellm-deployment-pitfalls.md` |

## Security Notes

- Dashboard binds only to `127.0.0.1:9119` — not exposed directly
- Nginx handles SSL termination and security headers
- Nous OAuth required for all non-loopback access
- Set strong `BULL_AUTH_KEY` in `.env` for queue admin UI