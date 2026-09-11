---
name: hermes-ariadne-memory
description: "Install, configure, and use Ariadne memory provider for Hermes Agent — local-first hybrid search (FAISS + FTS5 + RRF), knowledge graph, cognitive retention, auto-deduplication. Zero infrastructure, single SQLite file."
version: 1.0.0
author: Hermes Agent
license: MIT
tags:
  - hermes
  - memory
  - ariadne
  - faiss
  - fts5
  - knowledge-graph
  - embeddings
  - plugins
---

# Ariadne Memory Provider for Hermes Agent

Ariadne is a local-first AI agent memory system that combines:
- **Vector search** — FAISS (auto Flat → IVF at scale)
- **Keyword search** — SQLite FTS5 BM25
- **Hybrid fusion** — Reciprocal Rank Fusion (RRF)
- **Knowledge graph** — Typed entities/relationships with multi-hop traversal
- **Cognitive retention** — Ebbinghaus forgetting curve with use-based strengthening
- **Auto-deduplication** — MinHash LSH + SHA-256 exact match
- **Zero infrastructure** — Single SQLite file, no daemon, no server

## Quick Start

### 1. Install Ariadne Core

```bash
# Core (keyword search only)
pip install ariadne-memory

# With embeddings (semantic search) — requires torch/sentence-transformers
pip install "ariadne-memory[embeddings]"
```

### 2. Install Hermes Plugin

```bash
# Clone repo and copy plugin
git clone https://github.com/kyssta-exe/Ariadne.git /tmp/ariadne-repo
cp -r /tmp/ariadne-repo/plugin ~/.hermes/plugins/ariadne
```

### 3. Enable Plugin & Configure Hermes

```bash
hermes plugins enable ariadne
hermes config set memory.provider ariadne
# Restart Hermes session (CLI: /reset, Gateway: /restart)
```

The plugin auto-creates databases at:
- `~/.hermes/ariadne/memory.db` — personal memory
- `~/.hermes/ariadne/shared/memory.db` — cross-agent shared memory

### 4. Verify

```bash
hermes plugins list --plain | grep ariadne
# Should show: enabled  user  0.1.2  ariadne
```

## Configuration

### Hermes Config (`~/.hermes/config.yaml`)

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  provider: ariadne
  # Optional: custom DB paths
  # ariadne:
  #   db_path: ~/.hermes/ariadne/memory.db
  #   shared_db_path: ~/.hermes/ariadne/shared/memory.db
```

### Ariadne Config (Python API)

```python
from arriadne import AriadneConfig, AriadneMemory
from arriadne.embeddings import SentenceTransformerEmbedder

embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")  # 384-dim

config = AriadneConfig(
    db_path="memory.db",
    embedding_dim=embedder.dim,
    embedder=embedder,
    faiss_type="auto",           # auto | flat_ip | ivf_flat
    dedup_threshold=0.8,         # MinHash Jaccard threshold
    retention_half_life=86400,   # 1 day (seconds)
)

mem = AriadneMemory(config=config)
```

## Available Tools (once plugin enabled)

| Tool | Description |
|------|-------------|
| `ariadne_remember` | Store a durable memory (fact, preference, insight) |
| `ariadne_recall` | Hybrid search — FTS5 text + FAISS vector ranking |
| `ariadne_stats` | Memory system statistics |
| `ariadne_forget` | Permanently delete a memory by ID |
| `ariadne_update` | Update content or importance of existing memory |
| `ariadne_invalidate` | Soft-delete (mark as superseded) |
| `ariadne_export` | Export all memories to JSON file |
| `ariadne_import` | Import memories from JSON file |
| `ariadne_graph_query` | Traverse knowledge graph from seed entity |
| `ariadne_graph_link` | Declare relationship between two entities |
| `ariadne_sleep` | Run memory consolidation (compress old working memories) |
| `ariadne_diagnose` | Run diagnostics on Ariadne installation |
| `ariadne_scratchpad_write` | Write temporary note to scratchpad |
| `ariadne_scratchpad_read` | Read scratchpad entries |
| `ariadne_scratchpad_clear` | Clear all scratchpad entries |
| `ariadne_shared_remember` | Store memory in shared surface DB (cross-agent) |
| `ariadne_shared_recall` | Search shared surface DB |
| `ariadne_shared_forget` | Delete shared surface memory |
| `ariadne_shared_stats` | Shared surface DB stats |

## CLI Usage

```bash
# Initialize database
ariadne init

# Add memory
ariadne add "Production deploy script is in infra/deploy.sh"

# Search
ariadne search "deploy script"

# Statistics
ariadne stats

# Maintenance (consolidate + evict + prune)
ariadne maintain

# Backup / Restore
ariadne backup -o /backups/memory-$(date +%F).db
ariadne restore /backups/memory-2026-06-30.db

# Dashboard (web UI)
ariadne dashboard
```

## Python API Examples

### Basic Keyword Memory

```python
from arriadne import AriadneMemory

mem = AriadneMemory(db_path="memory.db")

mem.remember("User prefers dark mode", importance=0.7, tags=["preference"])
results = mem.recall("dark mode preference", k=5)
for r in results:
    print(r["content"], r["score"])

mem.close()
```

### Semantic Memory (with embeddings)

```python
from arriadne import AriadneMemory
from arriadne.arriadne.embeddings import SentenceTransformerEmbedder

embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
mem = AriadneMemory(db_path="memory.db", embedding_dim=embedder.dim, embedder=embedder)

mem.remember("VPS has 4 cores, 8GB RAM", importance=0.8)
results = mem.recall("server specs", k=5)  # Semantic match!
```

### Knowledge Graph

```python
mem.add_edge("WebApp", "API", edge_type="depends_on")
mem.add_edge("API", "Database", edge_type="depends_on")

# Multi-hop traversal
graph = mem.graph("WebApp", hops=2)
print(graph["nodes"])   # ['WebApp', 'API', 'Database']
print(graph["edges"])   # [{'source': 'WebApp', 'target': 'API', 'type': 'depends_on'}, ...]
```

### Maintenance

```python
# Run all maintenance tasks
mem.maintenance()

# Or individually:
mem.evict()              # Remove low-priority memories
mem.consolidate()        # Compress old working memories
mem.prune_access_log()   # Clean access history
mem.purge_deleted()      # Hard-delete soft-deleted entries
```

## Backup & Restore

```python
# Export
data = mem.export_json()
# data = {"memories": [...], "stats": {...}}

# Import
imported = mem.import_json(data)
print(f"Imported {imported} memories")
```

## Addons

Domain-specific extensions (auto-discovered via entry points):

```bash
# Finance addon — PDF/Excel extraction, ticker recognition, financial KG
pip install ariadne-finance

# With PDF support
pip install "ariadne-finance[pdf]"

# Full (PDF + yfinance market data)
pip install "ariadne-finance[full]"
```

```python
from arriadne.addons import AddonRegistry

registry = AddonRegistry()
registry.discover()
print(registry.addon_names)  # ['ariadne-finance']

extractor = registry.get_extractor_for_file("report.pdf")
result = extractor.extract("report.pdf")

registry.shutdown()
```

## Troubleshooting

### Embeddings Not Working (Bus Error / Torch Issues)

On ARM or systems without proper CUDA, `torch`/`sentence-transformers` may crash. Use keyword-only mode:

```python
# No embedder = keyword search only (still fast, uses FTS5 BM25)
mem = AriadneMemory(db_path="memory.db")
```

Or install CPU-only torch first:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
```

### Plugin Not Loading

1. Verify plugin exists: `ls ~/.hermes/plugins/ariadne/`
2. Check enabled: `hermes plugins list --plain`
3. Enable: `hermes plugins enable ariadne`
4. Restart session: `/reset` (CLI) or `/restart` (Gateway)

### Database Locked

Ensure only one Hermes process uses the DB at a time. The plugin uses `check_same_thread=False` for thread safety within a process, but cross-process access requires WAL mode (enabled by default).

## Improvement / Research Notes

When asked to make Ariadne stronger while preserving its core promise — local-first, zero infrastructure, single SQLite file — consult `references/ariadne-improvement-roadmap.md`. It captures competitor gaps and concrete roadmap items from research into Mem0, Zep/Graphiti, Letta/MemGPT, LangMem, LoCoMo, LongMemEval, and BEAM. Highest-priority themes: automatic extraction via episodes, first-class namespaces/scopes, temporal graph facts with invalidation, multi-signal retrieval, and quality benchmark harnesses.

## References

- **Documentation**: https://ariadne.mantes.net
- **Hermes Integration Guide**: https://ariadne.mantes.net/guide/hermes
- **API Reference**: https://ariadne.mantes.net/api/
- **Benchmarks**: https://ariadne.mantes.net/benchmarks
- **Improvement Roadmap**: `references/ariadne-improvement-roadmap.md`
- **Source**: https://github.com/kyssta-exe/Ariadne
- **Changelog**: https://github.com/kyssta-exe/Ariadne/blob/main/CHANGELOG.md