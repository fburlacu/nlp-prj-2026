# Pipeline sanity check (BM25)

Own-case retrieval with **no self-exclusion**: every query's own case stays in the index, so a working pipeline should find it near rank 1. BM25 only (k1 = 1.2, b = 0.75); there is no dense retriever yet.

| | |
|---|---|
| Queries | 345 main-set EEAS disinformation titles (300 test + 45 dev) |
| Gold | **strict** = a passage of the own case; **lenient** = own case or a direct near-duplicate (DATA_PREP §6.3) |
| Metrics | R@k = own case in the top k; MRR over the top 100 |
| Code | `sparse_bm25/sanity_check.py`; per-query first ranks in `results/sanity_check.per_query.csv` |

## 1. Retrieval

Strict gold. Lenient is at most 0.02 higher in every cell.

| Index | Passages | R@1 | R@5 | R@10 | R@100 | MRR@100 |
|---|---:|---:|---:|---:|---:|---:|
| A. Current `passages.parquet`: title + summary claims, disproof chunks, article chunks | 61,646 | 0.90 | 0.99 | 1.00 | 1.00 | 0.94 |
| B. Full EEAS pool, one passage per case = summary + disproof | 14,497 | 0.58 | 0.81 | 0.87 | 0.97 | 0.68 |
| C. Full EEAS pool, summary only | 14,497 | 0.71 | 0.84 | 0.88 | 0.97 | 0.77 |
| D. Full EEAS pool, disproof only (not chunked) | 14,497 | 0.20 | 0.33 | 0.41 | 0.72 | 0.27 |
| E. v2 main-set index `passages_v2_main.parquet`: disproofs without held-out cases and placeholders | 13,447 | 0.20 | 0.33 | 0.40 | 0.72 | 0.27 |

**E vs the disproof-only preview (D).** R@1 is 0.197 in both, and R@10 is 0.403 against 0.406, so removing the held-out cases and placeholders changes almost nothing. Leite article chunks are not in the main-set index; with them in a shared index, R@1 fell to 0.180 and R@10 to 0.357 (articles took 37% of the top-10 slots).



## 2. Why A misses 35 queries at rank 1

| Rank-1 passage | Queries |
|---|---:|
| Another case's disproof | 24 |
| Another case's claim passage | 11 |
| — of which the case has an identical title (tie) | 3 |

- **Cross-referencing disproofs.** Most winning disproofs quote other claims word for word, e.g. *"This disinformation message appeared in the same TV programme as the claims that 'The highly likely argument is used again to spread lies about Russia'"*. In a disproof-only index these quotes make a passage match the wrong case.
- **Length normalisation.** Winning passages are shorter (median 59 words, against 89 for the own claim passage).


