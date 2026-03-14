# Core Concept: Tasks

A `Task` represents one concrete user request.

```python
from nucleusiq.agents.task import Task

task = Task(
    id="task-1",
    objective="Summarize this report",
    metadata={"priority": "high"},
)
```

## Task fields

- `id`: unique task identifier
- `objective`: concrete user instruction
- `context`: optional auxiliary context
- `metadata`: optional tags/structured metadata
- `attachments`: optional multimodal inputs

## Attachment example

```python
from nucleusiq.agents.attachments import Attachment, AttachmentType

task = Task(
    id="task-2",
    objective="Extract key points from this PDF",
    attachments=[
        Attachment(type=AttachmentType.PDF, data=pdf_bytes, name="report.pdf"),
    ],
)
```
