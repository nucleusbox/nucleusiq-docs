# Core Concept: Tools, Memory, Plugins

These three components shape runtime behavior.

## Tools

Allow the agent to act on external systems (files/APIs/etc).

## Memory

Controls conversation state retention strategy.

## Plugins

Inject policy, guardrails, retry, limits, and validation via lifecycle hooks.

## Combined example

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.memory import MemoryFactory, MemoryStrategy
from nucleusiq.plugins.builtin import ModelCallLimitPlugin, ToolRetryPlugin
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.builtin import FileSearchTool
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="runtime-demo",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    tools=[FileSearchTool(workspace_root="./data")],
    memory=MemoryFactory.create_memory(MemoryStrategy.SLIDING_WINDOW, window_size=10),
    plugins=[ModelCallLimitPlugin(max_calls=20), ToolRetryPlugin(max_retries=2)],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```
