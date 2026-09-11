---
name: docker-auto-deploy
category: devops
description: Deploy Docker web apps with cron-triggered git auto-update, zero-downtime restarts, and 502 troubleshooting. Covers the git-poll + docker-compose rebuild pattern for self-hosted apps.
triggers:
  - User wants auto-deploy for a Docker web app (git push → auto rebuild)
  - Site is returning 502 Bad Gateway intermittently
  - Docker web app container restarts cause downtime
  - Need to detect/remediate false redeploy loops
---

# Docker Auto-Deploy & 502 Troubleshooting

> Class-level skill for deploying Docker web apps behind Nginx with a git-cron auto-update loop, zero-downtime restart pattern, and 502 root-cause investigation.

## Auto-Deploy via Cron + Git Poll

### Pattern

A cron job polls git every N minutes, checks for new commits on `main`, and redeploys via `docker compose up -d --build` when changes are detected.

### Cron entry (`/etc/cron.d/`)

```
*/5 * * * * root /path/to/auto_deploy.sh
```

### Script skeleton

```bash
#!/bin/bash
set -eu
REPO_DIR="/path/to/repo"
cd "$REPO_DIR"

git fetch origin

LOCAL=$(git rev-parse main)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" != "$REMOTE" ]; then
  echo "[$(date)] New commits. Redeploying..."
  git checkout main
  git pull --ff-only origin main
  docker compose up -d --build --wait
  echo "[$(date)] Redeploy complete."
fi
```

### Pitfall: Wrong branch causes false redeploy every cycle

If HEAD is on a non-`main` branch (feature branch, fix branch), `git rev-parse HEAD` never equals `origin/main`, triggering a full rebuild every poll cycle. Each rebuild kills the old container and starts a new one, causing 502 errors for ~10s.

**Fix:** Always compare `main` (local branch) vs `origin/main`, not `HEAD` vs `origin/main`. Add `git checkout main` before `git pull`.

### Pitfall: `git pull --ff-only` fails when local `main` has diverged

If someone force-pushed upstream, `git pull --ff-only` errors. Reset and pull:
```bash
git checkout main
git fetch origin
git reset --hard origin/main
```

## Zero-Downtime Restart

### Add healthcheck to docker-compose.yml

```yaml
services:
  web:
    build: .
    ports: ["5050:5050"]
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5050/')"]
      interval: 5s
      timeout: 5s
      retries: 3
      start_period: 15s
    restart: unless-stopped
```

### Use `--wait` flag

```bash
docker compose up -d --build --wait
```

Without `--wait`, docker compose kills the old container, starts the new one, and returns immediately. The new container takes 5-15s to start serving — during that window, nginx returns 502.

With `--wait`, docker compose keeps the old container running until the new one passes its healthcheck, then swaps traffic. Zero downtime.

### Start period is critical

The `start_period` (15s above) gives the container time to boot before healthcheck failures count. Without it, a healthy but slow-starting container gets killed during its first boot.

## Gunicorn Worker Sizing

For a Flask/FastAPI web app behind Docker + Nginx:

- **Minimum production:** `--workers 4 --threads 4`
- **Memory-bound server (8GB free):** `--workers 4`
- **CPU-bound:** match worker count to CPU cores
- **Add timeout:** `--timeout 60` prevents a single slow request from holding all workers

Example CMD:
```dockerfile
CMD ["gunicorn", "-b", "0.0.0.0:5050", "--workers", "4", "--threads", "4", "--timeout", "60", "app:app"]
```

Only 2 workers → if both get stuck on slow queries, all requests queue → nginx times out → 502.

## Nginx: Proxy Retry for 502

```nginx
location / {
    proxy_pass http://127.0.0.1:5050;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 86400;
    proxy_next_upstream error timeout http_502;
    proxy_next_upstream_tries 2;
}
```

The `proxy_next_upstream` directive tells nginx to retry the request on another upstream attempt when it gets a 502, timeout, or connection error. `tries 2` means one retry — enough to survive a brief restart blip without returning a visible error to the client.

## 502 Troubleshooting Flow

1. **Quick check — container age:**
   ```bash
   docker compose ps
   ```
   If STATUS shows `Up 26 seconds` or `Up 1 minute` when the app has been running for hours, the container was recently recreated. This is the fastest signal of a restart loop.

2. **Check nginx error log:**
   ```bash
   tail -100 /var/log/nginx/error.log
   ```
   Look for "connect() failed (111: Connection refused)" or "upstream prematurely closed connection".

3. **Check container restart history:**
   ```bash
   docker inspect <container> --format '{{.RestartCount}}'
   docker events --since '10m' | grep <container>
   ```
   If containers are recreated every 5 minutes, look for a git-poll auto-deploy cron (see pitfalls above).

4. **Check the auto-deploy log (if present):**
   ```bash
   tail -30 /path/to/repo/.auto_update.log
   ```
   Look for "New commits detected" running every cycle — confirms a false redeploy loop from the wrong-branch comparison issue.

3. **If containers restart every N minutes:**
   Check for auto-deploy cron job: `ls /etc/cron.d/` or `crontab -l`
   Verify the deploy script compares the correct branch (see pitfall above).

4. **Check gunicorn workers:**
   ```bash
   docker compose logs web | grep "Booting worker"
   # Should see 4+ workers, not 2
   ```

5. **Check memory/oom:**
   ```bash
   dmesg | grep oom
   free -m
   docker stats --no-stream
   ```
