"""First-stage retrieval. Several search strings for one claim are fused with RRF.

BM25 reads the unchunked v2 passages, one disproof per case. Dense reads the
chunked index from retrieval/dense.py and does not stem the text.
"""
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline.rrf import fuse
from retrieval.dense import encode, exclusion_lists, load_encoder, load_index, topk_indices

ROOT = Path(__file__).resolve().parents[1]


def load_queries(path, split=None, query_set=None, limit=None):
    queries = pd.read_csv(path, dtype=str, keep_default_na=False)
    if split:
        queries = queries[queries["split"] == split]
    if query_set:
        queries = queries[queries["set"] == query_set]
    if "set" in queries.columns:
        kept = queries["set"].isin({"main", "article"})
        skipped = int((~kept).sum())
        if skipped:
            print(f"Skipping {skipped} queries whose set has no passages")
        queries = queries[kept]
    if limit:
        queries = queries.head(limit)
    queries = queries[queries["text"].str.len() > 0].reset_index(drop=True)
    if queries.empty:
        raise SystemExit("no queries selected")
    for column in ("exclude_passage_ids", "exclude_doc_key", "date"):
        if column not in queries.columns:
            queries[column] = ""
    return queries


def search_strings(queries, query_mode, rewrite_path):
    """One row per string that will be searched. The claim title is always included."""
    base = queries[["query_id", "set", "text", "exclude_passage_ids", "exclude_doc_key"]].copy()
    base = base.rename(columns={"text": "claim"})
    if query_mode == "title":
        base["text"] = base["claim"]
        return base.reset_index(drop=True)

    path = Path(rewrite_path)
    if not path.exists():
        raise SystemExit(f"no rewritten queries at {path}. Run: python -m pipeline rewrite --split dev")
    written = pd.read_csv(path, dtype=str, keep_default_na=False)
    by_id = {qid: group["search_query"].tolist() for qid, group in written.groupby("query_id", sort=False)}
    rows = []
    missing = 0
    for record in base.to_dict("records"):
        strings = []
        for text in [record["claim"], *by_id.get(record["query_id"], [])]:
            text = str(text).strip()
            if text and text not in strings:
                strings.append(text)
        if record["query_id"] not in by_id:
            missing += 1
        for text in strings:
            rows.append({**record, "text": text})
    if missing:
        print(f"{missing} claims have no rewritten queries; those searches use the title only")
    return pd.DataFrame(rows)


def load_bm25_passages(path):
    frame = pd.read_parquet(path)
    if "source" in frame.columns:
        frame = frame.rename(columns={"source": "doc_type", "case_id": "case_links", "doc_id": "doc_key"})
        frame["doc_type"] = frame["doc_type"].replace({"leite_article": "article"})
    if "doc_key" not in frame.columns:
        frame["doc_key"] = ""
    frame["doc_key"] = frame["doc_key"].fillna("").astype(str)
    frame["set"] = frame["set"].fillna("").astype(str)
    return frame.reset_index(drop=True)


def _bm25_lists(passages, searches, k, k1, b):
    from retrieval.bm25 import BM25

    needed = set(searches["set"])
    indexes = {}
    for name, pos in passages.groupby("set").indices.items():
        if name not in needed:
            continue
        indexes[name] = (BM25(passages["text"].iloc[pos].tolist(), k1=k1, b=b), np.asarray(pos))
    print("BM25 index: " + ", ".join(f"{name} {len(pos)}" for name, (_, pos) in indexes.items()))

    row_of = {pid: i for i, pid in enumerate(passages["passage_id"])}
    rows_of_doc = {}
    for i, key in enumerate(passages["doc_key"].tolist()):
        if key:
            rows_of_doc.setdefault(key, []).append(i)
    pid = passages["passage_id"].to_numpy()
    lists = []
    for row in searches.itertuples(index=False):
        scores = np.full(len(passages), -np.inf, dtype=np.float32)
        model, pos = indexes.get(row.set, (None, None))
        if model is not None:
            scores[pos] = model.scores(row.text)
        banned = [row_of[p] for p in str(row.exclude_passage_ids).split("|") if p in row_of]
        banned += [i for key in str(row.exclude_doc_key).split("|") if key for i in rows_of_doc.get(key, [])]
        if banned:
            scores[banned] = -np.inf
        finite = np.flatnonzero(np.isfinite(scores) & (scores > 0))
        if len(finite) == 0:
            lists.append((row.query_id, []))
            continue
        keep = min(k, len(finite))
        chosen = finite[np.argpartition(-scores[finite], keep - 1)[:keep]]
        chosen = chosen[np.argsort(-scores[chosen], kind="stable")]
        lists.append((row.query_id, [pid[i] for i in chosen]))
    return lists


def _dense_lists(searches, index_dir, k, batch_size, device):
    config, embeddings, meta = load_index(index_dir)
    model = load_encoder(config["model"], device)
    prompt = config.get("query_prompt") or ""
    print(f"Encoding {len(searches)} search strings with {config['model']}")
    embedded = encode(model, searches["text"], batch_size, prompt=prompt)
    banned = exclusion_lists(searches, meta)
    pid = meta["passage_id"].to_numpy()
    sets = meta["set"].astype(str).to_numpy() if "set" in meta.columns else None
    lists = []
    for start in range(0, len(searches), batch_size):
        stop = min(start + batch_size, len(searches))
        sims = embedded[start:stop] @ embeddings.T
        block = searches.iloc[start:stop]
        for local, ban in enumerate(banned[start:stop]):
            if len(ban):
                sims[local, ban] = -np.inf
        if sets is not None:
            for local, query_set in enumerate(block["set"].astype(str)):
                sims[local, sets != query_set] = -np.inf
        chosen = topk_indices(sims, k)
        for local, query_id in enumerate(block["query_id"].tolist()):
            ranking = []
            for col in chosen[local]:
                if not np.isfinite(sims[local, col]):
                    continue
                ranking.append(pid[int(col)])
            lists.append((query_id, ranking))
        print(f"  searched {stop}/{len(searches)}", end="\r")
    print()
    return lists, meta


def _late_lists(passages, searches, k, batch_size, device):
    """Late interaction over every passage in the claim's set. Not a rerank of another list."""
    from pipeline.rerank import LATE_MODEL, _as_scores, clip_words
    from sentence_transformers import MultiVectorEncoder

    model = MultiVectorEncoder(LATE_MODEL, device=device, trust_remote_code=True)
    needed = set(searches["set"].astype(str))
    by_set = {}
    for name, idx in passages.groupby(passages["set"].astype(str)).indices.items():
        if name not in needed:
            continue
        pos = np.asarray(idx)
        texts = [clip_words(text, 400) for text in passages["text"].iloc[pos].tolist()]
        print(f"Encoding {len(texts)} {name} passages with {LATE_MODEL}")
        encoded = []
        for start in range(0, len(texts), batch_size):
            part = model.encode_document(
                texts[start:start + batch_size], batch_size=batch_size,
                show_progress_bar=False, convert_to_numpy=True,
            )
            encoded.extend(part)
            print(f"  encoded {min(start + batch_size, len(texts))}/{len(texts)}", end="\r")
        print()
        by_set[name] = (pos, encoded, {int(global_i): local for local, global_i in enumerate(pos)})

    row_of = {pid: i for i, pid in enumerate(passages["passage_id"])}
    rows_of_doc = {}
    for i, key in enumerate(passages["doc_key"].tolist()):
        if key:
            rows_of_doc.setdefault(key, []).append(i)
    pid = passages["passage_id"].to_numpy()
    lists = []
    total = len(searches)
    step = 256
    for done, row in enumerate(searches.itertuples(index=False), 1):
        packed = by_set.get(str(row.set))
        if packed is None:
            lists.append((row.query_id, []))
            continue
        pos, encoded, local_of = packed
        query = model.encode_query(row.text, show_progress_bar=False)
        parts = []
        for start in range(0, len(encoded), step):
            parts.append(_as_scores(model.similarity(query, encoded[start:start + step])))
        scores = np.concatenate(parts) if parts else np.zeros(0, dtype=np.float32)
        if len(scores) != len(encoded):
            raise SystemExit(f"late search returned {len(scores)} scores for {len(encoded)} passages")
        banned = [row_of[p] for p in str(row.exclude_passage_ids).split("|") if p in row_of]
        banned += [i for key in str(row.exclude_doc_key).split("|") if key for i in rows_of_doc.get(key, [])]
        for global_i in banned:
            local = local_of.get(global_i)
            if local is not None:
                scores[local] = -np.inf
        finite = np.flatnonzero(np.isfinite(scores))
        if len(finite) == 0:
            lists.append((row.query_id, []))
        else:
            keep = min(k, len(finite))
            chosen = finite[np.argpartition(-scores[finite], keep - 1)[:keep]]
            chosen = chosen[np.argsort(-scores[chosen], kind="stable")]
            lists.append((row.query_id, [pid[pos[i]] for i in chosen]))
        print(f"  searched {done}/{total}", end="\r")
    print()
    return lists


def retrieve(retriever, searches, k, passages_path, index_dir, batch_size, device, k1=1.2, b=0.75):
    """Return (ranked frame, passage table with passage_id, doc_type, case_links, doc_key, text)."""
    if retriever == "bm25":
        passages = load_bm25_passages(passages_path)
        lists = _bm25_lists(passages, searches, k, k1, b)
        lookup = passages
    elif retriever == "dense":
        lists, lookup = _dense_lists(searches, index_dir, k, batch_size, device)
    elif retriever == "late":
        passages = load_bm25_passages(passages_path)
        lists = _late_lists(passages, searches, k, batch_size, device)
        lookup = passages
    else:
        raise SystemExit(f"unknown retriever {retriever}")
    rows = fuse(lists, k)
    ranked = pd.DataFrame(rows, columns=["query_id", "rank", "passage_id", "score"])
    keep = ["passage_id", "doc_type", "case_links", "doc_key", "text"]
    return ranked, lookup[keep].drop_duplicates("passage_id")
