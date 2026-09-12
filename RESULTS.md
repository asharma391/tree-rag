# Frozen public results

This public repository reports only the MultiHop-RAG study. Restricted deployment
statistics remain in the private research repository and unpublished manuscript; no
private-derived result artifact is published here.

## MultiHop-RAG

The study uses a balanced 200-question sample: 50 comparison, 50 inference, 50 temporal,
and 50 null questions. Official retrieval is evaluated on the 150 non-null questions.

| System | QA accuracy (n=200) | Hits@4 | Hits@10 | MAP@10 | MRR@10 |
|---|---:|---:|---:|---:|---:|
| TreeRAG evaluated-v0 | 0.495 | 0.6667 | 0.6933 | 0.2258 | 0.4612 |
| Flat hybrid | 0.415 | unavailable | unavailable | unavailable | unavailable |
| Collapsed-tree control | 0.325 | 0.3533 | 0.4800 | 0.1058 | 0.2539 |
| Oracle diagnostic | 0.435 | 1.0000 | 1.0000 | 0.6700 | 1.0000 |

TreeRAG's retrieval advantage over collapsed search is large across all four official
retrieval metrics. Official QA also favors TreeRAG over flat hybrid by 8.0 points and
collapsed search by 17.0 points. The official QA rule is any token intersection with the
gold answer; the oracle's lower QA score than TreeRAG shows why it is a coarse
compatibility measure rather than a semantic gold standard.

A separate joint `gpt-oss:120b` judge scores TreeRAG 0.639 and flat hybrid 0.598. The
paired difference is 0.041, with 35 wins, 138 ties, 27 losses, bootstrap 95% CI
[-0.02925, 0.11150], and two-sided sign-flip `p=0.26177`. This direction is encouraging
but statistically uncertain and is not presented as a confirmed public semantic win.

TreeRAG averages 598.7 seconds, 127.9 model calls, and 4.37 evidence pieces per public
question. The hierarchy build takes 49,401 seconds (13 h 42 min) and 19,976 model calls,
producing a 28.7 MB JSON tree with 20,495 nodes and 19,212 chunks.

The immutable machine-readable source is
`experiments/multihop_rag/results/treerag_official_multihop_eval_v2_20260813.json`.
