# 🎯 Bug Bounty Skills

> **Every great bug bounty skill on GitHub. One repo. Refreshed daily.**

The `skills/` folder holds **every `.md` skill file** harvested daily from the best bug bounty, offensive security, OSINT and red team skill repositories on GitHub — flattened, deduplicated, and credited to every source author.

## 📅 How it works

A scheduled GitHub Actions workflow (harvest.yml) runs **daily at 03:17 UTC**: it reads `sources.txt`, downloads every `SKILL.md` from each source repo, dedupes by content hash, and drops one flat copy in `skills/` named `<owner>-<repo>-<path>.md`. Trigger manually anytime: **Actions → Daily Skill Harvest → Run workflow**.

## ➕ Add a repository

PR one line into `sources.txt`:

```text
owner/repo
```

The next daily run picks it up.

## ⚠️ Safety

Written by third parties for **authorized** security testing only. Read any skill before installing it into an agent, and run it only against targets you have permission to test. Aggregation is not endorsement.

---

## 🏆 Credits — the repositories this library is built from

**None of this content is ours.** Every skill was written and maintained by the authors below — this repo only collects and dedupes their work. **If a skill helped you land a bug, go star the original.**

### 🐞 Bug bounty & offensive security

| Repository | What it brings |
|---|---|
| **anthropics/skills** — ⭐ 175k+ | The official Agent Skills repository — the format this library speaks |
| **alirezarezvani/claude-skills** — ⭐ 25k+ | 380+ skills, agents and commands — the single biggest donor (850+) |
| **davepoon/buildwithclaude** — ⭐ 3k+ | Hub of Claude skills, agents, commands and plugins (379 skills) |
| **kyssta-exe/skills** | 886 Hermes agent skills — 817 cyber skills |
| **SnailSploit/Claude-Red** — ⭐ 3k+ | Curated offensive-security skill library for red-team workflows (78 skills) |
| **vigilantshield/Claude-HunterKit** | 150 skills for web, API and network hunting |
| **akashrpatil/awesome-offensive-security-skills** | 194 battle-tested skills: bug bounty, pentest, malware analysis |
| **killvxk/malskills-zh** | 120 offensive security skills for authorized pentesting |
| **elementalsouls/Claude-OSINT** — ⭐ 2.5k+ | 100+ recon capabilities, 80 secret-regex patterns, 80+ dorks |
| **0x002132/skills-bugbounty** | Bug bounty skills collection (50 skills) |
| **mrgoonie/claudekit-skills** | ClaudeKit skill collection (45 skills) |
| **Jeffallan/claude-skills** — ⭐ 11k+ | 67 specialized full-stack developer skills |
| **ctahok/hermes-bug-bounty-skills** | Hermes bug bounty skills (14 skills) |
| **Aetherdz/huntpack** | Method-first: compact 12-skill, 6-stage hunting pipeline |
| **murraywu/Bug-Bounty-Skills** | 10 security tools for web vulnerability hunting |
| **RajChowdhury240/AD-Red-Teaming-Claude-Skill** | Active Directory red teaming skill |
| **Gabson0x/bountyforge** | Parallelized agents for smart-contract + web/API hunting |
| **WolzenGeorgi/claude-skills-pentest** | Automated VPS-based pentest scanning |

> 🔍 **Want your repo here?** PR a line into `sources.txt` — attribution is automatic and permanent.

## 📄 License

Pipeline is MIT. **Each skill remains the property of its original author** under the license of its source repository — every filename encodes `owner-repo-path` so the source is always one click away.
