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
agent = Agent(
    ...,
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
    tools=[...],
    memory=...,
    plugins=[...],
)
```

Use [Observability](../usage-tracking.md) to tune mode vs cost.
