# Models

NucleusIQ uses a **provider-agnostic** `BaseLLM` interface. Swap providers without changing the rest of your agent code.

## Supported providers

| Provider | Package | Install |
|----------|---------|---------|
| OpenAI | `nucleusiq-openai` | `pip install nucleusiq-openai` |
| Mock (testing) | Built-in | `from nucleusiq.core.llms.mock_llm import MockLLM` |

## Usage

```python
from nucleusiq_openai import BaseOpenAI

llm = BaseOpenAI(model_name="gpt-4o-mini")
# or
llm = BaseOpenAI(model_name="gpt-4o", temperature=0.5, timeout=60.0)
```

```python
from nucleusiq.core.llms.mock_llm import MockLLM

llm = MockLLM()  # No API key needed
```

## AgentConfig overrides

Tune LLM parameters per agent:

```python
from nucleusiq.agents.config import AgentConfig

config = AgentConfig(
    llm_max_tokens=1024,
    verbose=True,
)
agent = Agent(..., config=config)
```

## Per-task overrides

Override parameters for a single execution:

```python
from nucleusiq_openai import OpenAILLMParams

result = await agent.execute(
    task,
    llm_params=OpenAILLMParams(temperature=0.2),
)
```

## See also

- [OpenAI provider guide](guides/openai-provider.md) — Full parameter control and three-layer design
- [Install](install.md) — Setup instructions
