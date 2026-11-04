# Retrieval evaluation

Runs: `dense_v2` | split: dev | cells: mean [95% bootstrap CI, 1000 resamples]

Gold levels: **strict** = own disproof; **lenient** = own or near-duplicate disproof; **proxy** = same-debunk trustworthy article

Rows: all queries, then by title–disproof word overlap (`overlap_bin`), by disproof length tertile (`len_bin`), and by entity type (`entity_bin`: entity-driven = the query's specific named entities occur in the gold evidence; formulation-driven = no specific entity, or the evidence does not repeat it). The groupings overlap; each sums to all.

## Results

### dense_v2 · strict · main/dev

| Bin | n | hit@1 | hit@5 | hit@10 | hit@20 | hit@100 | mrr@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| overlap: low | 15 | 0.13 [0.00, 0.33] | 0.13 [0.00, 0.33] | 0.27 [0.07, 0.53] | 0.27 [0.07, 0.53] | 0.53 [0.27, 0.73] | 0.15 [0.01, 0.35] |
| overlap: mid | 15 | 0.13 [0.00, 0.33] | 0.33 [0.07, 0.60] | 0.33 [0.13, 0.60] | 0.53 [0.27, 0.80] | 0.67 [0.40, 0.87] | 0.20 [0.05, 0.41] |
| overlap: high | 15 | 0.20 [0.00, 0.40] | 0.47 [0.27, 0.73] | 0.47 [0.27, 0.73] | 0.53 [0.27, 0.80] | 0.73 [0.47, 0.93] | 0.30 [0.12, 0.51] |
| length: short | 16 | 0.25 [0.06, 0.50] | 0.38 [0.12, 0.62] | 0.44 [0.19, 0.69] | 0.44 [0.19, 0.69] | 0.62 [0.38, 0.88] | 0.30 [0.11, 0.51] |
| length: medium | 11 | 0.09 [0.00, 0.27] | 0.36 [0.09, 0.64] | 0.36 [0.09, 0.64] | 0.55 [0.27, 0.82] | 0.73 [0.45, 1.00] | 0.18 [0.02, 0.39] |
| length: long | 18 | 0.11 [0.00, 0.28] | 0.22 [0.06, 0.39] | 0.28 [0.11, 0.50] | 0.39 [0.17, 0.61] | 0.61 [0.39, 0.83] | 0.16 [0.03, 0.34] |
| entity-driven | 16 | 0.31 [0.12, 0.56] | 0.56 [0.31, 0.81] | 0.62 [0.38, 0.88] | 0.75 [0.50, 0.94] | 1.00 [1.00, 1.00] | 0.41 [0.23, 0.63] |
| formulation-driven | 29 | 0.07 [0.00, 0.17] | 0.17 [0.03, 0.31] | 0.21 [0.07, 0.38] | 0.28 [0.14, 0.45] | 0.45 [0.28, 0.62] | 0.11 [0.02, 0.22] |
| **all** | 45 | 0.16 [0.07, 0.27] | 0.31 [0.18, 0.44] | 0.36 [0.22, 0.51] | 0.44 [0.31, 0.60] | 0.64 [0.51, 0.78] | 0.22 [0.12, 0.33] |

### dense_v2 · lenient · main/dev

| Bin | n | hit@1 | hit@5 | hit@10 | hit@20 | hit@100 | mrr@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| overlap: low | 15 | 0.13 [0.00, 0.33] | 0.20 [0.07, 0.40] | 0.27 [0.07, 0.47] | 0.27 [0.07, 0.47] | 0.53 [0.27, 0.80] | 0.15 [0.01, 0.35] |
| overlap: mid | 15 | 0.13 [0.00, 0.33] | 0.33 [0.13, 0.60] | 0.40 [0.13, 0.67] | 0.53 [0.27, 0.73] | 0.67 [0.40, 0.87] | 0.21 [0.06, 0.40] |
| overlap: high | 15 | 0.20 [0.00, 0.40] | 0.53 [0.27, 0.80] | 0.53 [0.27, 0.80] | 0.53 [0.27, 0.80] | 0.73 [0.53, 0.93] | 0.33 [0.15, 0.51] |
| length: short | 16 | 0.25 [0.06, 0.50] | 0.44 [0.19, 0.69] | 0.44 [0.19, 0.69] | 0.44 [0.19, 0.69] | 0.62 [0.38, 0.88] | 0.31 [0.12, 0.51] |
| length: medium | 11 | 0.09 [0.00, 0.27] | 0.36 [0.09, 0.64] | 0.45 [0.18, 0.73] | 0.55 [0.27, 0.82] | 0.73 [0.45, 1.00] | 0.21 [0.05, 0.41] |
| length: long | 18 | 0.11 [0.00, 0.28] | 0.28 [0.06, 0.50] | 0.33 [0.11, 0.56] | 0.39 [0.17, 0.61] | 0.61 [0.39, 0.83] | 0.17 [0.05, 0.33] |
| entity-driven | 16 | 0.31 [0.12, 0.56] | 0.56 [0.31, 0.81] | 0.62 [0.38, 0.81] | 0.75 [0.50, 0.94] | 1.00 [1.00, 1.00] | 0.41 [0.22, 0.64] |
| formulation-driven | 29 | 0.07 [0.00, 0.17] | 0.24 [0.10, 0.41] | 0.28 [0.14, 0.45] | 0.28 [0.10, 0.45] | 0.45 [0.28, 0.62] | 0.13 [0.04, 0.24] |
| **all** | 45 | 0.16 [0.04, 0.27] | 0.36 [0.22, 0.49] | 0.40 [0.27, 0.56] | 0.44 [0.31, 0.60] | 0.64 [0.51, 0.78] | 0.23 [0.13, 0.34] |

Command: `sparse_bm25/eval_retrieval.py --runs generator/dense-v2-results/results/dense_v2.parquet --passages generator/dense-v2-results/results/passages_for_eval.parquet --queries data/queries_v2.csv --split dev --set main --output generator/dense-v2-results/results/dev/retrieval_dev.csv`
