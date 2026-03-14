# Core Concept: LLM and Providers

NucleusIQ core is provider-agnostic. Provider packages implement concrete model APIs.

## Base + provider pattern

- Core contracts: `BaseLLM`, `LLMParams`
- Provider package: e.g., `nucleusiq-openai`

```python
from nucleusiq_openai import BaseOpenAI

llm = BaseOpenAI(model_name="gpt-4o-mini")
```

## Per-agent and per-task parameter control

```python
from nucleusiq.agents.config import AgentConfig
from nucleusiq_openai import OpenAILLMParams

config = AgentConfig(llm_params=OpenAILLMParams(temperature=0.2))
result = await agent.execute(task, llm_params=OpenAILLMParams(reasoning_effort="high"))
```
