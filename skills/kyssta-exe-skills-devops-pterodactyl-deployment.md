---
name: pterodactyl-deployment
description: Deploy Pterodactyl Panel (Docker) and Wings daemon with nodes, allocations, and API keys.
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [pterodactyl, game-servers, docker, deployment, daemon]
    category: devops
    config: []
---

# Pterodactyl Deployment Skill

Deploy Pterodactyl Panel (game server management) via Docker and install/configure the Wings daemon on the same or remote nodes. Covers Panel setup, API key creation, node registration, allocation configuration, and Wings systemd service.

## When to Use

- Setting up a new Pterodactyl Panel instance
- Adding Wings nodes to an existing Panel
- Creating allocations for game servers
- Troubleshooting Panel↔Wings connectivity

## Prerequisites

- Linux server (ARM64 or x86_64)
- Docker and Docker Compose v2
- Public IP or domain for the Panel
- Root access

## Procedure

### 1. Panel (Docker)

Clone and configure the Panel docker-compose:

```bash
mkdir -p /opt/pterodactyl && cd /opt/pterodactyl
git clone https://github.com/pterodactyl/panel.git panel-docker
```

Create `docker-compose.yml` based on `docker-compose.example.yml` with these key changes:
- Map **host port → container port 80** (e.g., `2377:80`) instead of `80:80`
- Set `APP_URL` to `http://<IP>:<port>`
- Generate secure DB passwords with `openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32`

Start containers: `docker compose up -d`

Wait ~15s for migrations/eggs to seed, then create admin user:
```bash
docker exec <panel-container> php artisan p:user:make \
  --email="admin@..." --username="admin" \
  --name-first="Admin" --name-last="User" \
  --password="SecurePass123!" --admin=1
```

### 2. Sanctum Migration (Critical)

The Panel uses Laravel Sanctum for API auth, but the `personal_access_tokens` table may not exist on fresh installs:

```bash
docker exec <panel> php artisan vendor:publish \
  --provider="Laravel\\Sanctum\\SanctumServiceProvider"
docker exec <panel> php artisan migrate --force
```

**Without this, ALL API calls return 401.**

### 3. Admin API Key

API keys are **encrypted** (not hashed) with the Panel's APP_KEY. You cannot INSERT raw values directly — use a PHP script inside the container:

```php
<?php
require '/app/vendor/autoload.php';
$app = require_once '/app/bootstrap/app.php';
$kernel = $app->make(Illuminate\\Contracts\\Console\\Kernel::class);
$kernel->bootstrap();

use Illuminate\\Support\\Facades\\DB;
use Pterodactyl\\Models\\ApiKey;

$userId = DB::table('users')->where('email', 'admin@...')->value('id');
$rawToken = bin2hex(random_bytes(32));
$encrypted = encrypt($rawToken);
$identifier = ApiKey::generateTokenIdentifier(ApiKey::TYPE_APPLICATION);

DB::table('api_keys')->insert([
    'user_id' => (int) $userId,
    'key_type' => ApiKey::TYPE_APPLICATION,
    'identifier' => $identifier,
    'token' => $encrypted,
    'memo' => 'AdminSetup',
    'r_servers' => 1, 'r_nodes' => 3,  // 3 = READ|WRITE (see pitfalls)
    'r_allocations' => 1, 'r_users' => 1,
    'r_locations' => 1, 'r_nests' => 1, 'r_eggs' => 1,
    'r_database_hosts' => 1, 'r_server_databases' => 1,
    'created_at' => now(), 'updated_at' => now(),
]);

$fullKey = $identifier . $rawToken;
// verify: ApiKey::findToken($fullKey) should return the model
```

**Key type constants:** `TYPE_APPLICATION = 2` (admin API), `TYPE_DAEMON_USER = 3` (Wings).

### 4. Node + Allocations

Use the same PHP-in-container approach:

```php
// Location (if new)
$locationId = DB::table('locations')->insertGetId([...]);

// Node — check actual DB schema first (see pitfalls for column names)
$nodeId = DB::table('nodes')->insertGetId([
    'uuid' => (string) Str::uuid(),
    'public' => 1,
    'name' => 'Main Node',
    'fqdn' => $publicIP,
    'scheme' => 'http',
    'behind_proxy' => 0,        // NOT 'behind_proxied'
    'memory' => 20480, 'disk' => 150000,
    'daemon_token_id' => $tokenIdentifier,
    'daemon_token' => $daemonEncrypted,
    'daemonListen' => 8080,     // camelCase, NOT snake_case
    'daemonSFTP' => 2022,
    'daemonBase' => '/srv/daemon-data',
    ...
]);

// Allocations
foreach ([25565, 25566, 25567] as $port) {
    DB::table('allocations')->insert([
        'node_id' => $nodeId, 'ip' => $publicIP, 'port' => $port,
        'notes' => "Port $port",  // 'notes' NOT 'note'
        ...
    ]);
}
```

### 5. Wings Installation

```bash
WINGS_VERSION="v1.11.13"
curl -L -o /usr/local/bin/wings \
  "https://github.com/pterodactyl/wings/releases/download/${WINGS_VERSION}/wings_linux_$(uname -m)"
chmod +x /usr/local/bin/wings
```

**Use `wings configure` to auto-generate config** (requires `r_nodes => 3` on API key):

```bash
wings configure \
  --panel-url "http://<IP>:<port>" \
  --token "<admin-api-key>" \
  --node "<node-id>" \
  --allow-insecure \
  --config-path "/etc/pterodactyl/config.yml" \
  --override
```

### 6. Docker Network Subnet Fix

Wings creates a `pterodactyl_nw` Docker network (default `172.18.0.0/16`). If that subnet is taken, fix the config:

```bash
sed -i 's/172.18.0.0\\/16/172.21.0.0\\/16/' /etc/pterodactyl/config.yml
sed -i 's/172.18.0.1/172.21.0.1/' /etc/pterodactyl/config.yml
# Also fix IPv6 subnet/gateway to match
```

Check existing networks: `docker network ls -q | xargs -I{} docker network inspect {} --format '{{.Name}}: {{range .IPAM.Config}}{{.Subnet}}{{end}}'`

### 7. Systemd Service

```ini
[Unit]
Description=Pterodactyl Wings Daemon
After=docker.service network-online.target
Wants=network-online.target
Requires=docker.service

[Service]
User=root
ExecStart=/usr/local/bin/wings --config /etc/pterodactyl/config.yml
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload && systemctl enable --now wings
```

### 8. Verification

```bash
# Panel accessible
curl -sI http://<IP>:<port>

# Wings daemon listening
ss -tlnp | grep -E '(8080|2022)'

# Docker network created
docker network ls | grep pterodactyl

# API returns node + allocations
curl -s -H "Authorization: Bearer <key>" \
  -H "Accept: Application/vnd.pterodactyl.v1+json" \
  http://<IP>:<port>/api/application/nodes/<id>
```

## Server Operations

Day-to-day operations on deployed Pterodactyl servers: lifecycle control, jar management, plugins, and version upgrades. Assumes the Panel and Wings are already deployed and connected.

### 1. API Key Types

| Type | Prefix | Endpoint | Where Created |
|------|--------|----------|--------------|
| Application | `ptla_` | `/api/application/...` | Panel Admin UI or PHP in container |
| Client | `ptlc_` | `/api/client/...` | User settings UI or PHP in container |
| Daemon (Wings) | `wq57pn...` | Wings port (8080) | `wings configure` or config.yml |

**Application keys** manage admin resources (nodes, servers, users). **Client keys** control individual servers (start/stop, files, console). They are NOT interchangeable — a 405/403 with `"requires a client API key"` means you're using one on the wrong endpoint.

### 2. Generate a Client API Key (via panel container)

When the UI is inaccessible, generate one directly via Laravel Tinker inside the panel container:

```bash
docker exec <panel-container> php artisan tinker --execute="
use Pterodactyl\Models\ApiKey;
use Illuminate\Support\Str;

\$identifier = ApiKey::generateTokenIdentifier(ApiKey::TYPE_ACCOUNT);
\$token = Str::random(ApiKey::KEY_LENGTH);
\$fullKey = \$identifier . \$token;

\$key = new ApiKey();
\$key->user_id = 1;     # admin user ID
\$key->key_type = ApiKey::TYPE_ACCOUNT;  # 1 = client
\$key->identifier = \$identifier;
\$key->token = encrypt(\$token);
\$key->memo = 'CLI auto';
\$key->save();

echo \$fullKey . PHP_EOL;
"
```

The `TYPE_ACCOUNT` (1) key gets the `ptlc_` prefix — this is what the Client API recognizes. The model is `Pterodactyl\Models\ApiKey` (not `App\Models`).

### 3. Server Power (Start / Stop / Restart / Kill)

Use the **Client API** endpoint with a client API key:

```bash
SERVER_UUID="f60fc6fd-aa68-4db3-9b41-348d36470117"
CLIENT_KEY="ptlc_..."

# Start
curl -s -X POST -H "Authorization: Bearer $CLIENT_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"signal":"start"}' \
  "http://<panel>:<port>/api/client/servers/$SERVER_UUID/power"

# Signals: start | stop | restart | kill
```

Empty response = 202 Accepted (command dispatched to Wings). Monitor with:
```bash
docker ps -a --format "{{.ID}} {{.Names}} {{.Status}}" | grep "$SERVER_UUID"
docker logs <container-id> --tail 30 2>&1
```

### 4. Wings Crash Detection

If the server container exits immediately (status 1), Wings enters a crash-handler loop:

```
detected server as entering a crashed state
did not restart server after crash; occurred too soon after the last
```

Common causes:
- **`server.jar` not found** — Wings' egg installer failed; copy it manually (see §6)
- **Wrong Java version** — egg `docker_image` doesn't match the jar's requirement
- **Missing startup dependencies** — check the container logs with `docker logs`

**Bypass crash detection when you know the fix worked**: If the issue was a missing `server.jar` and you've placed it, Wings' crash detection may still block restarts. Start the container directly:
```bash
# 1. Verify server.jar exists and has correct permissions
ls -la /var/lib/pterodactyl/volumes/$SERVER_UUID/server.jar

# 2. Start the existing container (the UUID is the container name)
docker start $SERVER_UUID

# 3. Wait 15-30s and check status
docker ps --format "{{.ID}} {{.Names}} {{.Status}}" | grep "$SERVER_UUID"

# 4. Check the log to confirm Paper loaded
docker logs $(docker ps -q --filter "name=$SERVER_UUID") --tail 20 2>&1
```

Wings will re-attach to the running container and continue monitoring normally. This is safe for one-off restarts after manual file fixes.

Wings rate-limits restarts after repeated immediate crashes, so fix the root cause before retrying.

### 5. Check Egg Configuration

The Panel egg defines how Wings downloads the server jar and what variables control the process:

```bash
CLIENT_KEY="ptlc_..."
curl -s -H "Authorization: Bearer $CLIENT_KEY" \
  -H "Accept: application/json" \
  "http://<panel>:<port>/api/client/servers/$SERVER_UUID" \
  | jq '.attributes.relationships.variables.data[].attributes | {name, env_variable, server_value}'
```

Key egg variables for Minecraft servers:
- `MINECRAFT_VERSION` — the major.minor version (e.g. `26.1.2`)
- `SERVER_JARFILE` — defaults to `server.jar`
- `BUILD_NUMBER` — build #, or `latest`

### 6. Server Jar Not Auto-Downloading

When the egg version changes (e.g., `1.21.4` → `26.1.2`), Wings may not re-download the jar automatically. Fix:

```bash
# 1. Place the server jar manually in the server volume
cp /path/to/paper-26.1.2.jar /var/lib/pterodactyl/volumes/$SERVER_UUID/server.jar
chown pterodactyl:pterodactyl /var/lib/pterodactyl/volumes/$SERVER_UUID/server.jar

# 2. Start the server via Client API
# 3. On first start, Paper will do world migration (see §8)
```

The volume directory maps to `/home/container` inside the server's Docker container.

### 7. Plugin Management

Plugins live in `plugins/` subdirectory of the server volume:

```bash
PLUGIN_DIR="/var/lib/pterodactyl/volumes/$SERVER_UUID/plugins"
cp /path/to/plugin.jar "$PLUGIN_DIR/PluginName.jar"
chown pterodactyl:pterodactyl "$PLUGIN_DIR/PluginName.jar"
```

**Plugin compatibility after version upgrades** — common failure modes when upgrading Minecraft versions:
- **NMS hooks fail** — plugins accessing internal server code (DeluxeMenus, ZNPCsPlus, GrimAC, AntiPopup) often need version-specific updates
- **Version string parsing error** — the format `26.1.2.build.72` confuses plugins expecting `major.minor[.patch]` format; this is a plugin-side bug
- **Duplicate plugin names** — FAWE and WorldEdit share the same plugin name; remove one
- **CommandAPI versions** — each CommandAPI release targets a specific Minecraft build; upgrading the server usually requires a matching CommandAPI update

**Lumora deployment pattern**: Place the fat jar, start the server, verify in logs:
```
[Lumora] Enabling Lumora v1.0.0
[Lumora] Hooked into PlaceholderAPI
[Lumora] Lumora has been enabled!
```

### 8. World Migration (Server Fork Upgrade)

When switching server forks (Leaf → Paper, Purpur → Paper) or major versions, Paper automatically migrates world formats on first boot:

```
[WorldFolderMigration] World storage migration is required during startup.
[LegacyCraftBukkitWorldMigration] Starting legacy CraftBukkit import for world '...'
[WorldMigrationSupport] Migrating world directory from ./world/region to ./spawn/dimensions/minecraft/world/region
```

This is **automatic and one-way**. It preserves old world files (moves them aside). Migration time depends on world count/size — a 20-world server can take 60+ seconds.

### 9. Debugging a Failed Server Start

1. Check container logs: `docker logs <container-id>`
2. Check Wings daemon log: `grep "<server-uuid>" /var/log/pterodactyl/wings.log`
3. Check Panel's server status via API: `GET /api/client/servers/{uuid}` — `status` field is `null` (offline), `running`, or `starting`
4. Verify `server.jar` exists and has correct permissions in the volume
5. Verify the Docker image (egg's `docker_image`) has the right Java version for the jar

## Quick Reference

| Component | Port | Config |
|-----------|------|--------|
| Panel web | 2377 (custom) | Docker compose |
| Wings API | 8080 | `/etc/pterodactyl/config.yml` |
| Wings SFTP | 2022 | Same config |
| MariaDB | internal | Docker network |

## Pitfalls

1. **Sanctum table missing** → All API calls 401. Run `vendor:publish` + `migrate` for Sanctum.
2. **API key tokens are encrypted** with APP_KEY, not hashed. Must use PHP `encrypt()` inside the container.
3. **`/configuration` endpoint needs `r_nodes=3`** (READ|WRITE bitmask), not `r_nodes=1` (READ only). The AdminAcl uses bitwise permissions: NONE=0, READ=1, WRITE=2, READ|WRITE=3.
4. **Column name gotchas** in Panel DB schema:
   - `behind_proxy` (NOT `behind_proxied`)
   - `notes` (NOT `note`) in allocations
   - `daemonListen`, `daemonSFTP`, `daemonBase` (camelCase, NOT snake_case)
   - `token_id` on nodes (not just `daemon_token`)
5. **Docker subnet conflicts** → Wings `pterodactyl_nw` defaults to `172.18.0.0/16`. Check `docker network ls` and adjust if occupied.
6. **IPv6 gateway must match subnet** in Wings config — sed replacements sometimes miss multi-line blocks.
7. **`wings configure`** is the proper way to generate config (vs manual YAML). It pulls the correct token from Panel and avoids config mismatches.
8. **twin.macro does NOT support** template literals in `tw` tagged templates, JIT arbitrary values (`bg-[#hex]`), or Tailwind v3+ classes (`w-fit`). Use inline `style` props for dynamic values. See `references/panel-customization.md`.
9. **Docker build cache** can silently serve stale JS bundles. After modifying any `.tsx`/`.ts` source, always rebuild with `--no-cache` (`docker build --no-cache -t pterodactyl/panel:custom .`). Verify the new code is baked in: `docker cp <container>:/app/public/assets /tmp/check && grep -rl "yourstring" /tmp/check/*.js`. Without `--no-cache`, Docker may reuse the Node build stage cache and produce the same old webpack output.
10. **docker-compose image swap** — after first custom build, update `docker-compose.yml` to reference `pterodactyl/panel:custom` instead of `ghcr.io/pterodactyl/panel:latest`, otherwise `docker compose up` pulls the stock image and overwrites your changes.
11. **NEVER bundle unsolicited changes.** When the user asks for a specific feature (e.g., "add a Plugins tab"), do ONLY that. Do not modify theme, colors, branding, layout, or any other visual aspect unless explicitly requested. Bundling extra changes — even ones that seem like improvements — will infuriate the user. This is a hard rule: "dont fucking ever do anything thats not said."
12. **Heroicons vs emoji** — The Panel uses Heroicons for UI consistency. Never use emoji in the UI when Heroicons equivalents exist (e.g., use <DownloadIcon /> instead of "⬇", use <ChevronDownIcon /> instead of "▼"). Import from `@heroicons/react/solid` or `@heroicons/react/outline` as appropriate.
13. **Spinner sizing** — The Spinner component only accepts `small`, `base`, or `large` as size props. Using `tiny` will cause TypeScript errors. Always check the component's PropTypes/TS definition before using.
14. **Modrinth search API field naming** — The search endpoint returns `project_id` (NOT `id`) in each hit. If your TypeScript interface uses `id: string`, it will be `undefined` at runtime, causing version/detail API calls to hit `/project/undefined/version` → 404. Always use `project.project_id`. See `references/panel-customization.md` and `references/modrinth-integration-pattern.md` for details.
15. **Modrinth API rate limits** — While the public API is generous, consider adding a simple cache layer or debounce for search requests if implementing heavy usage. The current implementation uses a 350ms debounce on search input which helps mitigate this.

## References

- `references/panel-db-schema.md` — Full database column reference for `nodes`, `allocations`, `api_keys` tables.
- `references/panel-customization.md` — Dark themes, Monaco editor, Modrinth integration, custom Docker builds. Includes twin.macro pitfalls.
- `references/modrinth-integration-pattern.md` — Detailed pattern for adding Modrinth plugin browser/installer to Pterodactyl panel