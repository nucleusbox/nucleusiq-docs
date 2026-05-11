<div class="home-hero" markdown>

# NucleusIQ Documentation

Build AI agents as durable software systems, not one-off demos.

[Get Started](python/nucleusiq/get-started/index.md){ .md-button .md-button--primary }
[Core Concepts](python/nucleusiq/core-concepts/index.md){ .md-button }

</div>

---

## What We Are Building

NucleusIQ is an **open-source, agent-first Python framework** for teams that want to ship agents into real products.

The core idea is simple: agents should be engineered like serious software systems:

- maintainable by teams over time
- testable and observable in production
- provider-portable as the ecosystem changes
- structured for tools, memory, policy, and validation

An agent is not just one model call. It is a managed runtime with responsibilities.

---

## Why NucleusIQ Exists

Modern models can produce impressive demos quickly.  
The hard part is owning those systems for months and years.

NucleusIQ is designed to close that gap between:

- what AI can generate fast, and
- what engineering teams can safely maintain long term.

This means less fragile glue code, less accidental complexity, and clearer architecture as systems grow.

---

## Our Philosophy

NucleusIQ follows a practical philosophy for dependable agent engineering:

### 1) Agent-first thinking
Design around the full agent lifecycle (execution, tools, memory, policy), not isolated model calls.

### 2) Harness over hype
Reliability comes from good scaffolding: boundaries, artifacts, visibility, and feedback loops.

### 3) Progressive complexity
Start simple, add orchestration only when the task justifies it.

### 4) Open integration, closed coupling
Integrate broadly with providers and tools, but keep the core architecture stable and portable.

### 5) Reliability is a feature
Validation, structured output, policy controls, and observability are first-class parts of the framework.

---

## Build Path

Choose your path based on where you are today:

- **Start**: [Installation](python/nucleusiq/install.md) and [Quickstart](python/nucleusiq/quickstart.md)
- **Understand**: [Overview](python/nucleusiq/overview.md) and [Core Concepts](python/nucleusiq/core-concepts/index.md)
- **Scale**: [Execution Modes](python/nucleusiq/execution-modes.md), [Tools](python/nucleusiq/tools.md), [Memory](python/nucleusiq/memory.md), [Plugins](python/nucleusiq/plugins/overview.md)
- **Ship**: [Production Architecture](python/nucleusiq/core-concepts/production-architecture.md), [Structured Output](python/nucleusiq/structured-output.md), [Observability](python/nucleusiq/usage-tracking.md)

---

## What's new in v0.7.x

### v0.7.10 (latest)

!!! success "Core security extras + Ollama alpha"
    - **`nucleusiq` 0.7.10** — optional **`nucleusiq[http]`**; **`urllib3`** resolution hardening in locks; structured-output resolver recognizes **Ollama** / Groq LLMs for **`OutputSchema`** payloads.
    - **`nucleusiq-ollama` 0.1.0a1** (**alpha**) — local / remote **[Ollama](https://ollama.com/)** via official **`ollama`** SDK: **`BaseOllama`**, tools, streaming, structured **`format`**, **`think`** / **`keep_alive`**. Requires **`nucleusiq>=0.7.10`**.

    [Changelog](reference/changelog.md){ .md-button } · [Ollama provider](python/nucleusiq/guides/ollama-provider.md){ .md-button } · [Ollama quickstart](python/nucleusiq/examples/ollama-quickstart.md){ .md-button } · [Migration (0.7.9 → 0.7.10)](python/nucleusiq/learn/migration-notes.md#from-v079-to-v0710){ .md-button }

### v0.7.9

!!! success "LLM rate limits + Groq beta"
    - **`nucleusiq.llms.retry_policy`** — shared **429** handling: **`Retry-After`** parsing, capped backoff, ceiling (**120s** default single sleep cap).
    - **Providers:** **`nucleusiq-openai` 0.6.4**, **`nucleusiq-gemini` 0.2.6**, **`nucleusiq-groq` 0.1.0b1** (public **beta**) — dependency floor **`nucleusiq>=0.7.9`**.
    - **Groq** — stream **open** uses the same **429** policy as chat; **`strict_model_capabilities`** on **`GroqLLMParams`**; **`nucleusiq_groq.capabilities`** allowlist for **`parallel_tool_calls`** (warnings vs strict **`InvalidRequestError`**).

    [Changelog](reference/changelog.md){ .md-button } · [Groq provider](python/nucleusiq/guides/groq-provider.md){ .md-button } · [Groq quickstart](python/nucleusiq/examples/groq-quickstart.md){ .md-button } · [Migration (0.7.8 → 0.7.9)](python/nucleusiq/learn/migration-notes.md#from-v078-to-v079){ .md-button }

### v0.7.8

!!! info "Run-local context state + Groq alpha debut"
    - **Workspace / evidence / lexical corpus** — per-run in-memory analyst state with optional framework tools (budget-exempt).
    - **L4.5 activation**, **phase control**, **evidence gate**, **synthesis package**, autonomous fixes — see [Run-local context state](python/nucleusiq/run-local-context-state.md).
    - **Groq** landed first as **`nucleusiq-groq` 0.1.0a1** (since superseded by **0.1.0b1** + **`nucleusiq>=0.7.9`**).

    [Changelog](reference/changelog.md){ .md-button } · [Migration (0.7.7 → 0.7.8)](python/nucleusiq/learn/migration-notes.md#from-v077-to-v078){ .md-button }

### v0.7.7

!!! success "Context Management v2 + execution fixes"
    - **Stable V2 pipeline** — compaction, masking, recall/rehydration tuned for PDF-heavy agents (`squeeze_threshold=0.70` default).
    - **Optional `@tool(idempotent=True)`** — safe dedup for pure tools; default remains non-idempotent.
    - **`AgentResult` + tool caps** — clearer `status=error` and `ToolCallLimitError` when limits bite; **tools-free synthesis** when the tool cap is hit (synthesis on).
    - **Providers:** `nucleusiq-openai` **0.6.3**, `nucleusiq-gemini` **0.2.5** — aligned with core 0.7.7.

    [Changelog](reference/changelog.md){ .md-button } · [Migration (0.7.6 → 0.7.7)](python/nucleusiq/learn/migration-notes.md#from-v076-to-v077){ .md-button }

### v0.7.6

!!! success "Context Window Management"

    Automatic context management for tool-heavy agents — prevents context overflow and ensures the LLM always has room to respond.

    ```python
    from nucleusiq.agents.context import ContextConfig, ContextStrategy

    config = AgentConfig(
        context=ContextConfig(strategy=ContextStrategy.PROGRESSIVE),
    )
    ```

    [Context management guide](python/nucleusiq/context-management.md){ .md-button }

!!! warning "Breaking: Prompt System Refactor"

    `prompt` is now **mandatory** on `Agent`. The `narrative` field has been removed. `role` and `objective` are labels only — they are **not** sent to the LLM.

    ```python
    from nucleusiq.prompts.zero_shot import ZeroShotPrompt

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a data analyst. Provide detailed analysis.",
        ),
        llm=llm,
    )
    ```

    [Migration guide](python/nucleusiq/learn/migration-notes.md#from-v075-to-v076){ .md-button }

!!! info "Synthesis Pass + ObservabilityConfig"

    - **Synthesis pass** — after multi-round tool loops, the agent makes one final LLM call without tools to produce the full deliverable
    - **ObservabilityConfig** — unified config replacing `verbose` + `enable_tracing`
    - **Context telemetry** — peak utilization, compaction events, token savings in `AgentResult`

    [Observability docs](python/nucleusiq/observability/index.md){ .md-button }

### v0.7.5

- **Gemini native + custom tool mixing** — transparent proxy pattern, zero code changes
- **Full observability wiring** — PluginEvent, MemorySnapshot, AutonomousDetail in AgentResult

### v0.7.4

- **ExecutionTracer** — full LLM/tool call observability
- **Pyrefly static type checking** — 121 type errors fixed, CI-gated
- **Exhaustive error wiring** — typed exceptions everywhere

### v0.7.2-0.7.3

- **Unified exception hierarchy** — 10 error families
- **AgentResult response contract** — typed, immutable Pydantic model
- **Gemini tool-calling fixes** — `$ref`/`$defs` inlining

Current packages: `nucleusiq` **0.7.10**, `nucleusiq-openai` **0.6.4**, `nucleusiq-gemini` **0.2.6**, `nucleusiq-groq` **0.1.0b1** (optional beta), `nucleusiq-ollama` **0.1.0a1** (optional alpha)

See the [full changelog](reference/changelog.md).

---

## Quick links

- [Get Started](python/nucleusiq/get-started/index.md)
- [Guides](python/nucleusiq/guides/index.md)
- [Examples](python/nucleusiq/examples/index.md)
- [Reference](reference/index.md)
