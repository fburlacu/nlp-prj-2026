# Detection evaluation

Prediction files: `noretrieval`, `bm25_k5`, `dense_k5` | 90 queries | cells: mean [95% bootstrap CI, 1000 resamples]

Main set: disinformation vs inconclusive (case held out, the model should answer *unknown*). Article set: disinformation vs fact. Predictions are 3-way; off-label = a class outside the set's label space.

## noretrieval

### main/dev (n = 90)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.46 [0.36, 0.56] | 0.37 [0.29, 0.46] | 0.08 [0.03, 0.14] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.38 [0.00, 0.75] | 0.07 [0.00, 0.14] | 0.11 [0.00, 0.23] |
| inconclusive | 0.51 [0.39, 0.62] | 0.84 [0.73, 0.94] | 0.63 [0.52, 0.72] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 3 | 5 | 37 |
| inconclusive | 5 | 2 | 38 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 15 | 0.07 [0.00, 0.20] |
| overlap: mid | 15 | 0.13 [0.00, 0.33] |
| overlap: high | 15 | 0.00 [0.00, 0.00] |
| length: short | 16 | 0.12 [0.00, 0.31] |
| length: medium | 11 | 0.09 [0.00, 0.27] |
| length: long | 18 | 0.00 [0.00, 0.00] |
| entity-driven | 16 | 0.00 [0.00, 0.00] |
| formulation-driven | 29 | 0.10 [0.00, 0.21] |

## bm25_k5

### main/dev (n = 90)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.50 [0.40, 0.60] | 0.33 [0.29, 0.37] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.50 [0.40, 0.60] | 1.00 [1.00, 1.00] | 0.67 [0.57, 0.75] |
| inconclusive | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 45 | 0 | 0 |
| inconclusive | 45 | 0 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 15 | 1.00 [1.00, 1.00] |
| overlap: mid | 15 | 1.00 [1.00, 1.00] |
| overlap: high | 15 | 1.00 [1.00, 1.00] |
| length: short | 16 | 1.00 [1.00, 1.00] |
| length: medium | 11 | 1.00 [1.00, 1.00] |
| length: long | 18 | 1.00 [1.00, 1.00] |
| entity-driven | 16 | 1.00 [1.00, 1.00] |
| formulation-driven | 29 | 1.00 [1.00, 1.00] |
| gold evidence in top-k | 13 | 1.00 [1.00, 1.00] |
| gold evidence not in top-k | 32 | 1.00 [1.00, 1.00] |

## dense_k5

### main/dev (n = 90)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.48 [0.38, 0.59] | 0.41 [0.33, 0.51] | 0.03 [0.00, 0.08] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.49 [0.38, 0.60] | 0.82 [0.71, 0.93] | 0.61 [0.51, 0.71] |
| inconclusive | 0.55 [0.25, 0.86] | 0.13 [0.04, 0.24] | 0.21 [0.08, 0.35] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 37 | 3 | 5 |
| inconclusive | 39 | 0 | 6 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 15 | 0.80 [0.60, 1.00] |
| overlap: mid | 15 | 0.93 [0.80, 1.00] |
| overlap: high | 15 | 0.73 [0.47, 0.93] |
| length: short | 16 | 0.81 [0.62, 1.00] |
| length: medium | 11 | 0.82 [0.55, 1.00] |
| length: long | 18 | 0.83 [0.67, 1.00] |
| entity-driven | 16 | 0.81 [0.62, 1.00] |
| formulation-driven | 29 | 0.83 [0.66, 0.97] |
| gold evidence in top-k | 16 | 0.69 [0.44, 0.94] |
| gold evidence not in top-k | 29 | 0.90 [0.79, 1.00] |

## Paired differences (file − `noretrieval`)

\* = 95% CI excludes 0.

| Comparison | Set | Accuracy | Macro-F1 | Recall disinformation |
|---|---|---:|---:|---:|
| bm25_k5 - noretrieval | main/dev | +0.04 [-0.14, +0.23] | -0.04 [-0.15, +0.06] | +0.93* [+0.85, +1.00] |
| dense_k5 - noretrieval | main/dev | +0.02 [-0.17, +0.21] | +0.04 [-0.09, +0.18] | +0.76* [+0.62, +0.88] |

## Cost

| File | Mode | k | Prompt tokens (mean) | LLM s / query | GPU peak GB | Retrieval ms / query (p50) |
|---|---|---:|---:|---:|---:|---:|
| noretrieval | no_retrieval | 0 | 140.5 | 0.0088 | 15.58 | – |
| bm25_k5 | rag | 5 | 1425.2 | 0.1285 | 23.7 | – |
| dense_k5 | rag | 5 | None | None | None | – |

Command: `sparse_bm25/llm/eval_detection.py --queries data/queries_v2.csv --preds sparse_bm25/llm/v2_results/preds/dev/noretrieval.csv sparse_bm25/llm/v2_results/preds/dev/bm25_k5.csv generator/dense-v2-results/preds/dev/dense_k5.csv --retrieval generator/dense-v2-results/results/dev_compare/retrieval_dev.per_query.csv --output generator/dense-v2-results/results/dev/detection_dev.csv`
