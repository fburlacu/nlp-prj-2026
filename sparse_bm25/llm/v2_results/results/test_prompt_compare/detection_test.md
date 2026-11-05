# Detection evaluation

Prediction files: `zs_noretrieval`, `zs_bm25_k5`, `zs_bm25_sens_k5`, `fs_noretrieval`, `fs_bm25_k5`, `fs_bm25_sens_k5` | 1104 queries | cells: mean [95% bootstrap CI, 1000 resamples]

Main set: disinformation vs inconclusive (case held out, the model should answer *unknown*). Article set: disinformation vs fact. Predictions are 3-way; off-label = a class outside the set's label space.

## zs_noretrieval

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

## zs_bm25_k5

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

## zs_bm25_sens_k5

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.50 [0.46, 0.54] | 0.57 [0.52, 0.61] | 0.23 [0.19, 0.27] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.71 [0.64, 0.78] | 0.46 [0.39, 0.51] | 0.56 [0.49, 0.61] |
| fact | 0.61 [0.55, 0.67] | 0.55 [0.49, 0.61] | 0.58 [0.53, 0.63] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 115 | 88 | 49 |
| fact | 46 | 139 | 67 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.26 [0.09, 0.43] |
| formulation-driven | 30 | 0.57 [0.40, 0.73] |
| gold evidence in top-k | 18 | 0.44 [0.22, 0.67] |
| gold evidence not in top-k | 35 | 0.43 [0.26, 0.60] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.50 [0.46, 0.54] | 0.34 [0.32, 0.36] | 0.01 [0.00, 0.01] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.50 [0.46, 0.54] | 0.99 [0.98, 1.00] | 0.67 [0.63, 0.70] |
| inconclusive | 1.00 [0.00, 1.00] | 0.00 [0.00, 0.01] | 0.01 [0.00, 0.02] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 298 | 2 | 0 |
| inconclusive | 298 | 1 | 1 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.99 [0.97, 1.00] |
| overlap: mid | 100 | 0.99 [0.97, 1.00] |
| overlap: high | 100 | 1.00 [1.00, 1.00] |
| length: short | 101 | 0.99 [0.97, 1.00] |
| length: medium | 103 | 1.00 [1.00, 1.00] |
| length: long | 96 | 0.99 [0.97, 1.00] |
| entity-driven | 125 | 1.00 [1.00, 1.00] |
| formulation-driven | 175 | 0.99 [0.97, 1.00] |
| gold evidence in top-k | 102 | 1.00 [1.00, 1.00] |
| gold evidence not in top-k | 198 | 0.99 [0.97, 1.00] |

## fs_noretrieval

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

## fs_bm25_k5

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.34 [0.29, 0.38] | 0.45 [0.41, 0.50] | 0.54 [0.50, 0.58] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.74 [0.64, 0.82] | 0.27 [0.21, 0.32] | 0.39 [0.33, 0.45] |
| fact | 0.72 [0.64, 0.79] | 0.40 [0.34, 0.47] | 0.52 [0.45, 0.58] |

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
| gold evidence not in top-k | 34 | 0.35 [0.21, 0.50] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.54 [0.50, 0.58] | 0.53 [0.49, 0.57] | 0.03 [0.01, 0.04] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.54 [0.49, 0.59] | 0.74 [0.69, 0.78] | 0.62 [0.58, 0.66] |
| inconclusive | 0.58 [0.51, 0.65] | 0.34 [0.29, 0.39] | 0.43 [0.37, 0.48] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 221 | 6 | 73 |
| inconclusive | 189 | 9 | 102 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.66 [0.57, 0.75] |
| overlap: mid | 100 | 0.74 [0.65, 0.83] |
| overlap: high | 100 | 0.81 [0.73, 0.88] |
| length: short | 101 | 0.71 [0.63, 0.80] |
| length: medium | 103 | 0.75 [0.66, 0.83] |
| length: long | 96 | 0.75 [0.67, 0.83] |
| entity-driven | 125 | 0.75 [0.67, 0.82] |
| formulation-driven | 175 | 0.73 [0.66, 0.78] |
| gold evidence in top-k | 102 | 0.78 [0.71, 0.86] |
| gold evidence not in top-k | 198 | 0.71 [0.64, 0.78] |

## fs_bm25_sens_k5

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.34 [0.30, 0.38] | 0.46 [0.41, 0.50] | 0.53 [0.49, 0.57] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.73 [0.65, 0.82] | 0.29 [0.23, 0.34] | 0.41 [0.34, 0.47] |
| fact | 0.72 [0.64, 0.79] | 0.40 [0.34, 0.46] | 0.51 [0.45, 0.57] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 72 | 39 | 141 |
| fact | 26 | 100 | 126 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.26 [0.09, 0.43] |
| formulation-driven | 30 | 0.47 [0.27, 0.63] |
| gold evidence in top-k | 18 | 0.39 [0.17, 0.61] |
| gold evidence not in top-k | 35 | 0.37 [0.20, 0.51] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.52 [0.48, 0.56] | 0.52 [0.48, 0.56] | 0.05 [0.03, 0.07] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.54 [0.49, 0.59] | 0.65 [0.60, 0.70] | 0.59 [0.55, 0.64] |
| inconclusive | 0.56 [0.49, 0.63] | 0.38 [0.33, 0.44] | 0.45 [0.40, 0.51] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 196 | 13 | 91 |
| inconclusive | 168 | 17 | 115 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.64 [0.54, 0.73] |
| overlap: mid | 100 | 0.66 [0.57, 0.75] |
| overlap: high | 100 | 0.66 [0.57, 0.75] |
| length: short | 101 | 0.61 [0.51, 0.70] |
| length: medium | 103 | 0.63 [0.54, 0.73] |
| length: long | 96 | 0.72 [0.62, 0.81] |
| entity-driven | 125 | 0.69 [0.60, 0.77] |
| formulation-driven | 175 | 0.63 [0.55, 0.70] |
| gold evidence in top-k | 102 | 0.63 [0.53, 0.73] |
| gold evidence not in top-k | 198 | 0.67 [0.61, 0.73] |

## Paired differences (file − `zs_noretrieval`)

\* = 95% CI excludes 0.

| Comparison | Set | Accuracy | Macro-F1 | Recall disinformation |
|---|---|---:|---:|---:|
| zs_bm25_k5 - zs_noretrieval | article/test | +0.43* [+0.38, +0.47] | +0.43* [+0.38, +0.48] | +0.43* [+0.37, +0.49] |
| zs_bm25_k5 - zs_noretrieval | main/test | +0.01 [-0.07, +0.08] | -0.07* [-0.11, -0.02] | +0.90* [+0.86, +0.93] |
| zs_bm25_sens_k5 - zs_noretrieval | article/test | +0.42* [+0.37, +0.46] | +0.42* [+0.37, +0.48] | +0.43* [+0.37, +0.49] |
| zs_bm25_sens_k5 - zs_noretrieval | main/test | +0.01 [-0.07, +0.08] | -0.07* [-0.12, -0.02] | +0.90* [+0.86, +0.93] |
| fs_noretrieval - zs_noretrieval | article/test | -0.09* [-0.11, -0.06] | -0.15* [-0.18, -0.11] | -0.03* [-0.05, -0.01] |
| fs_noretrieval - zs_noretrieval | main/test | +0.01 [-0.02, +0.03] | -0.07* [-0.10, -0.04] | -0.10* [-0.13, -0.07] |
| fs_bm25_k5 - zs_noretrieval | article/test | +0.25* [+0.21, +0.29] | +0.31* [+0.25, +0.36] | +0.24* [+0.18, +0.29] |
| fs_bm25_k5 - zs_noretrieval | main/test | +0.04 [-0.02, +0.11] | +0.12* [+0.07, +0.17] | +0.64* [+0.58, +0.69] |
| fs_bm25_sens_k5 - zs_noretrieval | article/test | +0.26* [+0.22, +0.30] | +0.32* [+0.27, +0.37] | +0.26* [+0.20, +0.31] |
| fs_bm25_sens_k5 - zs_noretrieval | main/test | +0.02 [-0.04, +0.08] | +0.12* [+0.06, +0.17] | +0.56* [+0.50, +0.62] |

## Cost

| File | Mode | k | Prompt tokens (mean) | LLM s / query | GPU peak GB | Retrieval ms / query (p50) |
|---|---|---:|---:|---:|---:|---:|
| zs_noretrieval | no_retrieval | 0 | 140.6 | 0.0071 | 15.62 | – |
| zs_bm25_k5 | rag | 5 | 1319.5 | 0.1039 | 27.37 | – |
| zs_bm25_sens_k5 | rag | 5 | 1424.2 | 0.1137 | 27.37 | – |
| fs_noretrieval | no_retrieval | 0 | 248.6 | 0.0619 | 15.48 | – |
| fs_bm25_k5 | rag | 5 | 1371.7 | 0.3072 | 27.48 | – |
| fs_bm25_sens_k5 | rag | 5 | 1476.4 | 0.327 | 27.48 | – |

Command: `eval_detection.py --queries ../../data/queries_v2.csv --preds /private/tmp/claude-501/-Users-fel-Documents-uni-nlp/d4cd6b14-020b-48f1-ac9a-f4006bd86f2c/scratchpad/cmp/zs_noretrieval.csv /private/tmp/claude-501/-Users-fel-Documents-uni-nlp/d4cd6b14-020b-48f1-ac9a-f4006bd86f2c/scratchpad/cmp/zs_bm25_k5.csv /private/tmp/claude-501/-Users-fel-Documents-uni-nlp/d4cd6b14-020b-48f1-ac9a-f4006bd86f2c/scratchpad/cmp/zs_bm25_sens_k5.csv /private/tmp/claude-501/-Users-fel-Documents-uni-nlp/d4cd6b14-020b-48f1-ac9a-f4006bd86f2c/scratchpad/cmp/fs_noretrieval.csv /private/tmp/claude-501/-Users-fel-Documents-uni-nlp/d4cd6b14-020b-48f1-ac9a-f4006bd86f2c/scratchpad/cmp/fs_bm25_k5.csv /private/tmp/claude-501/-Users-fel-Documents-uni-nlp/d4cd6b14-020b-48f1-ac9a-f4006bd86f2c/scratchpad/cmp/fs_bm25_sens_k5.csv --retrieval ../v2_results/results/test_compare/retrieval_test.per_query.csv --output v2_results/results/test_prompt_compare/detection_test.csv`
