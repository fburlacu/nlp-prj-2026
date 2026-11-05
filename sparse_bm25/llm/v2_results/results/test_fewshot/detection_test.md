# Detection evaluation

Prediction files: `noretrieval`, `bm25_k5`, `bm25_sens_k5` | 1104 queries | cells: mean [95% bootstrap CI, 1000 resamples]

Main set: disinformation vs inconclusive (case held out, the model should answer *unknown*). Article set: disinformation vs fact. Predictions are 3-way; off-label = a class outside the set's label space.

## noretrieval

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| fact | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 0 | 0 | 252 |
| fact | 0 | 0 | 252 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.00 [0.00, 0.00] |
| formulation-driven | 30 | 0.00 [0.00, 0.00] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.50 [0.46, 0.54] | 0.33 [0.32, 0.35] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] |
| inconclusive | 0.50 [0.46, 0.54] | 1.00 [1.00, 1.00] | 0.67 [0.63, 0.70] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 0 | 0 | 300 |
| inconclusive | 0 | 0 | 300 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.00 [0.00, 0.00] |
| overlap: mid | 100 | 0.00 [0.00, 0.00] |
| overlap: high | 100 | 0.00 [0.00, 0.00] |
| length: short | 101 | 0.00 [0.00, 0.00] |
| length: medium | 103 | 0.00 [0.00, 0.00] |
| length: long | 96 | 0.00 [0.00, 0.00] |
| entity-driven | 125 | 0.00 [0.00, 0.00] |
| formulation-driven | 175 | 0.00 [0.00, 0.00] |

## bm25_k5

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.34 [0.29, 0.38] | 0.45 [0.40, 0.50] | 0.54 [0.49, 0.58] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.74 [0.64, 0.82] | 0.27 [0.21, 0.32] | 0.39 [0.32, 0.45] |
| fact | 0.72 [0.64, 0.79] | 0.40 [0.34, 0.46] | 0.52 [0.45, 0.58] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 67 | 40 | 145 |
| fact | 24 | 102 | 126 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.30 [0.13, 0.48] |
| formulation-driven | 30 | 0.43 [0.27, 0.60] |
| gold evidence in top-k | 19 | 0.42 [0.21, 0.63] |
| gold evidence not in top-k | 34 | 0.35 [0.21, 0.53] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.54 [0.50, 0.58] | 0.53 [0.49, 0.57] | 0.03 [0.01, 0.04] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.54 [0.49, 0.59] | 0.74 [0.69, 0.79] | 0.62 [0.58, 0.66] |
| inconclusive | 0.58 [0.51, 0.66] | 0.34 [0.29, 0.40] | 0.43 [0.37, 0.48] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 221 | 6 | 73 |
| inconclusive | 189 | 9 | 102 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.66 [0.56, 0.75] |
| overlap: mid | 100 | 0.74 [0.65, 0.82] |
| overlap: high | 100 | 0.81 [0.73, 0.89] |
| length: short | 101 | 0.71 [0.62, 0.80] |
| length: medium | 103 | 0.75 [0.66, 0.83] |
| length: long | 96 | 0.75 [0.67, 0.83] |
| entity-driven | 125 | 0.75 [0.67, 0.82] |
| formulation-driven | 175 | 0.73 [0.66, 0.79] |
| gold evidence in top-k | 102 | 0.78 [0.70, 0.86] |
| gold evidence not in top-k | 198 | 0.71 [0.65, 0.77] |

## bm25_sens_k5

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.34 [0.30, 0.38] | 0.46 [0.41, 0.51] | 0.53 [0.49, 0.57] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.73 [0.63, 0.82] | 0.29 [0.23, 0.34] | 0.41 [0.35, 0.47] |
| fact | 0.72 [0.64, 0.79] | 0.40 [0.34, 0.45] | 0.51 [0.45, 0.57] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 72 | 39 | 141 |
| fact | 26 | 100 | 126 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.26 [0.09, 0.43] |
| formulation-driven | 30 | 0.47 [0.30, 0.63] |
| gold evidence in top-k | 18 | 0.39 [0.17, 0.61] |
| gold evidence not in top-k | 35 | 0.37 [0.23, 0.51] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.52 [0.48, 0.56] | 0.52 [0.48, 0.56] | 0.05 [0.03, 0.07] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.54 [0.49, 0.59] | 0.65 [0.60, 0.71] | 0.59 [0.55, 0.63] |
| inconclusive | 0.56 [0.49, 0.63] | 0.38 [0.33, 0.44] | 0.45 [0.40, 0.51] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 196 | 13 | 91 |
| inconclusive | 168 | 17 | 115 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.64 [0.55, 0.73] |
| overlap: mid | 100 | 0.66 [0.56, 0.75] |
| overlap: high | 100 | 0.66 [0.57, 0.75] |
| length: short | 101 | 0.61 [0.51, 0.71] |
| length: medium | 103 | 0.63 [0.54, 0.72] |
| length: long | 96 | 0.72 [0.64, 0.80] |
| entity-driven | 125 | 0.69 [0.60, 0.76] |
| formulation-driven | 175 | 0.63 [0.55, 0.70] |
| gold evidence in top-k | 102 | 0.63 [0.54, 0.73] |
| gold evidence not in top-k | 198 | 0.67 [0.61, 0.73] |

## Paired differences (file − `noretrieval`)

\* = 95% CI excludes 0.

| Comparison | Set | Accuracy | Macro-F1 | Recall disinformation |
|---|---|---:|---:|---:|
| bm25_k5 - noretrieval | article/test | +0.34* [+0.29, +0.38] | +0.45* [+0.41, +0.50] | +0.27* [+0.21, +0.32] |
| bm25_k5 - noretrieval | main/test | +0.04 [-0.03, +0.11] | +0.19* [+0.14, +0.24] | +0.74* [+0.68, +0.79] |
| bm25_sens_k5 - noretrieval | article/test | +0.34* [+0.30, +0.38] | +0.46* [+0.41, +0.51] | +0.29* [+0.23, +0.34] |
| bm25_sens_k5 - noretrieval | main/test | +0.02 [-0.05, +0.08] | +0.19* [+0.14, +0.23] | +0.65* [+0.60, +0.71] |

## Cost

| File | Mode | k | Prompt tokens (mean) | LLM s / query | GPU peak GB | Retrieval ms / query (p50) |
|---|---|---:|---:|---:|---:|---:|
| noretrieval | no_retrieval | 0 | 248.6 | 0.0619 | 15.48 | – |
| bm25_k5 | rag | 5 | 1371.7 | 0.3072 | 27.48 | – |
| bm25_sens_k5 | rag | 5 | 1476.4 | 0.327 | 27.48 | – |

Command: `eval_detection.py --queries ../../data/queries_v2.csv --preds v2_results/preds/test/noretrieval.csv v2_results/preds/test/bm25_k5.csv v2_results/preds/test/bm25_sens_k5.csv --retrieval ../v2_results/results/test_compare/retrieval_test.per_query.csv --output v2_results/results/test_fewshot/detection_test.csv`
