# Architecture

```mermaid
flowchart LR
  A["Governed folders and documents"] --> B["Structure-preserving parse"]
  B --> C["Bottom-up summaries"]
  C --> D["Persistent corpus tree"]
  Q["Question"] --> R["LLM child ranking"]
  D --> R
  R --> F["Active and reserve frontier"]
  R --> E["Read and same-file sweep"]
  E --> S{"Evidence sufficient?"}
  S -->|No| T["Residual / breadth / score teleport"]
  T --> R
  S -->|Yes| X["Contrast check"]
  X --> G["Grounded answer with sources"]
```

## Build phase

The builder preserves directory, document, and heading structure. Paragraphs, tables,
and figures become evidence-bearing leaves; summaries are created bottom-up and cached
per node. The tree is built once and amortized over future questions.

## Query phase

The controller scores a bounded candidate set with the language model, descends locally,
and retains runner-up branches globally. Reads can expand to an enclosing section and
sweep unread sections in the same document. A sufficiency gate names missing evidence;
teleports then target a contradiction, residual need, unvisited region, or best retained
alternative. Search ends under explicit visit, source, evidence, call, and cooperative
wall-clock budgets.

## Why a native hierarchy

A governed hierarchy is stable, human-auditable, and already maintained for operational
reasons. TreeRAG tests that regime rather than claiming every corpus has a useful native
tree. Claims concern retrieval over preserved document structure; alternative
collection-level tree methods require separate matched evaluation.

## Vector-signal boundary

Evidence is not selected by nearest-neighbor lookup. The controller uses LLM
branch scores and corpus-wide lexical frontier seeds. The evaluated-v0 source
contains optional embedding ordering of names inside over-wide previews, with a
lexical fallback; the retained telemetry does not establish successful activation.
Modular-v1 defaults to zero embedding calls for that helper. Preserve these
qualifications rather than claiming the historical run was proven vector-free.
