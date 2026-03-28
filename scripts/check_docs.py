"""Basic docs consistency checks for NucleusIQ.

This script catches two classes of docs regressions:
1) Broken relative markdown links under docs/
2) Known API-drift patterns in user-facing framework docs
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "documentation"


def find_markdown_files(root: Path) -> list[Path]:
    return sorted(root.rglob("*.md"))


def check_relative_links(md_files: list[Path]) -> list[str]:
    errors: list[str] = []
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        for match in link_pattern.finditer(content):
            link = match.group(1).strip()
            if link.startswith(("http://", "https://", "mailto:", "#")):
                continue

            rel_target = link.split("#", 1)[0].strip()
            if not rel_target:
                continue

            target = (md_file.parent / rel_target).resolve()
            if not target.exists():
                errors.append(
                    f"Broken relative link in {md_file.relative_to(REPO_ROOT)} -> {link}"
                )

    return errors


def _extract_code_blocks(content: str) -> list[str]:
    """Extract text inside fenced code blocks (``` ... ```)."""
    blocks: list[str] = []
    in_block = False
    lines: list[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if in_block:
                blocks.append("\n".join(lines))
                lines = []
                in_block = False
            else:
                in_block = True
        elif in_block:
            lines.append(line)
    return blocks


def check_global_patterns(md_files: list[Path]) -> list[str]:
    """Scan ALL markdown files for known wrong patterns."""
    errors: list[str] = []

    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        rel = md_file.relative_to(REPO_ROOT)
        code_text = "\n".join(_extract_code_blocks(content))

        if re.search(r"agent\.execute\(\s*[\"']", code_text):
            errors.append(
                f"{rel}: agent.execute() called with a string literal. "
                "Use Task(...) or dict form: agent.execute(" + '{"id": "...", "objective": "..."})'
            )

        if re.search(r"agent\.execute_stream\(\s*[\"']", code_text):
            errors.append(
                f"{rel}: agent.execute_stream() called with a string literal. "
                "Use dict form: agent.execute_stream(" + '{"id": "...", "objective": "..."})'
            )

        if re.search(r"event\.delta", code_text):
            errors.append(
                f"{rel}: event.delta does not exist. "
                "Use event.token for TOKEN events, event.message for THINKING/ERROR."
            )

        if re.search(r"llm_max_tokens\b", code_text):
            errors.append(
                f"{rel}: llm_max_tokens is stale (v0.5.0). "
                "Use llm_max_output_tokens (renamed in v0.6.0)."
            )

    return errors


def check_api_drift_patterns() -> list[str]:
    """Check specific files for known stale patterns."""
    errors: list[str] = []

    checks: dict[Path, list[tuple[str, str]]] = {
        Path("documentation/python/nucleusiq/memory.md"): [
            (
                r"SUMMARY_PLUS_WINDOW",
                "Use MemoryStrategy.SUMMARY_WINDOW (SUMMARY_PLUS_WINDOW is invalid).",
            ),
        ],
        Path("documentation/python/nucleusiq/models.md"): [
            (
                r"llm_params\s*=\s*\{",
                "Use LLMParams/OpenAILLMParams objects for llm_params.",
            ),
        ],
        Path("documentation/python/nucleusiq/streaming.md"): [
            (
                r"print\(\s*event\.content",
                "For TOKEN events, use event.token (event.content is for COMPLETE).",
            ),
        ],
    }

    for rel_file, patterns in checks.items():
        full_path = REPO_ROOT / rel_file
        if not full_path.exists():
            errors.append(f"Missing expected docs file: {rel_file}")
            continue

        content = full_path.read_text(encoding="utf-8")
        code_text = "\n".join(_extract_code_blocks(content))
        for pattern, message in patterns:
            if re.search(pattern, code_text):
                errors.append(f"{rel_file}: {message}")

    return errors


def main() -> int:
    if not DOCS_ROOT.exists():
        print("documentation/ directory not found.")
        return 1

    md_files = find_markdown_files(DOCS_ROOT)
    errors = check_relative_links(md_files)
    errors.extend(check_global_patterns(md_files))
    errors.extend(check_api_drift_patterns())

    if errors:
        print(f"Documentation checks failed ({len(errors)} issues):\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"Documentation checks passed ({len(md_files)} files scanned).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
