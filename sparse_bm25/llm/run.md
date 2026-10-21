# Running the LLM detection step (RQ2), v2

Llama 3.1 8B Instruct judges each claim as `false` (disinformation), `true` (fact) or `unknown` (inconclusive), either from the claim alone (no-retrieval baseline) or from the claim plus the top-k passages of a retrieval run (RAG).

| Script | Does |
|---|---|
| `detect.py` | Writes predictions for one configuration (one retrieval run + k, or no retrieval) |
| `eval_detection.py` | Scores one or more prediction files on the same queries and compares them with the first one |

All commands below are run from `sparse_bm25/llm/`. v1 predictions and results are in `v1_results/`.

**v2 setup.**
- **Queries:** `data/queries_v2.csv`.
  - Main set: EEAS disinformation titles and held-out (inconclusive) titles; dev 90, test 600.
  - Article set: Leite disinformation and fact headlines; test 504, never used on dev.
- **Evidence:** `data/passages_v2.parquet`. Main-set queries get EEAS disproofs (`set = main`, one per disproof, not chunked). Article-set queries get Leite article chunks (`set = article`).
- **Retrieval runs:** made with BM25, k1 = 1.2, b = 0.75. These were the defaults, kept after dev tuning (`../v2_results/results/tune_dev.ranking.md`).
- **Inputs:** every command below names the v2 files and the query set explicitly (`--passages`, `--queries`, `--sets` / `--set`), so nothing depends on script defaults.

**All decisions are made on main/dev**: the BM25 parameters, k and any prompt change. The article set is never used for a decision. Its retrieval gold is only proxy gold (14 dev queries), its "fact" label is a proxy, and dev is small (51 + 51 queries) with a topic signal (text-only macro-F1 0.61). It is evaluated once, on test, with the frozen configuration, together with the main set in the final analysis. This is enforced by the commands: every dev command uses `--sets main` / `--set main`, and the article set only appears in test commands.

**Passage length.** Disproofs go into the prompt whole: `--max_passage_words` defaults to 800, and the longest disproof is 766 words. With k = 10, a prompt can reach about 10k tokens. If the GPU runs out of memory, lower `--batch_size` (default 8) rather than cutting the evidence.

## Dev: BM25 parameters (already done)

The v2 tuning was run on main/dev only (from `sparse_bm25/`):

```bash
python tune.py --passages ../data/passages_v2.parquet --queries ../data/queries_v2.csv --set main \
  --select lenient:mrr@10 --runs_dir v2_results/runs_tune --output v2_results/results/tune_dev.csv
```

## Dev: choose k

Every prediction file comes from one `detect.py` call. Run the no-retrieval baseline and a range of k on dev, then score them together. The first file in `--preds` is the baseline for the paired differences.

```bash
P=../../data/passages_v2.parquet
Q=../../data/queries_v2.csv
RUN=../v2_results/runs_tune/bm25_dev_k1-1.2_b-0.75.parquet
python detect.py --queries $Q --sets main --split dev --output v2_results/preds/dev/noretrieval.csv
for k in 1 3 5 10; do
  python detect.py --run $RUN --passages $P --queries $Q --sets main --split dev --k $k \
    --output v2_results/preds/dev/bm25_k$k.csv
done
python eval_detection.py --queries $Q \
  --preds v2_results/preds/dev/noretrieval.csv v2_results/preds/dev/bm25_k{1,3,5,10}.csv \
  --retrieval ../v2_results/results/tune_dev.per_query.csv --output v2_results/results/dev/detection_dev.csv
```

`tune_dev.per_query.csv` holds all 20 tuning runs. `eval_detection.py` takes the rows of the run named in each prediction file's config (`bm25_dev_k1-1.2_b-0.75`).

Fix the selection rule before reading the results: **the k with the highest macro-F1 on main/dev**. In v1 the rule averaged over the main and article sets; v2 drops the article set from all decisions. Any prompt change must also be decided on main/dev, before test is run.

## Test: final analysis (run once)

Both query sets are judged with the configuration frozen on main/dev: the K chosen on dev and the BM25 runs below. Each `detect.py` call covers both sets (`--sets main article`), so one `eval_detection.py` call gives the final report. That report scores each set separately in its own label space, and gives paired differences between configurations per set.

**Retrieval (already done, from `sparse_bm25/`).** One BM25 run per configuration over all test queries:
- main-set queries search the EEAS disproofs (`set = main`), with no exclusion;
- article-set queries search the Leite article chunks (`set = article`), excluding their own document and its wire copies.

`default` (k1 = 1.2, b = 0.75) is the primary configuration. `sensitivity` (k1 = 1.5, b = 0.5) is the best dev configuration, which was not significantly better, and serves as the robustness check. Extra-set queries have no passages and get no results.

```bash
python retrieve.py --passages ../data/passages_v2.parquet --queries ../data/queries_v2.csv --split test \
  --k1 1.2 --b 0.75 --output v2_results/runs_test/default/bm25_test_k1-1.2_b-0.75.parquet
python retrieve.py --passages ../data/passages_v2.parquet --queries ../data/queries_v2.csv --split test \
  --k1 1.5 --b 0.5 --output v2_results/runs_test/sensitivity/bm25_test_k1-1.5_b-0.5.parquet
python eval_retrieval.py --runs v2_results/runs_test/default/bm25_test_k1-1.2_b-0.75.parquet \
  v2_results/runs_test/sensitivity/bm25_test_k1-1.5_b-0.5.parquet \
  --passages ../data/passages_v2.parquet --queries ../data/queries_v2.csv --split test \
  --output v2_results/results/test_compare/retrieval_test.csv
```

Test retrieval, default run: main strict Hit@10 0.41, MRR@10 0.27 (300 disinformation queries); article proxy Hit@10 0.42, MRR@10 0.29 (53 disinformation queries with proxy gold). See `../v2_results/results/test_default/retrieval_test.md`.

**Detection.**

```bash
P=../../data/passages_v2.parquet
Q=../../data/queries_v2.csv
K=5   # the k chosen on main/dev
python detect.py --queries $Q --sets main article --split test --output v2_results/preds/test/noretrieval.csv
python detect.py --run ../v2_results/runs_test/default/bm25_test_k1-1.2_b-0.75.parquet --passages $P --queries $Q \
  --sets main article --split test --k $K --output v2_results/preds/test/bm25_k$K.csv
python detect.py --run ../v2_results/runs_test/sensitivity/bm25_test_k1-1.5_b-0.5.parquet --passages $P --queries $Q \
  --sets main article --split test --k $K --output v2_results/preds/test/bm25_sens_k$K.csv
python eval_detection.py --queries $Q \
  --preds v2_results/preds/test/noretrieval.csv v2_results/preds/test/bm25_k$K.csv \
  v2_results/preds/test/bm25_sens_k$K.csv \
  --retrieval ../v2_results/results/test_compare/retrieval_test.per_query.csv \
  --output v2_results/results/test/detection_test.csv
```

Each prediction file holds 1,104 test queries: 600 main (300 disinformation, 300 inconclusive) and 504 article (252 disinformation, 252 fact). `test_compare/retrieval_test.per_query.csv` contains both runs and both sets. Both RAG files therefore get the "gold evidence in / not in top-k" breakdown: at the lenient level for the main set, and at the proxy level for the 53 article queries with proxy gold.

**Reading the report.** The main set is the primary result (RQ2: detection and abstention when the evidence is missing). The article set is a secondary check: do the findings hold on original headlines? Its "fact" label is a proxy, and the text-only classifier already reaches 0.61 macro-F1 on it, so compare the RAG files with `noretrieval` rather than reading absolute scores.

For a quick smoke test of a new configuration, add `--limit 20` and write to a scratch output file.

## Outputs

**`detect.py`** writes:

- `<output>.csv`: one row per query: `query_id, set, split, label, pred, p_disinformation, p_fact, p_inconclusive, passage_ids, n_prompt_tokens`. The three probabilities are the model's next-token probability mass for the three answer words, renormalised; `pred` is the largest. `passage_ids` (separated by `|`) are the passages the model saw.
- `<output>.config.json`: model, dtype, device, full prompt, k, `max_passage_words`, batch size, input files with hashes (run, passages, queries), timings (`model_load_s`, `llm_s_per_query`, `gpu_peak_mem_gb`).

The run is resumable: queries already in `<output>.csv` are skipped. Change the output name whenever k, the run or the prompt changes.

**`eval_detection.py`** writes `<output>.md` (report: read this first), `.csv` (all metrics with 95% bootstrap CIs, long format, for plots), `.paired.csv` (differences to the first file), `.per_query.csv` (all prediction files with bins) and `.results.json` (everything in one file).

| Set | Classes | Correct behaviour | Role |
|---|---|---|---|
| main | disinformation vs inconclusive | For inconclusive queries the case was held out of the index, so the model should answer `unknown` | Decisions (dev) and primary result (test) |
| article | disinformation vs fact | Separate fake from real headlines | Secondary check, test only |

The main metric is macro-F1, per set. A prediction outside the set's two classes counts as wrong and is reported as off-label: `true` on the main set, `unknown` on the article set. Disinformation recall is also broken down by:
- overlap bin, disproof length bin (main set only);
- entity bin;
- with `--retrieval`, whether gold evidence was among the k passages: a gold disproof (own case or near-duplicate) for the main set, a proxy-gold article for the article set.
