# Native server tools

!!! abstract "What this page covers"

    A **native server tool** is a tool that runs **inside the LLM provider's infrastructure** — you declare it, the provider invokes it, and the result is returned inline with the assistant's response. You never execute the tool yourself.

    NucleusIQ surfaces these uniformly across providers via the **`ServerToolCall`** model and emits a **`ToolCallRecord(executed_by="provider")`** entry on the tracer for every server-side invocation — so observability, cost, and audit trails look the same whether the tool ran in your process or on Anthropic / OpenAI / Google / Groq servers.

## Local vs server tools — at a glance

| Aspect | Local tool (`@tool`, `MCPTool`, …) | Native server tool |
| --- | --- | --- |
| Where it runs | **Your process** | **Provider's infra** |
| Who triggers execution | NucleusIQ agent loop | The provider, mid-response |
| Sandboxing | Yours to enforce | Provided by the vendor |
| Cost model | Your compute + LLM tokens | LLM tokens (often bundled premium) |
| `ToolCallRecord.executed_by` | `"local"` | `"provider"` |

!!! tip "One signal, all providers"

    A single query against `result.tool_calls` lets you split your bill / latency / failure modes between locally-run and provider-run tools, regardless of which model the agent used:

    ```python
    local    = [tc for tc in result.tool_calls if tc.executed_by == "local"]
    provider = [tc for tc in result.tool_calls if tc.executed_by == "provider"]
    ```

## Supported native tools — by provider

### Anthropic (`nucleusiq-anthropic` 0.2.0)

`AnthropicTool` factory in `nucleusiq_anthropic`:

| Tool | Factory | Dated wire type | `anthropic-beta` header |
| --- | --- | --- | --- |
| `web_search` | `AnthropicTool.web_search(max_uses=2)` | `web_search_20250305` | _(none required)_ |
| `web_fetch` | `AnthropicTool.web_fetch(citations=True, max_content_tokens=4000)` | `web_fetch_20250910` | `web-fetch-2025-09-10` (auto-injected) |
| `code_execution` | `AnthropicTool.code_execution()` | `code_execution_20250522` | `code-execution-2025-05-22` (auto-injected) |

```python
from nucleusiq_anthropic import AnthropicTool, BaseAnthropic

llm = BaseAnthropic(model_name="claude-sonnet-4-5-20250929", async_mode=True)
result = await llm.call(
    model="claude-sonnet-4-5-20250929",
    messages=[{"role": "user", "content": (
        "Use web_search to find current Tokyo population, then use "
        "code_execution to compute its square root.")
    }],
    tools=[
        AnthropicTool.web_search(max_uses=2),
        AnthropicTool.code_execution(),
    ],
    max_output_tokens=1024,
)

for stc in result.server_tool_calls:
    print(stc.name, stc.id, stc.result)
```

!!! warning "Phase B model required"

    Native Anthropic tools require **Claude Sonnet 4 / Opus 4 / 3.7-Sonnet** or newer. If you see `404 model_not_found`, override the model with `ANTHROPIC_PHASE_B_MODEL=<id>` after running `examples/agents/09_anthropic_list_models.py` to discover valid ids on your key.

### OpenAI (`nucleusiq-openai` 0.7.0)

OpenAI Responses-API output items are normalised into `_LLMResponse.server_tool_calls`:

| Wire type | Surfaces as `ServerToolCall.name` |
| --- | --- |
| `web_search_call` | `web_search` |
| `code_interpreter_call` | `code_interpreter` |
| `file_search_call` | `file_search` |
| `computer_use_call` | `computer_use` |
| `image_generation_call` | `image_generation` |

### Gemini (`nucleusiq-gemini` 0.3.0)

Gemini emits `executable_code` + `code_execution_result` parts (paired into a single record) and `grounding_metadata` on candidates (surfaces as `google_search`):

| Wire feature | Surfaces as `ServerToolCall.name` |
| --- | --- |
| `executable_code` + `code_execution_result` | `code_execution` |
| `grounding_metadata` (Google Search grounding) | `google_search` |

### Groq (`nucleusiq-groq` 0.1.0)

Groq's `message.executed_tools` field is parsed into `GroqLLMResponse.server_tool_calls` (emission stub today — full Phase B hosted tools land in `nucleusiq-groq 0.2.x`).

## How it shows up in your tracer

With `enable_tracing=True` (or `ObservabilityConfig(tracing=True)`), `result.tool_calls` contains entries for **both** local and server-executed tools. The `executed_by` field is the only thing you need to filter on:

```python
from collections import Counter

result = await agent.execute(task)

by_origin = Counter(tc.executed_by for tc in result.tool_calls)
print(by_origin)
# Counter({'provider': 3, 'local': 1})

for tc in result.tool_calls:
    badge = "🌐" if tc.executed_by == "provider" else "🏠"
    print(f"  {badge} {tc.tool_name:<20} id={tc.tool_call_id}  duration_ms={tc.duration_ms}")
```

!!! info "How it's wired"

    The core `base_mode.py` agent loop pulls `server_tool_calls` off every `LLMResponse` (or stream COMPLETE metadata) and runs them through `nucleusiq.agents.observability.build_server_tool_call_records()`. That helper accepts any shape — Pydantic models, dicts, or attribute-bearing objects — so every provider's normalizer can keep its native types and still feed the same observability pipeline.

## The `ServerToolCall` shape

Each provider package re-exports its own `ServerToolCall` Pydantic model with a uniform contract:

```python
class ServerToolCall(BaseModel):
    id: str             # provider-side id (e.g. "srvtoolu_01...")
    name: str           # e.g. "web_search", "code_execution"
    input: dict[str, Any]   # arguments the provider sent the tool
    result: Any = None  # decoded result payload (JSON-safe; provider-specific shape)
```

For Anthropic, `result` is the contents of the matching `*_tool_result` block — a `dict` for `code_execution_result` (stdout/stderr/return_code), a `list[dict]` for `web_search_result` items, etc. NucleusIQ runs `_coerce_tool_result_content()` so the result is always JSON-serialisable when the tracer dumps an `AgentResult`.

## See also

- [Anthropic provider guide](anthropic-provider.md) — full surface for Claude
- [Prompt caching](prompt-caching.md) — pair with `cache_system=True` for repeat-prompt workflows
- [Extended thinking](extended-thinking.md) — reasoning budgets
- [Observability](../observability/index.md) — `executed_by`, `LLMCallRecord` enrichment
