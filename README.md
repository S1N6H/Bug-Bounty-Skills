# 🎯 Bug Bounty Skills

> **Every great bug bounty skill on GitHub. One repo. Refreshed daily. Automatically.**

A living, deduplicated library of Agent Skills (`SKILL.md` files) for bug bounty hunters, offensive security researchers, OSINT investigators and red teamers — harvested **every day** from the best skill repositories on GitHub, merged into a single `ALL-SKILLS.md`, and credited back to every author.

**No curation rot. No dead links. No forgotten lists.** A scheduled GitHub Actions workflow re-scans every source repository daily, pulls new and updated skills, dedupes by content hash, and commits the refreshed library — so this repo is always current, and every skill always links back to the exact source file and its author.

---

## ✨ What you get

| File | Purpose |
|---|---|
| `ALL-SKILLS.md` | 🔥 The full merged library — every skill in one navigable document |
| `skills/` | Raw `SKILL.md` files organized as `skills/<owner>/<repo>/<path>` |
| `SOURCES.md` | Credits page — every source repo with stars, license and skill counts |
| `sources.txt` | The harvest list — add a repo here and it joins the next daily run |
| `stats.json` | Machine-readable stats from the latest run |

## 📅 How the daily run works

1. **Read** — `sources.txt` lists every repository to harvest.
2. **Scan** — the collector reads each repo's git tree and finds every `SKILL.md`.
3. **Fetch** — each skill is downloaded from the source repo's default branch.
4. **Dedupe** — identical content is collapsed by SHA-256; first source wins.
5. **Merge** — `ALL-SKILLS.md` is regenerated with a table of contents and per-skill source links.
6. **Credit** — `SOURCES.md` and `stats.json` are refreshed with stars, license and skill counts.
7. **Commit** — changes are pushed automatically by the bot.

Runs daily at **03:17 UTC** via `harvest.yml`. You can also trigger it manually: **Actions → Daily Skill Harvest → Run workflow**.

## ➕ Add a skill repository

Open a PR that appends one line to `sources.txt`:

```text
owner/repo
```

The very next daily run will pick it up. Repositories should be public and contain `SKILL.md` files (Agent Skills format).

## ⚠️ Honest safety note

These skills were written by third parties for **authorized** security testing — bug bounty programs, CTFs, labs and engagements you have permission to test. **Read any skill before you install it into an agent**, and run it only against targets you are explicitly authorized to test. Aggregation is not endorsement.

---

## 🏆 Credits — the repositories this library is built from

**None of this content is ours.** Every skill in this repo was written, tested and maintained by the authors and communities behind the repositories below. This project exists only to aggregate, dedupe and daily-refresh their work in one convenient place. **If a skill helped you land a bug — go star the original, follow the author, and support them.**

### 🐞 Bug bounty & offensive security skill packs

| Repository | Why it's here |
|---|---|
| **anthropics/skills** — ⭐ 175,734 | The official Agent Skills repository — the format this whole library speaks |
| **alirezarezvani/claude-skills** — ⭐ 25,826 | 380+ Claude Code skills, agents and commands — the single biggest donor to this library (770+ SKILL.md files) |
| **SnailSploit/Claude-Red** — ⭐ 3,196 | Curated offensive-security skill library for red-team workflows — 75 skills |
| **elementalsouls/Claude-OSINT** — ⭐ 2,587 | 8 skills · 100+ recon capabilities · 80 secret-regex patterns · 80+ dorks |
| **Gabson0x/bountyforge** — ⭐ 410 | All-round bug bounty skill with parallelized agents for smart-contract audits |
| **Jeffallan/claude-skills** — ⭐ 11,413 | 67 specialized skills for full-stack developers |
| **Aetherdz/huntpack** — ⭐ 3 | Method-first hunting: a compact 12-skill, 6-stage bug bounty pipeline |
| **murraywu/Bug-Bounty-Skills** — ⭐ 0 | Bug bounty skill pack of 10 security tools for web vulnerability hunting |

*Star counts and per-repo skill totals refresh automatically every run — see `SOURCES.md` and `stats.json` for live numbers.*

> 🔍 **Want your repo here?** PR a line into `sources.txt` — attribution, including the per-skill back-link in `ALL-SKILLS.md`, is automatic and permanent.

## 📄 License

The collection pipeline in `scripts/` and `harvest.yml` is MIT. **Each skill remains the property of its original author** under the license of its source repository — follow the back-links in `ALL-SKILLS.md` and the license column in `SOURCES.md`.

---

*🤖 Regenerated daily by GitHub Actions — last run: see `stats.json`.*
