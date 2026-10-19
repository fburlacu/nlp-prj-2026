# Setup

Run this project on the University of Twente EEMCS HPC cluster. The laptop has no Python environment for it.

Connect from campus or eduVPN, then log in to a head node:

```bash
ssh <ut-username>@hpc-head1.ewi.utwente.nl
```

`hpc-head2.ewi.utwente.nl` is the other head node. Copy this repository into your home directory. The head node is only for preparing the environment.

## Environment

Conda is provided as a module. Create the environment once:

```bash
module load anaconda3/2025.06
conda create -n nlp-prj python=3.11 -y
conda activate nlp-prj
pip install -r requirements.txt
```

Later jobs only need `module load anaconda3/2025.06` and `conda activate nlp-prj`.

## Hugging Face

Llama 3.1 8B Instruct is a gated model. Accept the license on the model page, then, on the head node:

```bash
huggingface-cli login
```

## Run

`data/passages.parquet` has to exist first. From `data/`, with `debunk_pool.csv` and `leite_en_clean.csv` in that folder:

```bash
python build_index.py --debunk_pool debunk_pool.csv --held_out held_out_links.csv --leite leite_en_clean.csv
```

Course work uses the `students` partition. Llama 3.1 8B needs a GPU with at least 16 GB of memory. From the repository root, one command selects the retriever and then runs the generator:

```bash
python main.py --retriever dense
```

`sparse` and `hybrid` are accepted and report that they are not implemented yet. `--reranker <name>` is the later slot for a reranker. On the cluster, submit that same command with `sbatch run_dense.sbatch`. The dense run writes `generator/verdicts_dense.csv`.

`generator/generator.py` is the RAG verdict model. `data/claim_check.py` is the separate Qwen title filter and does not read the retrieval run.
