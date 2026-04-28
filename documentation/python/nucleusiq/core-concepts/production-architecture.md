# Production Architecture (Gear Strategy)

NucleusIQ production design centers on the Gearbox strategy:

1. Choose execution mode
2. Add tools/memory/plugins
3. Observe token/call behavior
4. Iterate per use case

## Recommended architecture by complexity

### Gear 1: DIRECT

- Lowest latency/cost
- Minimal orchestration
- Ideal for straightforward Q&A

### Gear 2: STANDARD

- Default for most production apps
- Supports iterative tool loops
- Best balance of control and capability

### Gear 3: AUTONOMOUS

- Adds decomposition/verification/refinement patterns
- Useful for high-stakes workflows
- Higher orchestration overhead, often higher reliability

## Reference deployment pattern

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.memory import MemoryFactory, MemoryStrategy
from nucleusiq.plugins.builtin import ModelCallLimitPlugin, ToolRetryPlugin
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.builtin import FileReadTool
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="production-pattern",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    tools=[FileReadTool(workspace_root="./data")],
    memory=MemoryFactory.create_memory(MemoryStrategy.SLIDING_WINDOW, window_size=10),
    plugins=[
        ModelCallLimitPlugin(max_calls=20),
        ToolRetryPlugin(max_retries=2),
    ],
)
```

Use [Observability](../usage-tracking.md) to tune mode vs cost.
