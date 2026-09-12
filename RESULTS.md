# Research results

This page distinguishes the reported institutional aggregate from the reproducible
public MultiHop-RAG study. No restricted per-question artifact is added by this release.

## OICR institutional case study

The existing evaluated-v0 aggregate reports the following comparison on 294
institutional questions:

| Metric | TreeRAG evaluated-v0 | Deployed hybrid baseline |
|---|---:|---:|
| Questions | 294 | 294 |
| Mean LLM-judged quality, [0,1] | 0.5629 | 0.4686 |
| Recorded mean seconds | 586.7 | 84.4 |

The mean paired quality difference is **+0.0943 (9.43 percentage points)**, with
paired bootstrap 95% CI **[0.0628, 0.1265]**. This supports a higher judged quality
score in this case study; it is not a 9.43-point gain in binary answer accuracy.

Source: the
[previously released aggregate record](experiments/private_deployment_aggregate_294_20260813.json).
Its original `treequest_*` field names are retained for provenance. The underlying
corpus, questions, and per-question judgments are restricted, so these values are
reported rather than independently recomputed from public rows.

TreeRAG's recorded runtime is higher. The aggregate alone does not establish
harmonized timing boundaries for the two systems; their ratio should not be
presented as a controlled end-to-end latency comparison. Public-study timers have
their own explicitly different boundaries, described below.

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

### QA formatting sensitivity

A diagnostic on the **same frozen answers and 200-question sample** holds the
official answer extraction fixed and replaces whitespace-token intersection with
intersection of Unicode word tokens (`re.findall(r"\w+", text.casefold())`). It
changes tokenization, without generating new answers or judging semantic correctness.

| System | Original official any-token overlap | Unicode-word any-token overlap |
|---|---:|---:|
| TreeRAG evaluated-v0 | 0.495 | 0.600 |
| Flat hybrid | 0.415 | 0.590 |
| Collapsed-tree control | 0.325 | 0.390 |
| Oracle diagnostic | 0.435 | 0.775 |

The TreeRAG–flat gap decreases from **8.0 to 1.0 percentage points**. The much
larger oracle score after normalization also illustrates this metric's sensitivity
to answer formatting. The Unicode-word variant is an exploratory diagnostic,
**not an official or validated alternative metric**, and is not evidence of a
semantic quality gain. Preserve the official scores, this sensitivity check,
and the independent joint-judge comparison as separate results.

## Interpretation and corrected metadata

The joint judge uses continuous scores in [0,1]. The original aggregate's metric
name ends in `0_0.5_1`, but saved values include partial credit such as 0.9 and
0.25; that label is incorrect. The original artifact is retained unchanged;
new evaluations identify the scale correctly.

The systems do not share a model-call budget. Flat hybrid uses BM25 and dense
retrieval with reciprocal-rank fusion followed by one answer call; collapsed
search uses dense top-10 retrieval over tree nodes followed by one answer call.
The comparison does not causally isolate tree structure or establish superiority
under equal compute.

The archived TreeRAG `seconds` measurement includes the joint judge, while the
reported successful-call count excludes its separate counter. Flat baseline
`elapsed_sec` covers answer generation only, excluding retrieval. Treat these as
recorded costs with different measurement boundaries, not directly comparable
end-to-end latency estimates.

The historical runner's development-oriented resume queue could replay losses
while retaining wins/ties. The final public checkpoint alone does not establish
whether that behavior was used. Future runs use a score-independent missing-only
resume policy with separate provenance; archived results remain unchanged.
