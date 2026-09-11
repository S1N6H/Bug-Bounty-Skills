---
name: small-model-distillation
title: Small Model Distillation from Frontier Teachers
description: Distill frontier model (Claude, GPT, DeepSeek) into 4-9B local model for agentic/tool-calling tasks. Covers when it works, the playbook, hardware requirements, and the hard parameter ceiling.
tags: [distillation, fine-tuning, LoRA, QLoRA, agentic, tool-calling, small-language-models]
---

# Small Model Distillation from Frontier Teachers

Distill a frontier model (Claude, GPT, DeepSeek) into a 4-9B local model for agentic/tool-calling tasks. Covers when it works, when it doesn't, the playbook, and hardware requirements.

## When to use this

- You want a local model that matches frontier at **tool calling / structured output** but is 10-50× faster
- You need a model that runs on consumer GPUs (4-24 GB VRAM)
- You're building agentic applications, not general-purpose chatbots

## Do NOT use when

- You need **general intelligence parity** with a 100B+ model — the parameter ceiling is hard (see §Limits)
- Complex multi-hop reasoning is central — the gap shows on GPQA Diamond, SWE-bench
- You can afford API calls — just call the teacher directly

## The distillation playbook

### 1. Teacher data generation

Generate tool-calling trajectories from the frontier teacher API.

**Caveat: OpenCode Go supports ANY model provider** (DeepSeek, Anthropic, OpenAI, etc.) through its subscription, not just OpenAI models. The $10/mo plan gives you $60 of usage with time-window caps.

Each example = user request → tool call trace → final response. Multi-turn agent loops are more valuable than single-turn.

#### Teacher API provider options

| Provider | Cost | Rate limits | Notes |
|---|---|---|---|
| **OpenCode Go** ($10/mo) | $60/mo credit @ same per-tok pricing | $12/5h + $30/week + $60/mo caps | Best value if you need <$60/mo of calls. Calls any provider. |
| **Direct DeepSeek API** | $0.14/M in, $0.28/M out | None (pay-per-token) | No caps, blast through in hours |
| **OpenRouter (Nemotron 3 Ultra)** | **Free** | ~200 req/day | 550B/55B MoE, better at agentic than DS V4 Flash. 50 days for 10K — too slow for big datasets |
| **NVIDIA NIM (Nemotron 3 Ultra)** | **Free** with dev account | ~40 req/min, ~1K credits one-time | Free sample for proof-of-concept, not for full dataset |
| **OpenRouter paid** | $0.14/$0.28 (same as DS) | None | Same price as direct, no caps |

**Sweet spot for cost.** 10K trajectories via OpenCode Go using DS V4 Flash:
- ~$4.20 of your $60 credit (fits in one $12/5h window easily)
- ~90 minutes continuous API calls
- $10/mo subscription vs $14 direct API cost → only worth it if you already have the sub

**Sweet spot for speed.** Direct DeepSeek API:
- 10K in ~90 minutes, no caps, no window management
- Costs $14 directly vs $0 if you have OpenCode Go credit burning

**Trajectory count guide:**
- **Sweet spot:** 10K-20K examples (~$4-30 in teacher API costs)
- **Past 100K:** diminishing returns — the student's weights saturate
- **Minimum viable:** 500-1K example (~2 hours on a 3060, ~$1-5 API cost)

### 2. Pick your base model

| Target | Best base | Context | MMLU-Pro | GPQA Diamond | VRAM (QLoRA) |
|---|---|---|---|---|---|
| Ultra-light | Qwen3.5-4B | 262K | 79.1% | 76.2% | 3-5 GB |
| Balanced | Qwen3.5-9B | 262K | **82.5%** | **81.7%** | 6-8 GB |
| Heavy local | Qwen3.5-27B | 262K | ~85% | ~84% | 20-24 GB |

Qwen3.5 uses hybrid Gated DeltaNet + Attention (3:1 ratio) — more parameter-efficient than plain transformers. This is why 9B scores 82.5% MMLU-Pro.

### 3. Fine-tuning method

Use **Unsloth QLoRA** (fastest, lowest VRAM):

```
unsloth QLoRA | r=16 | lr=1e-5 | epochs=1-2 | bf16
```

| Method | VRAM (9B) | Quality vs BF16 LoRA | Speed |
|---|---|---|---|
| QLoRA NF4 | 6-8 GB | Within 0.5-1.5 pts | Fastest |
| LoRA BF16 | 20-24 GB | Reference | 1.5× slower |
| Full FT BF16 | 40-48 GB | Marginal gain | 3× slower |

### 4. Training time

| Model | GPU | 10K examples, 1 epoch |
|---|---|---|
| Qwen3.5-4B QLoRA | RTX 3060 12GB | 1-2 hours |
| Qwen3.5-9B QLoRA | RTX 3060 12GB | 2-4 hours |
| Qwen3.5-9B QLoRA | RTX 4090 24GB | 45-90 min |

## What distillation achieves (2026 benchmarks)

| Capability | Best 4B | Best 9B | Teacher (DS V4 Flash) |
|---|---|---|---|
| Tool calling accuracy | **97.5%** (match) | **98%** (match/beat) | ~97% |
| Format following (IFEval) | ~91% | ~93% | ~94% |
| Simple agent loops (2-3 hops) | ~92% | ~95% | ~96% |
| Complex multi-hop agents | ~78% | ~84% | ~90% |
| MMLU-Pro | ~80% | ~83% | 86.2% |
| GPQA Diamond | ~78% | ~82% | 88.1% |

## Limits (the hard parameter ceiling)

- **4B:** Hard ceiling at ~79% MMLU-Pro, ~76% GPQA Diamond in any architecture
- **9B:** ~82.5% MMLU-Pro, ~81.7% GPQA Diamond
- **These are NOT data problems** — the weights can't hold more computation per token
- To close the remaining gap: need MoE (3-4B active) or 14-27B dense architecture

## Pitfalls

- **OpenCode Go is NOT OpenAI-only.** It routes to any provider (DeepSeek, Anthropic, etc.) through its subscription. Don't assume it's locked to OpenAI like I did.
- **More data ≠ better model past saturation.** 500K examples won't outperform 20K well-curated ones once weights are full.
- **Architecture transfers through nothing in data.** Distillation teaches output distributions, not algorithmic mechanisms (sparse attention, MoE routing). The student never inherits the teacher's architecture.
- **Subscription API caps require script-level juggling.** OpenCode Go's $12/5h cap means your generation script must catch 429s, sleep, and resume. See `scripts/generate-trajectories.py`.
- **Benchmarks can be gamed.** A distilled model scoring 95% on BFCLv4 may still fail on novel tool schemas. Test on your actual workload.
- **Knowledge distillation narrows capability.** Training only on tool-calling data regresses general QA. Mix in 10-20% general instruction data.
