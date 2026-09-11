---
name: ariadne-memory
description: "Set up and use Ariadne as the local-first hybrid search memory provider for Hermes Agent."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [memory, ariadne, faiss, fts5, knowledge-graph, hybrid-search]
    related_skills: [hermes-agent, hermes-memory]
---

# Ariadne Memory Provider for Hermes

Ariadne is a local-first AI agent memory system with hybrid search (FAISS vector + FTS5 keyword + RRF fusion), knowledge graph traversal, cognitive retention modeling, and auto-deduplication — zero infrastructure, single SQLite file.

## Quick Start

```bash
# Install core + embeddings
pip install "ariadne-memory[embeddings]"

# Install Hermes plugin
git clone https://github.com/kyssta-exe/Ariadne.git /tmp/ariadne
cp -r /tmp/ariadne/plugin ~/.hermes/plugins/ariadne

# Enable plugin
hermes plugins enable ariadne

# Configure provider
hermes config set memory.provider ariadne

# Restart session to load tools
hermes chat  # or /reset in existing session
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AriadneMemory                        │
├─────────────────────────────────────────────────────────┤
│  SQLite (WAL)                                           │
│  ├── memories table (content, metadata, embeddings)    │
│  ├── FTS5 virtual table (BM25 keyword search)          │
│  ├── entities table (knowledge graph nodes)            │
│  ├── edges table (knowledge graph relationships)       │
│  └── access_log table (retention tracking)             │
├─────────────────────────────────────────────────────────┤
│  FAISS Index (in-process, rebuilt on open)             │
│  ├── IndexFlatIP (exact) → IndexIVFFlat (at scale)    │
│  └── IndexIDMap2 (vectors keyed by memory ID)          │
├─────────────────────────────────────────────────────────┤
│  MinHash LSH (deduplication index, rebuilt on open)    │
└─────────────────────────────────────────────────────────┘
```

## Configuration

### Config.yaml
```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200
  user_char_limit: 1375
  provider: ariadne
  nudge_interval: 10
  flush_min_turns: 6
```

### Python API
```python
from arriadne import AriadneMemory, AriadneConfig
from arriadne.embeddings import SentenceTransformerEmbedder

embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")  # 384-dim
mem = AriadneMemory(
    db_path="memory.db",
    embedding_dim=embedder.dim,
    embedder=embedder
)

# Or keyword-only (no embedder needed)
mem = AriadneMemory(db_path="memory.db")
```

## Available Tools (21)

| Tool | Description |
|------|-------------|
| `ariadne_remember` | Store a durable memory |
| `ariadne_recall` | Hybrid search (FTS5 + FAISS) |
| `ariadne_stats` | Memory system statistics |
| `ariadne_forget` | Permanently delete by ID |
| `ariadne_update` | Update content/importance |
| `ariadne_invalidate` | Soft-delete (mark superseded) |
| `ariadne_export` | Export all memories to JSON |
| `ariadne_import` | Import memories from JSON |
| `ariadne_graph_query` | Traverse knowledge graph |
| `ariadne_graph_link` | Declare entity relationship |
| `ariadne_sleep` | Run consolidation |
| `ariadne_diagnose` | Run diagnostics |
| `ariadne_scratchpad_*` | Temporary notes (3 tools) |
| `ariadne_shared_*` | Cross-agent shared surface (4 tools) |

## Core Features

### Hybrid Retrieval (RRF)
```python
# Vector + keyword fused automatically
results = mem.recall("how to deploy to production", k=5)
```

### Knowledge Graph
```python
mem.add_edge("WebAppEntity("WebApp", "API", edge_type="depends_on")
mem.addEdge("API", "Database", edge_type="depends_on")
mem.graph("WebApp", hops=2)  # → API, Database
```

### Cognitive Retention (Ebbinghaus)
```python
# R = e^(-t/S) — stability S grows on recall
# Priority = importance × recency × access_count × retention
mem.maintenance()  # evict, consolidate, prune, purge_deleted
```

### Auto-Deduplication
- MinHash LSH for near-duplicates
- SHA-256 for exact duplicates
- Index rebuilt from DB on open (survives restarts)

## Files

| File | Purpose |
|------|---------|
| `templates/ariadne-config.yaml` | Example config.yaml snippet |
| `scripts/test-ariadne.py` | Verify installation |
| `references/namespace-scope-implementation.md` | Development notes for namespace/scope isolation, Hermes plugin wiring, and regression tests |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: sentence_transformers` | `pip install sentence-transformers` |
| `torch` segfault on ARM | Use keyword-only mode (no embedder) |
| Plugin not loading | `hermes plugins enable ariadne` + restart session |
| Tools not appearing | `/reset` after enabling plugin |
| FAISS index drift | Auto-rebuilt on `AriadneMemory` init |

## Limitations

- Embeddings require `torch` + `sentence-transformers` (heavy deps)
- On ARM/aarch64, PyTorch binary compatibility issues may cause segfaults — keyword-only mode works perfectly
- No hosted/cloud option — fully local by design

## Resources

- Docs: https://ariadne.mantes.net
- Hermes guide: https://ariadne.mantes.net/guide/hermes
- GitHub: https://github.com/kyssta-exe/Ariadne