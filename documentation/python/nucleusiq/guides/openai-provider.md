# OpenAI provider

The NucleusIQ OpenAI provider (`nucleusiq-openai`) integrates OpenAI's Chat Completions and Responses API with automatic routing between them.

## Installation

```bash
pip install nucleusiq nucleusiq-openai
```

Set your API key:

```bash
export OPENAI_API_KEY=sk-...
```

## Quick start

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="assistant",
    prompt=ZeroShotPrompt().configure(
        system="You are a helpful assistant.",
    ),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
result = await agent.execute({"id": "openai-guide-1", "objective": "What is the capital of France?"})
```

## Supported models

| Model | Use case | API |
|-------|----------|-----|
| `gpt-4o` | High capability, multimodal | Chat Completions |
| `gpt-4o-mini` | Fast, cost-effective | Chat Completions |
| `gpt-4.1` | Latest GPT-4 series | Chat Completions |
| `gpt-4.1-mini` | Balanced cost/performance | Chat Completions |
| `gpt-4.1-nano` | Ultra-fast, lowest cost | Chat Completions |
| `o3`, `o3-mini` | Reasoning models | Chat Completions |
| `o4-mini` | Latest reasoning model | Chat Completions |

## Three-layer parameter design

| Layer | Who | How |
|-------|-----|-----|
| **Agent** | 90% of users | `Agent(model="gpt-4o-mini")` |
| **Config** | Power users | `AgentConfig(llm_params=OpenAILLMParams(temperature=0.2))` |
| **Per-task** | Advanced | `agent.execute(task, llm_params=OpenAILLMParams(...))` |

```python
from nucleusiq_openai import OpenAILLMParams

config = AgentConfig(
    llm_params=OpenAILLMParams(
        temperature=0.7,
        max_output_tokens=2048,
        reasoning_effort="high",  # For o-series models
    ),
)
```

## Native tools

The OpenAI provider supports server-side native tools:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI, OpenAITool

# Example: web search (repeat the same shape for other native tools)
agent = Agent(
    name="native-tools",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    tools=[OpenAITool.web_search()],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)

# Code interpreter: tools=[OpenAITool.code_interpreter()]
# File search: tools=[OpenAITool.file_search()]
# MCP:
# tools=[
#     OpenAITool.mcp(
#         server_label="my-mcp",
#         server_description="My MCP server",
#         server_url="https://my-server.example.com/sse",
#     ),
# ]
```

| Tool type | Description |
|-----------|-------------|
| `function` | Custom Python functions (via `@tool` or `BaseTool`) |
| `code_interpreter` | Code execution sandbox |
| `file_search` | File search over uploaded files |
| `web_search` | Web search |
| `image_generation` | DALL-E image generation |
| `mcp` | Model Context Protocol integration |
| `computer_use` | Computer use (preview) |

## API auto-routing

The provider automatically routes between Chat Completions and Responses API based on tool types. Native tools (code_interpreter, file_search, web_search, mcp) use the Responses API; custom function tools use Chat Completions. This is transparent — you don't need to choose.

## Error handling

The provider maps OpenAI SDK errors to NucleusIQ's framework-level exceptions:

```python
from nucleusiq.llms.errors import RateLimitError, AuthenticationError

try:
    result = await agent.execute({"id": "openai-guide-2", "objective": "Hello"})
except RateLimitError:
    print("Rate limited — retry with backoff")
except AuthenticationError:
    print("Check your OPENAI_API_KEY")
```

Automatic retry with exponential backoff for rate limits, server errors, and connection issues.

## Streaming

```python
async for event in agent.execute_stream({"id": "s1", "objective": "Write a poem"}):
    if event.type.value == "token":
        print(event.token, end="", flush=True)
```

Streaming works with both Chat Completions and Responses API.

## See also

- [Gemini provider guide](gemini-provider.md) — Gemini integration
- [Providers](../providers.md) — Provider portability
- [Error handling](../core-concepts/error-handling.md) — Framework error taxonomy
- [Cost estimation](../observability/cost-estimation.md) — OpenAI model pricing
