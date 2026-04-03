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

### v0.7.4 (latest)

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

Current packages: `nucleusiq` 0.7.4, `nucleusiq-openai` 0.6.1, `nucleusiq-gemini` 0.2.2

See the [full changelog](reference/changelog.md).

---

## Quick links

- [Get Started](python/nucleusiq/get-started/index.md)
- [Guides](python/nucleusiq/guides/index.md)
- [Examples](python/nucleusiq/examples/index.md)
- [Reference](reference/index.md)
