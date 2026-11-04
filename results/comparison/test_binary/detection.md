# Detection evaluation

Prediction files: `title_bm25_none`, `title_bm25_cross`, `title_bm25_late`, `title_dense_none`, `title_dense_cross`, `title_dense_late`, `title_late_none` | 504 queries | cells: mean [95% bootstrap CI, 1000 resamples]

Leite articles only. The model answers disinformation or fact. Off-label is a prediction outside those two words.

## title_bm25_none

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.62 [0.58, 0.66] | 0.59 [0.55, 0.63] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.58 [0.53, 0.63] | 0.88 [0.84, 0.92] | 0.70 [0.66, 0.74] |
| fact | 0.75 [0.68, 0.83] | 0.36 [0.30, 0.42] | 0.48 [0.42, 0.54] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 222 | 30 | 0 |
| fact | 162 | 90 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.78 [0.61, 0.91] |
| formulation-driven | 30 | 0.90 [0.80, 1.00] |

## title_bm25_cross

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.60 [0.56, 0.64] | 0.58 [0.54, 0.62] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.57 [0.52, 0.62] | 0.83 [0.79, 0.88] | 0.68 [0.63, 0.72] |
| fact | 0.69 [0.62, 0.78] | 0.37 [0.32, 0.43] | 0.48 [0.42, 0.54] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 210 | 42 | 0 |
| fact | 158 | 94 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.91 [0.78, 1.00] |
| formulation-driven | 30 | 0.83 [0.70, 0.97] |

## title_bm25_late

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.61 [0.56, 0.65] | 0.59 [0.54, 0.63] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.58 [0.52, 0.62] | 0.81 [0.76, 0.85] | 0.67 [0.63, 0.71] |
| fact | 0.68 [0.60, 0.75] | 0.40 [0.34, 0.46] | 0.51 [0.45, 0.56] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 204 | 48 | 0 |
| fact | 150 | 102 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.96 [0.87, 1.00] |
| formulation-driven | 30 | 0.83 [0.70, 0.93] |

## title_dense_none

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.59 [0.55, 0.63] | 0.57 [0.53, 0.61] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.56 [0.51, 0.61] | 0.78 [0.73, 0.83] | 0.65 [0.61, 0.70] |
| fact | 0.64 [0.56, 0.71] | 0.39 [0.33, 0.45] | 0.48 [0.42, 0.54] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 197 | 55 | 0 |
| fact | 154 | 98 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.65 [0.48, 0.83] |
| formulation-driven | 30 | 0.83 [0.67, 0.97] |

## title_dense_cross

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.61 [0.56, 0.65] | 0.58 [0.54, 0.62] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.57 [0.52, 0.62] | 0.85 [0.81, 0.89] | 0.68 [0.64, 0.72] |
| fact | 0.71 [0.64, 0.79] | 0.36 [0.31, 0.42] | 0.48 [0.42, 0.54] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 215 | 37 | 0 |
| fact | 161 | 91 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.83 [0.65, 0.96] |
| formulation-driven | 30 | 0.90 [0.80, 1.00] |

## title_dense_late

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.61 [0.56, 0.65] | 0.59 [0.54, 0.63] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.57 [0.52, 0.63] | 0.81 [0.76, 0.86] | 0.67 [0.63, 0.72] |
| fact | 0.68 [0.60, 0.76] | 0.40 [0.34, 0.47] | 0.50 [0.44, 0.56] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 204 | 48 | 0 |
| fact | 151 | 101 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.96 [0.87, 1.00] |
| formulation-driven | 30 | 0.87 [0.73, 0.97] |

## title_late_none

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.60 [0.56, 0.64] | 0.58 [0.54, 0.62] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.57 [0.52, 0.62] | 0.80 [0.75, 0.85] | 0.67 [0.62, 0.70] |
| fact | 0.66 [0.58, 0.74] | 0.39 [0.33, 0.45] | 0.49 [0.43, 0.55] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 202 | 50 | 0 |
| fact | 153 | 99 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.91 [0.78, 1.00] |
| formulation-driven | 30 | 0.83 [0.70, 0.97] |

## Paired differences (file − `title_bm25_none`)

\* = 95% CI excludes 0.

| Comparison | Set | Accuracy | Macro-F1 | Recall disinformation |
|---|---|---:|---:|---:|
| title_bm25_cross - title_bm25_none | article/test | -0.02 [-0.05, +0.02] | -0.01 [-0.05, +0.03] | -0.05 [-0.10, +0.00] |
| title_bm25_late - title_bm25_none | article/test | -0.01 [-0.05, +0.03] | -0.00 [-0.04, +0.04] | -0.07* [-0.12, -0.02] |
| title_dense_none - title_bm25_none | article/test | -0.03 [-0.07, +0.00] | -0.02 [-0.06, +0.02] | -0.10* [-0.15, -0.04] |
| title_dense_cross - title_bm25_none | article/test | -0.01 [-0.05, +0.02] | -0.01 [-0.05, +0.03] | -0.03 [-0.08, +0.02] |
| title_dense_late - title_bm25_none | article/test | -0.01 [-0.05, +0.02] | -0.00 [-0.04, +0.03] | -0.07* [-0.12, -0.02] |
| title_late_none - title_bm25_none | article/test | -0.02 [-0.06, +0.01] | -0.01 [-0.06, +0.03] | -0.08* [-0.13, -0.03] |

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

Command: `/home/jovyan/nlp-prj-2026/analysis/eval_detection.py --preds /home/jovyan/nlp-prj-2026/results/comparison/test_binary/predictions/title_bm25_none.csv /home/jovyan/nlp-prj-2026/results/comparison/test_binary/predictions/title_bm25_cross.csv /home/jovyan/nlp-prj-2026/results/comparison/test_binary/predictions/title_bm25_late.csv /home/jovyan/nlp-prj-2026/results/comparison/test_binary/predictions/title_dense_none.csv /home/jovyan/nlp-prj-2026/results/comparison/test_binary/predictions/title_dense_cross.csv /home/jovyan/nlp-prj-2026/results/comparison/test_binary/predictions/title_dense_late.csv /home/jovyan/nlp-prj-2026/results/comparison/test_binary/predictions/title_late_none.csv --queries /home/jovyan/nlp-prj-2026/data/queries_v2.csv --task binary --output /home/jovyan/nlp-prj-2026/results/comparison/test_binary/detection.csv`
