# Example: Autonomous Workflow

Autonomous mode decomposes complex tasks, executes subtasks, and verifies output via Critic/Refiner loops.

*Updated for v0.7.6: `prompt` is now mandatory.*

## Setup

```python
import asyncio
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.decorators import tool
from nucleusiq.tools.builtin import FileReadTool, FileSearchTool
from nucleusiq_openai import BaseOpenAI

@tool
def analyze_risk(factor: str) -> str:
    """Analyze a specific risk factor and return severity assessment."""
    risk_db = {
        "market_volatility": "HIGH — 30% revenue impact in downturn scenarios",
        "supply_chain": "MEDIUM — 2-3 month disruption tolerance",
        "regulatory": "LOW — compliant with current frameworks",
        "cybersecurity": "HIGH — critical data exposure risk",
    }
    return risk_db.get(factor, f"No data available for: {factor}")

@tool
def propose_mitigation(risk: str, severity: str) -> str:
    """Propose a mitigation strategy for a given risk and severity."""
    return f"Mitigation for {risk} ({severity}): implement monitoring, allocate contingency budget, quarterly review."
```

## Run in Autonomous mode

```python
async def main():
    agent = Agent(
        name="risk-analyst",
        prompt=ZeroShotPrompt().configure(
            system=(
                "You are a risk analyst. Break down complex risk assessments into subtasks. "
                "Use tools to analyze each risk factor and propose mitigations. "
                "Verify your final assessment is comprehensive."
            ),
        ),
        llm=BaseOpenAI(model_name="gpt-4.1-mini"),
        tools=[analyze_risk, propose_mitigation],
        config=AgentConfig(
            execution_mode=ExecutionMode.AUTONOMOUS,
            require_quality_check=True,
            max_iterations=5,
            max_tool_calls=50,
        ),
    )

    result = await agent.execute(
        {
            "id": "a1",
            "objective": (
                "Perform a risk assessment covering market volatility, supply chain, "
                "regulatory compliance, and cybersecurity. For each risk, analyze severity "
                "and propose mitigations. Provide an executive summary."
            ),
        }
    )
    print(result.output)

    # Check token usage
    usage = agent.last_usage
    print(f"\nTotal tokens: {usage.total.total_tokens}")
    print(f"LLM calls: {usage.call_count}")
    print(usage.display())

    if result.context_telemetry:
        print(f"Peak utilization: {result.context_telemetry.peak_utilization:.1%}")

asyncio.run(main())
```

## What happens under the hood

1. **Decomposition** — The agent breaks "risk assessment" into subtasks (one per risk factor)
2. **Execution** — Each subtask calls `analyze_risk` and `propose_mitigation` tools
3. **Critic** — An independent verification pass checks if the assessment is comprehensive
4. **Refiner** — If the Critic finds gaps, the Refiner corrects them
5. **Synthesis** — A final LLM call (without tools) produces the full deliverable (v0.7.6)
6. **Final output** — The verified, complete assessment is returned

## With Gemini

The same code works with Gemini — just swap the LLM:

```python
from nucleusiq_gemini import BaseGemini

agent = Agent(
    name="risk-analyst",
    prompt=ZeroShotPrompt().configure(
        system="You are a thorough risk analyst...",
    ),
    llm=BaseGemini(model_name="gemini-2.5-pro"),
    # ... same tools and config
)
```

## With context management

*New in v0.7.6*

For long-running autonomous tasks, add context management:

```python
from nucleusiq.agents.context import ContextConfig, ContextStrategy

config = AgentConfig(
    execution_mode=ExecutionMode.AUTONOMOUS,
    require_quality_check=True,
    max_iterations=5,
    context=ContextConfig(
        optimal_budget=40_000,
        strategy=ContextStrategy.PROGRESSIVE,
    ),
)
```

## See also

- [Execution modes](../execution-modes.md) — Direct vs Standard vs Autonomous
- [Gemini quickstart](gemini-quickstart.md) — Autonomous mode with Gemini
- [Context management](../context-management.md) — Context window management guide
- [Production path](../learn/production-path.md) — When to use Autonomous mode
