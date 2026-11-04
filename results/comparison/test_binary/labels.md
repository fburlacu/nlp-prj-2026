# Verdicts, test, fact versus disinformation

Leite articles only: 252 disinformation headlines and 252 fact headlines. Llama 3.1 8B reads the title and the top 5 passages and must answer disinformation or fact. Inconclusive is not an allowed word. Off-label is 0 on every run.

The same rankings, scored with the three-word prompt, landed at accuracy 0.323–0.363, because about half of those answers were inconclusive. Forcing the two-word choice moves accuracy to 0.585–0.619. The model still calls most fact headlines disinformation. Fact recall stays near 0.36–0.41, while disinformation recall is 0.78–0.88.

Tables are ordered by accuracy, then macro-F1. Source: results/comparison/test_binary/detection.csv and detection.per_query.csv. Intervals are in results/comparison/test_binary/detection.md.

## All 504 claims

| Rank | Run | Accuracy | Macro-F1 | Off-label | Disinf. precision | Disinf. recall | Disinf. F1 | Fact precision | Fact recall | Fact F1 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | title · BM25 | 0.619 | 0.591 | 0.000 | 0.578 | 0.881 | 0.698 | 0.750 | 0.357 | 0.484 |
| 2 | title · BM25 · late | 0.607 | 0.590 | 0.000 | 0.576 | 0.809 | 0.673 | 0.680 | 0.405 | 0.507 |
| 3 | title · dense · cross | 0.607 | 0.582 | 0.000 | 0.572 | 0.853 | 0.685 | 0.711 | 0.361 | 0.479 |
| 4 | title · dense · late | 0.605 | 0.588 | 0.000 | 0.575 | 0.809 | 0.672 | 0.678 | 0.401 | 0.504 |
| 5 | title · BM25 · cross | 0.603 | 0.581 | 0.000 | 0.571 | 0.833 | 0.677 | 0.691 | 0.373 | 0.484 |
| 6 | late only | 0.597 | 0.580 | 0.000 | 0.569 | 0.802 | 0.666 | 0.664 | 0.393 | 0.494 |
| 7 | title · dense | 0.585 | 0.569 | 0.000 | 0.561 | 0.782 | 0.653 | 0.640 | 0.389 | 0.484 |

## Confusion

Rows are the gold label. Columns are the predicted word. Each gold row sums to 252.

| Run | Gold | Disinformation | Fact |
| --- | --- | ---: | ---: |
| title · BM25 | disinformation | 222 | 30 |
|  | fact | 162 | 90 |
| title · BM25 · late | disinformation | 204 | 48 |
|  | fact | 150 | 102 |
| title · dense · cross | disinformation | 215 | 37 |
|  | fact | 161 | 91 |
| title · dense · late | disinformation | 204 | 48 |
|  | fact | 151 | 101 |
| title · BM25 · cross | disinformation | 210 | 42 |
|  | fact | 158 | 94 |
| late only | disinformation | 202 | 50 |
|  | fact | 153 | 99 |
| title · dense | disinformation | 197 | 55 |
|  | fact | 154 | 98 |

## Disinformation recall by entity and formulation

Of the 252 disinformation articles, 23 are entity-driven and 30 are formulation-driven. The other 199 have no entity bin, so they are not in this table.

| Run | Entity (n = 23) | Formulation (n = 30) |
| --- | ---: | ---: |
| title · BM25 | 0.783 | 0.900 |
| title · BM25 · late | 0.957 | 0.833 |
| title · dense · cross | 0.826 | 0.900 |
| title · dense · late | 0.957 | 0.867 |
| title · BM25 · cross | 0.913 | 0.833 |
| late only | 0.913 | 0.833 |
| title · dense | 0.652 | 0.833 |
