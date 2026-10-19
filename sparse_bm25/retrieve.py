"""BM25 retrieval run. Writes
  <output>.parquet      query_id, rank (1-based), passage_id, score  (top k per query)
  <output>.config.json  all settings, input file hashes, query counts and timings
"""
import sys
import json
import time
import hashlib
import argparse
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # project root, for data.preprocessing
from bm25 import BM25

ap = argparse.ArgumentParser()
ap.add_argument("--passages", default=str(HERE.parent / "data" / "passages.parquet"))
ap.add_argument("--queries", default=str(HERE.parent / "data" / "queries.csv"))
ap.add_argument("--output", required=True, help="run file (.parquet)")
ap.add_argument("--k", type=int, default=100, help="passages kept per query")
ap.add_argument("--k1", type=float, default=1.2)
ap.add_argument("--b", type=float, default=0.75)
ap.add_argument("--split", choices=["dev", "test"], help="only queries from this split")
ap.add_argument("--set", dest="qset", choices=["main", "article", "extra"], help="only queries from this set")
a = ap.parse_args()

split = lambda s: [x for x in str(s).split("|") if x and x != "nan"]

passages = pd.read_parquet(a.passages)
passages["doc_key"] = passages["doc_key"].fillna("")
queries = pd.read_csv(a.queries, dtype=str, keep_default_na=False)
if a.split:
    queries = queries[queries["split"] == a.split]
if a.qset:
    queries = queries[queries["set"] == a.qset]
print(f"{len(passages)} passages | {len(queries)} queries | k1={a.k1} b={a.b} k={a.k}")

t0 = time.perf_counter()
bm25 = BM25(passages["text"].tolist(), k1=a.k1, b=a.b)
build_s = time.perf_counter() - t0
print(f"Index built in {build_s:.1f}s | vocabulary {len(bm25.vocab)} terms | "
      f"{bm25.W.nnz} non-zeros ({bm25.W.data.nbytes / 2**20:.0f} MB weights)")

row_of = {p: i for i, p in enumerate(passages["passage_id"])}
rows_of_doc = passages.groupby("doc_key").indices  # positions in the FULL frame (do not filter first)
rows_of_doc.pop("", None)                           # EEAS passages have no doc_key
pid = passages["passage_id"].to_numpy()
k = min(a.k, len(passages) - 1)


def retrieve(q):
    s = bm25.scores(q.text)
    ex = [row_of[p] for p in split(q.exclude_passage_ids) if p in row_of]
    ex += [r for d in split(q.exclude_doc_key) for r in rows_of_doc.get(d, [])]
    s[ex] = -np.inf
    top = np.argpartition(-s, k)[:k]
    top = top[np.argsort(-s[top], kind="stable")]
    return top[np.isfinite(s[top])], s


rows, latency = [], []
for q in queries.itertuples(index=False):
    t = time.perf_counter()
    top, s = retrieve(q)
    latency.append(time.perf_counter() - t)
    rows += [(q.query_id, r, pid[i], float(s[i])) for r, i in enumerate(top, 1)]

run = pd.DataFrame(rows, columns=["query_id", "rank", "passage_id", "score"])

out = Path(a.output)
out.parent.mkdir(parents=True, exist_ok=True)
run.to_parquet(out, index=False)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


lat_ms = np.array(latency) * 1000
config = {
    "retriever": "bm25",
    "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "command": " ".join(sys.argv),
    "params": {"k1": a.k1, "b": a.b, "k": a.k, "idf": "lucene: log(1 + (N - df + 0.5) / (df + 0.5))",
               "tokenizer": "data.preprocessing.tokenize (lowercase, English stopwords, Snowball)"},
    "filters": {"split": a.split, "set": a.qset},
    "inputs": {"passages": str(Path(a.passages).resolve()), "passages_sha256": sha256(a.passages),
               "queries": str(Path(a.queries).resolve()), "queries_sha256": sha256(a.queries)},
    "counts": {"n_passages": len(passages), "n_queries": len(queries), "n_rows": len(run),
               "vocabulary": len(bm25.vocab), "nonzeros": int(bm25.W.nnz),
               "queries_by_set_label_split": {"/".join(k): int(v) for k, v in
                                              queries.groupby(["set", "label", "split"]).size().items()}},
    "timing": {"index_build_s": round(build_s, 2),
               "index_weights_mb": round(bm25.W.data.nbytes / 2**20, 1),
               "query_ms_p50": round(float(np.percentile(lat_ms, 50)), 3),
               "query_ms_p95": round(float(np.percentile(lat_ms, 95)), 3),
               "query_ms_mean": round(float(lat_ms.mean()), 3)},
}
out.with_suffix(".config.json").write_text(json.dumps(config, indent=2))
print(f"Saved {len(run)} rows to {out} | latency p50 {config['timing']['query_ms_p50']} ms, "
      f"p95 {config['timing']['query_ms_p95']} ms")
