# NucleusIQ overview

> NucleusIQ is an open-source, agent-first Python framework with execution modes, built-in tools, and provider-agnostic LLM support — so you can build agents that adapt to your workflow without lock-in.

NucleusIQ is the practical way to build AI agents that work in real environments. Connect to OpenAI, Google Gemini, Groq, **Ollama** (local inference), or MockLLM for testing — with the same agent code. NucleusIQ provides three execution modes, built-in file tools, the `@tool` decorator, memory strategies, plugins, streaming, structured output, usage tracking, cost estimation, and **context window management**.

!!! tip "Direct vs Standard vs Autonomous"
    NucleusIQ uses the **Gearbox Strategy** — three execution modes that scale from simple chat to autonomous reasoning:

    - **DIRECT** — Fast, single LLM call; default tool budget **25** invocations per run (override with `max_tool_calls`). Best for Q&A and simple lookups.
    - **STANDARD** — Tool-enabled, linear execution; default **80** invocations per run. Default mode for most workflows.
    - **AUTONOMOUS** — Planning, Critic/Refiner verification; default **300** invocations per run. For complex, high-stakes tasks.

    See [Execution modes](execution-modes.md) for details.

!!! success "Context window management (v0.7.6+) — V2 stable in v0.7.7"
    Automatic context management for tool-heavy agents — prevents context overflow and keeps token usage under control. **v0.7.7** stabilizes masking/compaction, rehydration with auto-detected model windows, and clearer behavior when tool budgets are exhausted.

    See [Context management](context-management.md). For how masking/compaction tiers (**L0–L3**) connect to run-local state (**L4–L6**) and output closure (**L7**), see [Context stack layers (L0–L7)](context-stack-layers.md).

!!! info "Run-local context state (v0.7.8)"
    Each **`execute()`** can populate an in-memory **workspace**, **evidence dossier**, and **lexical document corpus**, with automatic activation after tool results and telemetry under **`AgentResult.metadata`**. Separate from transcript compaction — complements context window management.

    See [Run-local context state](run-local-context-state.md).

NucleusIQ agents support memory, streaming, structured output, cost tracking, and 10 built-in plugins. Sensible defaults get you running quickly — add complexity only when the task needs it.

## Create an agent

*Changed in v0.7.6: `prompt` is mandatory. `narrative` removed. `role`/`objective` are labels only.*

=== "With OpenAI"

    ```python
    import asyncio
    from nucleusiq.agents import Agent
    from nucleusiq.agents.config import AgentConfig, ExecutionMode
    from nucleusiq.agents.task import Task
    from nucleusiq.prompts.zero_shot import ZeroShotPrompt
    from nucleusiq_openai import BaseOpenAI

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful data analyst.",
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )

    result = asyncio.run(
        agent.execute(Task(id="t1", objective="What is the capital of France?"))
    )
    print(result.output)
    ```

=== "With Gemini"

    ```python
    import asyncio
    from nucleusiq.agents import Agent
    from nucleusiq.agents.config import AgentConfig, ExecutionMode
    from nucleusiq.agents.task import Task
    from nucleusiq.prompts.zero_shot import ZeroShotPrompt
    from nucleusiq_gemini import BaseGemini

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful data analyst.",
        ),
        llm=BaseGemini(model_name="gemini-2.5-flash"),
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )

    result = asyncio.run(
        agent.execute(Task(id="t2", objective="What is the capital of France?"))
    )
    print(result.output)
    ```

=== "With Groq"

    ```python
    import asyncio
    from nucleusiq.agents import Agent
    from nucleusiq.agents.config import AgentConfig, ExecutionMode
    from nucleusiq.agents.task import Task
    from nucleusiq.prompts.zero_shot import ZeroShotPrompt
    from nucleusiq_groq import BaseGroq

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful data analyst.",
        ),
        llm=BaseGroq(model_name="llama-3.3-70b-versatile", async_mode=True),
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )

    async def _run():
        await agent.initialize()
        return await agent.execute(Task(id="t-groq", objective="What is the capital of France?"))

    result = asyncio.run(_run())
    print(result.output)
    ```

=== "With Ollama"

    ```python
    import asyncio
    from nucleusiq.agents import Agent
    from nucleusiq.agents.config import AgentConfig, ExecutionMode
    from nucleusiq.agents.task import Task
    from nucleusiq.prompts.zero_shot import ZeroShotPrompt
    from nucleusiq_ollama import BaseOllama

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful data analyst.",
        ),
        llm=BaseOllama(model_name="llama3.2", async_mode=True),
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )

    async def _run():
        await agent.initialize()
        return await agent.execute(Task(id="t-ollama", objective="What is the capital of France?"))

    result = asyncio.run(_run())
    print(result.output)
    ```

=== "With MockLLM (no API key)"

    ```python
    import asyncio
    from nucleusiq.agents import Agent
    from nucleusiq.agents.task import Task
    from nucleusiq.prompts.zero_shot import ZeroShotPrompt
    from nucleusiq.core.llms.mock_llm import MockLLM

    agent = Agent(
        name="analyst",
        prompt=ZeroShotPrompt().configure(
            system="You are a helpful assistant.",
        ),
        llm=MockLLM(),
    )

    result = asyncio.run(agent.execute(Task(id="t3", objective="What is 2 + 2?")))
    print(result.output)
    ```

See the [Install](install.md) and [Quickstart](quickstart.md) guides to get started.

## Core benefits

<div class="grid cards" markdown>

-   :material-swap-horizontal: **Provider-portable**
    ---
    Swap OpenAI, Gemini, Groq, Ollama, or Mock LLMs with one line. Same agent, same tools, same plugins.
    [:octicons-arrow-right-24: Providers](providers.md)

-   :material-cog: **Execution modes**
    ---
    Direct, Standard, and Autonomous — pick the right level of control for each use case.
    [:octicons-arrow-right-24: Execution modes](execution-modes.md)

-   :material-wrench: **Flexible tools**
    ---
    `@tool` decorator, built-in file tools, and provider native tools (Google Search, Code Execution, etc.).
    [:octicons-arrow-right-24: Tools](tools.md)

-   :material-memory: **Context management**
    ---
    Automatic context management prevents overflow in tool-heavy agents. *Shipped in v0.7.6; V2 stable in v0.7.7; extended by **run-local workspace/evidence/corpus** in v0.7.8 — see [Run-local context state](run-local-context-state.md).*
    [:octicons-arrow-right-24: Context management](context-management.md)

-   :material-chart-line: **Observability**
    ---
    Token usage by purpose/origin with `agent.last_usage.display()` plus dollar cost estimation.
    [:octicons-arrow-right-24: Observability](observability/index.md)

-   :material-shield-check: **Production plugins**
    ---
    10 built-in plugins: PII guard, tool guard, retry, fallback, human approval, and more.
    [:octicons-arrow-right-24: Plugins](plugins/overview.md)

-   :material-alert-circle: **Error handling**
    ---
    Provider-agnostic exception hierarchy with automatic retry and structured error context.
    [:octicons-arrow-right-24: Error handling](core-concepts/error-handling.md)

</div>
