# Detection evaluation

Prediction files: `noretrieval`, `bm25_k1`, `bm25_k3`, `bm25_k5`, `bm25_k10` | 192 queries | cells: mean [95% bootstrap CI, 1000 resamples]

Main set: disinformation vs inconclusive (case held out, the model should answer *unknown*). Article set: disinformation vs fact. Predictions are 3-way; off-label = a class outside the set's label space.

## noretrieval

### article/dev (n = 102)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.11 [0.05, 0.18] | 0.17 [0.08, 0.26] | 0.84 [0.77, 0.91] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.50 [0.00, 1.00] | 0.02 [0.00, 0.06] | 0.04 [0.00, 0.11] |
| fact | 0.71 [0.46, 0.93] | 0.20 [0.09, 0.31] | 0.31 [0.15, 0.46] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 1 | 4 | 46 |
| fact | 1 | 10 | 40 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 7 | 0.00 [0.00, 0.00] |
| formulation-driven | 7 | 0.00 [0.00, 0.00] |

### main/dev (n = 90)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.43 [0.33, 0.53] | 0.37 [0.29, 0.45] | 0.08 [0.02, 0.13] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.33 [0.08, 0.62] | 0.09 [0.02, 0.18] | 0.14 [0.04, 0.26] |
| inconclusive | 0.49 [0.38, 0.61] | 0.78 [0.65, 0.90] | 0.60 [0.49, 0.70] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 4 | 5 | 36 |
| inconclusive | 8 | 2 | 35 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 15 | 0.13 [0.00, 0.33] |
| overlap: mid | 15 | 0.13 [0.00, 0.33] |
| overlap: high | 15 | 0.00 [0.00, 0.00] |
| entity-driven | 16 | 0.06 [0.00, 0.19] |
| formulation-driven | 29 | 0.10 [0.00, 0.24] |

## bm25_k1

### article/dev (n = 102)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.60 [0.51, 0.69] | 0.62 [0.52, 0.71] | 0.10 [0.05, 0.16] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.64 [0.52, 0.77] | 0.75 [0.62, 0.86] | 0.69 [0.59, 0.78] |
| fact | 0.70 [0.54, 0.85] | 0.45 [0.32, 0.59] | 0.55 [0.41, 0.67] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 38 | 10 | 3 |
| fact | 21 | 23 | 7 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 7 | 0.86 [0.57, 1.00] |
| formulation-driven | 7 | 0.57 [0.28, 0.86] |
| gold evidence in top-k | 1 | 1.00 [1.00, 1.00] |
| gold evidence not in top-k | 13 | 0.69 [0.38, 0.92] |

### main/dev (n = 90)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.47 [0.37, 0.57] | 0.35 [0.29, 0.41] | 0.09 [0.03, 0.16] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.51 [0.41, 0.62] | 0.91 [0.82, 0.98] | 0.66 [0.56, 0.74] |
| inconclusive | 0.50 [0.00, 1.00] | 0.02 [0.00, 0.07] | 0.04 [0.00, 0.13] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 41 | 3 | 1 |
| inconclusive | 39 | 5 | 1 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 15 | 0.73 [0.47, 0.93] |
| overlap: mid | 15 | 1.00 [1.00, 1.00] |
| overlap: high | 15 | 1.00 [1.00, 1.00] |
| entity-driven | 16 | 0.94 [0.81, 1.00] |
| formulation-driven | 29 | 0.90 [0.76, 1.00] |
| gold evidence in top-k | 6 | 1.00 [1.00, 1.00] |
| gold evidence not in top-k | 39 | 0.90 [0.79, 0.97] |

## bm25_k3

### article/dev (n = 102)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.73 [0.64, 0.80] | 0.73 [0.64, 0.81] | 0.02 [0.00, 0.05] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.70 [0.60, 0.81] | 0.84 [0.74, 0.94] | 0.77 [0.67, 0.84] |
| fact | 0.79 [0.67, 0.92] | 0.61 [0.47, 0.73] | 0.69 [0.57, 0.79] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 43 | 8 | 0 |
| fact | 18 | 31 | 2 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 7 | 1.00 [1.00, 1.00] |
| formulation-driven | 7 | 0.86 [0.57, 1.00] |
| gold evidence in top-k | 2 | 1.00 [1.00, 1.00] |
| gold evidence not in top-k | 12 | 0.92 [0.75, 1.00] |

### main/dev (n = 90)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.48 [0.38, 0.58] | 0.34 [0.28, 0.41] | 0.03 [0.00, 0.08] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.49 [0.39, 0.59] | 0.93 [0.85, 1.00] | 0.65 [0.55, 0.73] |
| inconclusive | 0.50 [0.00, 1.00] | 0.02 [0.00, 0.08] | 0.04 [0.00, 0.14] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 42 | 2 | 1 |
| inconclusive | 43 | 1 | 1 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 15 | 0.87 [0.67, 1.00] |
| overlap: mid | 15 | 1.00 [1.00, 1.00] |
| overlap: high | 15 | 0.93 [0.80, 1.00] |
| entity-driven | 16 | 1.00 [1.00, 1.00] |
| formulation-driven | 29 | 0.90 [0.79, 1.00] |
| gold evidence in top-k | 9 | 1.00 [1.00, 1.00] |
| gold evidence not in top-k | 36 | 0.92 [0.81, 1.00] |

## bm25_k5

### article/dev (n = 102)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.74 [0.65, 0.82] | 0.74 [0.65, 0.83] | 0.02 [0.00, 0.05] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.70 [0.59, 0.82] | 0.84 [0.73, 0.94] | 0.77 [0.67, 0.84] |
| fact | 0.82 [0.68, 0.94] | 0.63 [0.49, 0.77] | 0.71 [0.59, 0.82] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 43 | 7 | 1 |
| fact | 18 | 32 | 1 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 7 | 1.00 [1.00, 1.00] |
| formulation-driven | 7 | 0.86 [0.57, 1.00] |
| gold evidence in top-k | 3 | 1.00 [1.00, 1.00] |
| gold evidence not in top-k | 11 | 0.91 [0.73, 1.00] |

### main/dev (n = 90)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.47 [0.38, 0.58] | 0.34 [0.28, 0.41] | 0.06 [0.01, 0.11] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.49 [0.39, 0.60] | 0.91 [0.82, 0.98] | 0.64 [0.55, 0.74] |
| inconclusive | 0.50 [0.00, 1.00] | 0.02 [0.00, 0.07] | 0.04 [0.00, 0.14] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 41 | 3 | 1 |
| inconclusive | 42 | 2 | 1 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 15 | 0.80 [0.60, 1.00] |
| overlap: mid | 15 | 1.00 [1.00, 1.00] |
| overlap: high | 15 | 0.93 [0.80, 1.00] |
| entity-driven | 16 | 0.94 [0.81, 1.00] |
| formulation-driven | 29 | 0.90 [0.79, 1.00] |
| gold evidence in top-k | 11 | 1.00 [1.00, 1.00] |
| gold evidence not in top-k | 34 | 0.88 [0.76, 0.97] |

## bm25_k10

### article/dev (n = 102)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.71 [0.62, 0.79] | 0.71 [0.62, 0.79] | 0.01 [0.00, 0.03] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.69 [0.57, 0.80] | 0.78 [0.67, 0.89] | 0.73 [0.63, 0.82] |
| fact | 0.74 [0.61, 0.87] | 0.63 [0.49, 0.76] | 0.68 [0.57, 0.78] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 40 | 11 | 0 |
| fact | 18 | 32 | 1 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 7 | 1.00 [1.00, 1.00] |
| formulation-driven | 7 | 1.00 [1.00, 1.00] |
| gold evidence in top-k | 3 | 1.00 [1.00, 1.00] |
| gold evidence not in top-k | 11 | 1.00 [1.00, 1.00] |

### main/dev (n = 90)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.46 [0.34, 0.56] | 0.31 [0.26, 0.36] | 0.03 [0.00, 0.07] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.48 [0.36, 0.58] | 0.91 [0.81, 0.98] | 0.63 [0.51, 0.71] |
| inconclusive | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 41 | 3 | 1 |
| inconclusive | 45 | 0 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 15 | 0.87 [0.67, 1.00] |
| overlap: mid | 15 | 1.00 [1.00, 1.00] |
| overlap: high | 15 | 0.87 [0.67, 1.00] |
| entity-driven | 16 | 0.88 [0.69, 1.00] |
| formulation-driven | 29 | 0.93 [0.83, 1.00] |
| gold evidence in top-k | 13 | 0.85 [0.62, 1.00] |
| gold evidence not in top-k | 32 | 0.94 [0.84, 1.00] |

## Paired differences (file − `noretrieval`)

\* = 95% CI excludes 0.

| Comparison | Set | Accuracy | Macro-F1 | Recall disinformation |
|---|---|---:|---:|---:|
| bm25_k1 - noretrieval | article/dev | +0.49* [+0.37, +0.60] | +0.45* [+0.32, +0.56] | +0.73* [+0.60, +0.84] |
| bm25_k1 - noretrieval | main/dev | +0.03 [-0.13, +0.22] | -0.02 [-0.14, +0.11] | +0.82* [+0.71, +0.93] |
| bm25_k3 - noretrieval | article/dev | +0.62* [+0.52, +0.73] | +0.56* [+0.45, +0.67] | +0.82* [+0.72, +0.92] |
| bm25_k3 - noretrieval | main/dev | +0.04 [-0.14, +0.22] | -0.03 [-0.15, +0.09] | +0.84* [+0.73, +0.95] |
| bm25_k5 - noretrieval | article/dev | +0.63* [+0.54, +0.72] | +0.57* [+0.48, +0.67] | +0.82* [+0.72, +0.93] |
| bm25_k5 - noretrieval | main/dev | +0.03 [-0.16, +0.21] | -0.03 [-0.16, +0.10] | +0.82* [+0.70, +0.93] |
| bm25_k10 - noretrieval | article/dev | +0.60* [+0.49, +0.70] | +0.53* [+0.42, +0.64] | +0.76* [+0.64, +0.87] |
| bm25_k10 - noretrieval | main/dev | +0.02 [-0.17, +0.20] | -0.06 [-0.17, +0.05] | +0.82* [+0.71, +0.93] |

## Cost

| File | Mode | k | Prompt tokens (mean) | LLM s / query | GPU peak GB | Retrieval ms / query (p50) |
|---|---|---:|---:|---:|---:|---:|
| noretrieval | no_retrieval | 0 | 141.1 | 0.0385 | 15.28 | – |
| bm25_k1 | rag | 1 | 280.7 | 0.0831 | 15.73 | 1.412 |
| bm25_k3 | rag | 3 | 558.7 | 0.1757 | 16.53 | 1.412 |
| bm25_k5 | rag | 5 | 850.3 | 0.2603 | 17.22 | 1.412 |
| bm25_k10 | rag | 10 | 1573.8 | 0.5085 | 19.11 | 1.412 |

Command: `eval_detection.py --preds preds/dev/noretrieval.csv preds/dev/bm25_k1.csv preds/dev/bm25_k3.csv preds/dev/bm25_k5.csv preds/dev/bm25_k10.csv --retrieval ../results/dev/retrieval_dev.per_query.csv --output results/dev/detection_dev.csv`
