# Prompts

*Changed in v0.7.6: `prompt` is now mandatory on `Agent`. `narrative` has been removed.*

NucleusIQ includes a prompt-engineering module with a factory-based API. The prompt object is the **single source of truth** for the LLM's system message and behaviour — everything the LLM sees is defined here.

## Creating a Prompt

The simplest and most common approach uses `ZeroShotPrompt` directly:

```python
from nucleusiq.prompts.zero_shot import ZeroShotPrompt

prompt = ZeroShotPrompt().configure(
    system="You are a precise analyst. Provide detailed, data-driven answers.",
)
```

Or use `PromptFactory` for technique-agnostic creation:

```python
from nucleusiq.prompts import PromptFactory, PromptTechnique

prompt = PromptFactory.create_prompt(PromptTechnique.ZERO_SHOT).configure(
    system="You are a precise analyst.",
)
```

## prompt.system vs prompt.user

| Field | Purpose | Required | What happens |
|-------|---------|----------|-------------|
| `system` | The LLM's system message — defines identity, behaviour, constraints | **Yes** | Sent as the system message in every LLM call |
| `user` | Optional preamble prepended before the task objective | No | If provided, prepended to the user's task objective |

The task objective (from `Task(objective="...")`) provides the actual user query. `prompt.user` is an optional preamble that gets prepended before it.

### System-only (most common)

When your system message contains all instructions:

```python
prompt = ZeroShotPrompt().configure(
    system="You are a financial analyst. Analyze data thoroughly and cite sources.",
)
```

### With user preamble

When you want to add execution instructions before every task:

```python
prompt = ZeroShotPrompt().configure(
    system="You are a research analyst specializing in financial data.",
    user="Gather all data using tools first, then write the full report.",
)
```

In this case, if the task objective is "Analyze TCS annual report", the LLM sees:

- **System:** "You are a research analyst specializing in financial data."
- **User:** "Gather all data using tools first, then write the full report.\n\nAnalyze TCS annual report"

## Built-in techniques

| Technique | Enum value | Best for |
|-----------|------------|----------|
| Zero-shot | `PromptTechnique.ZERO_SHOT` | General-purpose, most common |
| Few-shot | `PromptTechnique.FEW_SHOT` | Tasks where examples improve accuracy |
| Chain-of-thought | `PromptTechnique.CHAIN_OF_THOUGHT` | Step-by-step reasoning |
| Auto chain-of-thought | `PromptTechnique.AUTO_CHAIN_OF_THOUGHT` | Automatic reasoning chain generation |
| Retrieval augmented generation | `PromptTechnique.RETRIEVAL_AUGMENTED_GENERATION` | Context-grounded answers |
| Prompt composer | `PromptTechnique.PROMPT_COMPOSER` | Multi-section prompts |
| Meta prompting | `PromptTechnique.META_PROMPTING` | Self-improving prompts |

### Zero-shot example (most common)

```python
from nucleusiq.prompts.zero_shot import ZeroShotPrompt

prompt = ZeroShotPrompt().configure(
    system="You are a helpful coding assistant. Write clean, well-documented Python code.",
)
```

### Few-shot example

```python
from nucleusiq.prompts import PromptFactory, PromptTechnique

prompt = PromptFactory.create_prompt(PromptTechnique.FEW_SHOT).configure(
    system="Classify the sentiment of the given text as positive, negative, or neutral.",
    examples=[
        {"input": "I love this product!", "output": "positive"},
        {"input": "Terrible experience.", "output": "negative"},
        {"input": "It was okay.", "output": "neutral"},
    ],
)
```

### Chain-of-thought example

```python
from nucleusiq.prompts import PromptFactory, PromptTechnique

prompt = PromptFactory.create_prompt(PromptTechnique.CHAIN_OF_THOUGHT).configure(
    system="Solve math problems step by step. Show your reasoning before the final answer.",
)
```

## Use with Agent

`prompt` is mandatory on `Agent`. All LLM instructions go into the prompt:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="researcher",
    role="Research assistant",       # Label only — NOT sent to LLM
    objective="Find information",    # Label only — NOT sent to LLM
    prompt=ZeroShotPrompt().configure(
        system=(
            "You are a research assistant. Find and synthesize relevant information. "
            "Be concise and accurate. Cite your sources when possible."
        ),
    ),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

!!! tip "role and objective are labels"
    `role` and `objective` are used for logging, sub-agent naming, and documentation only. They are **never** sent to the LLM. Put all instructions in `prompt.system`.

## Complete example with tools

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq_openai import BaseOpenAI

@tool
def search_docs(query: str) -> str:
    """Search documentation for relevant content."""
    return f"Found 3 results for '{query}': [documentation excerpts...]"

async def main():
    prompt = ZeroShotPrompt().configure(
        system=(
            "You are a documentation assistant. Search the docs to find answers. "
            "Always cite the specific documentation section in your response."
        ),
        user="Search thoroughly before answering.",
    )

    agent = Agent(
        name="docs-bot",
        prompt=prompt,
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        tools=[search_docs],
        config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    )

    result = await agent.execute({
        "id": "p1",
        "objective": "How do I configure context management in NucleusIQ?",
    })
    print(result.output)

asyncio.run(main())
```

## Prompt strategy tracing

*New in v0.7.6*

When tracing is enabled (`AgentConfig(enable_tracing=True)`), `AgentResult.llm_calls[].prompt_technique` records which prompt strategy was used for each LLM call:

```python
config = AgentConfig(enable_tracing=True)
agent = Agent(name="traced", prompt=prompt, llm=llm, config=config)
result = await agent.execute(task)

for call in result.llm_calls:
    print(f"Purpose: {call['purpose']}, Technique: {call.get('prompt_technique', 'n/a')}")
    # Output: "Purpose: main, Technique: zero_shot"
```

## Extending with custom techniques

Register your own prompt class for custom strategies:

```python
from nucleusiq.prompts.base import BasePrompt
from nucleusiq.prompts import PromptFactory, PromptTechnique

class MyCustomPrompt(BasePrompt):
    """Custom prompt technique with domain-specific formatting."""

    @property
    def input_variables(self):
        return ["system"]

    @property
    def optional_variables(self):
        return ["user", "context"]

    # Implement required abstract methods...

# Register with the factory
# PromptFactory.register_prompt(PromptTechnique(...), MyCustomPrompt)
```

## See also

- [Agents](agents.md) — Agent configuration and lifecycle
- [Execution modes](execution-modes.md) — How prompts interact with mode behavior
- [Context management](context-management.md) — Context window management
- [Migration notes](learn/migration-notes.md) — Upgrading from v0.7.5 (narrative removal, prompt mandatory)
- [Examples](examples/index.md) — Working examples with prompts
