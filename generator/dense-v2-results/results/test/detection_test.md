# Detection evaluation

Prediction files: `noretrieval`, `bm25_k5`, `dense_k5` | 1104 queries | cells: mean [95% bootstrap CI, 1000 resamples]

Main set: disinformation vs inconclusive (case held out, the model should answer *unknown*). Article set: disinformation vs fact. Predictions are 3-way; off-label = a class outside the set's label space.

## noretrieval

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.09 [0.06, 0.11] | 0.15 [0.11, 0.18] | 0.88 [0.86, 0.91] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.88 [0.60, 1.00] | 0.03 [0.01, 0.05] | 0.05 [0.02, 0.09] |
| fact | 0.71 [0.57, 0.83] | 0.14 [0.10, 0.19] | 0.24 [0.17, 0.30] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 7 | 15 | 230 |
| fact | 1 | 36 | 215 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.00 [0.00, 0.00] |
| formulation-driven | 30 | 0.07 [0.00, 0.17] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.49 [0.46, 0.54] | 0.41 [0.37, 0.44] | 0.04 [0.02, 0.05] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.57 [0.42, 0.69] | 0.10 [0.07, 0.13] | 0.17 [0.11, 0.22] |
| inconclusive | 0.51 [0.47, 0.55] | 0.89 [0.85, 0.92] | 0.65 [0.61, 0.68] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 29 | 12 | 259 |
| inconclusive | 22 | 11 | 267 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.07 [0.03, 0.13] |
| overlap: mid | 100 | 0.10 [0.04, 0.16] |
| overlap: high | 100 | 0.12 [0.06, 0.19] |
| length: short | 101 | 0.04 [0.01, 0.08] |
| length: medium | 103 | 0.09 [0.04, 0.15] |
| length: long | 96 | 0.17 [0.09, 0.24] |
| entity-driven | 125 | 0.09 [0.05, 0.14] |
| formulation-driven | 175 | 0.10 [0.06, 0.15] |

## bm25_k5

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.51 [0.47, 0.56] | 0.58 [0.53, 0.62] | 0.22 [0.19, 0.26] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.72 [0.65, 0.79] | 0.46 [0.39, 0.52] | 0.56 [0.50, 0.62] |
| fact | 0.62 [0.55, 0.68] | 0.57 [0.51, 0.63] | 0.59 [0.54, 0.64] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 115 | 90 | 47 |
| fact | 44 | 144 | 64 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.35 [0.17, 0.57] |
| formulation-driven | 30 | 0.63 [0.47, 0.80] |
| gold evidence in top-k | 19 | 0.53 [0.32, 0.74] |
| gold evidence not in top-k | 34 | 0.50 [0.35, 0.68] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.50 [0.46, 0.54] | 0.34 [0.32, 0.36] | 0.01 [0.00, 0.01] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.50 [0.46, 0.54] | 1.00 [0.99, 1.00] | 0.67 [0.63, 0.70] |
| inconclusive | 1.00 [0.00, 1.00] | 0.00 [0.00, 0.01] | 0.01 [0.00, 0.02] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 299 | 1 | 0 |
| inconclusive | 296 | 3 | 1 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 1.00 [1.00, 1.00] |
| overlap: mid | 100 | 0.99 [0.97, 1.00] |
| overlap: high | 100 | 1.00 [1.00, 1.00] |
| length: short | 101 | 0.99 [0.97, 1.00] |
| length: medium | 103 | 1.00 [1.00, 1.00] |
| length: long | 96 | 1.00 [1.00, 1.00] |
| entity-driven | 125 | 0.99 [0.97, 1.00] |
| formulation-driven | 175 | 1.00 [1.00, 1.00] |
| gold evidence in top-k | 102 | 0.99 [0.97, 1.00] |
| gold evidence not in top-k | 198 | 1.00 [1.00, 1.00] |

## dense_k5

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.34 [0.30, 0.38] | 0.45 [0.41, 0.50] | 0.50 [0.45, 0.54] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.70 [0.61, 0.79] | 0.28 [0.22, 0.34] | 0.40 [0.33, 0.46] |
| fact | 0.67 [0.59, 0.74] | 0.40 [0.35, 0.47] | 0.50 [0.45, 0.56] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 71 | 51 | 130 |
| fact | 30 | 102 | 120 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.35 [0.17, 0.52] |
| formulation-driven | 30 | 0.47 [0.30, 0.67] |
| gold evidence in top-k | 20 | 0.50 [0.25, 0.70] |
| gold evidence not in top-k | 33 | 0.36 [0.21, 0.55] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.51 [0.47, 0.55] | 0.47 [0.43, 0.51] | 0.02 [0.01, 0.04] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.52 [0.47, 0.56] | 0.79 [0.74, 0.83] | 0.63 [0.58, 0.67] |
| inconclusive | 0.54 [0.45, 0.62] | 0.23 [0.18, 0.28] | 0.32 [0.26, 0.38] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 237 | 4 | 59 |
| inconclusive | 221 | 10 | 69 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.74 [0.65, 0.82] |
| overlap: mid | 100 | 0.83 [0.75, 0.90] |
| overlap: high | 100 | 0.80 [0.72, 0.88] |
| length: short | 101 | 0.70 [0.60, 0.79] |
| length: medium | 103 | 0.80 [0.72, 0.86] |
| length: long | 96 | 0.88 [0.81, 0.94] |
| entity-driven | 125 | 0.80 [0.73, 0.86] |
| formulation-driven | 175 | 0.78 [0.72, 0.85] |
| gold evidence in top-k | 102 | 0.78 [0.71, 0.86] |
| gold evidence not in top-k | 198 | 0.79 [0.74, 0.85] |

## Paired differences (file − `noretrieval`)

\* = 95% CI excludes 0.

| Comparison | Set | Accuracy | Macro-F1 | Recall disinformation |
|---|---|---:|---:|---:|
| bm25_k5 - noretrieval | article/test | +0.43* [+0.38, +0.47] | +0.43* [+0.37, +0.49] | +0.43* [+0.36, +0.49] |
| bm25_k5 - noretrieval | main/test | +0.01 [-0.07, +0.08] | -0.07* [-0.11, -0.02] | +0.90* [+0.87, +0.93] |
| dense_k5 - noretrieval | article/test | +0.26* [+0.22, +0.30] | +0.31* [+0.25, +0.36] | +0.25* [+0.20, +0.31] |
| dense_k5 - noretrieval | main/test | +0.02 [-0.05, +0.08] | +0.07* [+0.02, +0.12] | +0.69* [+0.64, +0.74] |

## Cost

| File | Mode | k | Prompt tokens (mean) | LLM s / query | GPU peak GB | Retrieval ms / query (p50) |
|---|---|---:|---:|---:|---:|---:|
| noretrieval | no_retrieval | 0 | 140.6 | 0.0071 | 15.62 | – |
| bm25_k5 | rag | 5 | 1319.5 | 0.1039 | 27.37 | – |
| dense_k5 | rag | 5 | None | None | None | – |

Command: `sparse_bm25/llm/eval_detection.py --queries data/queries_v2.csv --preds sparse_bm25/llm/v2_results/preds/test/noretrieval.csv sparse_bm25/llm/v2_results/preds/test/bm25_k5.csv generator/dense-v2-results/preds/test/dense_k5.csv --retrieval generator/dense-v2-results/results/test_compare/retrieval_test.per_query.csv --output generator/dense-v2-results/results/test/detection_test.csv`
