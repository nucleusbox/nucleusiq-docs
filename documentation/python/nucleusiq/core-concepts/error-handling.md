# Error handling

NucleusIQ provides a framework-level error taxonomy so you can write **provider-agnostic, domain-specific** error handling code. Whether you use OpenAI, Gemini, or any future provider — and whether an error originates in an LLM call, a tool, an agent, or the prompt layer — the same exception families apply.

As of **v0.7.2**, the framework ships 10 exception families covering every major subsystem.

---

## Error hierarchy

Every exception inherits from `NucleusIQError`. The full tree:

```
NucleusIQError                          # Root exception
├── LLMError                            # LLM provider errors
│   ├── AuthenticationError             # Invalid API key (401)
│   ├── PermissionDeniedError           # Insufficient permissions (403)
│   ├── RateLimitError                  # Too many requests (429)
│   ├── InvalidRequestError             # Malformed request (400)
│   ├── ModelNotFoundError              # Model not found (404)
│   ├── ContentFilterError              # Content blocked by safety filter
│   ├── ContextLengthError              # Input exceeds context window
│   ├── ProviderServerError             # Provider 5xx errors
│   ├── ProviderConnectionError         # Network failures
│   └── ProviderError                   # Other provider errors
├── ToolError                           # Tool execution errors
│   ├── ToolExecutionError              # Tool raised during execution
│   ├── ToolTimeoutError                # Tool execution timed out
│   ├── ToolValidationError             # Invalid tool args / schema
│   ├── ToolPermissionError             # Tool blocked by policy
│   └── ToolNotFoundError               # Tool not registered
├── AgentError                          # Agent lifecycle errors
│   ├── AgentConfigError                # Invalid agent configuration
│   ├── AgentExecutionError             # Execution failed
│   └── AgentTimeoutError               # Execution timed out
├── PromptError                         # Prompt construction errors
│   ├── PromptTemplateError             # Template rendering failed
│   └── PromptConfigError               # Invalid prompt config
├── NucleusMemoryError                  # Memory errors (named to avoid shadowing Python's MemoryError)
│   ├── MemoryStorageError              # Failed to persist memory
│   ├── MemoryRetrievalError            # Failed to retrieve memory
│   ├── MemoryCapacityError             # Memory store at capacity
│   └── MemorySerializationError        # Serialization / deserialization failed
├── AttachmentError                     # Attachment processing errors
│   ├── AttachmentProcessingError       # Failed to process attachment
│   ├── AttachmentUnsupportedError      # Attachment type not supported
│   └── AttachmentSizeError             # Attachment exceeds size limit
├── StreamingError                      # Streaming errors
│   ├── StreamConnectionError           # Stream connection lost
│   └── StreamParseError                # Failed to parse stream chunk
├── PluginError                         # Plugin lifecycle errors
│   ├── PluginExecutionError            # Plugin execution failed
│   └── PluginHalt                      # Plugin requests execution halt
├── StructuredOutputError               # Structured output errors
│   ├── SchemaValidationError           # Output does not match schema
│   └── SchemaParseError                # Failed to parse LLM output
└── WorkspaceSecurityError              # File / workspace security violations
```

---

## Error attributes

Every exception carries structured context so you can log, alert, or branch on specific fields without parsing message strings.

### Common (all exceptions)

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | `str` | Human-readable error description |

### `LLMError` family

| Attribute | Type | Description |
|-----------|------|-------------|
| `provider` | `str` | Which provider raised it (`"openai"`, `"gemini"`, …) |
| `status_code` | `int \| None` | HTTP status code if applicable |
| `original_error` | `BaseException \| None` | The original SDK exception |

### `ToolError` family

| Attribute | Type | Description |
|-----------|------|-------------|
| `tool_name` | `str` | Name of the tool that failed |

### `AgentError` family

| Attribute | Type | Description |
|-----------|------|-------------|
| `mode` | `str \| None` | Agent mode that was active (`"react"`, `"plan"`, …) |

### `PromptError` family

| Attribute | Type | Description |
|-----------|------|-------------|
| `template_name` | `str \| None` | Name/path of the prompt template that failed |

---

## Import paths

Exceptions can be imported from their domain-specific module **or** from the top-level `nucleusiq.errors` convenience module.

### Domain-specific imports

```python
# LLM errors (also available from nucleusiq.llms.errors)
from nucleusiq.llms.errors import (
    LLMError,
    AuthenticationError,
    RateLimitError,
    ContextLengthError,
    ProviderServerError,
)

# Tool errors
from nucleusiq.tools.errors import (
    ToolError,
    ToolExecutionError,
    ToolTimeoutError,
    ToolValidationError,
    ToolPermissionError,
    ToolNotFoundError,
)

# Agent errors
from nucleusiq.agents.errors import (
    AgentError,
    AgentConfigError,
    AgentExecutionError,
    AgentTimeoutError,
)
```

### Top-level convenience import

```python
from nucleusiq.errors import (
    NucleusIQError,
    LLMError,
    ToolError,
    AgentError,
    PromptError,
    NucleusMemoryError,
    AttachmentError,
    StreamingError,
    PluginError,
    StructuredOutputError,
    WorkspaceSecurityError,
)
```

All leaf exceptions are also re-exported from `nucleusiq.errors`, so you can do:

```python
from nucleusiq.errors import RateLimitError, ToolExecutionError, SchemaValidationError
```

---

## Usage examples

### 1. Catching specific LLM errors

```python
from nucleusiq.llms.errors import (
    AuthenticationError,
    RateLimitError,
    ContextLengthError,
    ProviderServerError,
    LLMError,
)

try:
    result = await agent.execute({"id": "e1", "objective": "Hello"})

except AuthenticationError as e:
    print(f"Bad API key for {e.provider}")

except RateLimitError as e:
    print(f"Rate limited (status {e.status_code}), implement backoff")

except ContextLengthError as e:
    print(f"Input too long for model — consider truncating or splitting")

except ProviderServerError:
    print("Provider is having issues, retry later")

except LLMError as e:
    print(f"Unexpected LLM error from {e.provider}: {e}")
```

### 2. Catching tool errors in agent execution

When an agent calls a tool and the tool fails, the framework wraps the failure in a `ToolError` subclass:

```python
from nucleusiq.tools.errors import (
    ToolExecutionError,
    ToolTimeoutError,
    ToolValidationError,
    ToolNotFoundError,
    ToolPermissionError,
    ToolError,
)

try:
    result = await agent.execute(task)

except ToolValidationError as e:
    # The LLM generated invalid arguments for the tool
    print(f"Tool '{e.tool_name}' received invalid arguments: {e}")

except ToolTimeoutError as e:
    print(f"Tool '{e.tool_name}' timed out — increase timeout or simplify input")

except ToolPermissionError as e:
    print(f"Tool '{e.tool_name}' blocked by security policy")

except ToolNotFoundError as e:
    print(f"Tool '{e.tool_name}' is not registered with the agent")

except ToolExecutionError as e:
    print(f"Tool '{e.tool_name}' raised an error during execution: {e}")

except ToolError as e:
    # Catch-all for any tool-related error
    print(f"Tool error ({e.tool_name}): {e}")
```

### 3. Catching agent lifecycle errors

Agent-level exceptions surface configuration and execution problems:

```python
from nucleusiq.agents.errors import (
    AgentConfigError,
    AgentExecutionError,
    AgentTimeoutError,
    AgentError,
)

try:
    result = await agent.execute(task)

except AgentConfigError as e:
    # Raised before execution starts — fix your agent setup
    print(f"Agent config invalid (mode={e.mode}): {e}")

except AgentTimeoutError as e:
    print(f"Agent timed out in '{e.mode}' mode — raise max_steps or simplify task")

except AgentExecutionError as e:
    print(f"Agent execution failed in '{e.mode}' mode: {e}")

except AgentError as e:
    print(f"Agent error: {e}")
```

### 4. Catching structured output errors

When the LLM output does not match your Pydantic schema:

```python
from nucleusiq.errors import SchemaValidationError, SchemaParseError, StructuredOutputError

try:
    result = await agent.execute(task)

except SchemaParseError as e:
    # LLM returned something that isn't parseable JSON / the expected format
    print(f"Could not parse LLM output into structured format: {e}")

except SchemaValidationError as e:
    # Parsed successfully but the data failed Pydantic validation
    print(f"Output failed schema validation: {e}")

except StructuredOutputError as e:
    print(f"Structured output error: {e}")
```

### 5. Catching streaming errors

```python
from nucleusiq.errors import StreamConnectionError, StreamParseError, StreamingError

try:
    async for chunk in agent.execute_stream(task):
        print(chunk, end="", flush=True)

except StreamConnectionError as e:
    print(f"\nStream connection lost: {e}")

except StreamParseError as e:
    print(f"\nFailed to parse stream chunk: {e}")

except StreamingError as e:
    print(f"\nStreaming error: {e}")
```

### 6. Generic catch-all with `NucleusIQError`

For top-level error boundaries where you want to catch **everything** the framework can throw:

```python
from nucleusiq.errors import NucleusIQError

try:
    result = await agent.execute(task)
except NucleusIQError as e:
    log.error(f"NucleusIQ error: {type(e).__name__}: {e}")
    # Still falls through for non-NucleusIQ errors (KeyError, etc.)
```

### 7. Provider-agnostic handling

The same error handling code works regardless of which LLM provider you use:

```python
from nucleusiq.llms.errors import RateLimitError, LLMError

try:
    result = await agent.execute({"id": "e2", "objective": "Analyze this data"})

except RateLimitError as e:
    # e.provider tells you which one hit the limit
    print(f"{e.provider} rate limit hit (status {e.status_code})")

except LLMError as e:
    # Works identically for openai, gemini, or any future provider
    log.warning(f"provider={e.provider} status={e.status_code} error={e}")
    if e.original_error:
        log.debug(f"Original: {type(e.original_error).__name__}")
```

### 8. Combining multiple families

Real-world agents can fail in any subsystem. A production handler typically layers specifics over a broad catch-all:

```python
from nucleusiq.errors import NucleusIQError
from nucleusiq.llms.errors import RateLimitError, AuthenticationError
from nucleusiq.tools.errors import ToolTimeoutError, ToolValidationError
from nucleusiq.agents.errors import AgentTimeoutError

try:
    result = await agent.execute(task)

except AuthenticationError as e:
    notify_ops(f"API key invalid for {e.provider}")

except RateLimitError as e:
    await backoff_and_retry(e)

except ToolTimeoutError as e:
    log.warning(f"Tool '{e.tool_name}' timed out, skipping")
    result = fallback_result()

except ToolValidationError as e:
    log.error(f"Tool '{e.tool_name}' got bad args — possible prompt issue")

except AgentTimeoutError as e:
    log.error(f"Agent hit time limit in '{e.mode}' mode")

except NucleusIQError as e:
    log.error(f"Unhandled framework error: {type(e).__name__}: {e}")
```

---

## Built-in retry

Both OpenAI and Gemini providers include automatic retry with exponential backoff for transient errors:

| Error type | Behavior |
|-----------|----------|
| Rate limits (429) | Retry up to 3 times with exponential backoff |
| Server errors (5xx) | Retry up to 3 times with exponential backoff |
| Connection errors | Retry up to 3 times with exponential backoff |
| Auth errors (401/403) | Fail immediately (no retry) |
| Bad requests (400) | Fail immediately (no retry) |
| Model not found (404) | Fail immediately (no retry) |
| Context length exceeded | Fail immediately (no retry) |
| Content filtered | Fail immediately (no retry) |

If retries are exhausted, the corresponding framework exception is raised with full context (`provider`, `status_code`, `original_error`).

---

## Design philosophy

### Typed exceptions everywhere

Every production code path in NucleusIQ raises **typed exceptions** from the hierarchy above. You will never see a raw `ValueError` or `RuntimeError` escape the framework boundary. This means:

- `except NucleusIQError` is a reliable catch-all for framework errors.
- You can always narrow to a specific family (`LLMError`, `ToolError`, …) or a leaf type (`RateLimitError`, `ToolTimeoutError`, …).

### Pydantic validators are the one exception

Pydantic model validators still raise `ValueError` and `ValidationError` by design — these are input validation errors at the schema level, not framework execution errors. If you pass bad data to a Pydantic model (e.g., an invalid agent config dict), expect standard Pydantic exceptions.

### Automatic provider error mapping

When an LLM provider SDK raises its own exception (e.g., `openai.RateLimitError`, `google.api_core.exceptions.ResourceExhausted`), the framework automatically maps it to the correct `LLMError` subclass. You never need to import or handle provider-specific exception types.

### Rich context for logging and alerting

Every exception carries enough context to build meaningful log entries and alerts without re-parsing the message string:

```python
except LLMError as e:
    log.error(
        "llm_error",
        provider=e.provider,
        status_code=e.status_code,
        error_type=type(e).__name__,
        message=str(e),
    )
```

```python
except ToolError as e:
    log.error(
        "tool_error",
        tool_name=e.tool_name,
        error_type=type(e).__name__,
        message=str(e),
    )
```

This structured context makes it straightforward to build dashboards, set up PagerDuty alerts on specific error types, or filter logs by provider or tool name.

---

## See also

- [Gemini provider](../guides/gemini-provider.md) — Gemini-specific error mapping
- [OpenAI provider](../guides/openai-provider.md) — OpenAI-specific error mapping
- [Providers](../providers.md) — Provider architecture
- [Tools](../tools.md) — Tool registration and execution
- [Agents](../agents.md) — Agent modes and lifecycle
- [Structured output](../structured-output.md) — Schema-based output parsing
