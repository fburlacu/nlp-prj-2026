# Comparison, dev, fact versus disinformation

Included: title_bm25_none, title_bm25_cross, title_bm25_late, title_dense_none, title_dense_cross, title_dense_late, title_late_none.
Not run yet: none.

Leite articles only. The verdict model chooses disinformation or fact.
These files do not replace the three-way comparison.
# Detection evaluation

Prediction files: `title_bm25_none`, `title_bm25_cross`, `title_bm25_late`, `title_dense_none`, `title_dense_cross`, `title_dense_late`, `title_late_none` | 102 queries | cells: mean [95% bootstrap CI, 1000 resamples]

Leite articles only. The model answers disinformation or fact. Off-label is a prediction outside those two words.

## title_bm25_none

### article/dev (n = 102)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.65 [0.55, 0.74] | 0.62 [0.52, 0.71] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.60 [0.49, 0.70] | 0.90 [0.81, 0.98] | 0.72 [0.62, 0.80] |
| fact | 0.80 [0.61, 0.95] | 0.39 [0.26, 0.53] | 0.53 [0.37, 0.66] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 46 | 5 | 0 |
| fact | 31 | 20 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 7 | 1.00 [1.00, 1.00] |
| formulation-driven | 7 | 0.86 [0.57, 1.00] |

## title_bm25_cross

### article/dev (n = 102)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.63 [0.53, 0.72] | 0.61 [0.51, 0.70] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.59 [0.47, 0.70] | 0.84 [0.73, 0.94] | 0.69 [0.59, 0.78] |
| fact | 0.72 [0.54, 0.88] | 0.41 [0.28, 0.54] | 0.53 [0.38, 0.65] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 43 | 8 | 0 |
| fact | 30 | 21 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 7 | 1.00 [1.00, 1.00] |
| formulation-driven | 7 | 0.71 [0.43, 1.00] |

## title_bm25_late

### article/dev (n = 102)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.66 [0.57, 0.75] | 0.64 [0.54, 0.74] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.61 [0.50, 0.73] | 0.86 [0.77, 0.94] | 0.72 [0.62, 0.80] |
| fact | 0.77 [0.61, 0.90] | 0.45 [0.31, 0.59] | 0.57 [0.43, 0.69] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 44 | 7 | 0 |
| fact | 28 | 23 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 7 | 1.00 [1.00, 1.00] |
| formulation-driven | 7 | 0.71 [0.29, 1.00] |

## title_dense_none

### article/dev (n = 102)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.67 [0.57, 0.76] | 0.65 [0.55, 0.75] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.62 [0.50, 0.74] | 0.86 [0.76, 0.95] | 0.72 [0.62, 0.81] |
| fact | 0.77 [0.62, 0.92] | 0.47 [0.33, 0.62] | 0.59 [0.45, 0.70] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 44 | 7 | 0 |
| fact | 27 | 24 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 7 | 1.00 [1.00, 1.00] |
| formulation-driven | 7 | 0.71 [0.43, 1.00] |

## title_dense_cross

### article/dev (n = 102)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.58 [0.49, 0.67] | 0.56 [0.46, 0.64] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.55 [0.44, 0.66] | 0.80 [0.69, 0.91] | 0.66 [0.56, 0.74] |
| fact | 0.64 [0.46, 0.82] | 0.35 [0.22, 0.48] | 0.46 [0.32, 0.57] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 41 | 10 | 0 |
| fact | 33 | 18 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 7 | 1.00 [1.00, 1.00] |
| formulation-driven | 7 | 0.57 [0.29, 1.00] |

## title_dense_late

### article/dev (n = 102)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.63 [0.53, 0.72] | 0.61 [0.51, 0.70] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.59 [0.48, 0.70] | 0.84 [0.74, 0.94] | 0.69 [0.60, 0.78] |
| fact | 0.72 [0.56, 0.88] | 0.41 [0.29, 0.55] | 0.53 [0.39, 0.64] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 43 | 8 | 0 |
| fact | 30 | 21 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 7 | 1.00 [1.00, 1.00] |
| formulation-driven | 7 | 0.86 [0.57, 1.00] |

## title_late_none

### article/dev (n = 102)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.66 [0.56, 0.75] | 0.64 [0.53, 0.73] | 0.00 [0.00, 0.00] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.61 [0.49, 0.71] | 0.88 [0.79, 0.96] | 0.72 [0.62, 0.80] |
| fact | 0.79 [0.62, 0.93] | 0.43 [0.29, 0.57] | 0.56 [0.41, 0.68] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 45 | 6 | 0 |
| fact | 29 | 22 | 0 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 7 | 1.00 [1.00, 1.00] |
| formulation-driven | 7 | 0.86 [0.57, 1.00] |

## Paired differences (file − `title_bm25_none`)

\* = 95% CI excludes 0.

| Comparison | Set | Accuracy | Macro-F1 | Recall disinformation |
|---|---|---:|---:|---:|
| title_bm25_cross - title_bm25_none | article/dev | -0.02 [-0.11, +0.07] | -0.01 [-0.11, +0.09] | -0.06 [-0.15, +0.02] |
| title_bm25_late - title_bm25_none | article/dev | +0.01 [-0.06, +0.08] | +0.02 [-0.06, +0.10] | -0.04 [-0.10, +0.00] |
| title_dense_none - title_bm25_none | article/dev | +0.02 [-0.06, +0.10] | +0.03 [-0.05, +0.11] | -0.04 [-0.14, +0.05] |
| title_dense_cross - title_bm25_none | article/dev | -0.07 [-0.15, +0.01] | -0.07 [-0.16, +0.02] | -0.10 [-0.20, +0.00] |
| title_dense_late - title_bm25_none | article/dev | -0.02 [-0.10, +0.05] | -0.01 [-0.10, +0.06] | -0.06 [-0.16, +0.02] |
| title_late_none - title_bm25_none | article/dev | +0.01 [-0.05, +0.07] | +0.02 [-0.05, +0.09] | -0.02 [-0.07, +0.00] |

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

Command: `/home/jovyan/nlp-prj-2026/analysis/eval_detection.py --preds /home/jovyan/nlp-prj-2026/results/comparison/dev_binary/predictions/title_bm25_none.csv /home/jovyan/nlp-prj-2026/results/comparison/dev_binary/predictions/title_bm25_cross.csv /home/jovyan/nlp-prj-2026/results/comparison/dev_binary/predictions/title_bm25_late.csv /home/jovyan/nlp-prj-2026/results/comparison/dev_binary/predictions/title_dense_none.csv /home/jovyan/nlp-prj-2026/results/comparison/dev_binary/predictions/title_dense_cross.csv /home/jovyan/nlp-prj-2026/results/comparison/dev_binary/predictions/title_dense_late.csv /home/jovyan/nlp-prj-2026/results/comparison/dev_binary/predictions/title_late_none.csv --queries /home/jovyan/nlp-prj-2026/data/queries_v2.csv --task binary --output /home/jovyan/nlp-prj-2026/results/comparison/dev_binary/detection.csv`
