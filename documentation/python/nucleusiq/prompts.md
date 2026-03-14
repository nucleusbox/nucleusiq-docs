# Prompts

NucleusIQ includes a prompt-engineering module with a factory-based API.

## PromptFactory and PromptTechnique

Use `PromptFactory` to create prompt strategies without changing agent code.

```python
from nucleusiq.prompts import PromptFactory, PromptTechnique

prompt = PromptFactory.create_prompt(PromptTechnique.ZERO_SHOT).configure(
    system="You are a precise analyst.",
    user="Answer clearly and include assumptions.",
)
```

## Built-in techniques

| Technique | Enum value |
|-----------|------------|
| Zero-shot | `PromptTechnique.ZERO_SHOT` |
| Few-shot | `PromptTechnique.FEW_SHOT` |
| Chain-of-thought | `PromptTechnique.CHAIN_OF_THOUGHT` |
| Auto chain-of-thought | `PromptTechnique.AUTO_CHAIN_OF_THOUGHT` |
| Retrieval augmented generation | `PromptTechnique.RETRIEVAL_AUGMENTED_GENERATION` |
| Prompt composer | `PromptTechnique.PROMPT_COMPOSER` |
| Meta prompting | `PromptTechnique.META_PROMPTING` |

## Use with Agent

```python
from nucleusiq.agents import Agent
from nucleusiq.prompts import PromptFactory, PromptTechnique
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="researcher",
    role="Research assistant",
    objective="Find and synthesize relevant information",
    llm=BaseOpenAI(model_name="gpt-4o-mini"),
    prompt=PromptFactory.create_prompt(PromptTechnique.ZERO_SHOT).configure(
        system="Be concise and accurate.",
        user="Use evidence from available context and tools.",
    ),
)
```

## Extending with custom techniques

Register your own prompt class if you need a custom strategy:

```python
from nucleusiq.prompts import PromptFactory, PromptTechnique

# PromptFactory.register_prompt(PromptTechnique(...), CustomPromptClass)
```

## See also

- [Agents](agents.md) — Agent configuration and lifecycle
- [Execution modes](execution-modes.md) — How prompts interact with mode behavior
- [OpenAI provider guide](guides/openai-provider.md) — Provider-specific behavior
