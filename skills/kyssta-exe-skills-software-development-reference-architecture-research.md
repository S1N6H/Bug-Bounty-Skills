---
name: reference-architecture-research
category: software-development
description: Systematic deep-architecture research of reference repositories before greenfield implementation — clone, audit, feature parity, ADRs, provenance, skeleton.
trigger: User provides a master plan / directive referencing specific repositories to study before building a new system
---

# Reference Architecture Research

Systematically study 1–3 existing repositories as references before designing and beginning implementation of a new system. Produces structured audits, a machine-readable feature-parity database, architecture decision records (ADRs), protocol schemas, provenance tracking, and a monorepo skeleton — without combining the references into an unmaintainable fork.

## When to Use

- User provides a directive referencing specific repositories as "mandatory reference implementations"
- You're building a greenfield system that must understand existing architecture before designing its own
- The goal is to create a distinct system (not a fork/reskin) informed by reference implementations
- Three or more features in the spec require cross-reference comparison (agent loop, tool dispatch, memory, security model, etc.)

## Process

### Phase 0: Clone and Pin

Create a read-only `references/` directory and clone every referenced repository:

```bash
mkdir -p references
git clone <url> references/<repo>
```

Record exact commits immediately:

```bash
for repo in <repo1> <repo2> <repo3>; do
  echo "$repo: $(git -C references/$repo rev-parse HEAD)"
done
```

Persist to `reference-lock.json` with URL, commit, version, license, and copyright for each.

### Phase 1: Read the Surface

For every reference repo, read in this order:

1. **LICENSE, NOTICE** — confirm license terms, copyright holders
2. **SECURITY.md** — trust model, threat boundaries, out-of-scope items  
3. **README.md** — high-level purpose, features, architecture
4. **AGENTS.md / CLAUDE.md** — scoped development guide for AI agents working on that codebase
5. **CONTRIBUTING.md** — release process, test organization
6. **Top-level config files** — pyproject.toml, package.json, Cargo.toml to get version, dependencies, build system
7. **Directory structure** — map the major source directories

### Phase 2: Deep Architecture Study

For each repo, inspect at minimum:

- **Agent loop** — how messages flow from input → model → tool → output
- **Tool registry** — how tools are registered, dispatched, permissioned
- **Plugin/extension system** — extension points, SDK, manifest format
- **Memory system** — storage, retrieval, persistence, cross-agent sharing
- **Gateway/channels** — message routing, platform adapters
- **Security model** — authentication, authorization, isolation, approval gates
- **Cron/scheduling** — how scheduled jobs work
- **MCP support** — client/server mode
- **Session management** — creation, persistence, search, resume
- **Subagent/delegation** — child agent lifecycle, isolation, cancellation

### Phase 3: Produce Audits

Write one audit document per repo. Each must include:

- Component map (directory tree or ASCII diagram)
- Agent lifecycle sequence diagram
- Tool-call lifecycle
- Subagent lifecycle
- Memory lifecycle
- Gateway/session lifecycle
- Feature inventory (organized by category)
- Strong design choices worth preserving in the new system
- Bottlenecks or complexity the new system should avoid
- Features the new system can integrate via adapter (not rebuild)

### Phase 4: Build Feature-Parity Database

Create a machine-readable YAML file (`docs/feature-parity.yaml`) with cross-reference entries:

```yaml
- id: category.feature-name
  category: agent|model|tool|memory|orchestration|policy|observability|channels|cli|daemon
  repo1: native|adapter|none|partial
  repo2: native|adapter|none|partial
  new_system_target: native|p1|p2
  priority: p0|p1|p2
  implementation: clean-room|reuse-<component>
  source_paths:
    - references/repo1/path/to/source
  acceptance_tests:
    - "Concrete behavior description"
  status: researched|designed|implementing|tested|shipped
```

Status lifecycle: `unresearched → researched → designed → implementing → tested → benchmarked → shipped`

### Phase 5: Write Architecture Decision Records

Create ADRs for each major architectural decision the research informed. Each ADR covers:

- Context (why this decision needed to be made)
- Decision (what was chosen)
- Rationale (specific evidence from reference audits)
- Consequences (trade-offs and compliance rules)

Initial ADR topics for multi-repo research projects:
- Orchestration language choice
- Memory engine selection
- Persistence strategy
- Agent communication model
- Recovery/reliability approach
- Security model
- Plugin strategy
- Provenance policy

### Phase 6: Define Protocol Schemas

Define the core data types before implementation begins:

- Workflow definition
- Step definition (all types: deterministic, llm, agent, tool, human, map, reduce, condition, wait, verify, compensate)
- Artifact (typed, content-addressed, immutable)
- Event (immutable state transition record)
- Permission grant
- Cross-agent capability announcement
- Cross-agent task contract
- Execution receipt

### Phase 7: Create Monorepo Skeleton

Create the directory structure reflecting the architecture decisions:

- Root build configs (Cargo.toml, package.json, pyproject.toml)
- Core runtime crates/packages
- CLI and daemon entry points
- Managed worker packages (if any runtime needs a separate process)
- SDK packages for external integration
- Adapter packages for cross-agent compatibility
- Docs directory with ADRs, audits, schemas, product docs
- Compliance directory with provenance tracking

## Compliance and Provenance

Track all reference-system interaction to prevent "fork with new name" anti-pattern:

- `reference-lock.json` — pinned SHAs and license info for every reference repo
- `THIRD_PARTY_NOTICES.md` — records any adapted code with source path, commit, and adaptation summary
- `source-provenance.yaml` — per-file manifest for any adapted code
- Never copy branding, trademarks, logos, or product identity from references
- Prefer clean-room reimplementation when direct copying would create architectural debt

## Pitfalls

- **Don't clone more than 3 repos for a single research phase** — more than that and the volume of `references/` data becomes unmanageable in context
- **Deep clone large repos** (`--depth 1`) for speed, but ensure you still record the commit SHA from the shallow clone
- **Record commits before reading** — if you read files and then the shell state is lost, you still have the pinned commit
- **Don't merge reference repos** into the new project's source tree. They stay in `references/`, read-only
- **Don't produce generic audits** — each must answer "what should Roshi (or your system) adopt, avoid, or bridge?"
- **ADRs before skeleton** — the skeleton layout depends on architecture decisions; don't reverse the order
- **Feature parity YAML needs acceptance tests** — without tests, parity is a claim, not evidence
- **P0 vs P1 is load-bearing** — don't list everything as P0. The spec's "initial demonstration workflow" determines the true P0 set
- **Post-build audit: compile IS the ground truth** — after the initial build, `cargo check` (or equivalent) is the only valid compilation signal. Linter false positives (e.g. sqlx macros producing "edition 2015" errors on code that compiles) must be ignored — trust the compiler, not the linter. The thrash-loop trap is rewriting the same file multiple times without recompiling between edits; break it with a compile gate after each single change.
- **Post-build audit: thread the dependency chain** — when fixing gaps detected during post-build audit, order fixes by dependency depth: DB schema → data layer types → wiring (AppState, constructors) → business logic → handlers → tests. Each fix compiles before the next begins.
- **Post-build gap-fill pattern** — the full cycle for fixing an overclaimed implementation: (1) run a simple e2e to prove real gaps exist, (2) fix one gap at a time with compile gates, (3) add a test that exercises the fixed path, (4) run full test suite again, (5) when all pass, write an honest audit doc documenting what's running vs stubbed. Do NOT mark phases "complete" until their acceptance tests pass on real running code.
- **Self-audit via reference subagents** — when auditing your own work, spawn 3-4 parallel subagents with the same brief (current code, plan, recent transcript). If they converge on the same diagnosis, it's probably correct — and the common errors they all identify are independent evidence, not groupthink. Use the `references/self-audit-convergence.md` file for the detailed protocol.
