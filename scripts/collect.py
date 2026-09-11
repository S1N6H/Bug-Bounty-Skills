#!/usr/bin/env python3
"""
Bug Bounty Skills — daily skill harvester.

Fetches every SKILL.md from the repos listed in sources.txt and drops a flat
copy into skills/ named <owner>-<repo>-<path>.md, deduplicating by content
hash. Identical content is skipped; name collisions get a numeric suffix.

Pure stdlib. Uses GITHUB_TOKEN when present (GitHub Actions), falls back to
unauthenticated calls otherwise.
"""

import hashlib
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(ROOT, "skills")
SOURCES_FILE = os.path.join(ROOT, "sources.txt")

API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"

TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "bug-bounty-skills-collector"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

# Safety caps so one runaway repo can't blow up the daily run.
MAX_FILES_PER_REPO = 1000
MAX_TOTAL_FILES = 4000
MAX_BYTES_PER_FILE = 1_000_000


def api_get(path: str, retries: int = 3) -> dict:
    url = f"{API}{path}"
    for attempt in range(retries):
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):  # rate limited — back off and retry
                wait = 30 * (attempt + 1)
                print(f"  rate-limited ({e.code}), sleeping {wait}s", flush=True)
                time.sleep(wait)
                continue
            if e.code == 404:
                return {}
            raise
        except urllib.error.URLError as e:
            print(f"  network error: {e}, retrying", flush=True)
            time.sleep(10)
    return {}


def raw_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "bug-bounty-skills-collector"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def flat_name(repo: str, path: str) -> str:
    """owner/repo/a/b/SKILL.md -> owner-repo-a-b.md"""
    owner, repo_name = repo.split("/")
    parts = [p for p in path.split("/") if p.lower() != "skill.md"]
    stem = "-".join([owner, repo_name] + parts)
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-")
    if len(stem) > 180:
        stem = stem[:170] + "-" + hashlib.sha256(stem.encode()).hexdigest()[:8]
    return stem + ".md"


def unique_path(skills_dir: str, name: str) -> str:
    dest = os.path.join(skills_dir, name)
    if not os.path.exists(dest):
        return dest
    base, ext = os.path.splitext(name)
    n = 2
    while os.path.exists(os.path.join(skills_dir, f"{base}-{n}{ext}")):
        n += 1
    return os.path.join(skills_dir, f"{base}-{n}{ext}")


def sha256_of(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main() -> int:
    os.makedirs(SKILLS_DIR, exist_ok=True)

    with open(SOURCES_FILE, encoding="utf-8") as f:
        repos = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    seen_hashes = {}
    claimed_names = {}  # flat name -> (repo, path)
    written = 0
    present = 0
    dups = 0
    total = 0

    for repo in repos:
        if total >= MAX_TOTAL_FILES:
            print("total file cap reached — stopping", flush=True)
            break
        print(f"[{repo}] resolving default branch", flush=True)
        meta = api_get(f"/repos/{repo}")
        if not meta:
            print(f"[{repo}] not found or private — skipping", flush=True)
            continue
        branch = meta.get("default_branch", "main")

        tree = api_get(f"/repos/{repo}/git/trees/{branch}?recursive=1")
        paths = [
            t["path"]
            for t in tree.get("tree", [])
            if t.get("type") == "blob" and t["path"].lower().endswith("skill.md")
        ][:MAX_FILES_PER_REPO]
        print(f"[{repo}] {len(paths)} SKILL.md file(s) @ {branch}", flush=True)

        for p in paths:
            total += 1
            raw_url = f"{RAW}/{repo}/{branch}/{p}"
            try:
                content = raw_get(raw_url)
            except Exception as e:  # noqa: BLE001 — one bad file must not kill the run
                print(f"  ! failed {p}: {e}", flush=True)
                continue
            if len(content) > MAX_BYTES_PER_FILE:
                print(f"  ! skipped {p} ({len(content)} bytes > cap)", flush=True)
                continue
            sha = hashlib.sha256(content).hexdigest()
            if sha in seen_hashes:
                dups += 1
                print(f"  dup {p} (same as {seen_hashes[sha]})", flush=True)
                continue
            seen_hashes[sha] = f"{repo}/{p}"
            name = flat_name(repo, p)
            if name in claimed_names and claimed_names[name] != (repo, p):
                dest = unique_path(SKILLS_DIR, name)
            else:
                claimed_names[name] = (repo, p)
                dest = os.path.join(SKILLS_DIR, name)
            if os.path.exists(dest):
                if sha256_of(dest) == sha:
                    present += 1  # already harvested — skip silently
                    continue
                # content changed upstream — refresh in place
            with open(dest, "wb") as f:
                f.write(content)
            written += 1
            time.sleep(0.15)  # be polite to the raw CDN

    print(f"\nDONE: {written} new/updated, {present} already present, "
          f"{dups} duplicates skipped, {total} files scanned -> skills/")
    return 0


if __name__ == "__main__":
    sys.exit(main())