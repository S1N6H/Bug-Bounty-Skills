---
name: session-search-tool
description: >
  Build a custom session search tool that indexes and queries past Claude Code CLI 
  chat logs to retrieve historical findings, techniques, and context. Based on 
  Critical Thinking Bug Bounty Podcast Episode 166.
domain: cybersecurity
subdomain: bug-hunting
category: Methodology
difficulty: intermediate
estimated_time: "1-2 hours"
platforms: [linux, macos, windows]
tags: [session-search, chat-history, knowledge-base, context-retrieval, past-findings]
tools: [claude-code-cli, typescript, ripgrep, fzf]
version: "1.0"
author: CyberSkills-Elite
license: Apache-2.0
source: "Critical Thinking Bug Bounty Podcast Ep. 166"
source_url: "http://www.youtube.com/watch?v=qTX9u-EsjmM"
---

# Session Search Tool

## When to Use
- When you remember finding something in a previous Claude session but cannot locate it.
- When starting a new target and want to check if you have prior research on similar tech stacks.
- When building a personal knowledge base from accumulated hunting sessions.
- When searching for specific payloads, techniques, or findings from past work.

## Prerequisites
- Claude Code CLI with session history stored locally
- Node.js 18+ / TypeScript toolchain
- `ripgrep` installed (for fast text search across session files)

## Core Concept

> **"Session Search is a custom tool that lets you search through your 
> old chat logs to find what you discussed before."**
> — Episode 166 [25:55]

After weeks of bug hunting, you accumulate hundreds of Claude sessions containing:
- Discovered endpoints and API mappings
- Successful payloads and bypass techniques
- Dead ends (equally valuable — don't repeat wasted effort)
- Partial findings that need follow-up

This tool indexes all of that and makes it searchable.

## Workflow

### Phase 1: Session Data Location

Claude Code CLI stores session data in platform-specific directories:

| Platform | Session Directory |
|----------|------------------|
| macOS | `~/.claude/sessions/` |
| Linux | `~/.claude/sessions/` |
| Windows | `%USERPROFILE%\.claude\sessions\` |

Each session is a JSON file containing the full conversation transcript.

### Phase 2: Build the Search Tool

```typescript
// scripts/session-search.ts
#!/usr/bin/env npx tsx

import { readdirSync, readFileSync, statSync } from "fs";
import { join } from "path";
import { homedir } from "os";

interface SearchResult {
  sessionId: string;
  timestamp: string;
  matchingLines: string[];
  context: string;
}

const SESSIONS_DIR = process.env.CLAUDE_SESSIONS_DIR 
  || join(homedir(), ".claude", "sessions");

function searchSessions(query: string, maxResults = 20): SearchResult[] {
  const results: SearchResult[] = [];
  const queryLower = query.toLowerCase();

  let sessionFiles: string[];
  try {
    sessionFiles = readdirSync(SESSIONS_DIR)
      .filter((f) => f.endsWith(".json"))
      .sort((a, b) => {
        const statA = statSync(join(SESSIONS_DIR, a));
        const statB = statSync(join(SESSIONS_DIR, b));
        return statB.mtime.getTime() - statA.mtime.getTime(); // newest first
      });
  } catch {
    console.error(`Cannot read sessions directory: ${SESSIONS_DIR}`);
    console.error("Set CLAUDE_SESSIONS_DIR env var or ensure Claude CLI has been used.");
    return [];
  }

  for (const file of sessionFiles) {
    if (results.length >= maxResults) break;

    try {
      const content = readFileSync(join(SESSIONS_DIR, file), "utf-8");
      const session = JSON.parse(content);
      const messages = session.messages || session.conversation || [];

      const matchingLines: string[] = [];
      for (const msg of messages) {
        const text = typeof msg === "string" ? msg : msg.content || msg.text || "";
        const lines = text.split("\n");
        for (const line of lines) {
          if (line.toLowerCase().includes(queryLower)) {
            matchingLines.push(line.trim().substring(0, 200));
          }
        }
      }

      if (matchingLines.length > 0) {
        const stat = statSync(join(SESSIONS_DIR, file));
        results.push({
          sessionId: file.replace(".json", ""),
          timestamp: stat.mtime.toISOString(),
          matchingLines: matchingLines.slice(0, 5), // top 5 matches per session
          context: `${matchingLines.length} total matches in this session`,
        });
      }
    } catch {
      // Skip corrupted session files
    }
  }

  return results;
}

// Fast search using ripgrep (if available)
async function ripgrepSearch(query: string): Promise<void> {
  const { execSync } = await import("child_process");
  try {
    const output = execSync(
      `rg --json -i "${query}" "${SESSIONS_DIR}" --max-count 5 --type json 2>/dev/null`,
      { maxBuffer: 10 * 1024 * 1024 }
    ).toString();

    const lines = output.split("\n").filter(Boolean);
    for (const line of lines.slice(0, 20)) {
      try {
        const match = JSON.parse(line);
        if (match.type === "match") {
          const filename = match.data.path.text.split(/[/\\]/).pop();
          console.log(`[${filename}] ${match.data.lines.text.trim().substring(0, 150)}`);
        }
      } catch { /* skip */ }
    }
  } catch {
    console.warn("ripgrep not available, falling back to native search...");
    const results = searchSessions(query);
    for (const r of results) {
      console.log(`\n[${r.sessionId}] — ${r.timestamp}`);
      r.matchingLines.forEach((l) => console.log(`  → ${l}`));
    }
  }
}

// Entry point
const query = process.argv.slice(2).join(" ");
if (!query) {
  console.error("Usage: npx tsx session-search.ts <search query>");
  console.error("Examples:");
  console.error("  npx tsx session-search.ts IDOR");
  console.error("  npx tsx session-search.ts 'api/v2/users'");
  console.error("  npx tsx session-search.ts 'SQL injection bypass'");
  process.exit(1);
}

console.log(`Searching sessions for: "${query}"\n`);
ripgrepSearch(query);
```

### Phase 3: Integrate as Claude Skill

Add to your skills directory so Claude can search its own history:

```markdown
## Instructions for Claude

When the user says "search sessions for X" or "have I found X before":
1. Run `npx tsx scripts/session-search.ts "<query>"`
2. Present results grouped by session date
3. Highlight actionable findings vs dead ends
4. If a past finding is relevant to current target, suggest follow-up actions
```

### Phase 4: MCP Server Version (Advanced)

```typescript
// Build session search as an MCP server for deep integration
// Register tools: search_sessions, get_session_detail, list_recent_sessions
// This lets Claude call session search as a native tool
```

## Use Cases

| Scenario | Search Query | Value |
|----------|-------------|-------|
| Starting new React target | `"React" OR "Next.js"` | Reuse past enumeration patterns |
| Found JWT auth | `"JWT" OR "alg:none"` | Check if you cracked similar JWT before |
| API fuzzing results | `"403" AND "bypass"` | Find past 403 bypass techniques |
| Avoiding duplicate work | `"example-corp"` | See all past sessions on this target |
| Payload reference | `"SSTI" OR "{{7*7}}"` | Retrieve working payloads from history |

## Creativity Directive

> **IMPORTANT**: Extend session search with semantic search (embeddings),
> auto-categorize findings by vulnerability type, build a personal 
> vulnerability database from accumulated sessions.
> **Think like an attacker. Adapt. Improvise.**

## 🔵 Blue Team
- Deploy robust WAF rules to detect anomalies.
- Monitor logs for unusual access patterns.

## 🛡️ Remediation & Mitigation Strategy
- **Input Validation:** Sanitize and strictly type-check all inputs.
- **Least Privilege:** Constrain component execution bounds.


## 📚 Shared Resources
> For cross-cutting methodology applicable to all vulnerability classes, see:
> - [`_shared/references/elite-chaining-strategy.md`](../_shared/references/elite-chaining-strategy.md) — Exploit chaining methodology and high-payout chain patterns
> - [`_shared/references/elite-report-writing.md`](../_shared/references/elite-report-writing.md) — HackerOne-optimized report writing, CWE quick reference
> - [`_shared/references/real-world-bounties.md`](../_shared/references/real-world-bounties.md) — Verified disclosed bounties by vulnerability class

## References
- Source: [Critical Thinking Ep. 166](http://www.youtube.com/watch?v=qTX9u-EsjmM) [25:55]
- ripgrep: [https://github.com/BurntSushi/ripgrep](https://github.com/BurntSushi/ripgrep)
