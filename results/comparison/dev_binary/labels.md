# Verdicts, dev, fact versus disinformation

Leite articles only: 51 disinformation headlines and 51 fact headlines. Llama 3.1 8B reads the title and the top 5 passages and must answer disinformation or fact. Off-label is 0 on every run.

Dev is the smaller split. The test file is the score to report. Tables are ordered by accuracy, then macro-F1. Source: results/comparison/dev_binary/detection.csv and detection.per_query.csv. Intervals are in results/comparison/dev_binary/detection.md.

## All 102 claims

| Rank | Run | Accuracy | Macro-F1 | Off-label | Disinf. precision | Disinf. recall | Disinf. F1 | Fact precision | Fact recall | Fact F1 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | title · dense | 0.667 | 0.653 | 0.000 | 0.620 | 0.863 | 0.721 | 0.774 | 0.471 | 0.585 |
| 2 | title · BM25 · late | 0.657 | 0.642 | 0.000 | 0.611 | 0.863 | 0.715 | 0.767 | 0.451 | 0.568 |
| 3 | late only | 0.657 | 0.638 | 0.000 | 0.608 | 0.882 | 0.720 | 0.786 | 0.431 | 0.557 |
| 4 | title · BM25 | 0.647 | 0.623 | 0.000 | 0.597 | 0.902 | 0.719 | 0.800 | 0.392 | 0.526 |
| 5 | title · BM25 · cross | 0.627 | 0.609 | 0.000 | 0.589 | 0.843 | 0.694 | 0.724 | 0.412 | 0.525 |
| 6 | title · dense · late | 0.627 | 0.609 | 0.000 | 0.589 | 0.843 | 0.694 | 0.724 | 0.412 | 0.525 |
| 7 | title · dense · cross | 0.578 | 0.556 | 0.000 | 0.554 | 0.804 | 0.656 | 0.643 | 0.353 | 0.456 |

## Confusion

Rows are the gold label. Columns are the predicted word. Each gold row sums to 51.

| Run | Gold | Disinformation | Fact |
| --- | --- | ---: | ---: |
| title · dense | disinformation | 44 | 7 |
|  | fact | 27 | 24 |
| title · BM25 · late | disinformation | 44 | 7 |
|  | fact | 28 | 23 |
| late only | disinformation | 45 | 6 |
|  | fact | 29 | 22 |
| title · BM25 | disinformation | 46 | 5 |
|  | fact | 31 | 20 |
| title · BM25 · cross | disinformation | 43 | 8 |
|  | fact | 30 | 21 |
| title · dense · late | disinformation | 43 | 8 |
|  | fact | 30 | 21 |
| title · dense · cross | disinformation | 41 | 10 |
|  | fact | 33 | 18 |

## Disinformation recall by entity and formulation

Seven disinformation articles are entity-driven and seven are formulation-driven. These counts are too small to separate the runs. Every entity bin is 1.000.

| Run | Entity (n = 7) | Formulation (n = 7) |
| --- | ---: | ---: |
| title · dense | 1.000 | 0.714 |
| title · BM25 · late | 1.000 | 0.714 |
| late only | 1.000 | 0.857 |
| title · BM25 | 1.000 | 0.857 |
| title · BM25 · cross | 1.000 | 0.714 |
| title · dense · late | 1.000 | 0.857 |
| title · dense · cross | 1.000 | 0.571 |
