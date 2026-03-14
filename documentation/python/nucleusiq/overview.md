# NucleusIQ overview

> NucleusIQ is an open-source, agent-first Python framework with execution modes, built-in tools, and provider-agnostic LLM support—so you can build agents that adapt to your workflow without lock-in.

NucleusIQ is the easy way to build AI agents that work in real environments. With a few lines of code, you can connect to OpenAI, MockLLM (for testing), and [more providers](guides/openai-provider.md). NucleusIQ provides three execution modes, built-in file tools, memory strategies, and plugins to help you get started quickly and build production-ready agents.

!!! tip "Direct vs Standard vs Autonomous"
    NucleusIQ uses the **Gearbox Strategy**—three execution modes that scale from simple chat to autonomous reasoning:

    - **DIRECT** — Fast, single LLM call, up to 5 tool calls. Best for Q&A and simple lookups.
    - **STANDARD** — Tool-enabled, linear execution, up to 30 tool calls. Default for most workflows.
    - **AUTONOMOUS** — Planning, Critic/Refiner verification, up to 100 tool calls. For complex, high-stakes tasks.

    See [Execution modes](execution-modes.md) for details.

NucleusIQ agents support memory, streaming, structured output, and 10 built-in plugins. You do not need to configure everything—sensible defaults get you running quickly.

We recommend NucleusIQ if you want to quickly build agents with clear execution semantics and production-ready features.

## Create an agent

```python
# pip install nucleusiq nucleusiq-openai
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.task import Task
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="analyst",
    role="Data analyst",
    objective="Answer questions and analyze data",
    llm=BaseOpenAI(model_name="gpt-4o-mini"),
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)

task = Task(id="t1", objective="What is the capital of France?")
result = asyncio.run(agent.execute(task))
print(result)
```

See the [Install](install.md) and [Quickstart](quickstart.md) guides to get started building your own agents.

!!! note "No API key? Use MockLLM"
    For testing without an API key, use `MockLLM` from `nucleusiq.core.llms.mock_llm`. See [Quickstart](quickstart.md#minimal-example-no-api-key).

## Core benefits

<div class="grid cards" markdown>

-   :material-refresh: **Provider-agnostic**
    ---
    Swap OpenAI, Mock (testing), or custom LLMs via a single `BaseLLM` interface. No lock-in.
    [:octicons-arrow-right-24: Learn more](models.md)

-   :material-cog: **Execution modes**
    ---
    Direct, Standard, and Autonomous—pick the right level of control for each use case.
    [:octicons-arrow-right-24: Learn more](execution-modes.md)

-   :material-folder: **Built-in tools**
    ---
    File read/write, search, directory listing, and extraction—sandboxed to a workspace.
    [:octicons-arrow-right-24: Learn more](tools.md)

-   :material-chart-line: **Usage tracking**
    ---
    Token usage by purpose and origin with `agent.last_usage.display()`.
    [:octicons-arrow-right-24: Learn more](usage-tracking.md)

</div>

