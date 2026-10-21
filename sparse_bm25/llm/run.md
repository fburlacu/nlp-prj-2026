# Running the LLM detection step (RQ2), v2

Llama 3.1 8B Instruct judges each claim as `false` (disinformation), `true` (fact) or `unknown` (inconclusive), either from the claim alone (no-retrieval baseline) or from the claim plus the top-k passages of a retrieval run (RAG).

| Script | Does |
|---|---|
| `detect.py` | Writes predictions for one configuration (one retrieval run + k, or no retrieval) |
| `eval_detection.py` | Scores one or more prediction files on the same queries and compares them with the first one |

All commands below are run from `sparse_bm25/llm/`. v1 predictions and results are in `v1_results/`.

**v2 setup.**
- **Queries:** `data/queries_v2.csv`, **main set only**: EEAS disinformation titles and held-out (inconclusive) titles. Dev has 90 queries, test 600.
- **Evidence:** EEAS disproofs from `data/passages_v2.parquet` (`set = main`), one passage per disproof, not chunked.
- **Retrieval runs:** made with BM25, k1 = 1.2, b = 0.75. These were the defaults, kept after dev tuning (`../v2_results/results/tune_dev.ranking.md`).
- **Script defaults:** `detect.py` and `eval_detection.py` already default to the v2 files and to `--sets main`.

**Passage length.** Disproofs go into the prompt whole: `--max_passage_words` defaults to 800, and the longest disproof is 766 words. With k = 10, a prompt can reach about 10k tokens. If the GPU runs out of memory, lower `--batch_size` (default 8) rather than cutting the evidence.

## Dev: choose k

Every prediction file comes from one `detect.py` call. Run the no-retrieval baseline and a range of k on dev, then score them together. The first file in `--preds` is the baseline for the paired differences.

```bash
RUN=../v2_results/runs_tune/bm25_dev_k1-1.2_b-0.75.parquet
python detect.py --split dev --output v2_results/preds/dev/noretrieval.csv
for k in 1 3 5 10; do
  python detect.py --run $RUN --split dev --k $k --output v2_results/preds/dev/bm25_k$k.csv
done
python eval_detection.py --preds v2_results/preds/dev/noretrieval.csv v2_results/preds/dev/bm25_k{1,3,5,10}.csv \
  --retrieval ../v2_results/results/tune_dev.per_query.csv --output v2_results/results/dev/detection_dev.csv
```

`tune_dev.per_query.csv` holds all 20 tuning runs. `eval_detection.py` takes the rows of the run named in each prediction file's config (`bm25_dev_k1-1.2_b-0.75`).

Fix the selection rule before reading the results. Proposed: **the k with the highest macro-F1 on main/dev**. In v1 the rule averaged over the main and article sets, but v2 has only the main set. Any prompt change must also be decided on dev, before test is run.

## Test: run once

Use the k chosen on dev. Retrieval runs: `default` is the primary configuration, and `sensitivity` (k1 = 1.5, b = 0.5, best on dev but not significantly better) is the robustness check.

```bash
K=5   # the k chosen on dev
python detect.py --split test --output v2_results/preds/test/noretrieval.csv
python detect.py --run ../v2_results/runs_test/default/bm25_test_k1-1.2_b-0.75.parquet --split test --k $K \
  --output v2_results/preds/test/bm25_k$K.csv
python detect.py --run ../v2_results/runs_test/sensitivity/bm25_test_k1-1.5_b-0.5.parquet --split test --k $K \
  --output v2_results/preds/test/bm25_sens_k$K.csv
python eval_detection.py --preds v2_results/preds/test/noretrieval.csv v2_results/preds/test/bm25_k$K.csv \
  v2_results/preds/test/bm25_sens_k$K.csv \
  --retrieval ../v2_results/results/test_compare/retrieval_test.per_query.csv \
  --output v2_results/results/test/detection_test.csv
```

`test_compare/retrieval_test.per_query.csv` contains both test runs, so both RAG files get the "gold evidence in / not in top-k" breakdown.

For a quick smoke test of a new configuration, add `--limit 20` and write to a scratch output file.

## Outputs

**`detect.py`** writes:

- `<output>.csv`: one row per query: `query_id, set, split, label, pred, p_disinformation, p_fact, p_inconclusive, passage_ids, n_prompt_tokens`. The three probabilities are the model's next-token probability mass for the three answer words, renormalised; `pred` is the largest. `passage_ids` (separated by `|`) are the passages the model saw.
- `<output>.config.json`: model, dtype, device, full prompt, k, `max_passage_words`, batch size, input files with hashes (run, passages, queries), timings (`model_load_s`, `llm_s_per_query`, `gpu_peak_mem_gb`).

The run is resumable: queries already in `<output>.csv` are skipped. Change the output name whenever k, the run or the prompt changes.

**`eval_detection.py`** writes `<output>.md` (report: read this first), `.csv` (all metrics with 95% bootstrap CIs, long format, for plots), `.paired.csv` (differences to the first file), `.per_query.csv` (all prediction files with bins) and `.results.json` (everything in one file).

| Set | Classes | Correct behaviour |
|---|---|---|
| main | disinformation vs inconclusive | For inconclusive queries the case was held out of the index, so the model should answer `unknown` |

The main metric is macro-F1. A prediction outside the set's two classes (here `true`) counts as wrong and is reported as off-label. Disinformation recall is also broken down by:
- overlap bin;
- disproof length bin;
- entity bin;
- with `--retrieval`, whether a gold disproof (own case or a near-duplicate, the lenient level) was among the k passages.
