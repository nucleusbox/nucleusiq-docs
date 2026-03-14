# File Tools Deep Dive

## Search -> Read workflow

```python
Task(id="t1", objective="Find timeout settings; use file_search then file_read")
```

## Extract workflow

```python
# Agent-level intent examples:
# file_extract(path="sales.csv", columns="region,revenue")
# file_extract(path="config.json", key_path="database.host")
```

## Write workflow

```python
# Agent-level intent examples:
# file_write(path="reports/summary.txt", content="...", mode="write")
# file_write(path="reports/summary.txt", content="...", mode="append")
```

## Safety

All file tools are sandboxed to `workspace_root` and block traversal/symlink escape.
