# Detection evaluation

Prediction files: `noretrieval`, `bm25_k5`, `bm25_sens_k5` | 1104 queries | cells: mean [95% bootstrap CI, 1000 resamples]

Main set: disinformation vs inconclusive (case held out, the model should answer *unknown*). Article set: disinformation vs fact. Predictions are 3-way; off-label = a class outside the set's label space.

## noretrieval

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.09 [0.06, 0.12] | 0.15 [0.11, 0.19] | 0.88 [0.85, 0.91] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.88 [0.60, 1.00] | 0.03 [0.01, 0.05] | 0.05 [0.02, 0.09] |
| fact | 0.72 [0.59, 0.84] | 0.15 [0.11, 0.20] | 0.25 [0.18, 0.31] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 7 | 15 | 230 |
| fact | 1 | 38 | 213 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.00 [0.00, 0.00] |
| formulation-driven | 30 | 0.07 [0.00, 0.17] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.49 [0.45, 0.53] | 0.40 [0.37, 0.44] | 0.04 [0.03, 0.06] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.54 [0.40, 0.66] | 0.09 [0.06, 0.13] | 0.16 [0.11, 0.21] |
| inconclusive | 0.50 [0.46, 0.55] | 0.88 [0.84, 0.91] | 0.64 [0.60, 0.68] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 28 | 13 | 259 |
| inconclusive | 24 | 12 | 264 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.06 [0.02, 0.11] |
| overlap: mid | 100 | 0.10 [0.04, 0.16] |
| overlap: high | 100 | 0.12 [0.06, 0.19] |
| entity-driven | 125 | 0.08 [0.04, 0.14] |
| formulation-driven | 175 | 0.10 [0.06, 0.15] |

## bm25_k5

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.71 [0.66, 0.74] | 0.70 [0.66, 0.74] | 0.02 [0.01, 0.04] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.66 [0.61, 0.71] | 0.89 [0.85, 0.92] | 0.76 [0.72, 0.80] |
| fact | 0.85 [0.79, 0.90] | 0.52 [0.46, 0.59] | 0.65 [0.59, 0.70] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 224 | 23 | 5 |
| fact | 113 | 132 | 7 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.74 [0.57, 0.91] |
| formulation-driven | 30 | 0.97 [0.87, 1.00] |
| gold evidence in top-k | 12 | 0.67 [0.42, 0.92] |
| gold evidence not in top-k | 41 | 0.93 [0.83, 1.00] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.49 [0.45, 0.53] | 0.34 [0.32, 0.36] | 0.02 [0.01, 0.03] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.50 [0.46, 0.54] | 0.98 [0.96, 0.99] | 0.66 [0.63, 0.70] |
| inconclusive | 0.67 [0.00, 1.00] | 0.01 [0.00, 0.02] | 0.01 [0.00, 0.03] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 294 | 5 | 1 |
| inconclusive | 292 | 6 | 2 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.95 [0.91, 0.99] |
| overlap: mid | 100 | 0.99 [0.97, 1.00] |
| overlap: high | 100 | 1.00 [1.00, 1.00] |
| entity-driven | 125 | 0.98 [0.94, 1.00] |
| formulation-driven | 175 | 0.98 [0.96, 1.00] |
| gold evidence in top-k | 89 | 1.00 [1.00, 1.00] |
| gold evidence not in top-k | 211 | 0.97 [0.95, 0.99] |

## bm25_sens_k5

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.68 [0.64, 0.71] | 0.69 [0.65, 0.73] | 0.06 [0.04, 0.08] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.67 [0.62, 0.72] | 0.81 [0.76, 0.85] | 0.73 [0.69, 0.77] |
| fact | 0.80 [0.74, 0.85] | 0.55 [0.48, 0.61] | 0.65 [0.59, 0.70] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 203 | 35 | 14 |
| fact | 100 | 138 | 14 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.78 [0.61, 0.96] |
| formulation-driven | 30 | 0.83 [0.70, 0.93] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.49 [0.45, 0.53] | 0.35 [0.33, 0.38] | 0.03 [0.02, 0.05] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.51 [0.46, 0.55] | 0.96 [0.93, 0.98] | 0.66 [0.63, 0.70] |
| inconclusive | 0.64 [0.31, 0.91] | 0.02 [0.01, 0.04] | 0.05 [0.01, 0.08] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 288 | 8 | 4 |
| inconclusive | 281 | 12 | 7 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.92 [0.86, 0.97] |
| overlap: mid | 100 | 0.98 [0.95, 1.00] |
| overlap: high | 100 | 0.98 [0.95, 1.00] |
| entity-driven | 125 | 0.96 [0.92, 0.99] |
| formulation-driven | 175 | 0.96 [0.93, 0.99] |

## Paired differences (file − `noretrieval`)

\* = 95% CI excludes 0.

| Comparison | Set | Accuracy | Macro-F1 | Recall disinformation |
|---|---|---:|---:|---:|
| bm25_k5 - noretrieval | article/test | +0.62* [+0.57, +0.66] | +0.55* [+0.50, +0.61] | +0.86* [+0.82, +0.90] |
| bm25_k5 - noretrieval | main/test | +0.01 [-0.07, +0.09] | -0.06* [-0.11, -0.01] | +0.89* [+0.85, +0.92] |
| bm25_sens_k5 - noretrieval | article/test | +0.59* [+0.54, +0.63] | +0.54* [+0.48, +0.59] | +0.78* [+0.72, +0.83] |
| bm25_sens_k5 - noretrieval | main/test | +0.00 [-0.07, +0.08] | -0.05 [-0.09, +0.00] | +0.87* [+0.83, +0.90] |

## Cost

| File | Mode | k | Prompt tokens (mean) | LLM s / query | GPU peak GB | Retrieval ms / query (p50) |
|---|---|---:|---:|---:|---:|---:|
| noretrieval | no_retrieval | 0 | 140.6 | 0.0364 | 15.28 | – |
| bm25_k5 | rag | 5 | 832.3 | 0.2538 | 17.59 | 1.477 |
| bm25_sens_k5 | rag | 5 | 981.0 | 0.2841 | 18.11 | 1.324 |

Command: `eval_detection.py --preds preds/test/noretrieval.csv preds/test/bm25_k5.csv preds/test/bm25_sens_k5.csv --retrieval ../results/test_default/retrieval_test.per_query.csv --output results/test/detection_test.csv`
