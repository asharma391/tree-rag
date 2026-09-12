# Evaluated-v0 source provenance

The implementation files in this directory are archived source, not the supported
command-line entry points. Do not modify them to run a new experiment.

- `agentic_benchmark_best_v000.py`: archived deployment runner.
- `benchmark_treequest_public_frozen_v0.py`: exact public runner bytes matching
  the original `SHA256SUMS` manifest, recovered from preserved upstream history.
- `benchmark_treerag_public_frozen_v0.py`: later upstream filename update. Its
  only source changes rename the report and failure-dossier output paths; the
  retrieval logic and prompts are unchanged. Its hash is in `SHA256SUMS.current`.

Verify both manifests from the repository root:

```bash
shasum -a 256 -c reference/evaluated_v0/SHA256SUMS
shasum -a 256 -c reference/evaluated_v0/SHA256SUMS.current
```

The original manifest previously named an absent pre-rename file. Restoring that
historical file fixes verification without changing either manifest or archived
source bytes. New benchmark runs should use
`experiments/multihop_rag/benchmark_treerag_public.py`, whose paths and endpoint
are configurable. The modular `src/treerag/` package is a separate version.
