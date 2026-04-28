# File Handling in NucleusIQ

NucleusIQ provides two complementary approaches for working with files:
**Attachments** (file-as-context) and **File Tools** (file-as-workspace).

---

## Decision Flowchart

```
Do you need the LLM to see file content in the prompt?
│
├─ YES ──> Is the file small (< 500 lines / < 100 KB)?
│          ├─ YES ──> Use Attachment (one-shot, full content)
│          └─ NO  ──> Use FileReadTool with line ranges
│
└─ NO  ──> Does the agent need to search/explore files iteratively?
           ├─ YES ──> Use File Tools (FileSearchTool, DirectoryListTool)
           └─ NO  ──> Use Attachment with FILE_URL for server-side processing
```

---

## Approach 1: Attachments (file-as-context)

Attachments embed file content directly into the LLM prompt. The content
is sent once and the LLM sees it in full.

**When to use:**
- Small to medium files (< 100 KB text, images, short PDFs)
- You know which file the LLM needs before execution
- One-shot analysis ("summarize this PDF", "describe this image")

**Supported types:**

| Type | Data format | Description |
|------|-------------|-------------|
| `TEXT` | `str` or `bytes` | Plain text (.txt, .md, .csv, .json, etc.) |
| `PDF` | `bytes` | PDF document (text extraction via pdfplumber) |
| `IMAGE_URL` | `str` (URL) | Remote image for vision |
| `IMAGE_BASE64` | `bytes` or `str` | Local image as base64 |
| `FILE_BYTES` | `bytes` | Raw file bytes (any format) |
| `FILE_BASE64` | `str` (base64) | Pre-encoded base64 file data |
| `FILE_URL` | `str` (URL) | Remote file URL (provider-native) |

**Example:**

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.attachments import Attachment, AttachmentType
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="attachment-summarize",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)

task = Task(
    id="summarize",
    objective="Summarize the key findings in this report",
    attachments=[
        Attachment(
            type=AttachmentType.TEXT,
            data=open("report.txt").read(),
            name="report.txt",
        ),
    ],
)
result = await agent.execute(task)
```

### Provider-native optimisation

When using the OpenAI provider, file attachments (PDF, CSV, XLSX) are
sent to OpenAI's server-side processing automatically. No code changes
needed — the provider override handles the conversion.

```python
# With OpenAI provider, PDFs are processed server-side
task = Task(
    id="pdf-analysis",
    objective="Extract all tables from this PDF",
    attachments=[
        Attachment(
            type=AttachmentType.FILE_URL,
            data="https://example.com/financial-report.pdf",
            name="report.pdf",
        ),
    ],
)
```

---

## Approach 2: File Tools (file-as-workspace)

File tools let the agent interactively explore and read files. The agent
decides which files to open, what to search for, and how much to read.

**When to use:**
- Large files or directories (the agent reads only what it needs)
- Exploratory tasks ("find all revenue figures in the reports folder")
- Multi-step file analysis (search, then read specific sections)

**Available tools:**

| Tool | Description |
|------|-------------|
| `FileReadTool` | Read file content, optional line range |
| `FileSearchTool` | Text/regex search across files |
| `DirectoryListTool` | List directory contents with glob filter |
| `FileExtractTool` | Structured extraction from CSV/JSON |

All tools are sandboxed to a `workspace_root` directory. Path traversal,
symlink escape, and absolute path injection are blocked.

**Example:**

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.builtin import (
    FileReadTool,
    FileSearchTool,
    DirectoryListTool,
    FileExtractTool,
)

agent = Agent(
    name="DataAnalyst",
    prompt=ZeroShotPrompt().configure(
        system="You are a data analyst. Analyze files and extract insights.",
    ),
    llm=llm,
    tools=[
        FileReadTool(workspace_root="./data"),
        FileSearchTool(workspace_root="./data"),
        DirectoryListTool(workspace_root="./data"),
        FileExtractTool(workspace_root="./data"),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)

result = await agent.execute(
    Task(id="t1", objective="Find all revenue figures in the reports")
)
```

---

## Approach 3: Combined (Attachment + Tools)

For advanced scenarios, combine both approaches. Attach a known file for
immediate context, and provide tools for the agent to explore related files.

**When to use:**
- "Summarize this report AND cross-reference with the data directory"
- The agent needs a starting document plus exploration capability

**Example:**

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.attachments import Attachment, AttachmentType
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.agents.task import Task
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.tools.builtin import FileReadTool, FileSearchTool

agent = Agent(
    name="Researcher",
    prompt=ZeroShotPrompt().configure(
        system="You are a research assistant. Cross-reference attached and workspace files.",
    ),
    llm=llm,
    tools=[
        FileReadTool(workspace_root="./data"),
        FileSearchTool(workspace_root="./data"),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)

task = Task(
    id="cross-ref",
    objective="Compare the attached summary with the raw data files",
    attachments=[
        Attachment(
            type=AttachmentType.TEXT,
            data="Q1: $1.2M, Q2: $1.5M, Q3: $1.8M",
            name="summary.txt",
        ),
    ],
)
result = await agent.execute(task)
```

---

## Safety & Validation

### AttachmentGuardPlugin

Control which attachments are allowed via the plugin system:

```python
from nucleusiq.agents import Agent
from nucleusiq.agents.attachments import AttachmentType
from nucleusiq.agents.config import AgentConfig, ExecutionMode
from nucleusiq.prompts.zero_shot import ZeroShotPrompt
from nucleusiq.plugins.builtin import AttachmentGuardPlugin
from nucleusiq_openai import BaseOpenAI

agent = Agent(
    name="attachment-policy",
    prompt=ZeroShotPrompt().configure(system="You are a helpful assistant."),
    llm=BaseOpenAI(model_name="gpt-4.1-mini"),
    plugins=[
        AttachmentGuardPlugin(
            allowed_types=[AttachmentType.TEXT, AttachmentType.IMAGE_URL],
            max_file_size=10 * 1024 * 1024,  # 10 MB
            max_attachments=5,
            allowed_extensions=[".txt", ".csv", ".png", ".jpg"],
        ),
    ],
    config=AgentConfig(execution_mode=ExecutionMode.STANDARD),
)
```

### Built-in validation

`AttachmentProcessor.process()` automatically:
- Rejects attachments exceeding 50 MB (`MAX_FILE_SIZE_BYTES`)
- Warns on MIME magic-byte mismatches (PDF, PNG, JPEG)
- Warns when text attachments exceed 100 KB (suggests FileReadTool)

### Workspace sandbox

All file tools resolve paths through `resolve_safe_path()` which blocks:
- `../` traversal
- Symlink escape
- Absolute path injection

---

## Memory integration

When an agent has memory, file context is preserved between turns:

- **User messages** get a prefix: `[Attached: report.pdf (text, 31.3 KB)]`
- **Attachment metadata** (name, type, size) is stored alongside messages
- File content itself is NOT stored in memory (too large) — only the summary

This means subsequent turns see that files were attached, even though the
raw content was only sent in the original prompt.

---

## Provider capabilities

Check what a provider supports at runtime:

```python
support = llm.describe_attachment_support()
print(support)
# {
#   "image_url":    "native",
#   "image_base64": "native",
#   "text":         "native",
#   "pdf":          "native",
#   "file_bytes":   "native",
#   "file_base64":  "native",
#   "file_url":     "native",
# }
```

`"native"` means the provider handles the type directly (e.g. OpenAI
server-side PDF processing). `"framework"` means the framework extracts
text before sending.
