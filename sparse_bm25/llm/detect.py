"""LLM verdicts (RQ2): Llama 3.1 8B Instruct judges each query, given the top-k passages of a run file
(RAG) or no evidence at all (--run omitted: no-retrieval baseline).

Usage (e.g. from a Jupyter cell with !python):
  python detect.py --run ../sparse_bm25/runs_dev/bm25_dev_k1-1.2_b-0.75.parquet --split dev \
                   --output preds/bm25_dev_k5.csv [--k 5 --limit 20]
  python detect.py --split dev --output preds/noretrieval_dev.csv          # no-retrieval baseline
Writes
  <output>.csv          query_id, set, split, label, pred, p_disinformation, p_fact, p_inconclusive,
                        passage_ids, n_prompt_tokens
  <output>.config.json  model, prompt, k, inputs (with hashes), timing and GPU memory
The run is resumable: queries already in <output>.csv are skipped.

Verdict scoring: no sampling. The answer is read from the next-token distribution after the prompt:
the probability mass of each answer word (summed over 'false' / 'False' / 'FALSE' etc.) is
renormalised over the three answers, and the prediction is the most probable one. This is
deterministic and gives probabilities for precision-recall analysis.
  false   -> disinformation    the evidence refutes the claim / shows a documented disinformation narrative
  true    -> fact              the evidence supports the claim
  unknown -> inconclusive      the evidence is not sufficient
"""
import sys
import json
import time
import inspect
import hashlib
import argparse
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import torch
from huggingface_hub import try_to_load_from_cache
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL = "meta-llama/Llama-3.1-8B-Instruct"
SETS = ["main", "article"]          # the extra fact set is not part of either benchmark
BATCH_SIZE = 8
MAX_PASSAGE_WORDS = 250             # claims can be longer than the 220-word chunk cap
ANSWERS = {"false": "disinformation", "true": "fact", "unknown": "inconclusive"}
TYPE_NAME = {"eeas_claim": "EUvsDisinfo database: documented disinformation claim",
             "eeas_disproof": "EUvsDisinfo database: analysts' refutation",
             "article": "News article"}

SYSTEM = ("You are a fact-checking assistant. You judge whether a claim is disinformation, using only "
          "the evidence you are given. Answer with exactly one word: false, true or unknown.")
RAG_PROMPT = """Claim: {claim}

Evidence:
{evidence}

Based only on the evidence above, is the claim:
false - the evidence refutes the claim, or shows that it is a documented disinformation narrative
true - the evidence supports the claim
unknown - the evidence is not sufficient to decide

Answer with one word (false, true or unknown)."""
NO_RAG_PROMPT = """Claim: {claim}

No evidence is available. Based on your own knowledge, is the claim:
false - the claim is false or a known disinformation narrative
true - the claim is true
unknown - you cannot decide

Answer with one word (false, true or unknown)."""

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--run", help="retrieval run file (.parquet); omit for the no-retrieval baseline")
ap.add_argument("--passages", default=str(HERE.parent.parent / "data" / "passages.parquet"))
ap.add_argument("--queries", default=str(HERE.parent.parent / "data" / "queries.csv"))
ap.add_argument("--output", required=True, help="predictions file (.csv)")
ap.add_argument("--split", choices=["dev", "test"], help="only queries from this split")
ap.add_argument("--k", type=int, default=5, help="passages given to the LLM")
ap.add_argument("--limit", type=int, help="only the first N queries (quick test)")
a = ap.parse_args()

split = lambda s: [x for x in str(s).split("|") if x and x != "nan"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# ---------------- queries and evidence ----------------
queries = pd.read_csv(a.queries, dtype=str, keep_default_na=False)
queries = queries[queries["set"].isin(SETS)]
if a.split:
    queries = queries[queries["split"] == a.split]
if a.limit:
    queries = queries.head(a.limit)

evidence_ids = {}
if a.run:
    run = pd.read_parquet(a.run)
    run = run[run["query_id"].isin(queries["query_id"]) & (run["rank"] <= a.k)].sort_values(["query_id", "rank"])
    evidence_ids = run.groupby("query_id")["passage_id"].apply(list).to_dict()
    missing = set(queries["query_id"]) - set(evidence_ids)
    if missing:
        sys.exit(f"{len(missing)} queries are not in the run file (e.g. {sorted(missing)[:3]}); check --split")
    passages = pd.read_parquet(a.passages, columns=["passage_id", "doc_type", "text"]).set_index("passage_id")


def shorten(text):
    w = text.split()
    return text if len(w) <= MAX_PASSAGE_WORDS else " ".join(w[:MAX_PASSAGE_WORDS]) + " ..."


def prompt(q):
    if not a.run:
        user = NO_RAG_PROMPT.format(claim=q.text)
    else:
        ev = "\n\n".join(f"[{i}] ({TYPE_NAME[passages.at[p, 'doc_type']]}) {shorten(passages.at[p, 'text'])}"
                         for i, p in enumerate(evidence_ids[q.query_id], 1))
        user = RAG_PROMPT.format(claim=q.text, evidence=ev)
    msgs = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)


# ---------------- model ----------------
device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
if device == "cuda":                           # bf16 is emulated (slow) on pre-Ampere GPUs, e.g. Turing
    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported(including_emulation=False) else torch.float16
else:
    dtype = torch.float16 if device == "mps" else torch.float32
# model already downloaded -> no hub requests (compute nodes without internet wait for timeouts)
cached = isinstance(try_to_load_from_cache(MODEL, "config.json"), str)
try:
    import accelerate  # noqa: F401
    to_device = {"device_map": device}         # load shards straight onto the device
except ImportError:
    to_device = {}                             # load into CPU memory, then move
print(f"Loading {MODEL} on {device} ({dtype}) | local cache: {cached} | direct to device: {bool(to_device)}", flush=True)
t0 = time.perf_counter()
tok = AutoTokenizer.from_pretrained(MODEL, local_files_only=cached)
tok.padding_side = "left"                      # last position = next-token position for every row
if tok.pad_token is None:
    tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=dtype, local_files_only=cached, **to_device)
model = model.to(device).eval()
load_s = time.perf_counter() - t0
# compute logits for the last position only (full logits: batch x prompt length x 128k vocabulary)
fwd_params = inspect.signature(model.forward).parameters
LAST_ONLY = ({"logits_to_keep": 1} if "logits_to_keep" in fwd_params else
             {"num_logits_to_keep": 1} if "num_logits_to_keep" in fwd_params else {})

# token ids of every single-token spelling of each answer word
answer_ids = {}
for w in ANSWERS:
    ids = {tok.encode(v, add_special_tokens=False)[0] for v in [w, w.capitalize(), w.upper()]
           if len(tok.encode(v, add_special_tokens=False)) == 1}
    if not ids:
        sys.exit(f"answer word '{w}' is not a single token for {MODEL}")
    answer_ids[w] = sorted(ids)
print("Answer tokens:", {w: tok.convert_ids_to_tokens(i) for w, i in answer_ids.items()})

# ---------------- resume ----------------
out = Path(a.output)
out.parent.mkdir(parents=True, exist_ok=True)
done = set(pd.read_csv(out, dtype=str)["query_id"]) if out.exists() else set()
todo = queries[~queries["query_id"].isin(done)]
print(f"{len(queries)} queries | {len(done)} already done | {len(todo)} to do | k={a.k if a.run else 0}", flush=True)

# ---------------- inference ----------------
if device == "cuda":
    torch.cuda.reset_peak_memory_stats()
n_tokens, gen_s = [], 0.0
rows_q = list(todo.itertuples(index=False))
for start in range(0, len(rows_q), BATCH_SIZE):
    batch = rows_q[start:start + BATCH_SIZE]
    enc = tok([prompt(q) for q in batch], return_tensors="pt", padding=True, add_special_tokens=False).to(device)
    t = time.perf_counter()
    with torch.no_grad():
        logits = model(**enc, **LAST_ONLY).logits[:, -1, :].float()
    if device == "cuda":
        torch.cuda.synchronize()
    gen_s += time.perf_counter() - t
    probs = torch.softmax(logits, dim=-1)
    mass = torch.stack([probs[:, ids].sum(dim=-1) for ids in answer_ids.values()], dim=-1)
    mass = (mass / mass.sum(dim=-1, keepdim=True)).cpu().numpy()
    lens = enc["attention_mask"].sum(dim=1).tolist()
    n_tokens += lens
    rows = []
    for q, m, n in zip(batch, mass, lens):
        p = dict(zip(ANSWERS.values(), m.round(5)))
        rows.append({"query_id": q.query_id, "set": q.set, "split": q.split, "label": q.label,
                     "pred": max(p, key=p.get), **{f"p_{k}": v for k, v in p.items()},
                     "passage_ids": "|".join(evidence_ids.get(q.query_id, [])), "n_prompt_tokens": n})
    pd.DataFrame(rows).to_csv(out, mode="a", header=not out.exists(), index=False)
    print(f"  {min(start + BATCH_SIZE, len(rows_q))}/{len(rows_q)}", flush=True)

# ---------------- config ----------------
preds = pd.read_csv(out, dtype={"query_id": str})
config = {
    "model": MODEL, "device": device, "dtype": str(dtype),
    "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "command": " ".join(sys.argv),
    "mode": "rag" if a.run else "no_retrieval",
    "params": {"k": a.k if a.run else 0, "batch_size": BATCH_SIZE, "max_passage_words": MAX_PASSAGE_WORDS,
               "answers": ANSWERS, "answer_tokens": {w: tok.convert_ids_to_tokens(i) for w, i in answer_ids.items()},
               "scoring": "next-token probability mass per answer word, renormalised; argmax"},
    "prompt": {"system": SYSTEM, "user": RAG_PROMPT if a.run else NO_RAG_PROMPT, "passage_types": TYPE_NAME},
    "filters": {"split": a.split, "sets": SETS, "limit": a.limit},
    "inputs": {"run": str(Path(a.run).resolve()) if a.run else None, "run_sha256": sha256(a.run) if a.run else None,
               "queries": str(Path(a.queries).resolve()), "queries_sha256": sha256(a.queries)},
    "counts": {"n_predictions": len(preds), "pred_distribution": preds["pred"].value_counts().to_dict()},
    "timing_this_session": {"model_load_s": round(load_s, 1), "n_queries": len(rows_q),
                            "llm_s_per_query": round(gen_s / max(len(rows_q), 1), 4),
                            "prompt_tokens_mean": round(sum(n_tokens) / max(len(n_tokens), 1), 1),
                            "gpu_peak_mem_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2) if device == "cuda" else None},
    "prompt_tokens_mean_all": round(float(preds["n_prompt_tokens"].mean()), 1),
}
out.with_suffix(".config.json").write_text(json.dumps(config, indent=2))
print(f"Saved {len(preds)} predictions to {out} | {config['counts']['pred_distribution']}")
