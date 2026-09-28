---
name: production-fast-api-template
description: Structure and execution rules for a unified, production-ready backend combining domain-oriented FastAPI, Retrieval-Augmented Generation (RAG) and Agentic AI in one codebase on AWS ECS Fargate. Use when scaffolding a new backend; adding a module, API domain, RAG component, agent, tool, workflow, LLM/provider integration or test; deciding where a file belongs; writing async/sync routes, services or clients; offloading blocking or CPU-heavy work (thread pools, process pools, AWS Lambda); designing background jobs, queues (SQS, Celery), workers and scaling; or writing Pydantic schemas, settings (pydantic-settings), serialization, structured LLM outputs, citation validation, agent plans or tool-call arguments; or writing FastAPI dependencies (request validation, auth, access scopes, chaining), REST paths, response models, OpenAPI docs, error responses, database naming and SQL queries, migrations, API tests (async client, dependency overrides) or lint/format setup (ruff); or adding content-safety guardrails (input/output checks, PII, prompt injection, toxicity, Bedrock Guardrails, AgentCore Policy/Gateway Cedar policies, Guardrails AI validators), fail-closed handling and guardrail evaluation; or evaluating RAG, retrieval stages, structured outputs, citations, agents, multi-agent workflows or conversations (DeepEval, Ragas, LLM-as-judge, G-Eval, golden datasets, regression tiers, thresholds, judge calibration); or securing the API (authentication, JWT/JWKS, OAuth 2.0/OIDC, RBAC/ABAC, BOLA/BFLA, tenant isolation, input/upload/SSRF validation, security headers, CORS, CSRF, rate limiting, audit logging, ECS/IAM/secrets hardening, CI security scanning, security tests) or LLM/agent security (OWASP LLM Top 10, OWASP Agentic Top 10, prompt injection, tool authorization, human approval, excessive agency).
---

# Production FastAPI Template: Rules

These rules define **where code lives** and **how it executes** in a unified FastAPI + RAG +
Agentic AI backend. Apply them whenever you generate or modify code in a project built from
this template.

**Companion references.** Read the relevant file before writing code:

| File | Read before writing… | Summarized in |
|---|---|---|
| [ASYNC_EXECUTION.md](ASYNC_EXECUTION.md) | Any route, service, client, agent tool, worker or background job | Section 5 |
| [PYDANTIC_STANDARDS.md](PYDANTIC_STANDARDS.md) | Any schema, settings class, serialization, LLM call with structured output, citation check, agent plan or tool argument model | Section 6 |
| [API_CONVENTIONS.md](API_CONVENTIONS.md) | Any dependency, route signature, auth/permission check, OpenAPI metadata, DB model or query, migration, API test or lint setup | Section 7 |
| [GUARDRAILS.md](GUARDRAILS.md) | Any user-facing LLM call, RAG answer, ingestion of untrusted documents, agent tool execution, gateway target or content-safety check | Section 8 |
| [AI_EVALUATION.md](AI_EVALUATION.md) | Any evaluation contract, metric, dataset, judge, runner, report or threshold; any new RAG stage, agent, tool or conversation feature that needs quality coverage | Section 9 |
| [API_SECURITY.md](API_SECURITY.md) | Any authentication, token, permission, tenant or ownership check; input/upload/outbound-URL handling; response headers, CORS, errors; rate limits; audit events; ECS/IAM/secrets; CI security; security tests | Section 10 |
| [AGENT_SECURITY.md](AGENT_SECURITY.md) | Any agent, tool, tool registry entry, approval flow, memory write, MCP connector or LLM-output sink | Section 10 |

**Status labels:**

- 🟢 **Convention.** A proposed rule. Follow it by default.
- 🟡 **Needs approval.** An open team decision. Surface the options to the user and never pick one silently.

These rules don't choose agent frameworks, LLM providers, models, vector stores or a queue
implementation. If a rule doesn't fit a real need, raise it with the user instead of silently
working around it.

---

## 1. Core structure rules 🟢

1. **One application.** FastAPI, RAG and Agentic AI are **not** separate apps. There is exactly one `src/` package, one FastAPI entry point (`src/main.py`) and one shared infrastructure layer.
2. **Never create a second entry point.** Don't add a second `src/`, a separate app folder (`rag_app/`, `agents_service/`, `worker_app/`) or an extra `FastAPI()` instance.
3. **Background workers and Lambda functions are extra entry points into the same codebase.** They are not separate applications, and they call the same service functions the API calls.
4. **One central API router.** All routers mount through `src/api/v1/router.py`. Domain, RAG and agent routers never mount themselves on the app.
5. **Domain-oriented modules.** Business code lives inside its domain package. `src/`'s root holds only application-wide concerns.
6. **No duplicated shared layers.** Model clients go in `src/llm/`, content-safety checks in `src/guardrails/` and external-service clients in `src/providers/`, each exactly once. RAG and agents **consume** them and never define their own copies (no `rag/llm_client.py`, no `agents/vector_db.py`).
7. **Provider-neutral naming.** Name files by responsibility, not vendor (`llm/embeddings.py`, not `openai_embeddings.py`). Vendor specifics stay behind `src/providers/` or `src/llm/`.
8. **`common/` is for genuinely reusable, domain-agnostic code only.** Never put business logic there.
9. **Keep agents, reasoning and execution apart.** Agent *definitions* go in `agents/`, *thinking* in `cognition/` and *doing, scheduling and offloading* in `execution/`.
10. **Tests mirror `src/`.** Quality evaluation (datasets, DeepEval/Ragas suites, deterministic metrics, runners, reports) lives in the top-level `evaluation/` directory, separate from `tests/`. `src/evaluation/` holds only framework-neutral contracts, the metric registry and adapters, with lazy framework imports (AI_EVALUATION.md §1).
11. **Every Python directory under `src/` has an `__init__.py`.** Non-Python directories that must survive in Git (prompt folders, data, empty test folders) get a `.gitkeep`.
12. **Explicit module imports across packages**, e.g. `from src.auth import constants as auth_constants`.
13. **Reuse existing files before adding new ones.** Extend `execution/background_worker.py` rather than creating `execution/worker2.py` or `rag/worker.py`.

---

## 2. Canonical structure

```text
<project-name>/
├── src/
│   ├── __init__.py
│   ├── main.py              # the single FastAPI entry point (lifespan creates shared clients/limiters)
│   ├── config.py            # application-wide configuration
│   ├── constants.py
│   ├── exceptions.py        # base domain exception + handlers rendering ErrorResponse
│   ├── middleware.py
│   ├── database.py          # shared metadata (naming convention), engine/session factory, get_db_session
│   ├── models.py            # genuinely shared models only
│   ├── pagination.py
│   │
│   ├── api/
│   │   └── v1/
│   │       └── router.py    # aggregates domain, RAG and agent routers
│   │
│   ├── auth/                # reference domain module
│   │   ├── router.py
│   │   ├── schemas.py       # the domain's own Pydantic API/internal schemas
│   │   ├── models.py        # persistence (ORM) models, not Pydantic
│   │   ├── dependencies.py  # current_principal, require_<permission>, scope dependencies
│   │   ├── config.py        # the domain's own pydantic-settings class (AUTH_ prefix: issuers, audiences, JWKS)
│   │   ├── constants.py     # permission and scope names
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   ├── tokens.py        # JWT/JWKS validation, token types, claims → Principal
│   │   ├── permissions.py   # RBAC/ABAC policy evaluation (default deny)
│   │   ├── security.py      # password hashing, only if local accounts are approved 🟡
│   │   ├── audit.py         # auth audit events (login, token rejected, session revoked)
│   │   └── utils.py
│   │
│   ├── example_domain/      # copy this layout for every new business domain
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py  # valid_<entity>_id and other I/O-backed validation
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   │
│   ├── rag/
│   │   ├── routes.py        # "routes", not "router": avoids clashing with rag/router/
│   │   ├── schemas.py       # RAG API schemas + cross-stage contracts (RetrievedEvidence)
│   │   ├── service.py       # container/lifecycle of long-lived RAG services
│   │   ├── dependencies.py
│   │   ├── config.py        # RAG settings (RAG_ prefix)
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── extraction.py    # structure-preserving document extraction
│   │   ├── ingestion.py     # coordinates processing and indexing (run by background jobs)
│   │   ├── semantic/
│   │   │   ├── metadata.py
│   │   │   ├── segmentation.py
│   │   │   └── chunks.py
│   │   ├── router/
│   │   │   ├── classifier.py
│   │   │   ├── fusion.py
│   │   │   └── evaluation.py
│   │   ├── preprocessing/
│   │   │   ├── query_expansion.py
│   │   │   └── hyde.py
│   │   ├── retrieval/
│   │   │   ├── semantic_search.py
│   │   │   ├── bm25.py
│   │   │   ├── rrf.py
│   │   │   ├── mmr.py
│   │   │   ├── evidence_filter.py
│   │   │   └── hybrid_retriever.py
│   │   ├── generation/
│   │   │   ├── context_builder.py
│   │   │   ├── citations.py
│   │   │   ├── streaming.py
│   │   │   ├── schemas.py        # LLM-output contracts: GeneratedAnswer, Citation
│   │   │   ├── validation.py     # application-level answer/citation validation
│   │   │   └── service.py
│   │   ├── chat/
│   │   │   ├── routes.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── storage.py
│   │   └── security/
│   │       ├── access_control.py     # AccessScope model + vector-store/DB filter translation
│   │       ├── document_validation.py  # ingestion file checks (type, signature, size, archives)
│   │       └── retrieval_policy.py   # post-retrieval ACL re-check, trust labels, provenance
│   │
│   ├── agents/
│   │   ├── router.py
│   │   ├── schemas.py            # AgentTask, ToolResult, AgentExecutionState
│   │   ├── structured_output.py  # LLM-produced: ExecutionPlan, ToolCall union, FinalAgentResponse
│   │   ├── dependencies.py
│   │   ├── config.py             # agent settings (AGENTS_ prefix)
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   ├── base_agent.py
│   │   ├── autonomous_agent.py
│   │   ├── planner_agent.py
│   │   ├── agent_interface.py
│   │   ├── team_orchestrator.py
│   │   ├── step_handler.py
│   │   ├── task_manager.py
│   │   ├── tools/
│   │   │   ├── calculator.py
│   │   │   ├── file_manager.py
│   │   │   ├── search_tool.py
│   │   │   └── tool_registry.py
│   │   ├── workflows/
│   │   │   ├── code_review_chain.py
│   │   │   ├── research_chain.py
│   │   │   ├── multi_agent_workflow.yaml
│   │   │   └── workflow_executor.py
│   │   └── security/                 # policies; enforced by execution/executor.py
│   │       ├── tool_permissions.py   # default-deny tool authorization (user perms ∩ agent profile)
│   │       ├── execution_policy.py   # step, tool-call, token, cost and time budgets
│   │       └── approval_policy.py    # human approval bound to argument hash
│   │
│   ├── cognition/
│   │   ├── cognitive_loop.py
│   │   ├── decision_policy.py
│   │   ├── planner.py
│   │   ├── reasoner.py
│   │   ├── state_interpreter.py
│   │   └── memory/
│   │       ├── long_term_memory.py
│   │       ├── short_term_memory.py
│   │       └── memory_manager.py
│   │
│   ├── execution/
│   │   ├── action_resolver.py
│   │   ├── controller.py
│   │   ├── error_handler.py
│   │   ├── executor.py
│   │   ├── threadpool.py         # thread-offload helpers and limiters (no custom executor yet)
│   │   ├── job_scheduler.py      # enqueue/schedule background jobs
│   │   └── background_worker.py  # queue consumer / job dispatch loop
│   │
│   ├── llm/                 # shared by RAG and agents
│   │   ├── client.py
│   │   ├── embeddings.py
│   │   ├── reranker.py
│   │   ├── model_loader.py
│   │   ├── cache.py
│   │   ├── dependencies.py       # accessors for lifespan-created model clients
│   │   ├── config.py             # LLM settings (LLM_ prefix, SecretStr keys)
│   │   ├── schemas.py            # structured-output modes, capabilities, failure kinds
│   │   ├── structured_output.py  # generate → validate → bounded retry (provider-independent)
│   │   └── prompts/
│   │       ├── system/
│   │       ├── tasks/
│   │       └── templates/
│   │
│   ├── guardrails/          # shared content-safety layer, used by RAG, agents and workers
│   │   ├── schemas.py            # GuardrailPhase, GuardrailOutcome, GuardrailFinding, GuardrailVerdict
│   │   ├── service.py            # run a phase's checks, decide outcome, enforce / log-only, fail closed
│   │   ├── policies.py           # which checks apply to which surface and phase
│   │   ├── config.py             # GUARDRAILS_ settings (mode, fail mode, thresholds, policy version)
│   │   ├── dependencies.py
│   │   ├── exceptions.py         # GuardrailBlocked, GuardrailUnavailable
│   │   └── validators/           # deterministic in-house checks (regex, lists, length)
│   │
│   ├── providers/           # external-service boundaries (MCP, vector DB, queues, Lambda, guardrails, …)
│   │   ├── guardrails/client.py  # managed guardrail API / validator-library adapters
│   │   ├── mcp/client.py
│   │   ├── vector_store/client.py
│   │   └── external/client.py
│   │
│   ├── evaluation/          # runtime-safe evaluation contracts only (no deepeval/ragas at import)
│   │   ├── schemas.py            # EvaluationSample, RetrievedContext, AgentTrajectory, EvaluationResult
│   │   ├── registry.py           # metric key → framework, class, version, required fields, result kind
│   │   └── adapters/
│   │       ├── deepeval_adapter.py   # contracts ↔ LLMTestCase / ConversationalTestCase (lazy import)
│   │       └── ragas_adapter.py      # contracts ↔ Ragas collections inputs / samples (lazy import)
│   │
│   └── common/
│       ├── schemas/
│       │   ├── base.py           # CustomModel, UtcDatetime, shared annotated types
│       │   ├── responses.py      # ErrorResponse and shared response shapes
│       │   └── pagination.py     # Page[T], PageParams (models only; logic in src/pagination.py)
│       ├── dependencies.py
│       ├── logging.py
│       ├── retry.py
│       ├── timers.py
│       ├── serialization.py
│       ├── validation.py
│       └── security/
│           ├── headers.py            # security-headers ASGI middleware (registered in src/middleware.py)
│           ├── rate_limiting.py      # distributed limiter interface + key builders (backend 🟡)
│           ├── request_validation.py # body size/depth, content type, filenames, outbound URL (SSRF) policy
│           └── audit_schemas.py      # AuditEvent, AuditActor, AuditTarget
│
├── tests/
│   ├── conftest.py          # async client (httpx + ASGITransport), dependency-override fixtures
│   ├── auth/
│   ├── rag/{ingestion,retrieval,generation}/
│   ├── agents/
│   ├── cognition/
│   ├── execution/
│   ├── guardrails/          # fake checkers; deny / suppress / fail-closed / log-only paths
│   ├── evaluation/          # test_schemas.py, test_adapters.py, test_deterministic.py (no LLM calls)
│   ├── security/
│   │   ├── authentication/  # JWT/JWKS validation, throttling
│   │   ├── authorization/   # BOLA, BFLA, BOPLA, cross-tenant, service-to-service
│   │   ├── api/             # headers, CORS, limits, uploads, SSRF, injection, CSRF, rate limits
│   │   ├── rag/             # unauthorized/cross-tenant retrieval, ACL revocation, citation integrity
│   │   └── agents/          # tool authorization, argument BOLA, approval bypass, budgets, injection
│   ├── integration/
│   ├── e2e/
│   └── fixtures/
├── evaluation/              # offline quality evaluation (never imported by src/)
│   ├── README.md
│   ├── config/{metrics.yaml,thresholds.yaml}
│   ├── datasets/{rag,agents,conversations,golden,guardrails}/
│   ├── deepeval/{rag,agents,conversations,custom}/
│   ├── ragas/{rag,agents,custom}/
│   ├── deterministic/{citations,retrieval,structured_output,tool_calls}.py
│   ├── tracing/{collectors,normalization}.py
│   ├── runners/{offline,regression,report}.py
│   ├── fixtures/
│   └── reports/             # generated, git-ignored 🟡
├── data/{documents,knowledge_bases,agent_state,fixtures}/
├── scripts/
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── development/
│   ├── decisions/
│   └── standards/
│       ├── ASYNC_EXECUTION.md      # copied from this skill
│       ├── PYDANTIC_STANDARDS.md   # copied from this skill
│       ├── API_CONVENTIONS.md      # copied from this skill
│       ├── GUARDRAILS.md           # copied from this skill
│       ├── AI_EVALUATION.md        # copied from this skill
│       ├── API_SECURITY.md         # copied from this skill
│       └── AGENT_SECURITY.md       # copied from this skill
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── CLAUDE.md
```

`__init__.py` files are omitted above for brevity. Rule 11 still applies.

---

## 3. Where does new code go?

| You are adding… | Put it in | Not in |
|---|---|---|
| A new business capability (orders, billing…) | `src/<domain>/` using the `example_domain/` layout | `src/` root, `common/` |
| An HTTP endpoint | The owning module's `router.py` (`routes.py` inside `rag/`), mounted via `api/v1/router.py` | `main.py` |
| Request/response models | `<module>/schemas.py`, inheriting `CustomModel` | `src/models.py`, direct `BaseModel` |
| Shared base model, `UtcDatetime`, shared annotated types | `common/schemas/base.py` | Per-domain base classes |
| Error, message and page response shapes | `common/schemas/{responses,pagination}.py` | Each domain redefining them |
| Settings for a domain or component | `<module>/config.py` (own prefix, cached getter) | The global `src/config.py` |
| LLM-output schema for answer generation | `rag/generation/schemas.py` | `rag/schemas.py` (API) |
| LLM-output schema for one RAG stage (metadata, classification, expansion) | `rag/<stage>/schemas.py`, created when the stage is implemented | API schemas |
| Citation and answer checks against evidence | `rag/generation/validation.py` | Pydantic validators |
| Agent plan, tool-call union, final agent response | `agents/structured_output.py` | `agents/schemas.py` |
| A tool's argument model | That tool's module in `agents/tools/` | A central args file |
| Structured-output generation, validation and retry flow | `llm/structured_output.py` + `llm/schemas.py` | Re-implemented in RAG or agents |
| Evaluation contracts (`EvaluationSample`, `EvaluationResult`, …), metric registry | `src/evaluation/{schemas,registry}.py` | `evaluation/`, per-suite copies |
| Contract ↔ DeepEval / Ragas mapping | `src/evaluation/adapters/` (lazy framework imports) | Suites building test cases ad hoc |
| Metric suites, G-Eval/DAG/custom metrics, judge wrappers | `evaluation/{deepeval,ragas}/` | `src/`, `tests/` |
| Deterministic metrics (retrieval P/R/MRR/NDCG, citations, schema, tool calls) | `evaluation/deterministic/` | LLM judges |
| Evaluation datasets, metric/threshold config, runners, reports | `evaluation/{datasets,config,runners,reports}/` | `data/`, `tests/fixtures/` |
| Tests of the evaluation code | `tests/evaluation/` | `evaluation/` |
| DB models used by one domain | `<domain>/models.py` | `src/models.py` |
| Existence, ownership or uniqueness checks that need I/O | `<domain>/dependencies.py` (`valid_<entity>_id`) | Pydantic validators, repeated in each route |
| `current_principal`, `require_<permission>`, scope dependencies | `auth/dependencies.py` | Each domain parsing tokens |
| JWT/JWKS validation, claims → `Principal` | `auth/tokens.py` | `auth/service.py`, routes |
| RBAC/ABAC policy evaluation | `auth/permissions.py` | Routes, prompts |
| Password hashing (only if local accounts are approved 🟡) | `auth/security.py` | `common/` |
| Auth audit events; shared `AuditEvent` schema | `auth/audit.py`; `common/security/audit_schemas.py` | Free-form log lines |
| Security headers, rate limiting, request/upload/outbound-URL validation | `common/security/{headers,rate_limiting,request_validation}.py` | Per-domain copies |
| RAG access scope, document validation, post-retrieval policy | `rag/security/` (scope resolved in `rag/dependencies.py`), applied as a store filter in retrieval | Prompts, the LLM, `evidence_filter.py` |
| Agent tool permissions, execution budgets, approval policy | `agents/security/` (context built in `agents/dependencies.py`), enforced by `execution/executor.py` | Prompts, the planner, tools themselves |
| Security tests | `tests/security/{authentication,authorization,api,rag,agents}/` | `evaluation/` |
| Domain exceptions | `<domain>/exceptions.py`, subclassing `src/exceptions.py` | `HTTPException` in services |
| SQL queries | `<domain>/service.py` | Routers, dependencies |
| DB naming convention, engine, session dependency | `src/database.py` | Per-domain engines |
| Migrations 🟡 | `alembic/` + `alembic.ini` at the root, only after approval | `src/`, the app lifespan |
| Lint/format script 🟡 | `scripts/lint.sh` | Ad-hoc commands in docs |
| Content-safety checks (input, context, tool, output) | Call `src/guardrails/service.py` at the checkpoints in GUARDRAILS.md §3 | Checks embedded in `rag/` or `agents/`, system prompts |
| Deterministic safety validators (regex, lists) | `guardrails/validators/` | `common/validation.py` |
| Managed guardrail or validator-library client | `providers/guardrails/client.py` | `guardrails/`, `llm/` |
| Gateway Cedar guardrail policies 🟡 | Infrastructure-as-code, outside `src/` (location needs approval) | `src/` |
| Guardrail red-team / benign datasets | `evaluation/datasets/guardrails/` | `tests/` |
| Long-lived clients, pools and limiters | Created in `main.py`'s lifespan and exposed through `dependencies.py` | Created per request |
| Document parsing and indexing logic | `rag/extraction.py`, `rag/ingestion.py`, `rag/semantic/` | `providers/`, workers |
| Query routing / classification | `rag/router/` | `agents/` |
| Query rewriting, HyDE | `rag/preprocessing/` | `rag/retrieval/` |
| A retrieval or ranking stage | `rag/retrieval/` | `rag/generation/` |
| Answer context, citations, streaming | `rag/generation/` | `rag/chat/` |
| Conversation API / history | `rag/chat/` | `rag/` root |
| A new agent type | `agents/<name>_agent.py` implementing `agent_interface.py` | `cognition/` |
| A tool an agent can call | `agents/tools/` + register in `tool_registry.py` | `common/` |
| A predefined multi-step workflow | `agents/workflows/` | `execution/` |
| Planning, reasoning, decision logic | `cognition/` | `agents/` |
| Agent memory | `cognition/memory/` | `rag/chat/storage.py` |
| Running actions, control flow, execution errors | `execution/{executor,controller,action_resolver,error_handler}.py` | `agents/` |
| Thread-offload helpers, per-dependency limiters | `execution/threadpool.py` | Ad-hoc in routes |
| Enqueueing or scheduling a background job | `execution/job_scheduler.py` | Routes calling the queue SDK directly |
| Queue consumer / job dispatch | `execution/background_worker.py` | A new app or `rag/worker.py` |
| Lambda handler (thin adapter) 🟡 | Same codebase. The location needs approval. It calls the existing service functions. | A separate repo or app with copied logic |
| Chat/completion, embedding or rerank model access | `llm/` | `rag/`, `agents/` |
| Prompt text | `llm/prompts/{system,tasks,templates}/` | Scattered `prompts.py` files |
| MCP, vector DB, SQS, Lambda or third-party API client | `providers/<kind>/client.py` | `rag/`, `agents/`, `llm/` |
| Logging, retry, timing, serialization | `common/` | Domain packages |
| Unit tests | `tests/<mirrored module>/` | Next to source |
| RAG/agent quality metrics, benchmarks | `evaluation/` (layout in section 2) | `tests/` |
| Sample docs, KB files, agent state | `data/` | `src/` |
| One-off CLIs (bulk upload, model training) | `scripts/` | `src/` |
| Engineering standards | `docs/standards/` | `README.md` |

If none of these rows fit, **ask the user** before inventing a new top-level package.

---

## 4. RAG naming conventions 🟢

Use these names. The alternatives were rejected for the reasons given.

| Use | Instead of | Why |
|---|---|---|
| `rag/routes.py`, `rag/chat/routes.py` | `rag/router.py` | `rag/router.py` would collide with the `rag/router/` package. Keep one name inside `rag/`. |
| `rag/router/classifier.py` | `rag/router/router.py` | Names the responsibility and avoids `router/router.py` |
| `rag/router/fusion.py` (only one) | Fusion routing in both `preprocessing/` and `router/` | Routing fusion lives in exactly one place |
| `rag/retrieval/rrf.py` | `retrieval/fusion.py` | Distinguishes rank fusion from routing fusion |
| `rag/retrieval/evidence_filter.py` | `retrieval/filtering.py` | Explicit responsibility |
| `rag/retrieval/hybrid_retriever.py` | `retrieval/hybrid.py` | Matches its role |
| `rag/retrieval/semantic_search.py` | Dense search hidden inside a vector-DB client | Dense search is its own stage, and the client lives in `providers/vector_store/` |
| `rag/semantic/chunks.py` | `rag/semantic/chunking.py` | Contextualized chunk building, kept distinct from any passage-formatting helper |
| `rag/generation/context_builder.py` | `generation/context.py` | Avoids confusion with conversational context in `chat/` |
| `rag/generation/citations.py` | Citation checks inside the context builder | Separate responsibilities |
| `rag/generation/service.py` + `llm/client.py` | `rag/generation/llm.py` | Orchestration stays in RAG, and model access is shared |
| `llm/{client,embeddings,reranker}.py` | `rag/<vendor>/…` | A vendor-neutral model layer, shared with agents |
| `llm/model_loader.py` | Client factories in `rag/embeddings.py` | Model construction is shared |
| `providers/vector_store/client.py` | `src/<vendor-db>/client.py` | A vendor-neutral provider boundary |
| `evaluation/deepeval/rag/`, `evaluation/ragas/rag/`, `evaluation/reports/` | `evals/` or artifacts inside `src/` | Evaluation suites and reports stay outside the app package; only contracts live in `src/evaluation/` |
| `scripts/` for training and bulk jobs | Training scripts inside `src/rag/router/` | CLIs stay outside `src/` |

Trained model artifacts, datasets and domain-specific label lists are **data**, not structure.
Keep them under `data/` or external storage 🟡, never hard-coded in `src/`.

---

## 5. Execution rules (summary of ASYNC_EXECUTION.md) 🟢

**Async vs sync**

1. Use `async def` only when the whole call chain (route → service → client) awaits genuinely asynchronous libraries.
2. Use `def` routes for work dominated by sync blocking I/O. FastAPI runs them in AnyIO's thread pool, which has **40 tokens per process by default** and is shared with sync dependencies and offloaded calls.
3. **Never** call blocking code inside `async def`: sync HTTP/DB/vector clients, `time.sleep`, file parsing or heavy CPU.
4. Never "convert" sync code by adding `async`. Never call `asyncio.run()` inside a request.
5. Offload unavoidable sync I/O with `anyio.to_thread.run_sync(..., limiter=...)` or `starlette.concurrency.run_in_threadpool`. Use AnyIO consistently rather than `asyncio.to_thread` or `run_in_executor(None)`, which use a different pool.

**Safeguards**

6. Give each heavy sync dependency its own `CapacityLimiter`, created in the lifespan.
7. Put timeouts on the **underlying client**. An outer `asyncio.timeout` or `fail_after` doesn't stop a thread.
8. Apply backpressure when capacity runs out: `503` + `Retry-After`, not unbounded queueing.
9. Monitor limiter utilization and waiters, plus event-loop lag.
10. Don't share non-thread-safe clients across threads. Check each library's documentation.
11. Cancelling the awaiting coroutine **doesn't** stop the thread, which keeps its token and resources.
12. Don't add a custom thread pool or executor until measurements justify one. `execution/threadpool.py` is reserved for that.

**CPU-intensive work**

13. Threads don't parallelize CPU-bound pure-Python code, because of the GIL, and they slow down the event loop too.
14. Classify each library by measurement: pure Python, native code that releases the GIL, or native code with internal threads (cap `OMP_NUM_THREADS` and similar to the vCPU count).
15. CPU-heavy work outside the interactive path goes to **AWS Lambda** (stateless, reliably under 15 minutes, ≤ 10 GB / 6 vCPU, no GPU) or the **ECS worker service** (longer, stateful, bigger). An in-process process pool needs approval 🟡.

**Background processing (Path B)**

16. Ingestion, indexing, batch evaluation, bulk embedding and long agent runs go **API → SQS → ECS worker or Lambda**, never through FastAPI `BackgroundTasks`. The API returns `202` with a job ID.
17. Messages carry IDs and S3 keys, never documents.
18. Every job is **idempotent**, with deterministic IDs and upserts, because SQS delivers at least once.
19. Every queue has a **DLQ** with a bounded `maxReceiveCount` and an alarm on DLQ depth.
20. Visibility timeout > processing time, extended with heartbeats for long jobs. For SQS → Lambda: visibility ≥ 6× the function timeout, with partial batch failures.
21. Workers handle **SIGTERM** gracefully (stop receiving, finish or abandon within ECS `stopTimeout` ≤ 120 s), checkpoint long jobs and use **ECS task scale-in protection** while working.

**Scaling (ECS Fargate)**

22. ECS Service Auto Scaling must be **explicitly configured**. It isn't instantaneous (expect minutes), and adding tasks **doesn't fix event-loop blocking**.
23. The API service and worker service scale independently. Workers scale on **backlog per task** = visible messages ÷ running tasks, with target = acceptable latency ÷ average processing time.
24. Keep every stage and stream under the ALB idle timeout. Send heartbeats on SSE.

**Open decisions 🟡.** Don't choose any of these without the user:

- Celery vs native SQS workers
- Lambda adoption, packaging and handler location
- Process pools
- Limiter sizes
- Standard vs FIFO queues
- Job-status storage
- Scaling metrics and targets
- Task sizing and Uvicorn worker count
- Step Functions
- Observability tooling
- Python runtime

---

## 6. Pydantic and structured-output rules (summary of PYDANTIC_STANDARDS.md) 🟢

**Models**

1. Use Pydantic v2 for API schemas, settings, LLM outputs and internal contracts that cross a trust boundary. Every non-settings model inherits `CustomModel` from `src/common/schemas/base.py`.
2. `CustomModel` accepts field names and aliases, sets `extra="forbid"` and provides `to_json_dict()` = `model_dump(mode="json")`. Provider payloads override with `extra="ignore"`, and settings use `extra="ignore"`.
3. Prefer declarative constraints (`Field(ge/le/min_length/max_length/pattern)`, `Literal`, `StrEnum`, `EmailStr`, `HttpUrl`) over custom validators. Use `model_validator(mode="after")` for cross-field rules. Validators do no I/O and raise `ValueError` with safe messages, never `assert`.
4. Every timestamp uses `UtcDatetime` (aware, normalized to UTC, serialized as ISO 8601 `Z`). **Naive datetimes are rejected**, never assumed to be UTC. Use `datetime.now(timezone.utc)`, never `utcnow()`.
5. Use discriminated unions (a `Literal` tag + `Field(discriminator=...)`) for multi-shape results. Build a `TypeAdapter` once per module for non-model types.
6. Separate `<Entity>Create` / `Update` / `Response` / internal models. ORM models aren't Pydantic. Apply PATCH with `exclude_unset=True`. Don't create a base class per domain.
7. Avoid double work. `response_model` re-validates returned data, `model_copy(update=)` and `model_construct()` skip validation, and model→dict→model hops are waste.
8. Serialize with `model_dump(mode="json")` / `model_dump_json()`. Use `jsonable_encoder` only for untyped mixed structures.

**Settings**

9. One `BaseSettings` class per domain or component, each with a unique env prefix, `SecretStr` secrets, required values without defaults, nested models via `env_nested_delimiter="__"` and an `@lru_cache` getter. There is no giant global class.
10. Never instantiate settings at import time. Validate the enabled components' settings in the lifespan at startup. In tests, override with `dependency_overrides`, `_env_file=None` and `cache_clear()`.

**Structured LLM outputs**

11. Output has three validation levels, and **all three are required**:
    - **(1) Generation constraints.** The provider's JSON schema, tool calls or JSON mode, where supported.
    - **(2) Pydantic validation.** `model_validate_json` against the full model.
    - **(3) Application validation.** Citations exist in the retrieved evidence, tools exist and are permitted, plans are consistent.
12. Output models are separate from API models, and every field has a `description`. Adapt the exported schema to the provider's capabilities. Don't assume every provider supports the same JSON Schema features, and keep enforcing stripped constraints in Pydantic.
13. Retries are bounded (3 by default 🟡), with separate budgets for validation and transport. Never retry forever. Never fill required fields with fabricated defaults. The final failure is a typed `StructuredOutputError`.
14. Correction feedback sent to the LLM contains only locations, messages and types (`errors(include_input=False, include_url=False, include_context=False)`), never secrets, prompts, raw inputs or internal IDs.
15. **RAG.** The LLM cites short evidence labels (`E1`…) that the application maps to real chunks. Every citation must exist in this request's evidence. Self-reported confidence is a coarse enum and **not a calibrated probability**. Pydantic can't prove the evidence supports the claim, so faithfulness is measured in `evaluation/`.
16. **Agents.** Validate plans, then tool arguments **before** execution, then tool results, then state updates (`validate_assignment=True`). **Pydantic validation isn't authorization.** Permissions, allowlists, sandboxing and confirmations are enforced in `execution/` and in the tools.
17. Validation is sync but fast, so do it inline. Profile before offloading, and move bulk validation to the background path.
18. Schema tests use synthetic data, a fake LLM client, no live calls and no credentials. Assert on error `type` and `loc`.

---

## 7. API, dependency, database and tooling rules (summary of API_CONVENTIONS.md) 🟢

**Dependencies**

1. Checks that need I/O (exists, owned, active, unique) go in **dependencies** (`valid_<entity>_id`), never in Pydantic validators and never repeated in each route.
2. Dependencies return **typed** objects (internal models, `Principal`), not dicts. Publish reusable ones as `Annotated` aliases (`ValidPost`). Raise domain exceptions, not `HTTPException`.
3. Chain small dependencies. FastAPI caches each result **per request**, so shared ones (token parsing) run once. Create dependency factories at module level. Use `use_cache=False` only with a comment explaining why.
4. Prefer `async def` dependencies, but only when nothing inside them blocks. `def` dependencies take thread-pool tokens.
5. Resource dependencies use `yield`. Never hand a request-scoped session to `BackgroundTasks` or a job. Pass IDs instead.
6. Authorization is enforced server-side, in dependencies and `execution/`. Secrets come from settings (`SecretStr`). RAG retrieval receives an explicit **access scope, applied as a store filter before ranking**. Agents receive their permitted tools in the execution context. Jobs carry the principal's ID and re-check permissions in the worker.

**API surface**

7. RESTful resources live under `/api/v1` (set in `api/v1/router.py`). Use the **same path-parameter name** for the same entity everywhere so dependencies chain. Long operations return `202` plus a job resource.
8. Declare the response shape once. FastAPI re-validates and **filters** output against `response_model`. Returning a raw `Response` skips both and needs a profiled reason.
9. `BackgroundTasks` is only for tiny best-effort side effects. If you'd page someone when a task is lost, it goes to SQS (Path B). No Celery, Arq or RQ without approval.
10. Validator messages become client-visible 422s, so keep them safe. Use `PydanticCustomError` for stable error types, and never raise `HTTPException` in validators. LLM-output models are never request bodies.
11. OpenAPI docs are **off by default** (`openapi_url=None`) and enabled for listed environments through settings. Every route sets `response_model`, `status_code`, `summary`, `description`, and `responses` using `ErrorResponse`.

**Database** (engine and ORM 🟡)

12. One shared `MetaData` with an explicit constraint naming convention. Tables are `lower_snake`, singular and module-prefixed (`rag_chunk`, `agent_run`). `_at` columns are `timestamptz` and map to `UtcDatetime`; `_date` columns are dates.
13. SQL-first: joins, filters, pagination, access-scope filters and JSON aggregation happen in SQL, and Pydantic validates the result. Use bound parameters only.
14. Migrations 🟡 are static and reversible, have descriptive `date_slug` names, and follow expand-then-contract. Review autogenerated output, and **never run migrations from the app lifespan** on ECS.

**Tests and tooling**

15. Use the async test client (`httpx.AsyncClient` + `ASGITransport`) from day 0. It doesn't run the lifespan, so override client accessors or use a lifespan manager 🟡. Pick one async pytest plugin 🟡.
16. Replace collaborators with `app.dependency_overrides` on the exact callable, and `pop` only what you added. No live LLM, vector store, queue or AWS calls.
17. Ruff is the only linter and formatter (`ruff check --fix`, `ruff format`). Its configuration, pre-commit hooks and a type checker are 🟡.

---

## 8. Guardrail rules (summary of GUARDRAILS.md) 🟢

1. Guardrails check **content risk** (harmful content, PII, prompt injection, denied topics). They don't replace Pydantic validation, citation checks, authorization or evaluation, and a system prompt is not a guardrail.
2. Checkpoints: **G0** documents at ingestion, **G1** request input, **G2** untrusted retrieved context, **G3** answer output (after L2/L3 validation, on user-visible text), **G4** tool input (after authorization), **G5** tool output, **G6** final agent response. Background jobs are guarded too.
3. All checks go through the shared `src/guardrails/` service, and vendor clients live in `providers/guardrails/`. Every check returns a typed `GuardrailVerdict`: `passed`, `denied`, `suppressed`, `redacted` 🟡 or `not_evaluated`.
4. An input denial stops the pipeline before retrieval, the LLM or the tool runs. An output suppression withholds the entire reply. Clients get a stable code and a generic message. Categories and scores stay in logs.
5. **Fail closed.** `not_evaluated` refuses the request (`503` + `Retry-After` on the API). Fail-open needs approval per surface.
6. Denials are **never retried** or regenerated around. Only transport failures of the guardrail call get a bounded retry. Never feed finding details to the model.
7. Layer the enforcement points: in-app checks (required for our API and in-process RAG/agents), gateway policy for AgentCore Gateway targets 🟡, and ingestion-time checks. Each tool in the registry declares its enforcement point.
8. Gateway (Bedrock Guardrails in AgentCore Policy) 🟡: Cedar `forbid … when guardrails` for input, `suppressOutput` for output. Data paths (`context.input.*`, `context.output.*`) must exist in the target schema, so generate schemas from Pydantic models. Interpret results by body: an MCP denial is HTTP 200 with JSON-RPC `-32002`. Roll out in log-only mode, check Region availability, and alarm on "could not be evaluated".
9. Guardrails AI 🟡: pinned PyPI validator packages only (no hub URIs, hub tokens or remote inference), used behind a checker. No `Guard.for_pydantic` or guard-driven LLM calls, no embedded Flask server, and no content-rewriting on-fail actions without approval.
10. Thresholds, categories, mode and `policy_version` are settings or policy, not literals. Pin a published managed-guardrail version. New policies start in log-only mode.
11. Sync guardrail SDKs and ML validators are offloaded with a dedicated limiter and client timeouts. Deterministic validators run inline and first.
12. Never log triggering text. Alarm on `not_evaluated` spikes and block-rate shifts. Measure false positives and negatives with paired harmful and benign datasets in `evaluation/datasets/guardrails/`, including indirect injection.

---

## 9. AI evaluation rules (summary of AI_EVALUATION.md) 🟢

1. Evaluation is **offline**: never in the interactive request path, never blocking the event loop. Large runs use the worker path.
2. `src/evaluation/` = contracts, registry and adapters only, with **lazy** DeepEval/Ragas imports in an optional dependency group 🟡. Importing `src.main` never imports `deepeval` or `ragas`. Everything else lives in `evaluation/`.
3. Every result is an `EvaluationResult` whose value is **numeric, binary, categorical or unavailable**. Missing fields, judge errors and timeouts are `unavailable` with a reason, never `0`.
4. **Deterministic checks never use an LLM judge:** JSON validity, schema compliance, enums, citation IDs, document references, retrieval IDs (P@K, R@K, Hit@K, MRR, NDCG@K), tool names and tool-argument schemas.
5. Starter suites: RAG = faithfulness, answer relevancy, contextual precision, contextual recall; agents = task completion, tool correctness, plus a deterministic end-state check. Add more as workflows grow.
6. **Ragas:** use the `ragas.metrics.collections` API with `llm_factory` and `await metric.ascore(...)`. The legacy `ragas.metrics.*` classes, `evaluate()` and `RunConfig` are deprecated. **DeepEval:** use native metrics with an explicit judge `model=`; DeepEval's Ragas wrapper is not a second implementation.
7. Scores from different frameworks aren't comparable, even for metrics with the same name. Registry keys are framework-prefixed.
8. Evaluate every retrieval stage on its own output, with stage and K in the metric name; filter violations are a security invariant (0 allowed).
9. Citations: structural validity and reference validity are deterministic; evidence support is judged. A citation present is not proof of correctness.
10. Reference-based metrics need human-authored or human-reviewed references. LLM-generated references are candidates, not ground truth. Held-out sets never leak into prompts, fixtures or tuning.
11. The runner owns bounded concurrency, timeouts, retries, token and cost accounting, cancellation and partial failures for both frameworks.
12. CI tiers: **Tier 1** deterministic (every change, no LLM), **Tier 2** small budgeted LLM suite, **Tier 3** comprehensive offline. No GitHub workflows until asked.
13. Thresholds are per metric × dataset × use case in `evaluation/config/thresholds.yaml`, `null` until baselined and approved. Never average unrelated metrics; keep raw per-sample results.
14. Judges are calibrated against human-labeled sets and re-calibrated on any model, framework, template or rubric change. Everything is versioned.
15. Synthetic data only; nothing goes to external judges or evaluation platforms (Confident AI, DeepEval `system_one` mode) without authorization.

**Open decisions 🟡:** framework choice per project, pinned versions, judge provider/model/hosting, thresholds and gating, claim segmentation, dataset storage and access, tracing hook design, budgets, calibration sample sizes (full list in AI_EVALUATION.md §18).

---

## 10. API and agent security rules (summary of API_SECURITY.md and AGENT_SECURITY.md) 🟢

**Authentication and tokens**

1. **Default deny.** Every route declares authentication and authorization dependencies; public routes are an explicit allowlist checked by a test.
2. Use the approved IdP via OIDC/OAuth 2.0 (Authorization Code + PKCE; client credentials for services). No custom auth protocol, no authorization server in this service, no implicit or password grant.
3. JWTs are validated in `auth/tokens.py`: **algorithms pinned per issuer**, signature, `iss`, `aud`, `exp`/`nbf` (small leeway 🟡), `typ`, scopes. Never trust `alg`, `jku`, `x5u` or `jwk` from the header. JWKS is cached, refreshed off the event loop and fails closed.
4. Browsers use a BFF with HttpOnly cookies and CSRF protection; no tokens in `localStorage`. No secrets or sensitive data in JWT payloads.

**Access control**

5. Authorize function, object, tenant, department and field access server-side. **Every client-supplied ID** is checked (path, body, nested, batch, tool arguments). UUIDs aren't authorization. Server-controlled fields never appear in input models.
6. Services and agents use their own identities; on-behalf-of calls carry the user's **narrowed** scope. Jobs carry principal IDs and workers re-check.

**Input, output and processing**

7. Limits on body size, JSON depth, pagination, prompt length and uploads. Uploads are checked by signature, size and name; filenames are never paths. Parameterized SQL, no shell, `defusedxml`, `yaml.safe_load`, no pickle.
8. All user- or model-influenced outbound URLs go through the SSRF destination policy (allowlist, DNS pinning, block private and metadata IPs, re-validate redirects), backed by network egress controls.
9. Explicit `response_model`s, `ErrorResponse` without internals, correct status codes (403 `insufficient_scope`), security headers from `common/security/headers.py`, HSTS at the TLS edge, no `Server` header, explicit CORS origins.
10. Rate limits, quotas and LLM/agent token and cost budgets are **distributed across ECS tasks**, keyed per user, tenant, key, endpoint and IP (backend 🟡).

**RAG and agents**

11. RAG applies the caller's `AccessScope` as a store filter **before ranking**, re-checks ACLs after retrieval, keeps provenance on every chunk and propagates deletions and ACL changes. Retrieved content is untrusted.
12. Agents: effective permissions = user ∩ agent profile ∩ tenant policy. Planning, authorization and execution are separate; **a plan never grants permissions**; authorization is re-checked right before each sensitive action; approvals bind to the argument hash; tool and MCP outputs are untrusted (AGENT_SECURITY §4).

**Infrastructure, monitoring and delivery**

13. ECS: execution role only pulls images, reads referenced secrets and writes logs; the task role is least-privilege per service. Secrets from Secrets Manager/SSM as `SecretStr`. Private subnets, non-root, read-only root filesystem, controlled ECS Exec, encrypted SQS with DLQs and no sensitive payloads.
14. Security events are typed `AuditEvent`s with request and correlation IDs. **Never log** tokens, passwords, keys, raw confidential documents or unnecessary PII.
15. `tests/security/` covers auth bypass, JWT, BOLA, BFLA, cross-tenant, rate limits, uploads, SSRF, injection, disclosure, prompt injection, agent escalation and unauthorized RAG with synthetic fixtures. No testing of external systems without authorization.
16. CI (when created): secret, dependency, SAST, image and IaC scanning, SBOM, pinned dependencies, protected branches and reviews, deploy approvals, rollback, severity-based gates with a documented exception process.

**Open decisions 🟡:** IdP and token format, algorithms and lifetimes, BFF details, local accounts, policy engine, 404 vs 403, on-behalf-of mechanism, limits, malware scanning, egress allowlists, rate-limit backend, vector-store tenancy, approval tool list, sandboxing, audit sink, CI tools and SLAs (full lists in API_SECURITY.md §17 and AGENT_SECURITY.md §11).

---

## 11. Scaffolding a new project

When the user asks you to create a project from this template:

1. Ask for the target project name if they haven't given one.
2. Check whether the target directory already exists. **Ask before modifying any existing file.**
3. Create the structure in section 2 exactly, as one project with one `src/`.
4. Python placeholders get **only** a one-line module docstring stating their responsibility.
5. Add `__init__.py` to every Python directory under `src/`, and `.gitkeep` to empty directories.
6. Copy this skill's `ASYNC_EXECUTION.md`, `PYDANTIC_STANDARDS.md`, `API_CONVENTIONS.md`, `GUARDRAILS.md`, `AI_EVALUATION.md`, `API_SECURITY.md` and `AGENT_SECURITY.md` into `docs/standards/`. Write `evaluation/README.md` from AI_EVALUATION.md Appendix A. Add `evaluation/reports/` to `.gitignore` 🟡.
7. `.env.example`: comments only. No real credentials and no speculative provider variables.
8. `pyproject.toml`: project metadata only (name, version, description, readme). No dependencies.
9. `README.md`: the project's purpose plus the generated tree.
10. `CLAUDE.md` (and the equivalent rules file for other IDEs, e.g. `AGENTS.md` or `.cursor/rules`) must contain at least:

    ```markdown
    # Project rules
    - Before adding or moving modules, follow the structure rules of the `production-fast-api-template` skill (or `docs/architecture/` if present).
    - Before writing any route, service, client, agent tool, worker or background job, read `docs/standards/ASYNC_EXECUTION.md` and follow its 🟢 conventions.
    - Before writing any Pydantic schema, settings class, serialization, structured LLM output, citation check, agent plan or tool-argument model, read `docs/standards/PYDANTIC_STANDARDS.md` and follow its 🟢 conventions.
    - Before writing any dependency, route signature, auth or permission check, OpenAPI metadata, DB model or query, migration, API test or lint setup, read `docs/standards/API_CONVENTIONS.md` and follow its 🟢 conventions.
    - Before adding or changing any user-facing LLM call, RAG answer, document ingestion, agent tool execution or gateway target, read `docs/standards/GUARDRAILS.md` and place its checkpoints.
    - Every new or changed RAG stage, structured output, citation format, agent, tool, workflow or conversation feature must state how it is evaluated, following `docs/standards/AI_EVALUATION.md` (deterministic checks first, then the starter judged metrics). Never call live judges from `tests/`.
    - Before writing any authentication, token, permission, tenant/ownership check, input or upload handling, outbound request, response header, rate limit, audit event, secret, IAM or CI security change, read `docs/standards/API_SECURITY.md` and follow its mandatory controls. Add the matching `tests/security/` tests.
    - Before adding or changing any agent, tool, approval flow, memory write or MCP connector, read `docs/standards/AGENT_SECURITY.md`: the LLM proposes, deterministic code authorizes, validates, approves, executes and audits.
    - Items marked 🟡 in these documents are unapproved decisions. Ask before choosing one.
    ```
11. Verify that every expected path exists, that there is exactly one `FastAPI()` entry point, and that no logic, integrations or secrets were added.
12. Report the generated tree and any deviations.

**Do not** implement classes, functions, endpoints, algorithms, DB connections, agent workflows,
queues, workers, Lambda functions or external API calls unless the user asks. Don't generate
GitHub Actions, Docker, Kubernetes, Terraform/CDK, migrations, `alembic.ini`, ruff configuration or
deployment scripts without being asked. Don't install dependencies (Celery, Redis, RabbitMQ, AWS SDKs, DeepEval, Ragas, JWT or crypto libraries, etc.) without approval. Don't run evaluations against live or paid judges, create signing keys or credentials, deploy security infrastructure or test external systems without being asked and authorized.

---

## 12. Working on an existing project

- Before adding a file, locate its row in section 3, and check that no file with the same responsibility exists already.
- Before writing execution-sensitive code, classify the work as async I/O, sync I/O, short CPU, heavy CPU or long/durable. Then choose the path from `ASYNC_EXECUTION.md` §0 and §5.
- Before accepting any data, classify its source: client request, settings, LLM output, tool output, or a third-party payload. Apply the matching model category and `extra` policy from `PYDANTIC_STANDARDS.md` §2. Treat LLM and tool output as untrusted, and apply all three validation levels.
- When a change would break a 🟢 convention, explain why and ask. When it touches a 🟡 decision, present the options with their trade-offs.
- Before writing a route, list the checks it needs. Reuse existing `valid_*` / `require_*` dependencies (`API_CONVENTIONS.md` §1–§2) instead of re-querying in the handler, and keep path-parameter names consistent with existing routes.
- Before adding an LLM-facing surface, tool or ingestion source, list its guardrail checkpoints (`GUARDRAILS.md` §3) and its enforcement point. A new surface without input and output checkpoints is incomplete.
- Before adding a route, state its authentication, function-level and object-level authorization, tenant scoping, input limits and rate-limit surface (`API_SECURITY.md` §0, §4, §8). A route without them is incomplete.
- Before adding an agent tool, fill in its authorization card (`AGENT_SECURITY.md` §4.2): side-effect class, permissions, argument model, approval, limits and audit event.
- When changing a RAG stage, prompt, model, tool or agent, name the evaluation that covers it (`AI_EVALUATION.md` §4–§6) and whether its baseline or thresholds need re-approval.
