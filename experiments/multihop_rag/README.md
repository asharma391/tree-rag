# MultiHop-RAG public experiment

The released evaluated-v0 study uses 609 public articles and a balanced sample of
200 questions (50 of each type, sampling seed 20260806). It is not the full
2,556-question benchmark. All files in this directory concern the public corpus.

## Released artifacts

| Artifact | File |
|---|---|
| Frozen sample | `input/sample_200.json` |
| Public questions and flat-hybrid answers | `questions_public.json`, `qms_answers_public.json` |
| Full evaluated-v0 TreeRAG report | `results/treerag_public_frozen_v0_200_20260811.json` |
| Collapsed and gold-context answers | `results/collapsed_answers.json`, `results/oracle_answers.json` |
| Original official aggregate | `results/treerag_official_multihop_eval_v2_20260813.json` |
| Public tree | `../../data/multihop_rag_demo/corpus_tree.json` |
| Archived source and hash provenance | `../../reference/evaluated_v0/` |
| Official evaluator at pinned revision | `vendor/multihop_rag/UPSTREAM.json` |

All systems have 200 saved answers. Flat-hybrid retrieval metrics remain unavailable:
the saved title-level records do not identify the exact ranked passages.

## Official evaluation

Run from the repository root after `uv sync --frozen`. This requires no model
calls and does not download data:

```bash
uv run python experiments/multihop_rag/official_multihop_eval.py \
  --output "work/official-eval-$(date -u +%Y%m%dT%H%M%SZ).json"
```

The adapter verifies the vendored source hashes before importing them, uses the
committed public tree, and reconstructs the missing collapsed text index using
the original deterministic tree walk. The reconstructed index matches the
SHA-256 in the released aggregate exactly; it requires no embeddings. To use a
stored index instead, pass `--collapsed-nodes /path/to/collapsed_nodes.jsonl`.

Version 3 of this adapter also rejects missing/invalid paired scores and duplicate
or mismatched question IDs, requires a new output path, and correctly labels the
joint judge's continuous [0,1] score. These changes do not alter the frozen results.
The official QA rule is any token overlap; report it separately from the semantic
judge. Navigation-only nodes are excluded from retrieval; non-null questions are
scored using first-visit passage reads in the saved traces.

## New answer-generation runs

```bash
export TREERAG_OLLAMA_URL=http://127.0.0.1:11434
export TREERAG_MODEL=gpt-oss:120b
uv run --extra build ./scripts/run_multihop_benchmark.sh
```

The launcher prints a new timestamped checkpoint path. To resume that same new
run, set `TREERAG_BENCHMARK_REPORT` to its path. Resume now processes **only
unrecorded question IDs**, regardless of earlier scores. Recorded losses,
ties, wins, and failed answers are all preserved. The runner rejects old
checkpoints, changed questions/model, and score-conditioned debug overrides.
A deliberately changed experiment must use a new path.

The runnable controller is labeled `evaluated-v0-resume-fixed-20260912`: retrieval
and answer logic are preserved, while checkpoint scheduling is corrected. Archived
source remains immutable. The historical runner's development scheduler could
selectively replay losses on resume; retained final records do not establish
whether that happened. Do not infer one-pass evaluation from a final checkpoint
alone. This concern does not change any archived result or prove historical bias.

## Rebuild the public hierarchy

```bash
export TREERAG_CACHE_DIR="$PWD/work/public-tree-$(date -u +%Y%m%dT%H%M%SZ)"
uv run --extra build ./scripts/build_tree.sh
```

The builder downloads public data, materializes DOCX files, and summarizes the
hierarchy. It preserves the committed tree and refuses to overwrite the frozen
question manifest if downloaded data changes the sample. The download URL uses
an upstream moving branch: the frozen sample and tree are the authoritative
released inputs, and a future corpus download must be checked for changes.
Build caches support resumption within the same output directory.

## Interpretation and resource boundaries

- The flat baseline uses BM25 plus dense retrieval fused with reciprocal-rank
  fusion. Collapsed search uses dense top-10 retrieval over tree nodes. Each uses
  one answer-generation call, unlike TreeRAG's adaptive multi-call search.
- These controls are not compute matched and do not isolate hierarchy as the
  causal source of an improvement.
- The archived TreeRAG `seconds` field includes joint judging, whereas its
  successful-call count excludes that separate judge. Flat `elapsed_sec`
  measures answer generation only and excludes retrieval. Do not interpret
  their ratio as an end-to-end speed comparison.
- Lexical frontier seeding is part of the controller. Archived code optionally
  attempts embedding ordering for over-wide previews, with fallback; successful
  activation was not logged. The modular package disables that helper by default.
- Human judgments and agreement with the LLM judge are pending. The matched
  semantic difference on this public sample has a confidence interval spanning zero.

See [RESULTS.md](../../RESULTS.md) and [REPRODUCIBILITY.md](../../REPRODUCIBILITY.md).
