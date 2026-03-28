# OpenAI Provider — User-Facing Design Guide

> How NucleusIQ keeps Agent creation simple while giving power users full control over 40+ OpenAI parameters.

> **Last updated:** 10 March 2026

---

## Implementation Status

| Feature | Status | Files |
|---------|--------|-------|
| Three-layer design (Agent / LLM Config / Direct) | **DONE** | `agent.py`, `base.py` |
| Type-safe `LLMParams` base class | **DONE** | `core/llms/llm_params.py` |
| Type-safe `OpenAILLMParams` subclass | **DONE** | `nucleusiq_openai/llm_params.py` |
| `AgentConfig.llm_params` (typed field) | **DONE** | `agent_config.py` |
| `Agent.execute(llm_params=...)` per-task overrides | **DONE** | `agent.py` |
| Merge chain (LLM < AgentConfig < per-execute) | **DONE** | `agent.py` -> `_resolve_llm_params()` |
| All 5 `llm.call()` sites wired with overrides | **DONE** | `agent.py` |
| All Chat Completions + Responses API params in `call()` | **DONE** | `base.py` |
| Multimodal attachments in task | **DONE** | Framework-level `Task.attachments` (7 types) + OpenAI native processing (v0.4.0) |
| **Streaming via `execute_stream()`** | **DONE** | `agent.py`, `base_mode.py`, `stream_adapters.py` |
| **Streaming via `call_stream()`** | **DONE** | `base_llm.py`, `nb_openai/base.py` |
| **Usage / token telemetry** | **DONE** | `_shared/response_models.py` |
| Platform APIs (Embeddings, Audio, Files, Realtime, Fine-tuning, Batch) | **NOT YET** | See full matrix in gap analysis |

---

## Readiness Snapshot

### What is solid today
- Text + tool orchestration with Chat Completions and Responses API
- Native tool routing (`web_search`, `code_interpreter`, `file_search`, `image_generation`, `mcp`, `computer_use`)
- Structured output parsing and typed internal message models
- Type-safe parameter merge chain (`BaseOpenAI` defaults < `AgentConfig.llm_params` < `execute(..., llm_params=...)`)
- **End-to-end streaming** (all 3 execution modes, both OpenAI backends)
- **Usage telemetry** (prompt tokens, completion tokens, reasoning tokens)

### What shipped in v0.4.0
- Framework-level `Task.attachments` for multimodal inputs (7 attachment types)
- OpenAI native attachment processing (server-side PDF/XLSX/CSV)
- 4 built-in file tools (FileReadTool, FileSearchTool, DirectoryListTool, FileExtractTool)
- AttachmentGuardPlugin for policy-based attachment validation
- File-aware memory (metadata in all 5 strategies)
- UsageTracker with CallPurpose enum

### What is intentionally out of scope (for now)
- Dedicated Embeddings API class
- Audio endpoint clients (STT/TTS/translations)
- Files and Vector Store management clients
- Realtime, Batch, Fine-tuning, Moderation endpoint wrappers

---

## The Problem

OpenAI's Chat Completions API has **25+ parameters**. The Responses API has **20+ parameters**. Exposing all of them to someone who just wants to create an Agent would be overwhelming and a terrible user experience.

## The Solution: Three Layers

NucleusIQ uses a **layered design** where each layer adds more control:

```
Layer 1: Agent (Simple)        — 90% of users stop here
Layer 2: LLM Config (Medium)   — Power users who need tuning
Layer 3: Direct API (Advanced)  — Full control, raw access
```

---

## How It Works Today (Inside the Agent)

When a user calls `agent.execute(task)`, here is exactly what happens internally:

```
User
  │
  ▼
agent.execute({"id": "q1", "objective": "What is GDP of Japan?"})
  │
  ├─ 1. Agent._build_messages(task)
  │     → Combines prompt.system + prompt.user + task.objective
  │     → Returns: [{"role": "system", ...}, {"role": "user", ...}]
  │
  ├─ 2. Agent converts tools → tool_specs
  │     → llm.convert_tool_specs(self.tools)
  │
  ├─ 3. Agent calls llm.call()     ◄── THIS IS WHERE PARAMS GO
  │     │
  │     │  call_kwargs = {
  │     │      "model":      llm.model_name,
  │     │      "messages":   messages,
  │     │      "tools":      tool_specs,
  │     │      "max_output_tokens": config.llm_max_output_tokens,
  │     │  }
  │     │  response = await llm.call(**call_kwargs)
  │     │
  │     ▼
  │  BaseOpenAI.call() uses DEFAULTS from __init__:
  │     temperature  → self.temperature (0.7)
  │     top_p        → 1.0 (hardcoded default)
  │     freq_penalty → 0.0 (hardcoded default)
  │     stream       → False (hardcoded default)
  │
  ├─ 4. If LLM returns tool_calls → Executor runs tools → loop back to step 3
  │
  └─ 5. Return final text response
```

---

## Design: How Configuration Flows (IMPLEMENTED)

### The Configuration Merge Chain

```
Priority (highest wins):
  ┌─────────────────────────────────────────────┐
  │ 3. Per-execute overrides (task-level)        │  ← Highest priority
  │    agent.execute(task, llm_params=OpenAILLMParams(...)) │
  ├─────────────────────────────────────────────┤
  │ 2. AgentConfig.llm_params (agent-level)      │  ← Agent-wide defaults
  │    AgentConfig(llm_params=OpenAILLMParams(...)) │
  ├─────────────────────────────────────────────┤
  │ 1. BaseOpenAI.__init__ (LLM-level)           │  ← Global defaults
  │    BaseOpenAI(temperature=0.3, seed=42)      │
  └─────────────────────────────────────────────┘
```

Each layer **merges** with the one below it. Per-execute overrides beat AgentConfig, which beats LLM defaults.

---

## Concrete Examples: Every User Level

### Example 1: Beginner — "Just make it work" (5 lines) — WORKS TODAY

```python
from nucleusiq.agents import Agent
from nucleusiq.prompts.factory import PromptFactory, PromptTechnique
from nucleusiq_openai import BaseOpenAI, OpenAITool

llm = BaseOpenAI(model_name="gpt-4o")

agent = Agent(
    name="Researcher",
    role="Research Assistant",
    objective="Find information using web search.",
    llm=llm,
    prompt=PromptFactory.create_prompt(PromptTechnique.ZERO_SHOT).configure(
        system="You are a helpful assistant.",
        user="Answer questions accurately.",
    ),
    tools=[OpenAITool.web_search()],
)

result = await agent.execute({"id": "q1", "objective": "What is the GDP of Japan?"})
```

**What happens behind the scenes:**
- `temperature=0.7`, `max_tokens=2048`, `top_p=1.0` (all defaults)
- Auto-routes to Responses API (because `web_search` is native)
- Retries on rate limits
- User sees none of this

---

### Example 2: Power User — "I need cost control + determinism" — WORKS TODAY

```python
llm = BaseOpenAI(
    model_name="o3",
    temperature=0.2,
    seed=42,
    service_tier="flex",
    reasoning_effort="low",
)

agent = Agent(
    name="CostEfficientBot",
    role="Analyst",
    objective="Analyze data efficiently.",
    llm=llm,
    prompt=prompt,
    tools=[OpenAITool.code_interpreter()],
)

result = await agent.execute({"id": "q1", "objective": "Calculate quarterly revenue."})
```

---

### Example 3: Different Settings Per Agent (Same LLM, Different Config) — WORKS TODAY

```python
llm = BaseOpenAI(model_name="gpt-4o", temperature=0.5)
from nucleusiq_openai import OpenAILLMParams

# Agent A: Creative writing — override temperature higher
agent_writer = Agent(
    name="Writer",
    role="Creative Writer",
    objective="Write creative content.",
    llm=llm,
    prompt=writer_prompt,
    config=AgentConfig(
        llm_max_output_tokens=4096,
        llm_params=OpenAILLMParams(
            temperature=0.9,
            presence_penalty=0.6,
        ),
    ),
)

# Agent B: Data analysis — override temperature lower
agent_analyst = Agent(
    name="Analyst",
    role="Data Analyst",
    objective="Analyze data precisely.",
    llm=llm,
    prompt=analyst_prompt,
    tools=[OpenAITool.code_interpreter()],
    config=AgentConfig(
        llm_max_output_tokens=2048,
        llm_params=OpenAILLMParams(
            temperature=0.1,
            seed=42,
        ),
    ),
)

# Writer uses temp=0.9, Analyst uses temp=0.1 — same underlying LLM
await agent_writer.execute({"id": "w1", "objective": "Write a poem about AI."})
await agent_analyst.execute({"id": "a1", "objective": "Sum column B of this data."})
```

---

### Example 4: Per-Task Overrides — "This specific task needs more reasoning" — WORKS TODAY

```python
agent = Agent(
    name="FlexBot",
    llm=BaseOpenAI(model_name="o3", reasoning_effort="low"),
    ...
)

# Normal task — uses default low reasoning
await agent.execute({"id": "q1", "objective": "What is 2+2?"})

# Complex task — override to high reasoning just for this call
await agent.execute(
    {"id": "q2", "objective": "Prove the Riemann hypothesis."},
    llm_params=OpenAILLMParams(reasoning_effort="high", max_tokens=8192),
)

# Back to low reasoning for the next task
await agent.execute({"id": "q3", "objective": "Summarize this text."})
```

---

### Example 5: Streaming — "Show results as they come" — WORKS TODAY (v0.3.0)

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.streaming.events import StreamEventType
from nucleusiq_openai import BaseOpenAI, OpenAITool

llm = BaseOpenAI(model_name="gpt-4o")

agent = Agent(
    name="StreamBot",
    role="Assistant",
    objective="Help users with real-time responses.",
    llm=llm,
    prompt=prompt,
    tools=[OpenAITool.web_search()],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)

# Streaming — async generator of StreamEvent objects
async for event in agent.execute_stream({"id": "s1", "objective": "Write a long essay on AI."}):
    match event.type:
        case StreamEventType.TOKEN:
            print(event.token, end="", flush=True)
        case StreamEventType.TOOL_CALL_START:
            print(f"\n[Calling {event.tool_name}...]")
        case StreamEventType.TOOL_CALL_END:
            print(f"[Result from {event.tool_name}]")
        case StreamEventType.THINKING:
            print(f"... {event.message}")
        case StreamEventType.COMPLETE:
            full_text = event.content
            print(f"\n\nDone! ({len(full_text)} chars)")
```

**How streaming works internally:**

```
agent.execute_stream(task)
    │
    ├─ Same lifecycle as execute(): resolve mode, params, plugins
    │
    ▼
mode.run_stream(agent, task)
    │
    ├─ build_messages + build_call_kwargs
    │
    ▼
call_llm_stream(agent, kwargs)
    │
    ├─ before_model hooks
    │
    ▼
llm.call_stream(**kwargs)
    │
    ├─ yield StreamEvent.TOKEN (content chunks)
    ├─ accumulate tool_calls across chunks
    │
    ▼
Stream done — tool_calls detected?
    │
    ├─ YES → yield TOOL_CALL_START → Execute → yield TOOL_CALL_END → loop back
    └─ NO  → yield COMPLETE (final answer)
```

**StreamEvent types:**

| Event Type | When | Useful Fields |
|---|---|---|
| `TOKEN` | Each content chunk | `event.token` |
| `TOOL_CALL_START` | Tool execution begins | `event.tool_name`, `event.tool_args` |
| `TOOL_CALL_END` | Tool execution completes | `event.tool_name`, `event.tool_result` |
| `LLM_CALL_START` | LLM call begins | `event.call_count` |
| `LLM_CALL_END` | LLM call completes | `event.call_count` |
| `THINKING` | Internal processing step | `event.message` |
| `COMPLETE` | Final result ready | `event.content`, `event.metadata` |
| `ERROR` | Error occurred | `event.message` |

**All 3 modes support streaming:** Direct, Standard, and Autonomous.

---

### Example 6: Multimodal — "Analyze this image" — DONE (v0.4.0)

Framework-level `Task.attachments` is now fully implemented:

```python
from nucleusiq.agents.task import Task
from nucleusiq.agents.attachments import Attachment, AttachmentType

task = Task(
    id="img-1",
    objective="What is in this image?",
    attachments=[
        Attachment(type=AttachmentType.IMAGE_URL, content="https://example.com/photo.jpg"),
    ],
)
result = await agent.execute(task)
```

All 7 attachment types are supported: `TEXT`, `PDF`, `IMAGE_URL`, `IMAGE_BASE64`, `FILE_BYTES`, `FILE_BASE64`, `FILE_URL`.

---

### Example 7: Direct LLM Access — "I don't need an Agent" — WORKS TODAY

For users who want full control without an Agent wrapper:

```python
from nucleusiq_openai import BaseOpenAI

llm = BaseOpenAI(model_name="gpt-4o")

# Direct call with ALL parameters
result = await llm.call(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": [
            {"type": "text", "text": "What's in this image?"},
            {"type": "image_url", "image_url": {"url": "https://...", "detail": "high"}},
        ]},
    ],
    temperature=0.2,
    max_tokens=4096,
    seed=42,
    reasoning_effort="high",
    service_tier="priority",
    n=3,
    logprobs=True,
    modalities=["text", "audio"],
    audio={"voice": "alloy", "format": "mp3"},
    response_format=MyPydanticModel,
)

# Or raw Responses API
response = await llm.responses_call(
    model="gpt-4o",
    input="Search for quantum computing breakthroughs",
    tools=[{"type": "web_search_preview"}],
    include=["output[*].web_search_call.results"],
    reasoning={"effort": "high", "summary": "auto"},
    truncation="auto",
    **any_future_params,
)

# Direct streaming (provider-level)
async for event in llm.call_stream(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a poem"}],
):
    if event.type == StreamEventType.TOKEN:
        print(event.token, end="")
```

---

## Type-Safe LLM Parameters (LLMParams) — IMPLEMENTED

The `llm_params` field is NOT a raw `Dict[str, Any]`. It is a **typed Pydantic model** that provides:
- IDE autocomplete for all parameter names
- Value validation (wrong types or invalid values are caught immediately)
- Provider-specific parameters via inheritance

### Architecture: Base + Provider-Specific

```
nucleusiq (core)                    nucleusiq_openai (provider)
┌──────────────────────┐           ┌────────────────────────────────┐
│  LLMParams (base)    │           │  OpenAILLMParams(LLMParams)    │
│                      │           │                                │
│  temperature: float  │  extends  │  reasoning_effort: Literal     │
│  max_tokens: int     │ ────────► │  service_tier: Literal         │
│  top_p: float        │           │  modalities: List[Literal]     │
│  seed: int           │           │  audio: AudioOutputConfig      │
│  stream: bool        │           │  parallel_tool_calls: bool     │
│  stop: List[str]     │           │  logprobs: bool                │
│  n: int              │           │  top_logprobs: int             │
│  ...common params    │           │  metadata: Dict                │
└──────────────────────┘           │  store: bool                   │
                                   │  truncation: Literal           │
       Future providers:           │  ...OpenAI-specific            │
       GeminiLLMParams             └────────────────────────────────┘
       OllamaLLMParams
```

### What Happens With a Typo

```python
from nucleusiq_openai import OpenAILLMParams

# TYPO: "temperture" instead of "temperature"
params = OpenAILLMParams(temperture=0.3)
# ❌ ValidationError: Extra inputs are not permitted
#    'temperture' → Did you mean 'temperature'?

# WRONG VALUE: reasoning_effort must be one of the Literal values
params = OpenAILLMParams(reasoning_effort="super_high")
# ❌ ValidationError: Input should be 'none', 'minimal', 'low',
#    'medium', 'high', or 'xhigh'

# CORRECT: IDE autocomplete guides you to the right values
params = OpenAILLMParams(
    temperature=0.3,
    reasoning_effort="high",
    service_tier="flex",
    seed=42,
)
```

---

## Complete Configuration Reference

### Where Each Parameter Lives

| Parameter | BaseOpenAI init | AgentConfig.llm_params | Per-execute llm_params | llm.call() direct |
|---|---|---|---|---|
| `temperature` | Default for all calls | Override per agent | Override per task | Full control |
| `max_output_tokens` | - | `llm_max_output_tokens` field | Override per task | Full control |
| `seed` | Default for all calls | Override per agent | Override per task | Full control |
| `reasoning_effort` | Default for all calls | Override per agent | Override per task | Full control |
| `service_tier` | Default for all calls | Override per agent | Override per task | Full control |
| `top_p` | - | Override per agent | Override per task | Full control |
| `frequency_penalty` | - | Override per agent | Override per task | Full control |
| `presence_penalty` | - | Override per agent | Override per task | Full control |
| `n` | - | - | Override per task | Full control |
| `logprobs` | - | - | - | Full control |
| `modalities` | - | Override per agent | Override per task | Full control |
| `audio` | - | Override per agent | Override per task | Full control |
| `stream` | - | Override per agent | - | Full control |
| `parallel_tool_calls` | - | Override per agent | Override per task | Full control |
| `metadata` | Default for all calls | Override per agent | Override per task | Full control |
| `attachments` (multimodal) | - | - | In task dict (v0.4.0) | Build manually |

---

## Design Principles

### 1. Progressive Disclosure
Users only see what they need. A beginner creates an Agent with 5 lines. An advanced user adds `llm_params` to `AgentConfig`. A power user calls `llm.call()` directly.

### 2. Sensible Defaults
Every parameter has a default that works for 90% of cases. Users override only what they need.

### 3. Merge Chain (LLM < AgentConfig < Per-Execute)
Settings merge in a clear priority order. Per-execute overrides beat AgentConfig, which beats LLM init defaults.

### 4. Agent Stays Clean
`Agent()` and `agent.execute()` never expose raw LLM parameters directly. The `llm_params` dict is an opt-in escape hatch that passes through transparently.

### 5. Don't Break Existing Code
All changes are additive. `llm_params` defaults to `None`. Existing code works identically. `execute_stream()` is a new method alongside the existing `execute()`.

### 6. Provider Isolation
The framework (`nucleusiq` core) defines abstract contracts (`BaseLLM`, `StreamEvent`, `BaseTool`). Providers (`nucleusiq-openai`, future Gemini/Ollama) implement those contracts. No provider-specific types leak into core.

---

## Platform APIs — Separate Focused Classes — NOT YET IMPLEMENTED

Platform APIs (embeddings, audio, files) are **not part of the LLM**. They will be standalone classes (GAPs 6-8):

```python
from nucleusiq_openai.embeddings import OpenAIEmbeddings
from nucleusiq_openai.audio import OpenAIAudio
from nucleusiq_openai.files import OpenAIFiles

# Embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectors = await embeddings.embed(["Hello world", "Goodbye world"])

# Audio
audio = OpenAIAudio()
transcript = await audio.transcribe("meeting.mp3")
speech = await audio.speak("Hello!", voice="nova", format="mp3")

# Files
files = OpenAIFiles()
file_id = await files.upload("report.pdf", purpose="file_search")
await files.delete(file_id)
```

---

## Summary: What Changes for the User

| User Level | What They Do | Capability | Status |
|---|---|---|---|
| Beginner | `Agent(llm=BaseOpenAI("gpt-4o"))` | Nothing changes — just works | **DONE** |
| Tuning | `BaseOpenAI(seed=42, reasoning_effort="low")` | Set LLM-wide defaults at init | **DONE** |
| Per-Agent | `AgentConfig(llm_params=OpenAILLMParams(temperature=0.9))` | Different settings per agent (type-safe) | **DONE** |
| Per-Task | `agent.execute(task, llm_params=OpenAILLMParams(reasoning_effort="high"))` | Override per task (type-safe) | **DONE** |
| **Streaming** | `async for event in agent.execute_stream(task)` | Real-time token-by-token output | **DONE** |
| Multimodal | `Task(attachments=[Attachment(type=..., content=...)])` | Images/files in tasks | **DONE** |
| Direct | `llm.call(...)` or `llm.responses_call(...)` | Full raw API access | **DONE** |
| **Direct Streaming** | `async for event in llm.call_stream(...)` | Provider-level streaming | **DONE** |
