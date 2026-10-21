# Sparse Retrieval (BM25) and Retrieval Evaluation

## 1. BM25 retriever

### 1.1 Why a custom implementation

BM25 is implemented as a small custom class (`bm25.py`, about 20 lines) rather than with `rank_bm25` or `bm25s`. The scoring function is standard Okapi BM25; only the implementation is our own.

1. **Same tokenisation as the data analysis.** The retriever uses `data.preprocessing.tokenize` (lowercasing, English stopword removal, Snowball stemming). The query–disproof overlap statistics and overlap bins (DATA_PREP §6.2) were computed with this tokenizer, so the bins measure exactly what BM25 sees.
2. **Full score vectors.** `scores()` returns a score for every passage. Self-retrieval exclusion sets the excluded passages to −∞ before ranking, so excluded passages cannot take up top-k slots (a Leite document and its wire copies can make up 20+ chunks). Full score vectors are also needed later for hybrid score fusion.
3. **Fair cost measurement (RQ2).** `rank_bm25` scores with a Python loop over all passages (≈ 0.1–0.3 s per query). Comparing that against an optimised dense retriever would overstate the cost of BM25. Our implementation precomputes a sparse matrix and scores in ≈ 1 ms per query, which is representative of production BM25 (Lucene).
4. **Non-negative IDF.** We use the Lucene IDF, log(1 + (N − df + 0.5) / (df + 0.5)). `rank_bm25`'s Okapi IDF becomes negative for terms in more than half of the passages and is patched with an ε heuristic.
5. **Transparency.** The full scoring logic is visible and easy to explain in the report.

### 1.2 How it works

The BM25 weight of term *t* in passage *d* does not depend on the query:

w(t, d) = idf(t) · tf(t,d)·(k1 + 1) / (tf(t,d) + k1·(1 − b + b·|d|/avgdl))

At construction, w is computed for every non-zero (passage, term) pair and stored as a sparse passages × terms matrix **W** (column-compressed for fast column access). A query is tokenised, mapped to term columns, and its score vector is the sum of those columns. k1 (term-frequency saturation) and b (length normalisation) default to 1.2 and 0.75 (see §1.4).

### 1.3 Run protocol (`retrieve.py`)

- The index is always built from the full `passages.parquet` (61,646 passages). `--split` and `--set` filter only the queries, so dev and test runs use the same index.
- The output is a run file (`query_id, rank, passage_id, score`, top 100 per query) and a `.config.json` with the parameters, the exact command, the SHA-256 hashes of the input files, query counts and timings (index build, p50/p95 query latency).
- All retrievers (sparse, dense, hybrid) write the same run format. Evaluation and the LLM step read run files, so retrievers are compared with everything else fixed.

**Cost (dev run, laptop CPU):** index build ≈ 6 s, 24 MB of weights, ≈ 1 ms per query.

### 1.4 Parameter tuning (`tune.py`)

**Protocol.** A grid of k1 ∈ {0.6, 0.9, 1.2, 1.5, 2.0} × b ∈ {0.3, 0.5, 0.75, 0.9} (20 configurations) was evaluated on the 45 main-set disinformation dev queries. Configurations are ranked by case-level MRR@10, the level closest to the evidence the LLM receives. The decision rule was fixed before the search: the standard defaults (k1 = 1.2, b = 0.75) are replaced only if the paired 95% bootstrap CI of the difference excludes 0. Test queries are never used for tuning.

**Result.** No configuration is significantly better than the baseline. The best, k1 = 1.5 and b = 0.3, gains +0.033 case MRR@10 (0.205 vs 0.173; CI [−0.033, +0.111]). **The defaults are kept.**

| k1 | b | Case MRR@10 | Case Hit@10 | Strict MRR@10 | Strict Hit@10 | Δ case MRR@10 [95% CI] |
|---:|---:|---:|---:|---:|---:|---|
| 1.5 | 0.3 | 0.205 | 0.31 | 0.152 | 0.22 | +0.033 [−0.033, +0.111] |
| 1.2 | 0.3 | 0.204 | 0.29 | 0.152 | 0.22 | +0.031 [−0.033, +0.101] |
| 1.5 | 0.5 | 0.192 | 0.29 | 0.133 | 0.22 | +0.020 [−0.025, +0.074] |
| **1.2** | **0.75** | **0.173** | **0.29** | **0.099** | **0.20** | baseline |
| 0.6 | 0.9 | 0.146 | 0.29 | 0.092 | 0.22 | −0.026 [−0.076, +0.011] |

(Top three, baseline and worst of 20; full ranking in `results/tune_dev.ranking.md`.)

**b matters, k1 barely does.** The nine best configurations all have b ≤ 0.5, and all configurations with b = 0.9 are below the baseline. At a fixed b, k1 changes MRR@10 by only about 0.02–0.03. This is consistent with the claim-crowding effect (§3.1): b is the length penalty, and claim passages (median 54 words) are much shorter than disproofs (114) and article chunks (147). A lower b weakens the advantage of short claim passages, so more gold disproofs move up (strict MRR@10 0.099 → 0.152).

**Sensitivity configuration.** An untuned default could be criticised as a weak baseline that favours dense retrieval. k1 = 1.5, b = 0.3 is therefore also run on the test queries as a labelled sensitivity analysis, not as the primary configuration. RQ1 conclusions are checked for both settings.

## 2. Retrieval evaluation (`eval_retrieval.py`)

### 2.1 Gold levels

| Level | A retrieved passage is a hit if it is … | Queries |
|---|---|---|
| Strict | an `eeas_disproof` chunk of the query's own case | Main / disinformation |
| Lenient | an `eeas_disproof` chunk of the own case or a direct near-duplicate | Main / disinformation |
| Case | an `eeas_disproof` **or `eeas_claim`** passage of the own case or a direct near-duplicate | Main / disinformation |
| Proxy | any chunk of a trustworthy article cited in the same debunk | Article / disinformation with `gold_doc_keys` |

The query's own claim passage is excluded at retrieval time. At the case level, a hit therefore comes from the own disproof or from a near-duplicate case's claim or disproof, never from the query's own claim.

**Why the case level.** A near-duplicate case's claim passage often restates the query almost word for word (e.g. *"The Turkish jet was guided by American…"* retrieved a near-duplicate case's claim at rank 1). For detection, this is strong evidence that the claim is documented disinformation, but strict and lenient gold count it as a miss. The case level measures whether the retriever found the case; strict and lenient measure whether it found the refutation. All three are reported.

### 2.2 Metrics

- **Hit@k** (k = 1, 5, 10, 20, 100): share of queries with at least one gold passage in the top k. Each query has one gold case, so this equals recall@k. The most important k is the number of passages passed to the LLM.
- **MRR@10**: mean of 1 / rank of the first gold passage (0 if not in the top 10). It rewards hits near the top, where the LLM uses the context most.
- Results are reported per set and split, for all queries and for two groupings: the overlap bin (low / mid / high title–disproof word overlap, DATA_PREP §6.2) and the entity bin (entity-driven / formulation-driven, DATA_PREP §6.5). The overlap bins measure how many words query and evidence share; the entity bins measure whether the match can rest on specific named entities, which is the contrast RQ1 asks about. The two groupings overlap, and each covers all queries. Every value comes with a 95% bootstrap confidence intervals (1,000 resamples of queries). When several runs are given, per-query differences to the first run are reported with paired bootstrap CIs.

## 3. BM25 dev baseline

k1 = 1.2, b = 0.75, 45 main-set disinformation dev queries (15 per bin), 14 article queries with proxy gold.

| Level | Hit@1 | Hit@5 | Hit@10 | Hit@100 | MRR@10 |
|---|---:|---:|---:|---:|---:|
| Strict | 0.07 | 0.16 | 0.20 | 0.53 | 0.10 |
| Lenient | 0.07 | 0.18 | 0.22 | 0.53 | 0.11 |
| Case | 0.13 | 0.24 | 0.29 | 0.60 | 0.17 |
| Proxy (article set) | 0.07 | 0.21 | 0.21 | 0.50 | 0.13 |

Strict Hit@10 by overlap bin: low 0.00, mid 0.13, high 0.47. By entity bin: entity-driven 0.31 (n = 16), formulation-driven 0.14 (n = 29); strict MRR@10 0.19 vs 0.05.

### 3.1 Why strict scores are low

A diagnosis of the passages ranked above the gold disproof shows that the pipeline is correct (all gold disproofs are indexed, the own claim is never retrieved). The low scores have three causes:

1. **Claim passages of other cases outrank disproofs.** 43% of passages ranked above the gold disproof are `eeas_claim` passages (41% other disproofs, 16% articles), and claims are ranked first for 24 of 45 queries. Claim passages (title + summary) are written in the same register as the query (an EEAS title), whereas disproofs use refutation language. Ranking disproofs only would raise strict Hit@10 from 0.20 to 0.38.
2. **Generic disproofs.** Many disproofs describe the narrative rather than the specific claim ("No evidence given, conspiracy theory. It is a recurring trait …"). For recurring narratives, many disproofs are equally good lexical matches, and none of them are near-duplicates, so the lenient level barely helps.
3. **Low lexical overlap by design.** In the low bin, only about 30% of the query's terms occur in the gold disproof, and BM25 does not find any gold disproof in the top 10. Chunking is not the cause: the best single chunk has the same overlap as the full disproof. This bin is where dense retrieval is expected to gain (RQ1).

### 3.2 Design decisions

- **The index stays unchanged.** Claim passages of other cases are legitimate evidence: they show that a narrative is known disinformation, which the LLM needs for detection (RQ2).
- **Claim summaries are not added to disproof passages.** The summary is an analyst's expansion of the case title, i.e. of the query. Adding it to the gold disproof would turn retrieval into self-retrieval and inflate all retrievers, dense models (which match paraphrases) the most. This is the same reason the own claim passage is excluded.
- **Report all gold levels, focus on differences.** RQ1 is answered by the gap between retrievers per bin and gold level, not by absolute BM25 scores.

### 3.3 Limitations

- **Small dev sample.** Each bin has 15 dev queries, so per-bin Hit@10 has a CI of roughly ±25 percentage points. Dev results are used for tuning only; conclusions are drawn from the 300 test queries.
- **Entity bins depend on NER and two fixed thresholds** (DATA_PREP §6.5). Some names in short titles are missed, which moves a query to the formulation bin. The dev entity bin is small (16 queries).
- **Proxy gold is incomplete** (DATA_PREP §7.5), so proxy hit rates underestimate retrieval quality on the article set.
