# Running the LLM detection step (RQ2)

Llama 3.1 8B Instruct judges each claim as `false` (disinformation), `true` (fact) or `unknown` (inconclusive), either from the claim alone (no-retrieval baseline) or from the claim plus the top-k passages of a retrieval run (RAG). 

| Script | Does |
|---|---|
| `detect.py` | Writes predictions for one configuration (one retrieval run + k, or no retrieval) |
| `eval_detection.py` | Scores one or more prediction files on the same queries and compares them with the first one |

All commands below are run from `sparse_bm25/llm/`.

## Dev: choose k

Every prediction file comes from one `detect.py` call. Run the no-retrieval baseline and a range of k on dev, then score them together; the first file in `--preds` is the baseline for the paired differences.

```bash
RUN=../runs_dev/bm25_dev_k1-1.2_b-0.75.parquet
python detect.py --split dev --output preds/dev/noretrieval.csv
for k in 1 3 5 10; do
  python detect.py --run $RUN --split dev --k $k --output preds/dev/bm25_k$k.csv
done
python eval_detection.py --preds preds/dev/noretrieval.csv preds/dev/bm25_k{1,3,5,10}.csv \
  --retrieval ../results/dev/retrieval_dev.per_query.csv --output results/dev/detection_dev.csv
```

About 10 minutes in total once the model is loaded (192 dev queries; 0.04 s per query without retrieval, 0.08–0.5 s with k = 1–10).

Fix the selection rule before reading the results. We used: **the k with the highest mean macro-F1 over the main and article sets**, which gave k = 5. Any prompt change must also be decided on dev, before test is run.

##  Test: run once

Use the k chosen on dev. Retrieval runs: `default` is the primary configuration and `sensitivity` the robustness check (see `../BM25_DESIGN.md` §1.4).

```bash
K=5
python detect.py --split test --output preds/test/noretrieval.csv
python detect.py --run ../runs_test/default/bm25_test_k1-1.2_b-0.75.parquet --split test --k $K \
  --output preds/test/bm25_k$K.csv
python detect.py --run ../runs_test/sensitivity/bm25_test_k1-1.5_b-0.3.parquet --split test --k $K \
  --output preds/test/bm25_sens_k$K.csv
python eval_detection.py --preds preds/test/noretrieval.csv preds/test/bm25_k$K.csv preds/test/bm25_sens_k$K.csv \
  --retrieval ../results/test_default/retrieval_test.per_query.csv --output results/test/detection_test.csv
```

About 1–5 minutes per run (1,104 test queries). `--retrieval` must be the per-query retrieval file of the run in the second position; it adds the "gold evidence in / not in top-k" breakdown for that run only.

For a quick smoke test of a new configuration, add `--limit 20` and write to a scratch output file.

## Outputs

**`detect.py`** writes:

- `<output>.csv`: one row per query: `query_id, set, split, label, pred, p_disinformation, p_fact, p_inconclusive, passage_ids, n_prompt_tokens`. The three probabilities are the model's next-token probability mass for the three answer words, renormalised; `pred` is the largest. `passage_ids` (separated by `|`) are the passages the model saw.
- `<output>.config.json`: model, dtype, device, full prompt, k, input file hashes, timings (`model_load_s`, `llm_s_per_query`, `gpu_peak_mem_gb`).

**`eval_detection.py`** writes `<output>.md` (report: read this first), `.csv` (all metrics with 95% bootstrap CIs, long format, for plots), `.paired.csv` (differences to the first file), `.per_query.csv` (all prediction files with bins) and `.results.json` (everything in one file).

The two query sets are scored separately:

| Set | Classes | Correct behaviour |
|---|---|---|
| main | disinformation vs inconclusive | For inconclusive queries the case was held out of the index, so the model should answer `unknown` |
| article | disinformation vs fact | Separate fake from real headlines |

The main metric is macro-F1. A prediction outside the set's two classes counts as wrong and is reported as off-label.

