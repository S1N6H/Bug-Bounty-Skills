---
name: hermes-free-tier-setup
category: devops
description: Class-level skill for configuring Hermes Agent with 100% free LLM providers, intelligent fallback chains, and optimized auxiliary models
triggers:
  - User wants to run Hermes Agent without paying for API credits
  - User hits rate limits and needs resilient multi-provider setup
  - User wants to configure auxiliary models for cost optimization
  - User needs key stacking to multiply free quotas
---

# Hermes Free-Tier Setup Skill

**Class-level skill for configuring Hermes Agent with 100% free LLM providers, intelligent fallback chains, and optimized auxiliary models.**

---

## Trigger Conditions

- User wants to run Hermes Agent without paying for API credits
- User hits rate limits on current provider and needs resilient multi-provider setup
- User wants to configure auxiliary models for cost optimization
- User needs key stacking (multiple API keys per provider) to multiply free quotas

---

## Procedure

### 1. Research Current Free Providers (if not cached)

Check these 13 providers for current free tier limits:
- **OpenRouter** — 29+ `:free` models, 200 req/day (1K with $10 top-up)
- **Groq** — Llama 3.3 70B, 1K req/day, 320 tok/s
- **Google AI Studio** — Gemini 2.5 Flash, 1,500 RPD, 1M context
- **NVIDIA NIM** — Nemotron/Llama, free credits, 40 RPM
- **OpenCode Zen** — 5 free coding models (limited time)
- **NovitaAI** — 200+ models, free credits on signup
- **Hugging Face** — Monthly credits via Inference Providers
- **GitHub Models** — GPT-4o, Claude 3.5, Llama, 150-1K/day
- **Cloudflare Workers AI** — 20+ models, 10K neurons/day
- **Cohere** — Command R+, ~100/day (non-commercial)
- **Mistral** — 1B tokens/month (Experiment tier, data training opt-in)
- **Cerebras** — 1M tokens/day on Llama 3.3 70B
- **Ollama (Local)** — Unlimited, zero cost, hardware dependent

### 2. Build Fallback Chain (20 layers recommended)

Order by: reasoning quality → speed → coding specialty → context window → local → others

```
1. OpenRouter: Nemotron 3 Ultra (primary, best reasoning)
2. OpenRouter: Nemotron 3 Super
3. Groq: Llama 3.3 70B (speed)
4. OpenRouter: Poolside Laguna M.1 (coding)
5. Google: Gemini 2.5 Flash (1M context)
6. Local: Ollama Qwen3.5 27B (unlimited)
7. OpenRouter: Cohere North Mini Code
8. OpenRouter: Gemma 4 31B (multimodal)
9. OpenRouter: GPT-OSS 120B
10. OpenRouter: Laguna XS 2.1
11. NVIDIA NIM: Nemotron 3 Ultra
12. OpenCode Zen: MiMo/North Mini/Nemotron/Big Pickle/DeepSeek
13. NovitaAI: Gemma 4 31B
14. Hugging Face: Llama 3.3 70B
15. GitHub Models: GPT-4o/Claude 3.5
16. Cloudflare: Llama 3.3 70B
17. Kimi/Moonshot: Long context
```

### 3. Configure Auxiliary Models (11 tasks)

Each auxiliary task gets its own optimized free model + fallback chain:

| Task | Primary | Fallback |
|------|---------|----------|
| Vision | Gemma 4 31B | Gemini Flash → Nemotron Nano Omni → Big Pickle |
| Compression | GPT-OSS 20B | Nemotron Nano 30B → Nemotron Nano 9B → Groq 8B → DeepSeek Flash |
| Web Extract | GPT-OSS 20B | Nemotron Nano 30B → Gemini Flash Lite → Groq 8B |
| Title Gen | Gemma 4 26B MoE | Ring 2.6 → Nemotron Nano → Groq 8B |
| Approval | Nemotron Nano 30B | Cohere North Mini → GPT-OSS 20B → Gemini Flash |
| Skills Hub | Auto (main) | GPT-OSS 20B → Groq 8B |
| MCP | Auto (main) | GPT-OSS 20B → Groq 8B |
| Triage Spec | Nemotron Nano 30B | Cohere North Mini → GPT-OSS 20B |
| Kanban Decomp | Nemotron 3 Super | Nemotron 3 Ultra → Gemini Flash |
| Profile Describer | Gemma 4 26B MoE | Ring 2.6 |
| Curator | GPT-OSS 20B | Nemotron Nano → Groq 8B |

### 4. Set Up Credential Pools (Key Stacking)

Add multiple keys per provider in `credential_pools` to multiply limits 3-5x:

```yaml
credential_pools:
  openrouter:
    - env: OPENROUTER_API_KEY
    - env: OPENROUTER_API_KEY_2
    - env: OPENROUTER_API_KEY_3
  groq:
    - env: GROQ_API_KEY
    - env: GROQ_API_KEY_2
  # ... etc
```

### 5. Apply Configuration

```bash
# Copy template to active config
cp ~/.hermes/config-free-tier.yaml ~/.hermes/config.yaml

# Add API keys to .env
nano ~/.hermes/.env

# For local models (optional but recommended)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen3.5:27b   # 16GB VRAM
# ollama pull qwen3:8b    # 8GB VRAM

# Migrate config to latest version (REQUIRED after applying new config)
hermes doctor --fix

# Verify
hermes doctor
hermes chat
```

### 6. Verify Fallback Works

In chat, test model switching:
```bash
/model openrouter/free
/model groq/llama-3.3-70b-versatile
/model gemini/gemini-2.5-flash
/model ollama/qwen3.5:27b
```

**Or use the verification script:**
```bash
./scripts/verify-free-tier.sh
```

**Or test individual providers non-interactively:**
```bash
hermes chat -q "Say OK"          # Primary (Nemotron 3 Ultra)
hermes chat -q "Say OK" --provider groq
hermes chat -q "Say OK" --provider gemini
hermes chat -q "Say OK" --provider opencode-zen
hermes chat -q "Say OK" --provider custom:ollama-local
```

**Optional: Remove unused custom providers** (e.g., if you don't run LiteLLM proxy):
```bash
# Edit config.yaml and remove the `litellm-free` entry from `providers:` section
# Also remove LITELLM_MASTER_KEY from .env if not needed
```

---

## Pitfalls & Gotchas

- **OpenRouter free tier is tight** — 200 req/day burns fast with agent loops. Key stacking essential.
- **Groq token budget is binding** — 500K tokens/day on 70B model = ~25-50 agent tasks/day.
- **Google AI Studio bans OAuth in third-party apps** — Use API key method only.
- **OpenCode Zen free models are time-limited** — "Limited time" free period, may become paid.
- **Local models need 64K+ context** — Configure Ollama `num_ctx` or modelfile.
- **Nemotron 3 Ultra is 550B MoE** — Excellent but can be slower; use Nemotron 3 Super for speed fallback.
- **Auxiliary models on `auto` use main model** — Explicitly configure cheap models for vision/compression/titles to save primary quota.
- **`--provider` flag for testing** — Use `hermes chat -q "test" --provider <name>` to test individual providers non-interactively. Provider names match `fallback_providers` entries: `openrouter`, `groq`, `gemini`, `opencode-zen`, `nvidia`, `novita`, `huggingface`, `github-models`, `cloudflare`, `kimi-coding`, `custom:litellm-free`, `custom:ollama-local`, etc.
- **Config version migration** — Run `hermes doctor --fix` after major version upgrades.
- **Template config must be migrated** — After copying `config-free-tier.yaml` to `config.yaml`, you MUST run `hermes doctor --fix` to migrate config version and register custom providers. Without this, custom providers won't be available and config will show as outdated.
- **Remove unused custom providers** — If you don't need a custom provider (e.g., no LiteLLM proxy), delete its entry from `providers:` in `config.yaml` and remove its key from `.env`. Run `hermes doctor --fix` after to clean up.

---

## References

- `references/free-provider-comparison.md` — Detailed provider limits, models, signup URLs
- `references/fallback-chain-design.md` — Reasoning behind 20-layer chain order
- `references/auxiliary-model-optimization.md` — Why each auxiliary task gets its model
- `references/key-stacking-guide.md` — How to multiply free quotas with multiple keys
- `references/provider-test-names.md` — Exact `--provider` flag values for each config entry
- `templates/config-free-tier.yaml` — Complete production-ready config template
- `scripts/setup-free-tier.sh` — Automated setup script
- `scripts/verify-free-tier.sh` — Complete verification script (run to test all fallbacks)

---

## Transitioning to Paid Subscriptions

When free-tier rate limits, auth failures, or model quality become blockers, use this procedure to diagnose provider health and recommend cost-effective paid subscriptions.

### 1. Audit Current Provider Health

```bash
hermes insights --days 30     # Usage volume: sessions, tokens, models used
hermes auth list              # Credential status (rate-limited? auth failed?)
hermes config                 # Active provider setup and fallback chain
hermes doctor                 # Config + dependency health check
```

Diagnose each signal:
- **`rate-limited (429)`** — hitting free quotas. $5-10 in OpenRouter credits often fixes everything at once since the fallback chain already routes through OpenRouter.
- **`auth failed (401)`** — expired keys or provider cutoff. Investigate; may need re-auth or new account.
- **`usage_limit_reached`** — OAuth account (e.g. ChatGPT/Codex Pro) hit its monthly cap. Upgrade plan or wait for reset.
- **No credential for a provider** — weak spot. If user has a model they want to use (Claude, GPT-5.5, GLM-5.1), they need either that provider's API key or OpenRouter credits.

### 2. Map Pain Points to Subscriptions

| Current barrier | Best fix | Monthly cost |
|----------------|----------|-------------|
| OpenRouter free 429s | **$5-20 OpenRouter credits** — unlocks rate limits, paid models, no config changes | $5-20 (pay-as-you-go, lasts 1-6 months at moderate use) |
| Need Claude for coding | **Claude Pro ($20) + `hermes proxy`** — OAuth proxy from your Claude subscription | $20/mo (limited) |
| Need Claude for heavy use | **Anthropic API key** — pay per token, ~$3/M in / $15/M out for Sonnet 4.6 | $50-300+/mo depending on volume |
| Need GPT-5.5 reliably | **OpenAI API credits** (already have key? just add billing) or OpenRouter | $10-100+/mo depending on model tier |
| Need DeepSeek V4 without limits | **DeepSeek API key** — cheapest paid option at $0.09/M in / $0.18/M out | ~$50-70/mo at heavy volume (1.8B tokens/mo) |
| Need GLM-5.1 / Kimi K2.6 / MiMo | **OpenRouter credits** — all available via existing OR key | Covered by $5-20 credits above |
| Multiple providers all exhausted | **Single OpenRouter credit top-up** — one billing, all providers unblocked | $10-50/mo |

### 3. Estimate for Heavy Users (example: 44 sessions/day, 1.8B tokens/11 days)

If the user is hitting free limits on OpenRouter + Gemini + several others simultaneously:

**Worst case — all sessions on cheapest paid model (deepseek-v4-flash):**
- ~$50-70/mo via DeepSeek API direct
- ~$60-80/mo via OpenRouter at same model pricing

**Mixed case — 80% deepseek-v4-flash + 20% GPT-5.5:**
- ~$40-60/mo for bulk DeepSeek + $30-50/mo for GPT-5.5 on the heavy sessions
- Total: $70-110/mo

**The single best $5-20 fix:** OpenRouter credits. Your existing fallback chain already routes through OpenRouter for free models — adding credits upgrades those same routes to paid tier with higher rate limits, no config changes required.

### 4. Budget-Constrained Decision Tree

```
Can user afford $50-100/mo?
├── YES → Do they need Claude/GPT-5.5 quality?
│   ├── YES → Get Claude Pro ($20) + $10-30 OpenRouter credits
│   └── NO  → Put $5-20 on OpenRouter credits. Done.
└── NO  → Maximize free tier stacking (see main procedure above)
         → Consider DeepSeek API direct ($0.09/M in — very cheap)
         → Consider one paid model on OR with $5 top-up
```

### 5. Gotchas

- **User may say "subscription" and mean Hermes/Nous Portal** — always clarify. They might mean ChatGPT Pro, Claude Max, Z.AI, or external AI subs. Ask before diving into one track.
- **Users with existing API keys** (OpenAI, OpenRouter) may just need to add billing — no new subscription needed.
- **`hermes proxy`** can proxy a ChatGPT Plus or Claude Pro subscription for model access without an API key — useful if they already pay for those services.
- **Always give exact dollar figures per scenario** (1/5/10/50 users or 1/10/100 sessions), not percentages or hedging — this user's preference.
- **Free OpenCode Go/Zen endpoints can provide deepseek-v4-flash at $0** — if that model suffices, the user may not need any paid subscription at all despite hitting limits on other providers.

---

## References

- `references/free-provider-comparison.md` — Detailed provider limits, models, signup URLs
- `references/fallback-chain-design.md` — Reasoning behind 20-layer chain order
- `references/auxiliary-model-optimization.md` — Why each auxiliary task gets its model
- `references/key-stacking-guide.md` — How to multiply free quotas with multiple keys
- `references/provider-test-names.md` — Exact `--provider` flag values for each config entry
- `references/subscription-audit-worked-example.md` — Worked example: analyzing provider health and recommending paid subscriptions from real `hermes insights` data
- `templates/config-free-tier.yaml` — Complete production-ready config template
- `scripts/setup-free-tier.sh` — Automated setup script
- `scripts/verify-free-tier.sh` — Complete verification script (run to test all fallbacks)

---

## Verification Checklist

- [ ] `hermes doctor` passes with no config errors
- [ ] Primary model (Nemotron 3 Ultra) responds
- [ ] Fallback chain triggers on simulated rate limit
- [ ] Auxiliary vision works with Gemma 4 31B
- [ ] Compression saves ~80% tokens on long conversation
- [ ] Local Ollama model loads and responds
- [ ] Key stacking: 3 OpenRouter keys = ~600 req/day
- [ ] `openrouter/free` auto-selects available free model
- [ ] Provider audit: `hermes auth list` checked for 429/401/limit-reached states
- [ ] Subscription recommendation: exact dollar figures per usage scenario
- [ ] Clarify phase: distinguished "Hermes/Nous Portal subscription" vs "external AI service subscription" before proceeding