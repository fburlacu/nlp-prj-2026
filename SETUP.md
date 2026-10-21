# Setup

Run this on the university Jupyter GPU session (the terminal user is `jovyan`). That session is a container with Python 3.10 and two Tesla T4 GPUs. It does not have `module` or Conda. `module load anaconda3/2025.06` belongs to the EEMCS HPC login nodes and fails here.

The container driver supports CUDA 12.5. `requirements.txt` installs PyTorch `2.6.0+cu124` so the T4 is used. A newer default PyTorch wheel refuses this driver and silently runs on CPU.

GPU 0 is often already in use. GPU 1 has 16 GB free. A T4 does not fit Llama 3.1 8B, so the generator model here is SmolLM2 1.7B. It is public, and it is not the Qwen model that built the fact-query filter (`data/claim_check.py`).

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

## Run

From the repository root. This writes a new index and does not reuse `retrieval/indexes/dense`:

```bash
CUDA_VISIBLE_DEVICES=1 python main.py --retriever dense --model HuggingFaceTB/SmolLM2-1.7B-Instruct
```

Omit `--model` to use Llama 3.1 8B. That model does not fit a 16 GB T4 in full precision. The first run embeds the v2 passages and, only after the batch bar reaches 100%, writes:

```text
retrieval/indexes/dense_v2/embeddings.npy
retrieval/indexes/dense_v2/meta.parquet
retrieval/indexes/dense_v2/config.json
```

The next run in the same home directory loads those files. `--reindex` builds them again. Verdicts go to `generator/verdicts_dense_v2.csv`. The SmolLM2 file from the first data version is left as it is.

`sparse` and `hybrid` are accepted and report that they are not implemented yet. `--reranker <name>` is the later slot for a reranker. `--split dev` and `--limit 5` shorten a trial. `--retrieve-only` stops before SmolLM2.

`generator/generator.py` is the verdict model. `data/claim_check.py` is the Qwen title filter and does not read the retrieval run.

## Keeping the index

Restarting the kernel does not delete the index. A new container keeps it only when the home directory is persistent. The index is generated data, about 90 MB, and does not belong in git.

After `config.json` exists, pack it in the container:

```bash
cd ~/nlp-prj-2026/retrieval/indexes
tar -czf ~/dense-index.tar.gz dense_v2
```

Download `dense-index.tar.gz` from the Jupyter file list (home directory). Unpack it on the laptop so the files sit at `retrieval/indexes/dense_v2`. Copy that folder back into a later session the same way. There is no SSH login as `jovyan`, so `scp jovyan@<host>` is not a real command.
