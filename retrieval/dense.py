"""Dense bi-encoder retrieval over the passage index.

Encodes raw passage and query text. Do not run preprocessing.tokenize on either
side: that stemmer is only for BM25.

The v2 table (data/passages_v2.parquet) is one disproof per case plus the
already-chunked article passages. Disproofs are chunked here, and every chunk
keeps case_links so a hit is still the gold case. A query searches only
passages of its own set (main disproofs, or article chunks).

The run file is one JSON object per query. generator/generator.py reads it.
A later sparse or hybrid retriever should write the same shape.

Usage (from the repo root):
  python retrieval/dense.py index
  python retrieval/dense.py search --split dev --limit 5
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BGE_QUERY_PROMPT = "Represent this sentence for searching relevant passages: "


def query_prompt_for(model_name):
    """BGE retrieval models expect an instruction on the query only."""
    name = model_name.lower()
    if "bge" in name and "bge-m3" not in name:
        return BGE_QUERY_PROMPT
    return ""


def read_table(path):
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"not found: {path}")
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def write_table(df, path):
    path = Path(path)
    try:
        df.to_parquet(path, index=False)
        return path
    except (ImportError, ValueError, OSError) as e:
        alt = path.with_suffix(".csv")
        df.to_csv(alt, index=False)
        print(f"(could not write parquet: {e}\n wrote {alt.name} instead)")
        return alt


def parse_pipe(value):
    if value is None:
        return []
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return []
    return [part for part in text.split("|") if part]


def load_encoder(model_name, device=None):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        raise SystemExit("pip install sentence-transformers") from e
    return SentenceTransformer(model_name, device=device)


def encode(model, texts, batch_size, prompt=""):
    texts = list(texts)
    if prompt:
        texts = [prompt + text for text in texts]
    emb = np.asarray(
        model.encode(texts, batch_size=batch_size, normalize_embeddings=True,
                     convert_to_numpy=True, show_progress_bar=True),
        dtype=np.float32,
    )
    norms = np.linalg.norm(emb, axis=1, keepdims=True)
    return emb / np.clip(norms, 1e-12, None)


_SENT = re.compile(r"(?<=[.!?…])[\"'”’)]*\s+(?=[\"'“‘(]?[A-Z0-9])")


def chunk_words(text, chunk_words=150, max_chunk_words=220, min_chunk_words=30):
    """Same sentence chunks as data/build_index.py. A short tail is merged back."""
    sents = []
    for para in re.split(r"\n\s*\n|\n", text or ""):
        for sentence in _SENT.split(para.strip()):
            words = sentence.split()
            while len(words) > max_chunk_words:
                sents.append(words[:chunk_words])
                words = words[chunk_words:]
            if words:
                sents.append(words)
    chunks, cur = [], []
    for words in sents:
        if cur and len(cur) + len(words) > chunk_words and len(cur) >= min_chunk_words:
            chunks.append(cur)
            cur = []
        cur = cur + words
        if len(cur) >= max_chunk_words:
            chunks.append(cur[:max_chunk_words])
            cur = cur[max_chunk_words:]
    if cur:
        if chunks and len(cur) < min_chunk_words:
            chunks[-1] = chunks[-1] + cur
        else:
            chunks.append(cur)
    return [" ".join(chunk) for chunk in chunks]


def normalize_passages(passages):
    """v2 columns become the names the run file and the scorer already use.

    Disproofs are one row per case in passages_v2.parquet. Chunk them and keep
    case_links on every piece. Article rows are already chunks.
    """
    frame = passages.copy()
    version = "v2" if "source" in frame.columns else "v1"
    if version == "v2":
        frame = frame.rename(columns={"source": "doc_type", "case_id": "case_links", "doc_id": "doc_key"})
        frame["doc_type"] = frame["doc_type"].replace({"leite_article": "article"})
    if "set" not in frame.columns:
        frame["set"] = ""
    for column in ("case_links", "doc_key", "set"):
        frame[column] = frame[column].fillna("").astype(str).replace({"None": "", "nan": ""})
    if version != "v2":
        return frame, version
    rows = []
    for record in frame.to_dict("records"):
        if record["doc_type"] != "eeas_disproof":
            rows.append(record)
            continue
        parts = chunk_words(record["text"]) or [record["text"]]
        if len(parts) == 1:
            record["text"] = parts[0]
            rows.append(record)
            continue
        for i, part in enumerate(parts):
            piece = dict(record)
            piece["passage_id"] = f"{record['case_links']}#disproof-{i}"
            piece["text"] = part
            rows.append(piece)
    return pd.DataFrame(rows), version


def build_index(passages_path, index_dir, model_name, batch_size, device, query_prompt):
    passages, version = normalize_passages(read_table(passages_path))
    keep = ["passage_id", "doc_type", "text", "case_links", "doc_key", "set"]
    missing = [c for c in keep if c not in passages.columns]
    if missing:
        raise SystemExit(f"{passages_path} is missing columns: {', '.join(missing)}")
    meta = passages[keep].fillna("").astype(str).reset_index(drop=True)
    meta = meta[meta["text"].str.len() > 0]
    if not meta["passage_id"].is_unique:
        raise SystemExit("duplicate passage_id in the passage table")

    print(f"Encoding {len(meta)} passages with {model_name}")
    model = load_encoder(model_name, device)
    embeddings = encode(model, meta["text"], batch_size)

    index_dir = Path(index_dir)
    index_dir.mkdir(parents=True, exist_ok=True)
    np.save(index_dir / "embeddings.npy", embeddings)
    meta_path = write_table(meta, index_dir / "meta.parquet")
    config = {
        "model": model_name,
        "query_prompt": query_prompt,
        "embeddings": "embeddings.npy",
        "meta": meta_path.name,
        "n_passages": int(len(meta)),
        "dim": int(embeddings.shape[1]),
        "passages": str(passages_path),
        "version": version,
    }
    (index_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(meta.groupby("doc_type").size().to_string())
    print(f"Wrote {index_dir} ({embeddings.shape[0]} x {embeddings.shape[1]})")


def load_index(index_dir):
    index_dir = Path(index_dir)
    config_path = index_dir / "config.json"
    if not config_path.exists():
        raise SystemExit(f"no index at {index_dir}; run: python retrieval/dense.py index")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    embeddings = np.load(index_dir / config["embeddings"])
    meta = read_table(index_dir / config["meta"]).reset_index(drop=True)
    if len(meta) != len(embeddings):
        raise SystemExit("meta rows and embeddings.npy disagree; rebuild the index")
    return config, embeddings, meta


def exclusion_lists(queries, meta):
    """Row indices to drop before ranking: own claim passage, own article, wire copies."""
    pid_index = {pid: i for i, pid in enumerate(meta["passage_id"])}
    doc_index = {}
    for i, key in enumerate(meta["doc_key"].astype(str)):
        if key:
            doc_index.setdefault(key, []).append(i)
    banned = []
    for row in queries.itertuples(index=False):
        rows = []
        for pid in parse_pipe(getattr(row, "exclude_passage_ids", "")):
            hit = pid_index.get(pid)
            if hit is not None:
                rows.append(hit)
        for key in parse_pipe(getattr(row, "exclude_doc_key", "")):
            rows.extend(doc_index.get(key, ()))
        banned.append(np.unique(np.asarray(rows, dtype=np.int64)) if rows else np.empty(0, dtype=np.int64))
    return banned


def topk_indices(sims, k):
    n = sims.shape[1]
    k = min(k, n)
    if k == n:
        return np.argsort(-sims, axis=1)
    part = np.argpartition(-sims, kth=k - 1, axis=1)[:, :k]
    row = np.arange(sims.shape[0])[:, None]
    order = np.argsort(-sims[row, part], axis=1)
    return part[row, order]


def search(queries_path, index_dir, output, k, batch_size, device, split, limit, model_name):
    if k < 1:
        raise SystemExit("--k must be at least 1")
    config, embeddings, meta = load_index(index_dir)
    if model_name and model_name != config["model"]:
        raise SystemExit(
            f"index was built with {config['model']}; omit --model or rebuild the index")
    model_name = config["model"]
    prompt = config.get("query_prompt") or ""

    queries = pd.read_csv(queries_path, dtype=str, keep_default_na=False)
    if split:
        queries = queries[queries["split"] == split]
    passage_sets = set(meta["set"].astype(str)) - {""} if "set" in meta.columns else set()
    if passage_sets and "set" in queries.columns:
        # Same scope as sparse_bm25/llm/detect.py: main and article. The extra
        # fact set has no passages in passages_v2.parquet and is not scored.
        kept = queries["set"].isin(passage_sets)
        skipped = sorted(set(queries.loc[~kept, "set"]))
        if skipped:
            print(f"Skipping {int((~kept).sum())} queries with no passages ({', '.join(skipped)})")
        queries = queries[kept]
    if limit:
        queries = queries.head(limit)
    queries = queries[queries["text"].str.len() > 0].reset_index(drop=True)
    if "exclude_passage_ids" not in queries.columns:
        queries["exclude_passage_ids"] = ""
    if "exclude_doc_key" not in queries.columns:
        queries["exclude_doc_key"] = ""
    if queries.empty:
        raise SystemExit("no queries to encode")

    print(f"Encoding {len(queries)} queries with {model_name}")
    model = load_encoder(model_name, device)
    q_emb = encode(model, queries["text"], batch_size, prompt=prompt)
    banned = exclusion_lists(queries, meta)
    records = meta.to_dict("records")

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with output.open("w", encoding="utf-8") as f:
        for start in range(0, len(queries), batch_size):
            stop = min(start + batch_size, len(queries))
            sims = q_emb[start:stop] @ embeddings.T
            block = queries.iloc[start:stop]
            for local, ban in enumerate(banned[start:stop]):
                if len(ban):
                    sims[local, ban] = -np.inf
            if "set" in meta.columns and "set" in block.columns and meta["set"].astype(str).str.len().any():
                sets = meta["set"].astype(str).to_numpy()
                for local, query_set in enumerate(block["set"].astype(str)):
                    sims[local, sets != query_set] = -np.inf
            chosen = topk_indices(sims, k)
            for local, (_, query) in enumerate(block.iterrows()):
                passages = []
                for col in chosen[local]:
                    score = float(sims[local, col])
                    if not np.isfinite(score):
                        continue
                    src = records[int(col)]
                    passages.append({
                        "passage_id": src["passage_id"],
                        "doc_type": src["doc_type"],
                        "score": round(score, 6),
                        "text": src["text"],
                        "case_links": src["case_links"],
                        "doc_key": src["doc_key"],
                    })
                f.write(json.dumps({
                    "query_id": query["query_id"],
                    "text": query["text"],
                    "passages": passages,
                }, ensure_ascii=False) + "\n")
                written += 1
            print(f"  retrieved {stop}/{len(queries)}", end="\r")
    print()
    print(f"Wrote {output}: {written} queries, k={k}")


def main():
    ap = argparse.ArgumentParser(description="Dense bi-encoder retrieval")
    sub = ap.add_subparsers(dest="cmd", required=True)

    idx = sub.add_parser("index", help="embed passages.parquet")
    idx.add_argument("--passages", default=str(ROOT / "data" / "passages_v2.parquet"))
    idx.add_argument("--index-dir", default=str(ROOT / "retrieval" / "indexes" / "dense_v2"))
    idx.add_argument("--model", default="BAAI/bge-small-en-v1.5")
    idx.add_argument("--batch-size", type=int, default=64)
    idx.add_argument("--device", default=None)
    idx.add_argument("--query-prompt", default=None,
                     help="prepended to queries only; default is the BGE instruction for BGE models")

    sea = sub.add_parser("search", help="embed queries.csv and write a run")
    sea.add_argument("--queries", default=str(ROOT / "data" / "queries_v2.csv"))
    sea.add_argument("--index-dir", default=str(ROOT / "retrieval" / "indexes" / "dense_v2"))
    sea.add_argument("--output", default=str(ROOT / "retrieval" / "runs" / "dense_v2.jsonl"))
    sea.add_argument("--k", type=int, default=10)
    sea.add_argument("--batch-size", type=int, default=64)
    sea.add_argument("--device", default=None)
    sea.add_argument("--split", choices=["dev", "test"], default=None)
    sea.add_argument("--limit", type=int, default=None)
    sea.add_argument("--model", default=None, help="must match the model stored in the index")

    args = ap.parse_args()
    if args.cmd == "index":
        prompt = args.query_prompt
        if prompt is None:
            prompt = query_prompt_for(args.model)
        build_index(args.passages, args.index_dir, args.model, args.batch_size, args.device, prompt)
    else:
        search(args.queries, args.index_dir, args.output, args.k, args.batch_size,
               args.device, args.split, args.limit, args.model)


if __name__ == "__main__":
    main()
