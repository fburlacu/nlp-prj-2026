# Detection evaluation

Prediction files: `title_bm25_none`, `title_bm25_cross`, `title_bm25_late`, `title_dense_none`, `title_dense_cross`, `title_dense_late`, `title_late_none` | 1104 queries | cells: mean [95% bootstrap CI, 1000 resamples]

Main set: disinformation vs inconclusive (case held out, the model should answer *unknown*). Article set: disinformation vs fact. Predictions are 3-way; off-label = a class outside the set's label space.

## title_bm25_none

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.33 [0.29, 0.37] | 0.45 [0.40, 0.49] | 0.54 [0.50, 0.59] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.73 [0.63, 0.82] | 0.27 [0.22, 0.33] | 0.39 [0.33, 0.46] |
| fact | 0.71 [0.63, 0.79] | 0.39 [0.33, 0.45] | 0.50 [0.44, 0.56] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 68 | 40 | 144 |
| fact | 25 | 98 | 129 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.30 [0.13, 0.48] |
| formulation-driven | 30 | 0.50 [0.33, 0.67] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.55 [0.51, 0.59] | 0.53 [0.50, 0.58] | 0.03 [0.01, 0.04] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.54 [0.49, 0.59] | 0.74 [0.69, 0.80] | 0.63 [0.58, 0.67] |
| inconclusive | 0.60 [0.53, 0.68] | 0.35 [0.30, 0.40] | 0.44 [0.38, 0.50] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 223 | 7 | 70 |
| inconclusive | 188 | 8 | 104 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.69 [0.60, 0.77] |
| overlap: mid | 100 | 0.74 [0.65, 0.83] |
| overlap: high | 100 | 0.80 [0.72, 0.88] |
| length: short | 101 | 0.72 [0.62, 0.81] |
| length: medium | 103 | 0.74 [0.64, 0.83] |
| length: long | 96 | 0.77 [0.69, 0.85] |
| entity-driven | 125 | 0.76 [0.69, 0.83] |
| formulation-driven | 175 | 0.73 [0.67, 0.79] |

## title_bm25_cross

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.32 [0.28, 0.37] | 0.43 [0.38, 0.48] | 0.53 [0.48, 0.57] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.67 [0.57, 0.77] | 0.24 [0.19, 0.29] | 0.35 [0.28, 0.42] |
| fact | 0.69 [0.62, 0.76] | 0.41 [0.35, 0.47] | 0.51 [0.45, 0.57] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 60 | 46 | 146 |
| fact | 29 | 103 | 120 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.39 [0.22, 0.61] |
| formulation-driven | 30 | 0.40 [0.23, 0.60] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.52 [0.48, 0.56] | 0.52 [0.48, 0.56] | 0.04 [0.03, 0.06] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.53 [0.48, 0.58] | 0.69 [0.64, 0.74] | 0.60 [0.55, 0.64] |
| inconclusive | 0.57 [0.50, 0.65] | 0.35 [0.30, 0.40] | 0.43 [0.38, 0.49] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 207 | 15 | 78 |
| inconclusive | 183 | 12 | 105 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.62 [0.52, 0.71] |
| overlap: mid | 100 | 0.77 [0.69, 0.85] |
| overlap: high | 100 | 0.68 [0.58, 0.77] |
| length: short | 101 | 0.66 [0.57, 0.76] |
| length: medium | 103 | 0.65 [0.56, 0.75] |
| length: long | 96 | 0.76 [0.68, 0.84] |
| entity-driven | 125 | 0.70 [0.62, 0.78] |
| formulation-driven | 175 | 0.69 [0.62, 0.75] |

## title_bm25_late

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.35 [0.31, 0.39] | 0.46 [0.41, 0.50] | 0.48 [0.44, 0.52] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.68 [0.58, 0.76] | 0.29 [0.23, 0.34] | 0.40 [0.34, 0.46] |
| fact | 0.66 [0.59, 0.73] | 0.41 [0.35, 0.47] | 0.51 [0.44, 0.56] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 72 | 53 | 127 |
| fact | 34 | 104 | 114 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.35 [0.17, 0.57] |
| formulation-driven | 30 | 0.53 [0.37, 0.73] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.48 [0.45, 0.52] | 0.47 [0.44, 0.51] | 0.05 [0.03, 0.07] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.51 [0.46, 0.56] | 0.69 [0.64, 0.74] | 0.59 [0.54, 0.63] |
| inconclusive | 0.52 [0.44, 0.59] | 0.28 [0.23, 0.33] | 0.36 [0.31, 0.42] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 207 | 14 | 79 |
| inconclusive | 200 | 16 | 84 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.61 [0.52, 0.70] |
| overlap: mid | 100 | 0.78 [0.70, 0.86] |
| overlap: high | 100 | 0.68 [0.58, 0.77] |
| length: short | 101 | 0.68 [0.59, 0.77] |
| length: medium | 103 | 0.65 [0.56, 0.74] |
| length: long | 96 | 0.74 [0.66, 0.82] |
| entity-driven | 125 | 0.69 [0.61, 0.77] |
| formulation-driven | 175 | 0.69 [0.62, 0.76] |

## title_dense_none

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.34 [0.29, 0.38] | 0.44 [0.40, 0.49] | 0.50 [0.46, 0.54] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.69 [0.60, 0.78] | 0.27 [0.21, 0.32] | 0.39 [0.32, 0.45] |
| fact | 0.66 [0.58, 0.73] | 0.40 [0.34, 0.46] | 0.50 [0.44, 0.56] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 68 | 52 | 132 |
| fact | 30 | 101 | 121 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.30 [0.13, 0.48] |
| formulation-driven | 30 | 0.43 [0.27, 0.60] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.51 [0.47, 0.55] | 0.48 [0.44, 0.52] | 0.02 [0.01, 0.04] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.52 [0.47, 0.56] | 0.79 [0.74, 0.84] | 0.63 [0.58, 0.66] |
| inconclusive | 0.55 [0.46, 0.63] | 0.24 [0.19, 0.29] | 0.33 [0.27, 0.39] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 237 | 4 | 59 |
| inconclusive | 219 | 10 | 71 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.75 [0.66, 0.83] |
| overlap: mid | 100 | 0.83 [0.76, 0.90] |
| overlap: high | 100 | 0.79 [0.71, 0.87] |
| length: short | 101 | 0.69 [0.60, 0.78] |
| length: medium | 103 | 0.80 [0.71, 0.86] |
| length: long | 96 | 0.89 [0.82, 0.94] |
| entity-driven | 125 | 0.78 [0.70, 0.85] |
| formulation-driven | 175 | 0.80 [0.74, 0.86] |

## title_dense_cross

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.32 [0.29, 0.36] | 0.44 [0.39, 0.48] | 0.54 [0.50, 0.58] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.69 [0.59, 0.78] | 0.26 [0.21, 0.31] | 0.38 [0.31, 0.44] |
| fact | 0.72 [0.64, 0.79] | 0.38 [0.32, 0.44] | 0.50 [0.44, 0.56] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 66 | 38 | 148 |
| fact | 30 | 97 | 125 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.39 [0.17, 0.61] |
| formulation-driven | 30 | 0.40 [0.23, 0.57] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.55 [0.51, 0.59] | 0.53 [0.49, 0.57] | 0.02 [0.01, 0.03] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.55 [0.50, 0.59] | 0.80 [0.75, 0.84] | 0.65 [0.61, 0.69] |
| inconclusive | 0.62 [0.54, 0.70] | 0.31 [0.26, 0.36] | 0.41 [0.35, 0.47] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 239 | 4 | 57 |
| inconclusive | 199 | 8 | 93 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.78 [0.69, 0.85] |
| overlap: mid | 100 | 0.78 [0.69, 0.86] |
| overlap: high | 100 | 0.83 [0.75, 0.90] |
| length: short | 101 | 0.71 [0.63, 0.80] |
| length: medium | 103 | 0.82 [0.74, 0.88] |
| length: long | 96 | 0.86 [0.79, 0.93] |
| entity-driven | 125 | 0.80 [0.73, 0.87] |
| formulation-driven | 175 | 0.79 [0.73, 0.85] |

## title_dense_late

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.36 [0.32, 0.40] | 0.47 [0.42, 0.51] | 0.47 [0.42, 0.51] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.69 [0.60, 0.77] | 0.29 [0.23, 0.34] | 0.40 [0.34, 0.46] |
| fact | 0.67 [0.60, 0.74] | 0.44 [0.38, 0.49] | 0.53 [0.47, 0.58] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 72 | 54 | 126 |
| fact | 33 | 110 | 109 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.35 [0.17, 0.57] |
| formulation-driven | 30 | 0.57 [0.40, 0.73] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.53 [0.49, 0.57] | 0.48 [0.44, 0.52] | 0.02 [0.01, 0.03] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.53 [0.48, 0.57] | 0.86 [0.82, 0.90] | 0.65 [0.61, 0.69] |
| inconclusive | 0.62 [0.53, 0.72] | 0.21 [0.16, 0.26] | 0.31 [0.25, 0.37] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 257 | 5 | 38 |
| inconclusive | 229 | 8 | 63 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.83 [0.75, 0.90] |
| overlap: mid | 100 | 0.85 [0.77, 0.92] |
| overlap: high | 100 | 0.89 [0.82, 0.94] |
| length: short | 101 | 0.74 [0.65, 0.82] |
| length: medium | 103 | 0.87 [0.81, 0.93] |
| length: long | 96 | 0.96 [0.91, 0.99] |
| entity-driven | 125 | 0.82 [0.74, 0.89] |
| formulation-driven | 175 | 0.89 [0.83, 0.93] |

## title_late_none

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.36 [0.32, 0.41] | 0.47 [0.43, 0.52] | 0.48 [0.43, 0.52] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.71 [0.62, 0.79] | 0.30 [0.24, 0.35] | 0.42 [0.35, 0.48] |
| fact | 0.69 [0.61, 0.76] | 0.43 [0.37, 0.49] | 0.53 [0.47, 0.58] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 75 | 49 | 128 |
| fact | 31 | 108 | 113 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.39 [0.22, 0.61] |
| formulation-driven | 30 | 0.53 [0.33, 0.70] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.48 [0.45, 0.52] | 0.47 [0.44, 0.51] | 0.06 [0.04, 0.08] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.51 [0.46, 0.56] | 0.70 [0.65, 0.75] | 0.59 [0.55, 0.63] |
| inconclusive | 0.53 [0.45, 0.60] | 0.27 [0.22, 0.32] | 0.36 [0.30, 0.41] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 210 | 17 | 73 |
| inconclusive | 200 | 19 | 81 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| overlap: low | 100 | 0.63 [0.53, 0.72] |
| overlap: mid | 100 | 0.77 [0.69, 0.85] |
| overlap: high | 100 | 0.70 [0.61, 0.79] |
| length: short | 101 | 0.69 [0.59, 0.78] |
| length: medium | 103 | 0.68 [0.58, 0.77] |
| length: long | 96 | 0.73 [0.65, 0.81] |
| entity-driven | 125 | 0.69 [0.61, 0.77] |
| formulation-driven | 175 | 0.71 [0.64, 0.77] |

## Paired differences (file − `title_bm25_none`)

\* = 95% CI excludes 0.

| Comparison | Set | Accuracy | Macro-F1 | Recall disinformation |
|---|---|---:|---:|---:|
| title_bm25_cross - title_bm25_none | article/test | -0.01 [-0.05, +0.04] | -0.02 [-0.06, +0.04] | -0.03 [-0.08, +0.03] |
| title_bm25_cross - title_bm25_none | main/test | -0.03 [-0.07, +0.02] | -0.02 [-0.06, +0.03] | -0.05 [-0.11, +0.00] |
| title_bm25_late - title_bm25_none | article/test | +0.02 [-0.02, +0.06] | +0.01 [-0.04, +0.05] | +0.02 [-0.04, +0.07] |
| title_bm25_late - title_bm25_none | main/test | -0.06* [-0.10, -0.02] | -0.06* [-0.10, -0.02] | -0.05 [-0.11, +0.01] |
| title_dense_none - title_bm25_none | article/test | +0.01 [-0.04, +0.05] | -0.00 [-0.05, +0.04] | +0.00 [-0.06, +0.05] |
| title_dense_none - title_bm25_none | main/test | -0.03 [-0.08, +0.01] | -0.05* [-0.10, -0.01] | +0.05 [-0.01, +0.11] |
| title_dense_cross - title_bm25_none | article/test | -0.01 [-0.05, +0.03] | -0.01 [-0.05, +0.04] | -0.01 [-0.07, +0.05] |
| title_dense_cross - title_bm25_none | main/test | +0.01 [-0.03, +0.05] | -0.00 [-0.05, +0.04] | +0.05 [-0.01, +0.11] |
| title_dense_late - title_bm25_none | article/test | +0.03 [-0.01, +0.07] | +0.02 [-0.03, +0.06] | +0.02 [-0.04, +0.07] |
| title_dense_late - title_bm25_none | main/test | -0.01 [-0.05, +0.03] | -0.05* [-0.10, -0.01] | +0.11* [+0.06, +0.17] |
| title_late_none - title_bm25_none | article/test | +0.03 [-0.00, +0.07] | +0.03 [-0.02, +0.07] | +0.03 [-0.02, +0.08] |
| title_late_none - title_bm25_none | main/test | -0.06* [-0.10, -0.02] | -0.06* [-0.10, -0.02] | -0.04 [-0.10, +0.01] |

## Cost

| File | Mode | k | Prompt tokens (mean) | LLM s / query | GPU peak GB | Retrieval ms / query (p50) |
|---|---|---:|---:|---:|---:|---:|
| title_bm25_none | ? | None | None | None | None | – |
| title_bm25_cross | ? | None | None | None | None | – |
| title_bm25_late | ? | None | None | None | None | – |
| title_dense_none | ? | None | None | None | None | – |
| title_dense_cross | ? | None | None | None | None | – |
| title_dense_late | ? | None | None | None | None | – |
| title_late_none | ? | None | None | None | None | – |

Command: `/home/jovyan/nlp-prj-2026/analysis/eval_detection.py --preds /home/jovyan/nlp-prj-2026/results/comparison/test/predictions/title_bm25_none.csv /home/jovyan/nlp-prj-2026/results/comparison/test/predictions/title_bm25_cross.csv /home/jovyan/nlp-prj-2026/results/comparison/test/predictions/title_bm25_late.csv /home/jovyan/nlp-prj-2026/results/comparison/test/predictions/title_dense_none.csv /home/jovyan/nlp-prj-2026/results/comparison/test/predictions/title_dense_cross.csv /home/jovyan/nlp-prj-2026/results/comparison/test/predictions/title_dense_late.csv /home/jovyan/nlp-prj-2026/results/comparison/test/predictions/title_late_none.csv --queries /home/jovyan/nlp-prj-2026/data/queries_v2.csv --retrieval /home/jovyan/nlp-prj-2026/results/comparison/test/retrieval.per_query.csv --output /home/jovyan/nlp-prj-2026/results/comparison/test/detection.csv`
