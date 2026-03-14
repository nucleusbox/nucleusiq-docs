# Attachments

Attachments embed file content directly into the LLM prompt. Use them when the file is small and you know which file the LLM needs before execution.

## Supported types

| Type | Use case |
|------|----------|
| `TEXT` | Plain text, markdown, CSV |
| `PDF` | PDF documents |
| `IMAGE_URL` | Remote images |
| `IMAGE_BASE64` | Local images |
| `FILE_BYTES` | Raw file bytes |
| `FILE_BASE64` | Pre-encoded base64 |
| `FILE_URL` | Remote file URL (provider-native) |

## Usage

```python
from nucleusiq.agents.task import Task
from nucleusiq.agents.attachments import Attachment, AttachmentType

task = Task(
    id="t1",
    objective="Summarize this document",
    attachments=[
        Attachment(type=AttachmentType.PDF, data=pdf_bytes),
    ],
)
result = await agent.execute(task)
```

## When to use attachments vs tools

- **Attachments** — Small files (< 100 KB), one-shot analysis, you know the file upfront
- **File tools** — Agent needs to search/explore files iteratively

See the [File handling guide](guides/file-handling.md) for the full decision flowchart.
