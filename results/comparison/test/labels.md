# Verdicts, test

Llama 3.1 8B reads the title and the top 5 passages and answers with one word: disinformation, fact, or inconclusive. The score is the next-token probability. There is no sampling.

On the main set the gold labels are disinformation and inconclusive, 300 each. Fact is outside that label space. On the article set the gold labels are disinformation and fact, 252 each. Inconclusive is outside that label space. Off-label is the share of predictions that fall outside the set.

Tables are ordered by accuracy, then macro-F1. Source: results/comparison/test/detection.csv and detection.per_query.csv. Intervals are in results/comparison/test/detection.md.

## Main

### All 600 claims

| Rank | Run | Accuracy | Macro-F1 | Off-label | Disinf. precision | Disinf. recall | Disinf. F1 | Inconc. precision | Inconc. recall | Inconc. F1 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | title · dense · cross | 0.553 | 0.530 | 0.020 | 0.546 | 0.797 | 0.648 | 0.620 | 0.310 | 0.413 |
| 2 | title · BM25 | 0.545 | 0.533 | 0.025 | 0.543 | 0.743 | 0.627 | 0.598 | 0.347 | 0.439 |
| 3 | title · dense · late | 0.533 | 0.484 | 0.022 | 0.529 | 0.857 | 0.654 | 0.624 | 0.210 | 0.314 |
| 4 | title · BM25 · cross | 0.520 | 0.517 | 0.045 | 0.531 | 0.690 | 0.600 | 0.574 | 0.350 | 0.435 |
| 5 | title · dense | 0.513 | 0.479 | 0.023 | 0.520 | 0.790 | 0.627 | 0.546 | 0.237 | 0.330 |
| 6 | title · BM25 · late | 0.485 | 0.474 | 0.050 | 0.509 | 0.690 | 0.586 | 0.515 | 0.280 | 0.363 |
| 7 | late only | 0.485 | 0.474 | 0.060 | 0.512 | 0.700 | 0.592 | 0.526 | 0.270 | 0.357 |

### Confusion

Rows are the gold label. Columns are the predicted word. Each gold row sums to 300.

| Run | Gold | Disinformation | Fact | Inconclusive |
| --- | --- | ---: | ---: | ---: |
| title · dense · cross | disinformation | 239 | 4 | 57 |
|  | inconclusive | 199 | 8 | 93 |
| title · BM25 | disinformation | 223 | 7 | 70 |
|  | inconclusive | 188 | 8 | 104 |
| title · dense · late | disinformation | 257 | 5 | 38 |
|  | inconclusive | 229 | 8 | 63 |
| title · BM25 · cross | disinformation | 207 | 15 | 78 |
|  | inconclusive | 183 | 12 | 105 |
| title · dense | disinformation | 237 | 4 | 59 |
|  | inconclusive | 219 | 10 | 71 |
| title · BM25 · late | disinformation | 207 | 14 | 79 |
|  | inconclusive | 200 | 16 | 84 |
| late only | disinformation | 210 | 17 | 73 |
|  | inconclusive | 200 | 19 | 81 |

### Disinformation recall by group

These rows are the 300 disinformation claims only. Overlap bins have 100 claims. Length bins are short 101, medium 103, long 96. Entity-driven is 125 and formulation-driven is 175.

| Run | low | mid | high | short | medium | long | entity | formulation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| title · dense · cross | 0.780 | 0.780 | 0.830 | 0.713 | 0.816 | 0.865 | 0.800 | 0.794 |
| title · BM25 | 0.690 | 0.740 | 0.800 | 0.723 | 0.738 | 0.771 | 0.760 | 0.731 |
| title · dense · late | 0.830 | 0.850 | 0.890 | 0.743 | 0.874 | 0.958 | 0.816 | 0.886 |
| title · BM25 · cross | 0.620 | 0.770 | 0.680 | 0.663 | 0.650 | 0.760 | 0.696 | 0.686 |
| title · dense | 0.750 | 0.830 | 0.790 | 0.693 | 0.796 | 0.885 | 0.776 | 0.800 |
| title · BM25 · late | 0.610 | 0.780 | 0.680 | 0.683 | 0.650 | 0.740 | 0.688 | 0.691 |
| late only | 0.630 | 0.770 | 0.700 | 0.693 | 0.680 | 0.729 | 0.688 | 0.709 |

### Inconclusive recall by group

These rows are the 300 inconclusive claims. A recall here is the share predicted inconclusive. Overlap bins are low 103, mid 106, high 91. Length bins are short 115, medium 91, long 94. Inconclusive claims have no entity bin.

| Run | low | mid | high | short | medium | long |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| title · dense · cross | 0.340 | 0.311 | 0.275 | 0.365 | 0.297 | 0.255 |
| title · BM25 | 0.427 | 0.302 | 0.308 | 0.443 | 0.286 | 0.287 |
| title · dense · late | 0.243 | 0.236 | 0.143 | 0.304 | 0.198 | 0.106 |
| title · BM25 · cross | 0.398 | 0.368 | 0.275 | 0.461 | 0.352 | 0.213 |
| title · dense | 0.272 | 0.283 | 0.143 | 0.322 | 0.242 | 0.128 |
| title · BM25 · late | 0.330 | 0.283 | 0.220 | 0.348 | 0.286 | 0.191 |
| late only | 0.350 | 0.264 | 0.187 | 0.348 | 0.264 | 0.181 |

## Article

### All 504 claims

| Rank | Run | Accuracy | Macro-F1 | Off-label | Disinf. precision | Disinf. recall | Disinf. F1 | Fact precision | Fact recall | Fact F1 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | late only | 0.363 | 0.474 | 0.478 | 0.708 | 0.298 | 0.419 | 0.688 | 0.429 | 0.528 |
| 2 | title · dense · late | 0.361 | 0.466 | 0.466 | 0.686 | 0.286 | 0.403 | 0.671 | 0.436 | 0.529 |
| 3 | title · BM25 · late | 0.349 | 0.455 | 0.478 | 0.679 | 0.286 | 0.402 | 0.662 | 0.413 | 0.509 |
| 4 | title · dense | 0.335 | 0.444 | 0.502 | 0.694 | 0.270 | 0.389 | 0.660 | 0.401 | 0.499 |
| 5 | title · BM25 | 0.329 | 0.448 | 0.542 | 0.731 | 0.270 | 0.394 | 0.710 | 0.389 | 0.503 |
| 6 | title · dense · cross | 0.323 | 0.440 | 0.542 | 0.688 | 0.262 | 0.379 | 0.719 | 0.385 | 0.501 |
| 7 | title · BM25 · cross | 0.323 | 0.433 | 0.528 | 0.674 | 0.238 | 0.352 | 0.691 | 0.409 | 0.514 |

### Confusion

Rows are the gold label. Columns are the predicted word. Each gold row sums to 252.

| Run | Gold | Disinformation | Fact | Inconclusive |
| --- | --- | ---: | ---: | ---: |
| late only | disinformation | 75 | 49 | 128 |
|  | fact | 31 | 108 | 113 |
| title · dense · late | disinformation | 72 | 54 | 126 |
|  | fact | 33 | 110 | 109 |
| title · BM25 · late | disinformation | 72 | 53 | 127 |
|  | fact | 34 | 104 | 114 |
| title · dense | disinformation | 68 | 52 | 132 |
|  | fact | 30 | 101 | 121 |
| title · BM25 | disinformation | 68 | 40 | 144 |
|  | fact | 25 | 98 | 129 |
| title · dense · cross | disinformation | 66 | 38 | 148 |
|  | fact | 30 | 97 | 125 |
| title · BM25 · cross | disinformation | 60 | 46 | 146 |
|  | fact | 29 | 103 | 120 |

### Disinformation recall by entity and formulation

Of the 252 disinformation articles, 23 are entity-driven and 30 are formulation-driven. The other 199 have no entity bin, so they are not in this table.

| Run | Entity (n = 23) | Formulation (n = 30) |
| --- | ---: | ---: |
| late only | 0.391 | 0.533 |
| title · dense · late | 0.348 | 0.567 |
| title · BM25 · late | 0.348 | 0.533 |
| title · dense | 0.304 | 0.433 |
| title · BM25 | 0.304 | 0.500 |
| title · dense · cross | 0.391 | 0.400 |
| title · BM25 · cross | 0.391 | 0.400 |
