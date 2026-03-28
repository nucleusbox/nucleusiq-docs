# NucleusIQ overview

> NucleusIQ is an open-source, agent-first Python framework with execution modes, built-in tools, and provider-agnostic LLM support — so you can build agents that adapt to your workflow without lock-in.

NucleusIQ is the practical way to build AI agents that work in real environments. Connect to OpenAI, Google Gemini, or MockLLM for testing — with the same agent code. NucleusIQ provides three execution modes, built-in file tools, the `@tool` decorator, memory strategies, plugins, streaming, structured output, usage tracking, and cost estimation.

!!! tip "Direct vs Standard vs Autonomous"
    NucleusIQ uses the **Gearbox Strategy** — three execution modes that scale from simple chat to autonomous reasoning:

    - **DIRECT** — Fast, single LLM call, up to 5 tool calls. Best for Q&A and simple lookups.
    - **STANDARD** — Tool-enabled, linear execution, up to 30 tool calls. Default for most workflows.
    - **AUTONOMOUS** — Planning, Critic/Refiner verification, up to 100 tool calls. For complex, high-stakes tasks.

    See [Execution modes](execution-modes.md) for details.

NucleusIQ agents support memory, streaming, structured output, cost tracking, and 10 built-in plugins. Sensible defaults get you running quickly — add complexity only when the task needs it.

## Create an agent

=== "With OpenAI"

    ```python
    import asyncio
    from nucleusiq.agents import Agent
    from nucleusiq.agents.config import AgentConfig, ExecutionMode
    from nucleusiq.agents.task import Task
    from nucleusiq_openai import BaseOpenAI

    agent = Agent(
        name="analyst",
        llm=BaseOpenAI(model_name="gpt-4o-mini"),
        model="gpt-4o-mini",
        instructions="You are a helpful data analyst.",
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )

    result = asyncio.run(
        agent.execute(Task(id="t1", objective="What is the capital of France?"))
    )
    print(result.content)
    ```

=== "With Gemini"

    ```python
    import asyncio
    from nucleusiq.agents import Agent
    from nucleusiq.agents.config import AgentConfig, ExecutionMode
    from nucleusiq.agents.task import Task
    from nucleusiq_gemini import BaseGemini

    agent = Agent(
        name="analyst",
        llm=BaseGemini(model_name="gemini-2.5-flash"),
        model="gemini-2.5-flash",
        instructions="You are a helpful data analyst.",
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )

    result = asyncio.run(
        agent.execute(Task(id="t2", objective="What is the capital of France?"))
    )
    print(result.content)
    ```

=== "With MockLLM (no API key)"

    ```python
    import asyncio
    from nucleusiq.agents import Agent
    from nucleusiq.agents.task import Task
    from nucleusiq.core.llms.mock_llm import MockLLM

    agent = Agent(
        name="analyst",
        llm=MockLLM(),
        instructions="You are a helpful assistant.",
    )

    result = asyncio.run(agent.execute(Task(id="t3", objective="What is 2 + 2?")))
    print(result.content)
    ```

See the [Install](install.md) and [Quickstart](quickstart.md) guides to get started.

## Core benefits

<div class="grid cards" markdown>

-   :material-swap-horizontal: **Provider-portable**
    ---
    Swap OpenAI, Gemini, or Mock LLMs with one line. Same agent, same tools, same plugins.
    [:octicons-arrow-right-24: Providers](providers.md)

-   :material-cog: **Execution modes**
    ---
    Direct, Standard, and Autonomous — pick the right level of control for each use case.
    [:octicons-arrow-right-24: Execution modes](execution-modes.md)

-   :material-wrench: **Flexible tools**
    ---
    `@tool` decorator, built-in file tools, and provider native tools (Google Search, Code Execution, etc.).
    [:octicons-arrow-right-24: Tools](tools.md)

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
