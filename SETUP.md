# Setup

Run this on the university Jupyter GPU session (the terminal user is `jovyan`). That session is a container with Python 3.10 and two Tesla T4 GPUs. It does not have `module` or Conda. `module load anaconda3/2025.06` belongs to the EEMCS HPC login nodes and fails here.

The container driver supports CUDA 12.5. `requirements.txt` installs PyTorch `2.6.0+cu124` so the T4 is used. A newer default PyTorch wheel refuses this driver and silently runs on CPU.

GPU 0 is often already in use. GPU 1 has 16 GB free. A T4 does not fit Llama 3.1 8B in full precision. SmolLM2 1.7B fits, and it is not the Qwen model that built the fact-query filter (`data/claim_check.py`).

## Environment

In the Jupyter terminal, once:

```bash
python -m venv ~/nlp-env
source ~/nlp-env/bin/activate
cd ~/nlp-prj-2026
pip install -r requirements.txt
CUDA_VISIBLE_DEVICES=1 python -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

The check must print `2.6.0+cu124 True Tesla T4`. Later terminals need `source ~/nlp-env/bin/activate` again. The environment lives in the home directory.

## Passages

The dense run reads `data/passages_v2.parquet` and `data/queries_v2.csv` (see `data/DATA_v2.md`). Disproofs are one row per case in that file. `retrieval/dense.py` chunks them at index time and keeps `case_links` on every chunk. A main query searches disproofs only. An article query searches article chunks only. The old claim passages are not in this index.

## Where the code lives

```text
data/            v2 passages, queries, and the scripts that built them
retrieval/       both first-stage retrievers, same shape: a module plus a command
  dense.py       bi-encoder
  bm25.py        BM25. Imported by the pipeline; also writes a run on its own
  tune_bm25.py   k1 and b grid. BM25 is the only retriever with those parameters
  eval_retrieval.py  Hit@k and MRR for either retriever
  indexes/       dense embedding index, not committed
generator/       verdict model for every retriever, including BM25
  bm25_verdicts.py  the older BM25 prompt, which shows passage type
pipeline/        the 12 systems below
analysis/        detection scorer (eval_detection.py) and the older combined scorer
results/         finished outputs, kept on disk and not committed
  bm25/retrieval/v1, v2    BM25 runs and retrieval reports
  bm25/detection/v1, v2    BM25 verdict predictions and detection reports
  dense/v1, v2             dense runs, verdicts, predictions, and reports
papers/          the INFACT paper
scripts/         the HPC batch script
runs/            new 12-system outputs (gitignored)
```

`results/` is the finished BM25 and dense work. It stays on this machine and is not committed. New 12-system runs go to `runs/`, which is also gitignored.

## The 12 systems

Each system is one choice from each row. That is 12 runs. The two `title` systems with no reranker are the BM25 and dense results already reported.

| Piece | Choices |
|---|---|
| Query | `title` or `rewrite` |
| First stage | `bm25` or `dense` |
| Reranker | `none`, `cross`, or `late` |

`rewrite` is the INFACT retrieval front end: the LLM rewrites the claim, writes questions, and writes a search query for each question. It does not give a verdict. Those queries, plus the original title, are searched separately and fused with reciprocal rank fusion. A reranker then scores the original claim against that fused list. `cross` is `BAAI/bge-reranker-base`. `late` is `answerdotai/answerai-colbert-small-v1` (MaxSim). Both see the first 400 words of a passage.

Decide on main/dev. Run test once, after one system wins on dev.

```bash
python main.py list
python main.py rewrite --split dev
python main.py run --query title --retriever bm25 --reranker none --split dev --retrieve-only
python main.py run --query rewrite --retriever dense --reranker cross --split dev --retrieve-only
python main.py report --split dev
```

`report` writes `results/comparison/<split>/comparison.md`. It scores every system that already has a run, with `title_bm25_none` as the baseline, and lists the systems that have not been run. The two finished title systems are included from `results/` until a new run replaces them.

Three dev checks sit outside the 12. A `k` other than 100 is stored in its own folder, so it does not replace the run at `k=100`. `title_late_none` searches every v2 passage with late interaction. The other two ask the late reranker to reorder 200 passages instead of 100.

```bash
export CUDA_VISIBLE_DEVICES=0
python main.py run --query title --retriever late --reranker none --split dev --retrieve-only
python main.py run --query title --retriever bm25 --reranker late --k 200 --split dev --retrieve-only
python main.py run --query title --retriever dense --reranker late --k 200 --split dev --retrieve-only
python main.py report --split dev
```

`sparse` is accepted as `bm25`. `--retrieve-only` skips the verdict model, which is what you want while comparing rankings. Omit it to score the top 5 with Llama after retrieval. A run is written to `runs/dev/<query>_<retriever>_<reranker>/`. The printed `eval_retrieval.py` command is the report.

The dense index is still `retrieval/indexes/dense_v2`. `--reindex` rebuilds it. Rewritten queries are cached in `runs/rewrite.csv`, so a second `rewrite` continues rather than starting over. `--questions` defaults to 10, matching the paper. `--limit 5` is a smoke test.

GPU 0 is often already in use. Prefix the commands with `CUDA_VISIBLE_DEVICES=1`.

## Run

From the repository root. This writes a new index and does not reuse `retrieval/indexes/dense`:

```bash
CUDA_VISIBLE_DEVICES=1 python main.py --retriever dense --retrieve-only
```

Omit `--retrieve-only` to also run the verdict model. Omit `--model` to use Llama 3.1 8B. That model does not fit a 16 GB T4 in full precision; pass `--model HuggingFaceTB/SmolLM2-1.7B-Instruct` for the verdict, and the same flag to `rewrite` if Llama does not load. The first dense run embeds the v2 passages and, only after the batch bar reaches 100%, writes:

```text
retrieval/indexes/dense_v2/embeddings.npy
retrieval/indexes/dense_v2/meta.parquet
retrieval/indexes/dense_v2/config.json
```

The next run in the same home directory loads those files. `--reindex` builds them again. Do not commit the index, `runs/`, or `results/`.

`generator/generator.py` is the verdict model. `data/claim_check.py` is the Qwen title filter and does not read the retrieval run. The verdict prompt still shows passage text only.

## Keeping the index

Restarting the kernel does not delete the index. A new container keeps it only when the home directory is persistent. The index is generated data, about 90 MB, and does not belong in git.

After `config.json` exists, pack it in the container:

```bash
cd ~/nlp-prj-2026/retrieval/indexes
tar -czf ~/dense-index.tar.gz dense_v2
```

Download `dense-index.tar.gz` from the Jupyter file list (home directory). Unpack it on the laptop so the files sit at `retrieval/indexes/dense_v2`. Copy that folder back into a later session the same way. There is no SSH login as `jovyan`, so `scp jovyan@<host>` is not a real command.
