---
name: llm-api-provider
description: Build and operate an LLM API provider business — cost modeling, multi-provider routing, subscription billing, sub-limit enforcement.
domain: mlops
tags:
  - llm
  - api
  - business
  - billing
  - infrastructure
  - lite-llm
---

# LLM API Provider Business

Build a subscription-based API provider for agentic coding tools (Hermes, OpenCode, Cline, etc.). Covers cost analysis, infrastructure setup, pricing design, and sub-limit enforcement.

## When to Load

Load this skill when the user asks to:
- Start an API reseller/provider business for LLMs
- Compete with OpenCode Go, Command Code, Freebuff, or similar services
- Build a multi-provider routing proxy with billing
- Analyze pricing, margins, and breakeven for an API service
- Set up LiteLLM + Stripe + PostgreSQL for subscription-based LLM access
- Ship a free-tier agentic coding CLI built from OpenCode's open-source codebase

## Core Concepts

### The Business Model
- Users pay a flat monthly subscription (e.g. $6.90/mo)
- They get up to a dollar-value cap of usage (e.g. $60/mo worth of tokens)
- Free models (Nemotron, Llama, Mistral via NVIDIA NIM/Groq) cost you $0
- Paid models (DeepSeek, GLM, Kimi) cost you wholesale rates
- Your margin comes from: (a) subscription fees, (b) cache pooling across users, (c) multi-provider routing to cheapest backend
- **Sub-limits** (5hr/daily/weekly) prevent burst abuse but don't eliminate risk — the monthly cap is what binds

### Key Numbers (Current Market)
- DeepSeek V4 Flash: $0.14/$0.28 per 1M tokens (cache hit: ~$0.018)
- DeepSeek V4 Pro: $0.44/$0.87 per 1M tokens (cache hit: ~$0.058)
- MiMo-V2.5: $0.14/$0.28 per 1M tokens (cache hit: ~$0.028)
- MiMo-V2.5-Pro: $0.44/$0.87 per 1M tokens (cache hit: ~$0.058)
- MiniMax M2.7: $0.18/$0.72 per 1M tokens (cache hit: ~$0.024)
- MiniMax M3: $0.30/$1.20 per 1M tokens (cache hit: ~$0.039)
- Qwen3.7 Plus: $0.32/$1.28 per 1M tokens (cache hit: ~$0.064)
- Qwen3.6 Plus: $0.325/$1.95 per 1M tokens (cache hit: ~$0.033)
- Avg coding agent request: ~790 new input + ~68K cached input + ~295 output tokens
- Avg cost per request (DeepSeek Flash, with caching): ~$0.0014 wholesale
- Avg cost per request across all models (blended): ~$0.0024 wholesale

## Step-by-Step

### 1. Cost Analysis
Always start with hard numbers. Use tables showing exact dollar figures per scenario:

| Users | Type | Revenue | LLM Cost | Fixed Cost | Profit |
|-------|------|---------|----------|------------|--------|
| 5 | All light | $34.50 | $5 | $4.50 | +$25 |
| 5 | 1 heavy | $34.50 | $23 | $4.50 | +$7 |
| 10 | Normal mix | $69 | $29 | $4.50 | +$36 |
| 10 | 2 heavies | $69 | $58 | $4.50 | +$6 |

**Always include worst-case, expected, and best-case scenarios.**

### 2. Architecture Planning

```
User → Nginx :80
         │
         ▼
Flask App (auth + sub-limit check + usage logging)
         │
         ▼
LiteLLM Proxy (provider routing + fallback + caching)
         │
         ├──► DeepSeek (paid primary)
         ├──► NVIDIA NIM (free — Nemotron, Llama, MiniMax)
         ├──► Groq (free — Llama, Qwen, fast LPU)
         ├──► Mistral (free — Medium, Codestral)
         ├──► SiliconFlow (paid fallback)
         └──► OpenRouter (free fallback)
```

**Database tables needed:**
- `users` — email, password_hash, plan, stripe_id, is_active
- `api_keys` — key_hash, key_prefix, user_id (FK)
- `usage_log` — user_id, model, tokens, cost_usd, billed_usd
- `spend_snapshots` — user_id, billing_period, total_cost
- `invoices` — user_id, stripe_invoice_id, amount
- `stripe_events` — id, type, processed (idempotency)

### 3. Price Design

#### 3a. Calculate Per-Request Wholesale Cost

Before setting ANY prices, calculate the true cost per request for each model accounting for cached tokens:

```python
# Typical agentic coding request:
NEW_IN = 790      # uncached input tokens
CACHED_IN = 68000  # cached (repeated) input tokens
OUT = 295          # output tokens

def cost_per_request(input_rate, cached_rate, output_rate):
    return (NEW_IN * input_rate / 1_000_000) + \
           (CACHED_IN * cached_rate / 1_000_000) + \
           (OUT * output_rate / 1_000_000)
```

Example for DeepSeek V4 Flash: $0.14 input, $0.018 cached, $0.28 output
→ (790 × 0.14 + 68000 × 0.018 + 295 × 0.28) / 1M = **$0.001417/request**

#### 3b. The Per-Model Markup Matrix (CRITICAL)

**Do NOT use a single markup across all models.** Each model has a different competitive position vs OpenCode Go/Command Code, and your wholesale cost vs their internal rate varies wildly:

| Model | Wholesale/req | OC Internal/req | Ratio | Status |
|-------|-------------|----------------|-------|--------|
| DeepSeek V4 Flash | $0.001417 | $0.000379 | **3.7x** | OC sells at loss |
| MiMo-V2.5 | $0.002097 | $0.000399 | **5.3x** | OC sells at loss |
| MiniMax M2.7 | $0.001987 | $0.003529 | **0.56x** | You're cheaper |
| Qwen3.6 Plus | $0.003042 | $0.003636 | **0.84x** | You're cheaper |
| DeepSeek V4 Pro | $0.004544 | $0.003478 | **1.3x** | Near cost |

OpenCode Go uses **DeepSeek Flash and MiMo V2.5 as loss leaders** — they sell them at prices below wholesale to attract users. They fund this by making margin on MiniMax/Qwen models and charging $10/mo instead of $6.90.

**Set a DIFFERENT internal billing rate per model** to balance competitiveness and margin:

```python
nectar_internal_rate = {
    "DeepSeek V4 Flash": 0.001200,   # -18% margin (loss leader, but less bleeding)
    "MiMo-V2.5":         0.001800,   # -16% margin
    "MiniMax M2.7":      0.002800,   # +29% margin — YOUR STAR MODEL
    "MiniMax M3":        0.004200,   # +23% margin
    "DeepSeek V4 Pro":   0.005500,   # +17% margin
    "MiMo-V2.5-Pro":     0.005500,   # +17% margin
    "Qwen3.7 Plus":      0.005500,   # +9% margin
    "Qwen3.6 Plus":      0.003800,   # +20% margin
}
```

These internal rates determine how fast a user burns through their dollar cap on each model. A user gets MORE requests on profitable models (where their dollar goes further) and FEWER on loss leaders.

#### 3c. The Dual-Cap System

Implement TWO constraints that BOTH apply — the user is limited by whichever hits first:

**Cap 1: Per-model request limits** — "You can make X requests of model Y per window"
These are calculated as: `dollar_cap / internal_rate[model]`

**Cap 2: Shared dollar caps** — "Your total billed usage across all models cannot exceed $Z"
This is the overall financial safety net.

Example for Starter plan ($10/5hr) using the per-model rates above:

| Model | 5hr Request Limit | vs OpenCode Go |
|-------|------------------|---------------|
| DeepSeek V4 Flash | 8,333 (=$10÷$0.001200) | 26% |
| MiniMax M2.7 ★ | 3,571 (=$10÷$0.002800) | **105% — WIN** |
| Qwen3.6 Plus | 2,632 (=$10÷$0.003800) | **80%** |

MiniMax M2.7 gives users **better value than OpenCode Go** while being your most profitable model. Position it as the hero/primary model.

#### 3d. Reverse-Engineer Competitor Internal Rates

OpenCode Go publishes per-model request limits per 5-hour window. From these, you can derive their internal billing rate:

```python
oc_internal_rate = dollar_cap / requests_per_window
# Example: $12 / 31,650 DeepSeek Flash requests = $0.000379/request
```

Full OC rates table (at $12/5hr cap):
- DeepSeek V4 Flash: $12/31,650 = $0.000379/req
- MiMo-V2.5: $12/30,100 = $0.000399/req
- MiniMax M2.7: $12/3,400 = $0.003529/req
- DeepSeek V4 Pro: $12/3,450 = $0.003478/req
- Qwen3.7 Plus: $12/4,300 = $0.002791/req

This tells you exactly where competitors are subsidizing (rates far below wholesale) and where they're making margin.

#### 3e. Blended Margin & Portfolio Math

Calculate the expected blended margin using an estimated usage mix:

```python
usage_mix = {
    "DeepSeek V4 Flash": 0.35,
    "MiMo-V2.5":         0.15,
    "MiniMax M2.7":      0.20,
    # ... rest of models
}

wavg_cost = sum(mix[m] * wholesale_cost[m] for m in mix)
wavg_rate = sum(mix[m] * internal_rate[m] for m in mix)
portfolio_margin = (wavg_rate - wavg_cost) / wavg_rate
```

Then model per-user economics:
| User Type | Req/mo | Cost | Revenue | Net |
|-----------|--------|------|---------|-----|
| Light | 2,000 | $4.78 | $6.90 | +$2.12 |
| Medium | 15,000 | $35.82 | $6.90 | -$28.92 |
| Heavy | 50,000 | $119.39 | $6.90 | -$112.49 |

**Break-even analysis**: At a given user tier mix, find the minimum user count where total revenue exceeds total cost. With the $6.90/$50 cap model, breakeven requires ~50+ users with a 90% light user base.

#### 3f. Practical Request-Volume Threshold Analysis (Critical)

**The key insight: 95% of real users NEVER hit the per-model request limits, even if your limits are 70-80% lower than OpenCode Go's.**

A real human using agentic coding operates at **4-12 requests per minute** (each tool call takes 5-15 seconds). Contrast this with the per-model limits:

| Scenario | Requests | Duration | Nectar Flash Limit (7,698/5hr at cost+10%) | Hits limit? |
|----------|---------|----------|------------------------------------------|-------------|
| Fix a bug | 30 | 1 hr | Consumes 0.4% of $12 cap | No |
| Build a feature | 150 | 2 hr | Consumes 1.9% of $12 cap | No |
| Half-day coding | 500 | 5 hr | Consumes 6.5% of $12 cap | No |
| Full day coding | 1,200 | 8 hr | Consumes 15.6% of $12 cap | No |
| Power user (all-day agents) | 3,000 | 12 hr | Consumes 39% of $12 cap | No |
| **Bot / script / abuser** | **8,000+** | 24 hr | **Exceeds $12/5hr cap** | **Yes** |

Even at Nectar's cost+10% Flash rate ($0.001559/req), a power user making **3,000 requests in 12 hours** only burns **$4.68** of the $12 5hr cap. The cap only matters for automated scripts doing 8,000+ requests in 5 hours — which is **25+ requests per minute** sustained.

**The real constraint for daily users is the monthly cap ($50-60), not the per-model limits.** The per-model limits only prevent bots from draining your budget overnight.

Document this in your marketing: "OC's 31,650 Flash limit sounds generous, but no human makes 100 requests per minute. Our limit matches real-world coding speed. The extra only benefits abusers."

#### 3g. Student / Solo Founder Budget Strategy

When you can only tolerate **$25-50/month total loss** (not per-user), use this approach:

**Step 1: Calculate your monthly burn ceiling.**
Ask: what's the most I can lose per month before I shut this down?
- $25/mo → treat as learning experiment
- $50/mo → side project budget
- $100/mo → serious solo business

**Step 2: Use the cost+10% approach for simplest math.**

Set every model's internal rate at wholesale × 1.1 (10% margin per request):

```python
nectar_rate = {model: wholesale_cost[model] * 1.1 for model in wholesale_cost}
```

This means Nectar makes 10% on every single request regardless of model. The only way you lose money is if a user makes ENOUGH requests that cumulative cost exceeds the subscription. That's handled by the monthly cap.

**Step 3: Sub-limits protect you from overnight ruin, not monthly loss.**

The $12/5hr cap prevents ONE user from burning $60 in one session. But over a month, even with sub-limits, a determined user can still max the $60 monthly cap. The monthly cap is YOUR real protection — sub-limits just prevent burst.

**Step 4: Model the portfolio, not the individual.**

| Scenario | 10 users | 25 users | 50 users |
|----------|---------|---------|---------|
| Worst case (all heavy) | -$470/mo ❌ | -$1,190/mo ❌ | -$2,380/mo ❌ |
| Realistic (80% light, 15% regular, 5% heavy) | -$46/mo | **+$47/mo ✅** | **+$107/mo ✅** |
| Ideal (95% light) | **+$38/mo ✅** | **+$114/mo ✅** | **+$238/mo ✅** |

With the cost+10% approach and $60 monthly cap:
- A pure Flash abuser maxes out at **-$47.65/month** loss
- A MiniMax user maxes out at **-$26.88/month** loss
- **Light users (500-2K reqs/mo) are always profitable (+$3 to $6/user)**
- **Breakeven at ~15-20 users with normal mix**
- At 50 users: **profitable even with 5% heavy users**

**Step 5: Accept some loss-leader models or cut them.**

| Strategy | Models offered | Max loss/user | Breakeven users | Student-viable? |
|----------|--------------|--------------|----------------|-----------------|
| All models, $60 cap | Flash + MiMo + all | -$47.65 | ~15 | ✅ Yes |
| No loss leaders, $60 cap | All EXCEPT Flash/MiMo | -$34.41 | ~10 | ✅ Yes |
| All models, $30 cap | Flash + MiMo + all | -$23.82 | ~8 | ✅ Yes |

**The cost+10% approach is the safest for a solo founder.** You make 10% margin on every request, the sub-limits prevent burst bleeding, and the monthly cap is the only real loss exposure. You cannot lose more than $47.65/month per Flash abuser, which is a known, manageable ceiling.

**Do NOT do what VC-funded competitors do** — don't sell Flash/MiMo 3-5x below wholesale to capture market share. You don't have the runway. Let OpenCode Go hemorrhage money on Flash abusers while you profit on the same users through cost+10% pricing and superior caching.

### ⚠️ CRITICAL WARNING: The 80% Heavy User Adverse Selection Trap

**This is the single most dangerous assumption in flat-rate LLM reselling.**

Every financial model in this skill assumes a "normal" user mix (70-80% light, 15-20% medium, 5% heavy). **If you price too low, you attract the opposite mix: 80% heavy, 20% light.**

Why? Because $6.90 for $60 of DeepSeek Flash access is an insane deal for a heavy user — they save ~$35/month vs buying Flash directly. Light users barely notice the savings. The people who MOST want your service are the ones who COST you the most.

**The 80% heavy scenario kills every flat-rate model:**

| Plan | 100 users (80% heavy @ 30K Flash reqs/mo) | Monthly loss |
|------|-------------------------------------------|-------------|
| $6.90/mo, $60 cap, all models | 80 × -$47.65 + 20 × +$6.19 = -$3,687 | **-$3,687/mo ❌** |
| $10/mo, $60 cap, all models | 80 × -$43.36 + 20 × +$9.29 = -$3,082 | **-$3,082/mo ❌** |
| $6.90/mo, $30 cap, all models | 80 × -$23.82 + 20 × +$6.19 = -$1,781 | **-$1,781/mo ❌** |
| $6.90/mo, $60 cap, MiniMax only | 80 × -$26.88 + 20 × +$5.91 = -$1,436 | **-$1,436/mo ❌** |

**NO flat-rate plan survives 80% heavy usage.** Period.

**The only strategies that work against adverse selection:**
1. **BYOK Flash** — users bring their own DeepSeek key. Nectar never pays for Flash. $6.90 pure profit on every user regardless of usage.
2. **Pay-per-use models** — $6.90 base includes limited Flash (2K reqs/mo), then $0.002/req extra. Heavy users auto-convert to paying their own cost.
3. **Don't target the bottom of the market** — price at $12-15/mo so you attract users who value quality over cheapest price.
4. **Accept it as customer acquisition cost** — if you have VC funding to cover 6 months of losses while you grow.

#### 3h. The "5-Hour Window is Your Shield" Principle

When a user asks "what if someone maxes out $60 in a day?" — the answer is they CAN'T because of the $12/5hr sub-limit. Here's how it actually plays out:

```
A heavy Flash user tries to burn through everything:
• Hours 0-5: $12 cap hit → 7,698 req → costs you $10.90
• Hours 5-10: $8 remaining on daily $20 cap → 5,132 req → costs you $7.27
• Day total: $20 cap hit → 12,830 req → costs you $18.17
• Day loss: $18.17 - $6.90/30 = $18.17 - $0.23 = $17.94 loss today
• BUT: can they do this EVERY day? No — $30/weekly cap binds after ~$20+$10 on day 2
• Monthly cap ($60) means they can have 3 such days max before cutoff
• Total monthly loss: ~$54.52 wholesale cost - $6.90 revenue = -$47.62
```

The sub-limits turn a potential overnight blowout into a manageable, capped loss.

#### 3i. Honest Price Floor

Use the **6:1 rule** — the market standard set by OpenCode Go ($10/mo → $60 cap). Your monthly cap should be ~6x the subscription price. A ratio higher than 6:1 (e.g., 8.7:1 at $6.90/$60) means a single heavy user maxing their cap loses you **-$53.10/mo** with cost+10% pricing. At 6:1, the same worst case loses only **-$10/mo** — manageable.

**BUT the 6:1 rule assumes the competitor's blended cost structure.** Your actual break-even price depends heavily on which models you offer and your wholesale rates. For a lineup that includes DeepSeek Flash and MiMo V2.5 (OC's loss leaders), the minimum viable price is **$12-19/user/month** depending on user mix.

Realistic pricing options:
| Strategy | Price | Monthly Cap | Viability | Max Loss/User (cost+10%) |
|----------|-------|------------|-----------|------------------------|
| Match OC | $10/mo | $60 | Sustainable at 50+ users | -$37.65 |
| Undercut | $6.90/mo | $50 | Requires ~100 users | -$47.65 |
| Lite | $6.90/mo | $30 | Zero-loss at any scale | -$23.82 |
| Premium | $15/mo | $75 | Profitable from 10 users | -$32.94 |

Recommended tier structure:

| Plan | Price | Monthly Cap | Ratio | 5hr | Daily | Weekly |
|------|-------|------------|------|-----|-------|--------|
| Starter | **$6.90/mo** | $40-60 | 5.8-8.7:1 | $12 | $20 | $30 |
| Pro | **$15/mo** | $90 | 6:1 | $25 | $40 | $60 |
| Power | **$30/mo** | $180 | 6:1 | $50 | $80 | $120 |

**Free models should NOT count toward caps** — they cost you nothing, let users use them unlimited.

### 7. Competitive Positioning vs OpenCode Go

When you can't match OC's loss-leader pricing on Flash/MiMo (they sell 3-5x below wholesale), compete on these 7 differentiators:

| # | Differentiator | What it means for the user |
|---|---|---|
| 1 | **$6.90 flat forever** | Save $32/year vs OC's $5→$10. No ballooning. |
| 2 | **3-day free trial, no card** | Lower risk to try. OC: $5 first month billed. |
| 3 | **Shared Redis cache** | System prompts cached once across ALL users. 87% cheaper cached tokens = user's $12 cap buys more diverse work, not the same system prompt. |
| 4 | **Auto multi-provider failover** | DeepSeek down? Routes to MiniMax/Qwen seamlessly. OC users burn cap on retries. |
| 5 | **Daily $20 sub-limit** | OC has no daily cap. Nectar's $20/day keeps service healthy for everyone — prevents one user from dragging down latency for all. |
| 6 | **BYOK option** (future) | Hit the $60 cap? Plug in your own DeepSeek key to keep going. OC is locked into their own billing pool. |
| 7 | **Usage dashboard** | Per-model, per-session breakdown. OC shows a number; Nectar shows the story. |

**The core messaging:**

> *"Nectar gives you the same Flash, MiMo, MiniMax, and Pro models as OpenCode Go. Same $60 monthly cap. Same per-model request limits for real-world coding. But $6.90 flat — not $5 that turns into $10. With caching that makes your cap go further and auto-failover when DeepSeek has an outage.*

> *OC's 31,650 Flash limit sounds generous — but a human makes 4-12 requests per minute in agentic coding. You'd need a bot running 24/7 to hit that limit. Our 7,698 limit matches every real coding workflow. The extra headroom only benefits abusers who cost OC money."*

**When to cut loss-leader models vs keep them:**

| Strategy | Models offered | Max loss/user | When to use |
|----------|--------------|--------------|-------------|
| All-in (include Flash + MiMo) | All 8 models | -$47.65/mo | Need flashy marketing (same models as OC) |
| Premium-only (cut loss leaders) | MiniMax, Pro, Qwen only | -$34.41/mo | Safer; position as no cheap models eating your credits |
| Tiered (Flash limited) | All models, Flash capped | -$35-40/mo | Best compromise — Flash exists but doesnt drain you |

### BYOK Flash: The Only Student-Proof Strategy

DeepSeek V4 Flash is the cheapest capable model on earth ($0.14/$0.28 per M tokens). There is no cheaper model to fall back to. This means:

1. Every competitor (OpenCode Go, Command Code, etc.) sells Flash at near or below wholesale
2. Users KNOW Flash is cheapest and will use it for everything — it gives them the most requests per dollar of cap
3. Reselling Flash at flat-rate pricing is structurally unprofitable for anyone without VC funding or bulk discounts

**The solution: Let users bring their own DeepSeek API key for Flash/MiMo.** Nectar provides everything else:

| Component | Who pays |
|-----------|----------|
| Flash / MiMo requests | **User** (via their own DeepSeek key) |
| MiniMax M2.7/M3 | **Nectar** (included in $6.90 — profitable) |
| Qwen Pro / DeepSeek Pro / MiMo Pro | **Nectar** (included in $6.90 — profitable) |
| Infrastructure (cache, routing, dashboard) | **Nectar** ($0-15/mo AWS free tier) |

**User proposition:**
- Same $6.90/month (cheaper than OCs $10)
- Flash through their own key = unlimited, no cap contention
- MiniMax M2.7 included for free (OC makes you use Flash to save your cap)
- One unified endpoint — no switching between providers
- Shared cache + auto-failover — faster than running raw DeepSeek API

**Your risk: $0 on Flash. Profit on every user from day one.**

**Variation: Pay-per-use hybrid** — $6.90 includes 2,000 Flash reqs/mo, then $0.002/req (cost + 40%). Heavy users self-fund their overage. Light users never notice. Zero loss exposure.

See `references/student-bootstrap-strategy.md` for the full implementation timeline, including the AWS credit bootstrap play (use credits to cover infrastructure for 6-12 months while you build the user base).

### 4. Infrastructure Setup

Use Docker Compose with:
- `postgres:16-alpine` — usage tracking + user data
- `redis:7-alpine` — caching + rate limiting
- `ghcr.io/berriai/litellm:main-latest` — LLM proxy
- Custom Flask app — billing, auth, dashboard
- Nginx — reverse proxy with SSL termination

**Critical: Create custom database tables from the Flask app on startup** (not via postgres init scripts). LiteLLM's Prisma migrations run on the same database and can drop custom tables. Use `CREATE TABLE IF NOT EXISTS` + `CREATE INDEX IF NOT EXISTS` in the Flask app's module-level init.

### 5. Sub-Limit Enforcement

Sub-limits protect against burst abuse but don't eliminate monthly risk. The monthly cap is what actually binds. Implement as a middleware that queries PostgreSQL for rolling-window spend before each request:

```python
def check_limits(user_id, estimated_cost):
    usage = get_user_usage(user_id)  # Query: SUM(billed_usd) WHERE created_at > NOW() - interval
    limits = get_plan_limits(plan)
    for period, cap in limits.items():
        if usage[period] + estimated_cost > cap:
            return {"allowed": False, "reason": f"{period} limit exceeded"}
    return {"allowed": True}
```

### 6. Free Backend Strategy

Maximize traffic routed to free backends to improve margins:

| Free Backend | Models | Rate Limit |
|-------------|--------|-----------|
| NVIDIA NIM (build.nvidia.com) | Nemotron 3 Ultra/Super/Nano, Llama 3.1 405B, MiniMax M2.7, DeepSeek R1 | ~40 RPM, no daily cap |
| Groq | Llama 3.3 70B, Qwen3 32B | 30 RPM, 1,000 RPD |
| Mistral | Mistral Medium 3.5, Codestral | ~1B tokens/month |
| OpenRouter (:free) | Nemotron 3 Ultra, Qwen3 Coder, GPT-OSS | 20 RPM, 200 RPD |
| Google Gemini (AI Studio) | Gemini 2.5 Flash, 3.5 Flash | 15 RPM, 1,500 RPD |

## Price Design Principles

- **Always show worst-case + expected + best-case tables with exact dollar figures.** When the user asks "will I be in profit?" give them the table, not the lecture. Show: "5 users → +$25 best, -$3 worst, +$20 expected."
- **Sub-limits prevent burst, not loss.** Be clear that only the monthly cap protects against total loss.
- **The cache pooling moat is essential.** Without cross-user cache, your costs are 50x higher on input tokens.
- **Compare against competitors explicitly.** Show a table: "OpenCode Go → your offer" side by side with exact prices and caps.
- **Be honest about risk.** Don't say "you're guaranteed profit at 10 users" — show the variance. But lead with the numbers, not the hedging.
- **When the user asks "what if everyone maxes out" — show the exact table immediately.** Don't explain why it's unlikely first. Show the worst-case dollars at 1/10/50 users, then explain why that scenario is improbable. The user needs to see the ceiling before they'll trust your numbers.

### The 6:1 Rule (Industry Standard)

OpenCode Go (market leader for low-cost coding API) charges **$10/mo with a $60/mo usage cap** — a **6:1 ratio** of cap to price. This is the market baseline. A ratio like 8.7:1 ($6.90/$60) means a single heavy user maxing their cap loses **-$53.10/mo**. At 6:1, same heavy user loses only **-$10/mo**.

**Breakeven math at 6:1 ratio (assuming $0.0024 blended wholesale cost):**

The simple 6:1 ratio is only part of the story. You MUST model the blended wholesale cost:

| Plan | Price | Cap | Wavg Req/mo @ Cap | Wavg Cost @ Cap | Max Loss/User | Breakeven @ 80/15/5 |
|------|-------|-----|------------------|----------------|---------------|--------------------|
| Starter | $6.90/mo | $50 | 18,621 | $44.46 | -$37.56 | ~Never |
| Starter | $10/mo | $60 | 22,346 | $53.36 | -$43.36 | ~50 users |
| Pro | $20/mo | $120 | 44,691 | $106.72 | -$86.72 | ~25 users |

Real-world breakeven is lower because: (a) most users use 10-30% of cap, (b) free backends cover some traffic at $0 cost, (c) cross-user cache pooling cuts paid-model costs.

**Critical: Portfolio mix matters more than unit economics.**

### "What If Every User Maxes Out" — The Worst-Case Template

When the user asks this (and they will), show the table immediately before any caveats:

| Users | Revenue | Token Cost (worst) | Profit/Loss |
|-------|---------|--------------------|-------------|
| 1 | $10 | $60 | **-$50** |
| 10 | $100 | $600 | **-$500** |
| 50 | $500 | $3,000 | **-$2,500** |

Then explain why it's practically impossible:
1. **$12/5hr sub-limit** — burst abuse is caught in hours, not days
2. **~158K requests/mo** needed to burn $60 (~5,200/day, every day)
3. **Real heavy users** do 10-30K req/mo ($4-$11 cost)
4. **Free backend routing** drops cost to $0 for most requests

### Answer Style Rules

**This user wants:**
1. Hard numbers first — tables with exact dollar figures for every scenario
2. Direct yes/no — "Can I guarantee 0% loss?" → "At $6.90/$60 cap: no. At $6.90/$30 cap: yes."
3. Multiple scenarios — always show best, expected, worst in a table
4. No fluff — "Here's the math. Here's what happens at 5 users. Here's what happens at 10."
5. When the user says "I don't care about profit, I care about 0 loss" — give them the cap that achieves zero loss, not a lecture on averages

**Do NOT:**
- Lead with disclaimers before giving the answer
- Hedge repeatedly ("depends on usage patterns" without showing the range)
- Explain caching economics when they asked about pricing
- Say "we need to consider X, Y, Z" — just give the table first, explain caveats after

## Shipping a Free-Tier Agentic Coding CLI

You can evolve from a pure API proxy into a shipping-your-own-CLI product by leveraging OpenCode's MIT-licensed codebase (already extracted at `nectar-v2/`). The **same code that powers OpenCode Go** can be rebranded and shipped as your own agentic coding CLI.

### The Architecture in One Diagram

```
models.dev catalog (remote or bundled JSON)  ← defines ALL models + costs
        │
        ▼
"nectar" provider loads catalog, checks for API key
        │
        ├── Has Nectar API key → All models available (paid + free)
        └── No key → Deletes models with cost > 0, keeps cost=0 only
                        → CLI ships free models, no API key required
        │
        ▼
AI SDK providers (@ai-sdk/groq, @ai-sdk/mistral, etc.) handle actual API calls
```

### Key Insight: The Free Model Gate

The "nectar" provider in `packages/opencode/src/provider/provider.ts` (lines 179-201) is the entitlement mechanism:

- Models with `cost.input === 0` are "free" — always available
- Models with `cost.input > 0` are "paid" — hidden unless user has an API key
- The `models.dev` catalog defines which models have zero cost
- The AI SDK providers handle the actual API routing (Groq, Mistral, NVIDIA, etc.)

**For your CLI:** You don't need to change code. You just control which models appear in your catalog with `cost.input === 0`. The code already handles the rest.

### Three Ways to Ship Free Models

| Approach | How | When to Use |
|----------|-----|-------------|
| **Hosted catalog** | Set `OPENCODE_MODELS_URL` to your own API | Dynamic pricing / model updates |
| **Bundled snapshot** | Set `OPENCODE_MODELS_PATH` + `OPENCODE_DISABLE_MODELS_FETCH=true` | Ship a static catalog with the binary |
| **Use existing models.dev** | Just works — `https://models.dev` already has free models | Fine with nectar.ai's catalog |

### Binary Pipeline

```
src/index.ts (yargs, scriptName "nectar")  →  bun build --compile  →  static binary
```

The extracted `nectar-v2/` is already rebranded — `scriptName("nectar")`, cache path `~/.cache/nectar/`, HTTP referrer headers say `nectar.ai`, i18n strings say "Free models provided by Nectar". **No rebranding work needed.**

### What Ships Out of the Box (already working, no code changes needed)

The OpenCode codebase has **21 provider integrations** pre-wired: Anthropic, OpenAI, Google, Groq, Mistral, xAI, DeepInfra, Cerebras, TogetherAI, Perplexity, OpenRouter, NVIDIA (via OpenAI-compatible), and more.

The TUI includes: model selector with "Free" badge, session management, file editing with diff view, MCP tool integration, terminal emulation, and 17-language i18n.

### Retry / Free Tier Upsell (session/retry.ts)

Default upsell URLs point to `https://nectar.ai/go` — change these for your own product.

### Key Files at a Glance

| File | Purpose |
|------|---------|
| `packages/opencode/src/index.ts` | CLI entry point (yargs) |
| `packages/opencode/src/provider/provider.ts` | All provider/model loading, auth, free gate |
| `packages/opencode/src/cli/cmd/run/footer.command.tsx` | Model selector UI, "Free" badge display |
| `packages/opencode/src/session/retry.ts` | Free tier limits, upsell messaging |
| `packages/opencode/script/build.ts` | Build pipeline (Bun compile) |
| `packages/core/src/models-dev.ts` | models.dev catalog fetcher + cache |
| `packages/llm/src/providers/` | Low-level provider route implementations |
| `packages/llm/src/providers/openai-compatible-profile.ts` | Pre-configured provider endpoints |

See `references/opencode-cli-architecture.md` for the full deep-dive — models.dev catalog schema, provider route architecture, bundled provider list, environment flags, and everything else about how the CLI model system works.

## Pitfalls

### Reselling other providers' subscriptions (ToS violation)
Tempting to buy OpenCode Go accounts and pool them behind your own API to lower costs. **Don't do it.** Every provider's Terms of Service explicitly prohibit reselling accounts. If detected (and they will detect API key patterns), all accounts get banned simultaneously, taking your entire user base down. Build on direct provider relationships instead — NVIDIA NIM, Groq, and Mistral all have free tiers that are perfectly legitimate to resell.

### Database tables getting dropped
LiteLLM uses Prisma for schema management. If it connects to the same PostgreSQL database, Prisma migrations may drop custom tables. **Fix:** Create tables from the Flask app on startup using `CREATE TABLE IF NOT EXISTS`, not from postgres init scripts.

### LiteLLM not reconnecting to PostgreSQL
If Postgres restarts, LiteLLM may not reconnect. Use `--detailed_debug` flag and health checks.

### Testing free models only (this user's preference)
When testing API providers, **ONLY test free models** ($0 cost) unless the user explicitly asks for paid model testing. This user is building a free-tier coding CLI (Nectar) and is focused on zero-cost model availability. Testing paid models without explicit permission provokes frustration. Always verify a model's cost before running a test — if `cost.input > 0` or the model is not marked as free in the pricing page, skip it. For OpenCode specifically: stick to models in the Per-Model Matrix under "Zen (x-api-key)" with ✅ WORKS status. Paid models (`glm-5`, `kimi-k2.5`, `deepseek-v4-pro`, etc.) are NOT free — do not test them.

### Stripe webhook signature verification
When testing locally without HTTPS, Stripe webhook signatures will fail. Use the Stripe CLI to forward webhooks: `stripe listen --forward-to localhost:5000/api/stripe/webhook`

### Nginx port conflicts
Port 80 is commonly taken by other services (panels, other proxies). Use port 8080 for the public nginx port during development.

### SQL init script permissions
Postgres init scripts in docker-entrypoint-initdb.d need world-read permissions (chmod 644) or they get "Permission denied" inside the container.

### Extracting Frontend from OpenSource Competitors

Instead of building a dashboard from scratch, you can extract the console/UI/TUI from OpenCode's open-source monorepo (anomalyco/opencode, MIT license). The repo contains:

- **packages/console/app** — Full SaaS dashboard with usage graphs, billing, API keys, workspace management, and the Zen API proxy backend
- **packages/ui** — SolidJS UI component library (icons, dialogs, selects, i18n in 17 languages)
- **packages/tui** — Terminal UI with dialog system
- **packages/app** — Desktop workspace UI (file tree, terminal, prompt input, sessions)

**The extraction challenge:** The repo is deeply tied to SST (Ion) infrastructure on AWS/Cloudflare with Upstash Redis. The console app uses SolidJS Start with server functions (`"use server"`) and Nitro as the server engine. Key extraction steps:
1. Copy routes, components, and assets from console/app
2. Strip SST Resource bindings — replace with env vars + direct DB queries
3. Replace server functions with Flask API endpoints or Express routes
4. The Zen API routes (in `routes/zen/`) are a standalone OpenAI-compatible proxy — they can replace LiteLLM entirely

See `references/opencode-monorepo-extraction.md` for the full package breakdown, extraction phases, and key file list.

## Consumer-Side Usage Analysis

This skill also covers the **consumer-side** workflow: evaluating a subscription plan's models against personal usage patterns. See `references/consumer-plan-model-selection.md` for the burn-rate calculation, per-model selection rules, and the $60 vs $15 bucket filter.

When the user asks "which model should I use on my plan?" — this is NOT the same as "build me a provider." You still load this skill because the pricing tables, burn rate logic, and model comparison framework are shared. The consumer reference has the specific workflow.

## References

- `references/provider-cost-analysis.md` — Detailed per-request costs, competitor pricing, margin projections
- `references/nectar-architecture.md` — Full build notes from the Nectar API project
- `references/opencode-inference-api.md` — OpenCode inference API testing: which free models work without API key, the $0.50 minimum balance requirement, `big-pickle`→`deepseek-v4-flash` mapping, token behavior, rate limits (none), and the full model list
- `references/opencode-go-competitor-data.md` — Exact OpenCode Go pricing, model list, request estimates per cap period
- `references/opencode-monorepo-extraction.md` — Extracting the SolidJS dashboard from OpenCode's monorepo
- `references/per-model-pricing-model.md` — Per-request wholesale cost tables, per-model markup matrix, blended portfolio math, breakeven analysis across user mixes
- `references/request-volume-thresholds.md` — Why 95% of real users never hit per-model limits; agentic coding speed analysis, real-world consumption scenarios, marketing leverage quotes
- `references/student-bootstrap-strategy.md` — AWS credit bootstrap timeline, BYOK migration plan, backup strategies for the solo founder
- `references/opencode-cli-architecture.md` — Full architecture of OpenCode's CLI model system: models.dev catalog, provider route design, free model entitlement gate, bundled provider list, build pipeline, and CLI entry point analysis