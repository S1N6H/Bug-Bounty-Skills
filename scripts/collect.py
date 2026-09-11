#!/usr/bin/env python3
"""
Bug Bounty Skills — daily skill harvester.

Fetches every SKILL.md from the repos listed in sources.txt, stores a copy
under skills/<owner>/<repo>/<path>, dedupes by content hash, and regenerates:

  ALL-SKILLS.md  — every skill merged into one navigable file
  SOURCES.md     — credits page: repo, stars, license, skill count
  stats.json     — machine-readable run stats (for the README footer)

Pure stdlib. Uses GITHUB_TOKEN when present (GitHub Actions), falls back to
unauthenticated calls otherwise.
"""

import hashlib
import json
import os
import sys
import time
import urllib.request
import urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(ROOT, "skills")
SOURCES_FILE = os.path.join(ROOT, "sources.txt")
ALL_SKILLS_FILE = os.path.join(ROOT, "ALL-SKILLS.md")
SOURCES_MD_FILE = os.path.join(ROOT, "SOURCES.md")
STATS_FILE = os.path.join(ROOT, "stats.json")

API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"

TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "bug-bounty-skills-collector"}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"

# Safety caps so one runaway repo can't blow up the daily run.
MAX_FILES_PER_REPO = 1000
MAX_TOTAL_FILES = 3000
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


def collect_repo(repo: str, stats: dict) -> list:
    """Return list of (relative_path, content) for every SKILL.md in repo."""
    print(f"[{repo}] resolving default branch", flush=True)
    meta = api_get(f"/repos/{repo}")
    if not meta:
        print(f"[{repo}] not found or private — skipping", flush=True)
        return []
    branch = meta.get("default_branch", "main")
    stats["repos"][repo] = {
        "stars": meta.get("stargazers_count", 0),
        "description": (meta.get("description") or "")[:160],
        "license": (meta.get("license") or {}).get("spdx_id") or "unknown",
        "branch": branch,
        "html_url": meta.get("html_url", f"https://github.com/{repo}"),
    }

    print(f"[{repo}] reading tree @ {branch}", flush=True)
    tree = api_get(f"/repos/{repo}/git/trees/{branch}?recursive=1")
    paths = [
        t["path"]
        for t in tree.get("tree", [])
        if t.get("type") == "blob" and t["path"].lower().endswith("skill.md")
    ]
    paths = paths[:MAX_FILES_PER_REPO]
    print(f"[{repo}] {len(paths)} SKILL.md file(s)", flush=True)

    out = []
    for p in paths:
        raw_url = f"{RAW}/{repo}/{branch}/{p}"
        try:
            content = raw_get(raw_url)
        except Exception as e:  # noqa: BLE001 — one bad file must not kill the run
            print(f"  ! failed {p}: {e}", flush=True)
            continue
        if len(content) > MAX_BYTES_PER_FILE:
            print(f"  ! skipped {p} ({len(content)} bytes > cap)", flush=True)
            continue
        out.append((p, content))
        time.sleep(0.15)  # be polite to the raw CDN
    return out


def main() -> int:
    os.makedirs(SKILLS_DIR, exist_ok=True)

    with open(SOURCES_FILE, encoding="utf-8") as f:
        repos = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    stats = {"run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "repos": {}}
    seen_hashes = {}
    merged = []
    total_files = 0
    entries = []  # (repo, path, skill_name, url, sha)

    for repo in repos:
        if total_files >= MAX_TOTAL_FILES:
            print("total file cap reached — stopping", flush=True)
            break
        files = collect_repo(repo, stats)
        for path, content in files:
            total_files += 1
            sha = hashlib.sha256(content).hexdigest()[:16]
            dest = os.path.join(SKILLS_DIR, repo, path)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if sha in seen_hashes:
                print(f"  dup  {repo}/{path} (same as {seen_hashes[sha]})", flush=True)
                continue
            seen_hashes[sha] = f"{repo}/{path}"
            with open(dest, "wb") as f:
                f.write(content)
            name = os.path.splitext(os.path.basename(path))[0]
            entries.append((repo, path, name, f"https://github.com/{repo}/blob/{stats['repos'][repo]['branch']}/{path}", sha))
            merged.append((repo, path, name, f"https://github.com/{repo}/blob/{stats['repos'][repo]['branch']}/{path}", content.decode("utf-8", errors="replace")))

    # ---- per-repo skill counts (used by ALL-SKILLS.md, SOURCES.md, stats) ----
    per_repo_counts = {}
    for repo, _, _, _, _ in entries:
        per_repo_counts[repo] = per_repo_counts.get(repo, 0) + 1
    for repo, count in per_repo_counts.items():
        stats["repos"][repo]["skills"] = count

    # ---- ALL-SKILLS.md -------------------------------------------------
    print(f"writing {ALL_SKILLS_FILE} ({len(merged)} skills)", flush=True)
    with open(ALL_SKILLS_FILE, "w", encoding="utf-8") as f:
        f.write("# Bug Bounty Skills — Merged Library\n\n")
        f.write(f"> Auto-generated {stats['run_at']} · {len(merged)} skills · "
                f"{len(repos)} source repositories · regenerated daily by GitHub Actions.\n\n")
        f.write("Each section links back to the exact source file. "
                "GitHub renders a full table of contents via the ☰ menu above.\n\n")
        f.write("| Source repository | Skills collected |\n|---|---|\n")
        for repo in repos:
            f.write(f"| {repo} | {per_repo_counts.get(repo, 0)} |\n")
        f.write("\n---\n\n")
        for repo, path, name, url, content in merged:
            f.write(f"## {name} — `{repo}/{path}`\n\n")
            f.write(f"**Source:** {repo}/{path}\n\n")
            f.write(content.rstrip() + "\n\n---\n\n")

    # ---- SOURCES.md (credits) ------------------------------------------
    print(f"writing {SOURCES_MD_FILE}", flush=True)
    rows = sorted(stats["repos"].values(), key=lambda r: -r["stars"])
    with open(SOURCES_MD_FILE, "w", encoding="utf-8") as f:
        f.write("# Credits & Source Repositories\n\n")
        f.write("This library is an aggregation project. Every skill below was authored by the "
                "maintainers of the repositories listed here — we collect, dedupe and index them; "
                "they wrote them. **Please star and follow the originals.**\n\n")
        f.write("| Repository | Stars | Skills | License | Description |\n")
        f.write("|---|---|---|---|---|\n")
        for r in rows:
            f.write(f"| [{r['html_url'].replace('https://github.com/', '')}]({r['html_url']}) "
                    f"| {r['stars']} | {r.get('skills', '—')} | {r['license']} | {r['description']} |\n")
        f.write("\n---\n*Skill counts reflect the last daily run. See `stats.json` for full details.*\n")

    # ---- stats.json ------------------------------------------------------
    stats["totals"] = {"skills": len(merged), "files_downloaded": total_files, "repos": len(repos)}
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    print(f"\nDONE: {len(merged)} unique skills from {len(repos)} repos -> {ALL_SKILLS_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())