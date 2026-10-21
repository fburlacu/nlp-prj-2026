# Detection evaluation

Prediction files: `dense_v2_verdicts` | 1296 queries | cells: mean [95% bootstrap CI, 1000 resamples]

Main set: disinformation vs inconclusive (case held out, the model should answer *unknown*). Article set: disinformation vs fact. Predictions are 3-way; off-label = a class outside the set's label space.

## dense_v2_verdicts

### article/dev (n = 102)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.46 [0.36, 0.56] | 0.58 [0.47, 0.67] | 0.40 [0.31, 0.49] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.79 [0.63, 0.93] | 0.43 [0.29, 0.56] | 0.56 [0.42, 0.67] |
| fact | 0.76 [0.61, 0.89] | 0.49 [0.35, 0.62] | 0.60 [0.46, 0.72] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 22 | 8 | 21 |
| fact | 6 | 25 | 20 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 7 | 0.29 [0.00, 0.57] |
| formulation-driven | 7 | 0.43 [0.14, 0.71] |

### article/test (n = 504)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.34 [0.30, 0.38] | 0.45 [0.40, 0.50] | 0.50 [0.45, 0.54] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.70 [0.61, 0.79] | 0.28 [0.23, 0.33] | 0.40 [0.34, 0.46] |
| fact | 0.67 [0.59, 0.74] | 0.40 [0.35, 0.46] | 0.50 [0.44, 0.56] |

Confusion (rows: gold, columns: predicted)

| | disinformation | fact | inconclusive |
|---|---:|---:|---:|
| disinformation | 71 | 51 | 130 |
| fact | 30 | 102 | 120 |

Disinformation recall by group

| Group | n | Recall |
|---|---:|---:|
| entity-driven | 23 | 0.35 [0.17, 0.52] |
| formulation-driven | 30 | 0.47 [0.30, 0.63] |
| gold evidence in top-k | 20 | 0.50 [0.30, 0.70] |
| gold evidence not in top-k | 33 | 0.36 [0.18, 0.55] |

### main/dev (n = 90)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.48 [0.38, 0.58] | 0.41 [0.32, 0.52] | 0.03 [0.00, 0.07] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.49 [0.38, 0.60] | 0.82 [0.71, 0.93] | 0.61 [0.51, 0.70] |
| inconclusive | 0.55 [0.25, 0.85] | 0.13 [0.04, 0.24] | 0.21 [0.08, 0.36] |

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
| formulation-driven | 29 | 0.83 [0.69, 0.97] |

### main/test (n = 600)

| Accuracy | Macro-F1 | Off-label |
|---:|---:|---:|
| 0.51 [0.47, 0.55] | 0.47 [0.43, 0.51] | 0.02 [0.01, 0.04] |

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| disinformation | 0.52 [0.47, 0.56] | 0.79 [0.74, 0.84] | 0.63 [0.58, 0.66] |
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
| length: short | 101 | 0.70 [0.61, 0.79] |
| length: medium | 103 | 0.80 [0.72, 0.87] |
| length: long | 96 | 0.88 [0.81, 0.94] |
| entity-driven | 125 | 0.80 [0.72, 0.86] |
| formulation-driven | 175 | 0.78 [0.72, 0.84] |
| gold evidence in top-k | 102 | 0.78 [0.70, 0.85] |
| gold evidence not in top-k | 198 | 0.79 [0.73, 0.85] |

## Cost

| File | Mode | k | Prompt tokens (mean) | LLM s / query | GPU peak GB | Retrieval ms / query (p50) |
|---|---|---:|---:|---:|---:|---:|
| dense_v2_verdicts | rag | 5 | None | None | None | – |

Command: `sparse_bm25/llm/eval_detection.py --preds generator/dense-v2-results/results/dense_v2_verdicts.csv --queries data/queries_v2.csv --retrieval generator/dense-v2-results/results/retrieval_test.per_query.csv --output generator/dense-v2-results/results/detection_test.csv`
