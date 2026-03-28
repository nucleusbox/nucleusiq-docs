# Attachments

Attachments embed file content directly into the LLM prompt. Use them when the file is small and you know which file the LLM needs before execution.

Both OpenAI and Gemini providers support attachments natively.

## Supported types

| Type | Use case | OpenAI | Gemini |
|------|----------|--------|--------|
| `TEXT` | Plain text, markdown, CSV | Yes | Yes |
| `PDF` | PDF documents | Yes | Yes |
| `IMAGE_URL` | Remote images | Yes | Yes |
| `IMAGE_BASE64` | Local images | Yes | Yes |
| `FILE_BYTES` | Raw file bytes | Yes | Yes |
| `FILE_BASE64` | Pre-encoded base64 | Yes | Yes |
| `FILE_URL` | Remote file URL | Yes | — |

## Usage

```python
from nucleusiq.agents.task import Task
from nucleusiq.core.attachments.models import Attachment, AttachmentType

task = Task(
    id="t1",
    objective="Summarize this document",
    attachments=[
        Attachment(type=AttachmentType.PDF, data=pdf_bytes),
    ],
)
result = await agent.execute(task)
```

## Image analysis

```python
task = Task(
    id="img",
    objective="Describe what you see in this image",
    attachments=[
        Attachment(
            type=AttachmentType.IMAGE_URL,
            content="https://example.com/photo.jpg",
        ),
    ],
)
```

## Provider capability introspection

Check what a provider supports at runtime:

```python
print(llm.describe_attachment_support())
print(llm.NATIVE_ATTACHMENT_TYPES)
print(llm.SUPPORTED_FILE_EXTENSIONS)
```

## AttachmentGuardPlugin

Validate attachments with policy controls:

```python
from nucleusiq.plugins.builtin import AttachmentGuardPlugin

plugin = AttachmentGuardPlugin(
    allowed_types=[AttachmentType.PDF, AttachmentType.TEXT],
    max_file_size=5_000_000,  # 5 MB
    max_count=3,
)
agent = Agent(..., plugins=[plugin])
```

## When to use attachments vs tools

| Criteria | Attachments | File tools |
|----------|-------------|-----------|
| File size | Small (< 100 KB) | Any size |
| Known upfront? | Yes | No (agent discovers) |
| Interaction | One-shot analysis | Iterative search/read |
| Provider processing | Native (server-side) | Framework-level |

See the [File handling guide](guides/file-handling.md) for the full decision flowchart.
