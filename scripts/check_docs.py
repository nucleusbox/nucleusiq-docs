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


def check_api_drift_patterns() -> list[str]:
    errors: list[str] = []

    checks: dict[Path, list[tuple[str, str]]] = {
        Path("documentation/python/nucleusiq/overview.md"): [
            (r"agent\.execute\(\s*[\"']", "Use Task objects with agent.execute(task)."),
        ],
        Path("documentation/python/nucleusiq/memory.md"): [
            (
                r"SUMMARY_PLUS_WINDOW",
                "Use MemoryStrategy.SUMMARY_WINDOW (SUMMARY_PLUS_WINDOW is invalid).",
            ),
            (
                r"memory_strategy\s*=",
                "Memory is configured via Agent(memory=...) with MemoryFactory, not AgentConfig.memory_strategy.",
            ),
            (
                r"memory_window_size\s*=",
                "Use window_size when creating memory instances.",
            ),
        ],
        Path("documentation/python/nucleusiq/structured-output.md"): [
            (
                r"execute\(\s*task\s*,\s*response_format\s*=",
                "Set response_format on Agent(...), not per execute() call.",
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
        Path("documentation/python/nucleusiq/guides/openai-provider.md"): [
            (
                r"llm_params\s*=\s*\{",
                "Use OpenAILLMParams(...) in examples instead of dict overrides.",
            ),
            (
                r"\]\(\.\./\.\./openai_provider_user_guide\.md\)",
                "Use ../../../openai_provider_user_guide.md from documentation/python/nucleusiq/guides/openai-provider.md.",
            ),
        ],
        Path("documentation/openai_provider_user_guide.md"): [
            (
                r"llm_params\s*=\s*\{",
                "Use OpenAILLMParams(...) in examples instead of dict overrides.",
            ),
        ],
    }

    for rel_file, patterns in checks.items():
        full_path = REPO_ROOT / rel_file
        if not full_path.exists():
            errors.append(f"Missing expected docs file: {rel_file}")
            continue

        content = full_path.read_text(encoding="utf-8")
        for pattern, message in patterns:
            if re.search(pattern, content):
                errors.append(f"{rel_file}: {message}")

    return errors


def main() -> int:
    if not DOCS_ROOT.exists():
        print("docs/ directory not found.")
        return 1

    md_files = find_markdown_files(DOCS_ROOT)
    errors = check_relative_links(md_files)
    errors.extend(check_api_drift_patterns())

    if errors:
        print("Documentation checks failed:\n")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Documentation checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
