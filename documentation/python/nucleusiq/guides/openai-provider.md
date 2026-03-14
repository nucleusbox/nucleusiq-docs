# OpenAI provider

The NucleusIQ OpenAI provider (`nucleusiq-openai`) gives you full access to Chat Completions and Responses API with a simple agent interface.

## Quick start

```python
from nucleusiq_openai import BaseOpenAI

llm = BaseOpenAI(model_name="gpt-4o-mini")
agent = Agent(..., llm=llm)
```

Set `OPENAI_API_KEY` in your environment.

## Three-layer design

NucleusIQ keeps agent creation simple while giving power users full control:

| Layer | Who | Control |
|-------|-----|---------|
| **Agent** | 90% of users | Model name, basic config |
| **LLM Config** | Power users | `AgentConfig.llm_params` — temperature, max_tokens, etc. |
| **Direct API** | Advanced | Per-task `execute(..., llm_params=OpenAILLMParams(...))` overrides |

## Native tools

The OpenAI provider supports native tool types:

- `function` — Custom Python functions
- `code_interpreter` — Code execution
- `file_search` — File search
- `web_search` — Web search
- `image_generation` — DALL·E
- `mcp` — Model Context Protocol
- `computer_use` — Computer use

## Streaming and usage

- **Streaming** — `execute_stream()` works with both Chat Completions and Responses API
- **Usage tracking** — `agent.last_usage.display()` shows prompt/completion/reasoning tokens

## Full guide

For the complete design guide (parameter merge chain, all 40+ parameters, implementation status), see [openai_provider_user_guide.md](../../../openai_provider_user_guide.md) in the repo.
