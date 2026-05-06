# Run-local context state (v0.7.8+)

NucleusIQ **0.7.8** adds a **per-execution**, **in-memory** stack that sits alongside Context Window Management (compaction/masking). It helps agents **organize** what they learned during a run—notes, structured evidence, a searchable text corpus, and framework-visible phase/evidence gates—without replacing your own tools or databases.

This page explains **what layer does what**, **how it is wired**, and **what you can observe** after `execute()`.

For **L0–L3** (transcript masking/compaction tiers) and **L7** (synthesis / `AgentResult` closure), see **[Context stack layers (L0–L7)](context-stack-layers.md)**.

---

## Mental model: layers L4–L6

| Layer | Name | Role |
|-------|------|------|
| **L4** | **Workspace** | Bounded “analyst notebook”: notes, artifacts, summaries for *this* run only (`InMemoryWorkspace`). |
| **L4.5** | **Context state activation** | After each **business** tool result (skipping framework context tools), heuristics may promote evidence-shaped facts, append workspace notes, and index text into the corpus (`ContextStateActivator`). |
| **L5** | **Document corpus** | Lexical, chunked index over caller-provided or ingested **text** (`InMemoryDocumentCorpus`). No PDF parsing, embeddings, or Task E logic inside the framework API. |
| **L6** | **Phase control + evidence gate** | Ordered phases, durations, evidence-gate decisions, and flags such as whether synthesis/critic used the package (`PhaseController`, `EvidenceGate`). |

**Context window management** (V2 compaction, masking, recall tools) remains separate: it controls **token pressure on the chat transcript**. Run-local state controls **curated working memory** and **telemetry** for that run.

---

## Lifecycle: fresh state every `execute()`

At the start of each `agent.execute(...)`, the framework constructs **new** workspace, evidence dossier, document corpus, phase controller, evidence gate, and `ContextStateActivator` instances. Nothing leaks across tasks.

Lazy accessors on `Agent` (`workspace`, `evidence_dossier`, `document_corpus`, …) create objects if you touch them **outside** a full execute path, but a normal execution **resets** them when `_setup_execution` runs.

---

## Framework-injected tools

When your agent has **at least one user-defined tool**, the runtime may append extra tools (recall tools from Context Mgmt v2, plus workspace/evidence/corpus tools when those subsystems are active). These tools:

- Are visible to the model in the tool list.
- **Do not** count toward the user’s **registered tool count** or external tool budget (`is_context_management_tool_name`).

### Workspace tools (`build_workspace_tools`)

Bound to the run’s `InMemoryWorkspace`:

| Tool | Purpose |
|------|---------|
| `write_workspace_note` | Append a durable note with optional source refs / metadata. |
| `write_workspace_artifact` | Store a larger artifact entry (still bounded by workspace caps). |
| `list_workspace_entries` | Discover entries (titles, kinds, previews). |
| `read_workspace_entry` | Read full content by id. |
| `summarize_workspace` | Compact overview of the notebook. |

Imports live under `nucleusiq.agents.context.workspace_tools`. Helpers: `is_workspace_tool_name`, `is_context_management_tool_name`.

### Evidence tools (`build_evidence_tools`)

Bound to `InMemoryEvidenceDossier`:

| Tool | Purpose |
|------|---------|
| `add_evidence` | Structured claim with status, confidence, tags, quotes, provenance. |
| `add_evidence_gap` | Record missing coverage. |
| `list_evidence` / `summarize_evidence` / `evidence_coverage` | Inspect dossier state. |

Helpers: `is_evidence_tool_name` (included in `is_context_management_tool_name`).

### Document corpus tools (`build_document_corpus_tools`)

Bound to `InMemoryDocumentCorpus` and optionally linked to the dossier:

| Tool | Purpose |
|------|---------|
| `search_document_corpus` | Lexical search over indexed chunks. |
| `get_document_chunk` | Retrieve chunk text by id. |
| `list_indexed_documents` | See what was indexed. |
| `promote_document_chunk_to_evidence` | Lift a chunk into the evidence dossier (when dossier is wired). |

Helper: `is_document_corpus_tool_name`.

---

## L4.5 activation (automatic)

`ContextStateActivator` runs after **business** tool results (not framework context tools). It can:

- Apply **strict heuristics** to promote evidence-shaped tool output into the dossier (and optional gap items).
- Perform **light ingest**: workspace notes plus L5 indexing for substantive read/search/file-style outputs, gated by tool-name hints, length floors, and guards against junk matches (e.g. bare `"ai"` substring false positives).

Tune ingestion via `AgentConfig`:

| Field | Default | Meaning |
|-------|---------|---------|
| `context_tool_result_corpus_max_chars` | `500_000` | Max characters of each business tool result **text** eligible for automatic corpus indexing; **`0` disables** indexing. |
| `context_activation_ingest_min_chars` | `200` | Minimum inspected characters for light ingest when output is **not** evidence-shaped; **`0`** allows any non-empty text; raise high to approximate “promote only when evidence-shaped”. |

---

## Evidence gate (optional completeness check)

`EvidenceGate` checks whether the dossier satisfies **required tags** before downstream phases. Configure on `AgentConfig`:

| Field | Default | Meaning |
|-------|---------|---------|
| `evidence_gate_required_tags` | `()` | Tag names that must be present for a **pass** (string, list, or tuple coerced to a tuple of non-empty strings). |
| `evidence_gate_enforce` | `False` | If **`True`**, missing tags **block** the gate; if **`False`**, decisions are recorded without blocking. |

Decisions surface in phase telemetry (`EvidenceGateDecision`: passed/blocked, missing tags, gaps).

---

## Synthesis package

`SynthesisPackage` + `build_synthesis_package` assemble a **deterministic, bounded** bundle from workspace + evidence (supported claims, gaps, source index, recalled snippets) with omission metadata.

Use **`Agent.build_synthesis_package(...)`** from application or tests; the framework may use package-based synthesis when curated state exists (`_build_synthesis_messages_from_context`). Metadata from the last package may appear under **`AgentResult.metadata["synthesis_package"]`**.

---

## `AgentResult.metadata` keys (v0.7.8)

When the corresponding subsystem ran, `result.metadata` may include:

| Key | Content |
|-----|---------|
| `workspace` | `InMemoryWorkspace.stats()` — entry counts, limits. |
| `evidence` | `InMemoryEvidenceDossier.stats()` — item counts. |
| `document_search` | `InMemoryDocumentCorpus.stats()` — documents/chunks indexed, search counts, chars returned, promotions to evidence. |
| `phase_control` | `PhaseController.stats().to_dict()` — phases, durations, evidence gate, flags (`synthesis_used_package`, `critic_used_package`, `refiner_used_gaps`, …). |
| `context_activation` | `ContextActivationMetrics.to_dict()` — activator counters (promotions, ingests, skips, synthesis-package flags, …). |
| `synthesis_package` | Dict copy of the last package **metadata** (if any). |

These sit **next to** existing fields such as `result.context_telemetry` (context window engine), not inside it.

---

## Tool result serialization fix

**Standard**, **Direct**, and shared **base** execution paths now route tool outputs through **`tool_result_to_context_string`**: raw **`str`** results pass through **without** being JSON-double-wrapped. Other types are serialized safely for the visible transcript.

---

## Autonomous-mode robustness

- **`CriticRunner`**: On **any** exception during critique (infrastructure, LLM, parser), the verdict is **`UNCERTAIN`** with score **`0.0`** and explicit feedback—no silent “pass”.
- **`SimpleRunner`**: After a successful **Refiner** pass, **`agent._last_messages`** is refreshed so a subsequent **Critic** sees the revised trace.

---

## Scope and limitations

- **In-memory only** — Workspace, dossier, and corpus are **not** durable stores; they reset each execution.
- **L5 is lexical text search** — You supply text (or rely on automatic ingest). There is **no** built-in PDF pipeline or embedding store in this API surface.
- **Requires user tools for injection** — If the agent has **zero** user tools, context-tool injection is skipped (avoids confusing models that would otherwise always pick a helper tool).

For compaction, masking, and recall, see [Context management](context-management.md). For execution modes, see [Execution modes](execution-modes.md).

---

## See also

- [Context stack layers (L0–L7)](context-stack-layers.md) — Full stack map including L0–L3 compaction and L7 closure
- [Agent Config guide](guides/agent-config.md) — New `AgentConfig` fields (`evidence_gate_*`, `context_tool_result_corpus_max_chars`, `context_activation_ingest_min_chars`).
- [Observability](observability/index.md) — Tracing + metadata inspection.
- [Changelog](../../reference/changelog.md) — v0.7.8 release notes (upstream `CHANGELOG.md` is authoritative).
- [Migration notes](learn/migration-notes.md#from-v077-to-v078) — Upgrade from v0.7.7.
