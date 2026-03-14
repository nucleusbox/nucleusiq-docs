# Built-in Tools

NucleusIQ ships five file-oriented built-ins:

- `FileReadTool`
- `FileWriteTool`
- `FileSearchTool`
- `DirectoryListTool`
- `FileExtractTool`

## Typical setup

```python
from nucleusiq.tools.builtin import (
    FileReadTool, FileWriteTool, FileSearchTool, DirectoryListTool, FileExtractTool
)

tools = [
    FileReadTool(workspace_root="./workspace"),
    FileWriteTool(workspace_root="./workspace"),
    FileSearchTool(workspace_root="./workspace"),
    DirectoryListTool(workspace_root="./workspace"),
    FileExtractTool(workspace_root="./workspace"),
]
```
