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

### v0.7.5 (latest)

!!! success "Gemini Native + Custom Tool Mixing"

    **The problem:** Google's Gemini 2.5 API rejects requests that combine native tools (`google_search`, `code_execution`) with custom function declarations — a 400 error that blocks the most common agent pattern.

    **No other framework solves this.** LangChain blocks it. Google ADK requires sub-agent restructuring. CrewAI and AutoGen don't address it.

    **NucleusIQ v0.7.5 fixes it transparently** with a proxy pattern — zero code changes, works across all execution modes, all Gemini models. Just pass your tools and it works.

    ```python
    agent = Agent(
        llm=BaseGemini(model_name="gemini-2.5-flash"),
        tools=[
            GeminiTool.google_search(),      # Native
            GeminiTool.code_execution(),     # Native
            my_unit_converter,               # Custom
            my_note_taker,                   # Custom
        ],
        ...
    )
    result = await agent.execute(task)  # Just works.
    ```

    [Read the full guide](python/nucleusiq/guides/gemini-provider.md#mixing-native-and-custom-tools){ .md-button }

!!! info "Full Observability Wiring"

    `AgentResult` now captures the complete execution picture when tracing is enabled:

    - **Plugin events** — every plugin hook with timing (`result.plugin_events`)
    - **Memory snapshot** — conversation state at execution end (`result.memory_snapshot`)
    - **Autonomous detail** — decomposition, sub-tasks, validation, and critic scores (`result.autonomous`)
    - **Decomposer LLM call** — previously invisible `Decomposer.analyze()` call now traced

    [Observability docs](python/nucleusiq/observability/index.md){ .md-button }

### v0.7.4

- **ExecutionTracer** — full LLM/tool call observability with `AgentConfig(enable_tracing=True)`
- **Pyrefly static type checking** — 121 type errors fixed, CI-gated
- **Error package restructure** — `core/errors/` with lazy re-exports
- **Usage & pricing extraction** — `core/agents/usage/` package
- **Exhaustive error wiring** — every `ValueError`/`RuntimeError` replaced with typed exceptions
- **Dead code cleanup** — removed unused GPT-2 tokenizer, added `BaseLLM.estimate_tokens()`

### v0.7.3

- **Gemini tool-calling fixes** — empty `function_response.name`, non-dict response wrapping
- **`$ref`/`$defs` inlining** for Gemini structured output

### v0.7.2

- **Unified exception hierarchy** — 10 error families (Tool, Agent, Attachment, Memory, Prompt, Streaming, Plugin, StructuredOutput, LLM, Workspace)
- **AgentResult response contract** — typed, immutable Pydantic model returned from `agent.execute()`

Current packages: `nucleusiq` 0.7.5, `nucleusiq-openai` 0.6.1, `nucleusiq-gemini` 0.2.3

See the [full changelog](reference/changelog.md).

---

## Quick links

- [Get Started](python/nucleusiq/get-started/index.md)
- [Guides](python/nucleusiq/guides/index.md)
- [Examples](python/nucleusiq/examples/index.md)
- [Reference](reference/index.md)
