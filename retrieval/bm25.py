
"""BM25 retrieval. Same shape as retrieval/dense.py: the class is imported by the
pipeline, and `python retrieval/bm25.py` writes one run.

The stemmer in data.preprocessing is only for this retriever.
"""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import scipy.sparse as sp
from data.preprocessing import tokenize

class BM25:
    def __init__(self, texts, k1=1.2, b=0.75):
        toks = [tokenize(t) for t in texts]
        self.vocab, rows, cols, vals = {}, [], [], []
        for d, ts in enumerate(toks):
            for t, c in Counter(ts).items():
                rows.append(d); cols.append(self.vocab.setdefault(t, len(self.vocab)))
                vals.append(c)
        tf = sp.coo_matrix((vals, (rows, cols)), shape=(len(toks), len(self.vocab)), dtype=np.float32)
        dl = np.bincount(tf.row, weights=tf.data, minlength=len(toks))
        avgdl = dl.mean()
        df = np.bincount(tf.col, minlength=len(self.vocab))
        N = len(toks)
        idf = np.log1p((N - df + 0.5) / (df + 0.5))           # Lucene idf
        w = tf.data * (k1 + 1) / (tf.data + k1 * (1 - b + b * dl[tf.row] / avgdl)) * idf[tf.col]
        self.W = sp.csc_matrix((w, (tf.row, tf.col)), shape=tf.shape)   # passages x terms

    def scores(self, query):
        ids = [self.vocab[t] for t in tokenize(query) if t in self.vocab]
        if not ids:
            return np.zeros(self.W.shape[0], np.float32)
        return np.asarray(self.W[:, ids].sum(axis=1)).ravel()


def main():
    """Write a BM25 run. Used by retrieval/tune_bm25.py. The 12 systems call the class through pipeline/."""
    import argparse
    import hashlib
    import json
    import time
    from datetime import datetime, timezone

    import pandas as pd

    ap = argparse.ArgumentParser(description="BM25 retrieval run")
    ap.add_argument("--passages", default=str(ROOT / "data" / "passages.parquet"))
    ap.add_argument("--queries", default=str(ROOT / "data" / "queries.csv"))
    ap.add_argument("--output", required=True, help="run file (.parquet)")
    ap.add_argument("--k", type=int, default=100, help="passages kept per query")
    ap.add_argument("--k1", type=float, default=1.2)
    ap.add_argument("--b", type=float, default=0.75)
    ap.add_argument("--split", choices=["dev", "test"], help="only queries from this split")
    ap.add_argument("--set", dest="qset", choices=["main", "article", "extra"], help="only queries from this set")
    a = ap.parse_args()

    parts = lambda s: [x for x in str(s).split("|") if x and x != "nan"]

    passages = pd.read_parquet(a.passages)
    if "doc_id" in passages:  # v2 index (data/passages_v2.parquet)
        passages = passages.rename(columns={"doc_id": "doc_key"})
    passages["doc_key"] = passages["doc_key"].fillna("")
    queries = pd.read_csv(a.queries, dtype=str, keep_default_na=False)
    if a.split:
        queries = queries[queries["split"] == a.split]
    if a.qset:
        queries = queries[queries["set"] == a.qset]
    print(f"{len(passages)} passages | {len(queries)} queries | k1={a.k1} b={a.b} k={a.k}")

    t0 = time.perf_counter()
    sets = ({s: pos for s, pos in passages.groupby("set").indices.items() if s in set(queries["set"])}
            if "set" in passages else {None: np.arange(len(passages))})
    indexes = {s: (BM25(passages["text"].iloc[pos].tolist(), k1=a.k1, b=a.b), pos) for s, pos in sets.items()}
    build_s = time.perf_counter() - t0
    vocab = sum(len(bm.vocab) for bm, _ in indexes.values())
    nnz = sum(int(bm.W.nnz) for bm, _ in indexes.values())
    weights_mb = sum(bm.W.data.nbytes for bm, _ in indexes.values()) / 2**20
    print(f"Index built in {build_s:.1f}s | " + ", ".join(
        f"{s or 'all'}: {len(pos)} passages, {len(bm.vocab)} terms" for s, (bm, pos) in indexes.items()
    ) + f" | {nnz} non-zeros ({weights_mb:.0f} MB weights)")

    row_of = {p: i for i, p in enumerate(passages["passage_id"])}
    rows_of_doc = passages.groupby("doc_key").indices
    rows_of_doc.pop("", None)
    pid = passages["passage_id"].to_numpy()
    k = min(a.k, len(passages) - 1)

    def search(q):
        s = np.full(len(passages), -np.inf, dtype=np.float32)
        bm, pos = indexes.get(q.set if "set" in passages else None, (None, None))
        if bm is not None:
            s[pos] = bm.scores(q.text)
        banned = [row_of[p] for p in parts(q.exclude_passage_ids) if p in row_of]
        banned += [r for d in parts(q.exclude_doc_key) for r in rows_of_doc.get(d, [])]
        s[banned] = -np.inf
        top = np.argpartition(-s, k)[:k]
        top = top[np.argsort(-s[top], kind="stable")]
        return top[np.isfinite(s[top])], s

    rows, latency = [], []
    for q in queries.itertuples(index=False):
        t = time.perf_counter()
        top, s = search(q)
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
                   "passages_by_set": {str(s): len(pos) for s, (_, pos) in indexes.items()},
                   "vocabulary": vocab, "nonzeros": nnz,
                   "queries_by_set_label_split": {"/".join(k): int(v) for k, v in
                                                  queries.groupby(["set", "label", "split"]).size().items()}},
        "timing": {"index_build_s": round(build_s, 2),
                   "index_weights_mb": round(weights_mb, 1),
                   "query_ms_p50": round(float(np.percentile(lat_ms, 50)), 3),
                   "query_ms_p95": round(float(np.percentile(lat_ms, 95)), 3),
                   "query_ms_mean": round(float(lat_ms.mean()), 3)},
    }
    out.with_suffix(".config.json").write_text(json.dumps(config, indent=2))
    print(f"Saved {len(run)} rows to {out} | latency p50 {config['timing']['query_ms_p50']} ms, "
          f"p95 {config['timing']['query_ms_p95']} ms")


if __name__ == "__main__":
    main()
