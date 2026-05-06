# Context stack layers (L0–L7)

NucleusIQ documentation uses **L0–L7** as a single map across **transcript hygiene** (context window management), **run-local analyst state** (v0.7.8+), and **how the final answer is assembled**. This page is the glossary; deeper guides link here.

!!! warning "Two different “Layer” numbers in code"

    **`validation.py`** uses **Layer 1 / 2 / 3** for **post-step validation** (tool-output checks → plugins → optional LLM review). That is **orthogonal** to **L0–L7** on this page. Where both appear in docs, say **validation Layer N** versus **context stack L0–L7**.

---

## Full map

| Layer | Focus | Primary implementation | User-facing docs |
|-------|--------|---------------------------|------------------|
| **L0** | **Observation masking** — after each assistant reply, consumed tool turns can be replaced with slim markers; heavy content stays in `ContentStore` for recall. | `ObservationMasker` (“Tier 0” in engine/compactor terminology); `ContextEngine.post_response()` | [Context management](context-management.md) |
| **L1** | **Minor GC on tool results** — per-result offload/truncate when pressure builds against `optimal_budget`. | Compactor Tier 1 (formerly `ToolResultCompactor`) | [Context management](context-management.md) |
| **L2** | **Major GC on conversation** — evict older turns / summarize when utilization crosses the conversation threshold. | Compactor Tier 2 (`ConversationCompactor`) | [Context management](context-management.md) |
| **L3** | **Emergency / full GC** — last-resort reduction so the model can still respond. | Compactor Tier 3 (`EmergencyCompactor`) | [Context management](context-management.md) |
| **L4** | **Run-local structured state** — bounded **workspace** (notes/artifacts) and **evidence dossier** (claims, gaps, provenance) for *this* `execute()` only. | `InMemoryWorkspace`, `InMemoryEvidenceDossier`; optional tools via `build_workspace_tools` / `build_evidence_tools` | [Run-local context state](run-local-context-state.md) |
| **L4.5** | **Automatic activation** — after **business** tool results, promote evidence-shaped output, light-ingest into workspace + **L5** corpus (length/tool gates). | `ContextStateActivator`; knobs on `AgentConfig` (`context_tool_result_corpus_max_chars`, `context_activation_ingest_min_chars`) | [Run-local context state](run-local-context-state.md) |
| **L5** | **Lexical document corpus** — chunked in-memory text index + search tools (no PDF parsing or embeddings in this API). | `InMemoryDocumentCorpus`; `build_document_corpus_tools` | [Run-local context state](run-local-context-state.md) |
| **L6** | **Phase telemetry & evidence gate** — ordered phases, durations, tag-based completeness vs the dossier. | `PhaseController`, `EvidenceGate`; `AgentConfig.evidence_gate_*` | [Run-local context state](run-local-context-state.md) |
| **L7** | **Output closure** — tools-off **synthesis** pass when enabled, optional **`SynthesisPackage`** from workspace + evidence, and the **`AgentResult`** contract (including **`metadata`** summaries for run-local state). Autonomous **Critic/Refiner** sits on this closure side of the stack (verification after generation). | `AgentConfig.enable_synthesis`, `build_synthesis_package`, result builders; autonomous runners | [Execution modes](execution-modes.md), [Agents](agents.md), [Observability](observability/index.md) |

---

## How L0–L3 relate to “Tier” in code

Internal comments use **Tier 0–3** for compaction:

- **Tier 0** = observation masking → documented here as **L0**.
- **Tier 1** = tool-result pass → **L1**.
- **Tier 2** = conversation pass → **L2**.
- **Tier 3** = emergency pass → **L3**.

So **L0–L3** are entirely about **the visible chat transcript + backing store** under `ContextEngine`, driven by `ContextConfig`.

---

## How L4–L6 relate to run-local state

**L4–L6** do **not** replace L0–L3. They add a **second axis**: curated pockets of state and telemetry that reset every **`execute()`**. See [Run-local context state](run-local-context-state.md) for tools, limits, and `AgentResult.metadata` keys.

---

## How L7 fits

**L7** is not a separate subprocess with its own class named “Layer7”; it names the **assembly boundary**:

1. **Synthesis** — final LLM call without tools when `enable_synthesis=True` (Standard/streaming paths and related autonomous flows).
2. **`SynthesisPackage`** — deterministic bundle from workspace + evidence for package-aware synthesis (v0.7.8+).
3. **`AgentResult`** — structured outcome; **`metadata`** may carry `workspace`, `evidence`, `document_search`, `phase_control`, `context_activation`, `synthesis_package` when populated.
4. **Autonomous verification** — Critic/Refiner loops consume the evolving trace and package-aware critique where wired — documented under [Execution modes — Autonomous](execution-modes.md#autonomous).

---

## See also

- [Context management](context-management.md) — `ContextConfig`, telemetry, V2 notes  
- [Run-local context state](run-local-context-state.md) — L4–L6 detail  
- [Agents — AgentResult](agents.md#agentresult) — `metadata` and tracing  
- [Migration notes](learn/migration-notes.md) — version-to-version deltas  
