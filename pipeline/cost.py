"""Space, work, and wall time for one retrieval run.

A run records this under "cost" in its config. The comparison report reads it
back. Runs written before this recording have their score counts filled in
from the passage table; their clock and GPU peak stay blank.
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PASSAGES = ROOT / "data" / "passages_v2.parquet"
INDEX = ROOT / "retrieval" / "indexes" / "dense_v2"

_BM25_SIZES = {}
_DENSE = {}


def gpu_reset():
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
    except Exception:
        return


def gpu_gb():
    """Peak PyTorch reserved memory, in GB. None when this process used no GPU."""
    try:
        import torch
        if not torch.cuda.is_available():
            return None
        reserved = torch.cuda.max_memory_reserved()
        if reserved <= 0:
            return None
        return round(reserved / 1024**3, 3)
    except Exception:
        return None


def _bm25_sizes(path):
    key = str(path)
    if key not in _BM25_SIZES:
        frame = pd.read_parquet(path, columns=["set"])
        _BM25_SIZES[key] = frame["set"].astype(str).value_counts().to_dict()
    return _BM25_SIZES[key]


def _dense_index(index_dir, passages_path):
    key = str(index_dir)
    if key in _DENSE:
        return _DENSE[key]
    config_path = Path(index_dir) / "config.json"
    embeddings = Path(index_dir) / "embeddings.npy"
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding="utf-8"))
        n = int(config["n_passages"])
        dim = int(config["dim"])
        nbytes = embeddings.stat().st_size if embeddings.exists() else n * dim * 4
    else:
        from retrieval.dense import normalize_passages, read_table
        chunks, _ = normalize_passages(read_table(passages_path))
        n, dim = len(chunks), 384
        nbytes = n * dim * 4
    _DENSE[key] = (n, dim, int(nbytes))
    return _DENSE[key]


def _pairs_in_set(searches, sizes):
    counts = searches["set"].astype(str).value_counts().to_dict()
    return sum(int(count) * int(sizes.get(name, 0)) for name, count in counts.items())


def counts(retriever, reranker, searches, ranked, passages_path=PASSAGES, index_dir=INDEX):
    """How many scores this run computes, and how much the dense index stores."""
    sizes = _bm25_sizes(passages_path)
    record = {
        "n_queries": int(searches["query_id"].nunique()),
        "n_search_strings": int(len(searches)),
        "first_stage": retriever if retriever != "dense" else "dense_dot",
        "passage_encodings": 0,
        "stored_vectors": 0,
        "stored_bytes": 0,
        "vector_dim": None,
        "rerank": reranker,
        "rerank_pairs": 0 if reranker == "none" else int(len(ranked)),
    }
    if retriever == "bm25":
        record["first_stage"] = "bm25"
        record["first_stage_pairs"] = _pairs_in_set(searches, sizes)
    elif retriever == "dense":
        n, dim, nbytes = _dense_index(index_dir, passages_path)
        record["first_stage"] = "dense_dot"
        record["first_stage_pairs"] = int(len(searches) * n)
        record["stored_vectors"] = n
        record["stored_bytes"] = nbytes
        record["vector_dim"] = dim
    elif retriever == "late":
        record["first_stage"] = "late_maxsim"
        record["first_stage_pairs"] = _pairs_in_set(searches, sizes)
        present = set(searches["set"].astype(str))
        record["passage_encodings"] = sum(int(sizes.get(name, 0)) for name in present)
    else:
        raise SystemExit(f"unknown retriever {retriever}")
    return record


def attach_timing(record, retrieve_s, rerank_s):
    record = dict(record)
    record["retrieve_s"] = round(float(retrieve_s), 2)
    record["rerank_s"] = round(float(rerank_s), 2)
    record["gpu_peak_gb"] = gpu_gb()
    return record


def _commas(value):
    return f"{int(value):,}"


def format_stage(cost):
    kind = {"bm25": "BM25 scores", "dense_dot": "dot products", "late_maxsim": "MaxSim"}[cost["first_stage"]]
    text = f"{_commas(cost['first_stage_pairs'])} {kind}"
    if cost["n_search_strings"] != cost["n_queries"]:
        text += f" ({_commas(cost['n_search_strings'])} strings)"
    if cost.get("passage_encodings"):
        text += f", {_commas(cost['passage_encodings'])} passages encoded"
    return text


def format_rerank(cost):
    if not cost.get("rerank_pairs"):
        return "—"
    kind = {"cross": "cross-encoder pairs", "late": "MaxSim pairs"}.get(cost.get("rerank"), "pairs")
    return f"{_commas(cost['rerank_pairs'])} {kind}"


def format_space(cost):
    nbytes = cost.get("stored_bytes") or 0
    if not nbytes:
        return "—"
    mb = nbytes / 1024 / 1024
    if mb >= 1024:
        return f"{mb / 1024:.2f} GB"
    return f"{mb:.0f} MB"


def format_gpu(cost):
    value = cost.get("gpu_peak_gb")
    if value is None:
        return "—"
    return f"{float(value):.2f} GB"


def format_time(cost):
    if cost.get("retrieve_s") is None:
        return "—"
    total = float(cost["retrieve_s"]) + float(cost.get("rerank_s") or 0)
    if total < 60:
        return f"{total:.1f} s"
    return f"{total / 60:.1f} min"


def summarize(cost):
    clock = format_time(cost)
    detail = ""
    if cost.get("retrieve_s") is not None:
        detail = f" ({format_s(cost['retrieve_s'])} retrieval, {format_s(cost.get('rerank_s') or 0)} rerank)"
    return (
        f"Cost: {clock}{detail}, GPU peak {format_gpu(cost)}, "
        f"{format_stage(cost)}; rerank {format_rerank(cost)}; stored index {format_space(cost)}"
    )


def format_s(seconds):
    seconds = float(seconds)
    if seconds < 60:
        return f"{seconds:.1f} s"
    return f"{seconds / 60:.1f} min"


def label(name):
    if name == "title_late_none":
        return "late only"
    text, k = name, ""
    if "_k" in name:
        base, suffix = name.rsplit("_k", 1)
        if suffix.isdigit():
            text, k = base, f" · k{suffix}"
    query, retriever, reranker = text.split("_")
    retriever = {"bm25": "BM25", "dense": "dense", "late": "late"}[retriever]
    tail = "" if reranker == "none" else f" · {reranker}"
    if retriever == "late" and reranker == "none":
        return "late only" + k
    return f"{query} · {retriever}{tail}{k}"


def _config_for(name, parquet):
    path = Path(parquet).parent / f"{name}.config.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _identity(name, config):
    if config.get("retriever"):
        filters = config.get("filters") or {}
        return config["query"], config["retriever"], config["reranker"], filters
    text = name
    if "_k" in name:
        base, suffix = name.rsplit("_k", 1)
        if suffix.isdigit():
            text = base
    query, retriever, reranker = text.split("_")
    return query, retriever, reranker, {}


def cost_for(name, parquet, split):
    """Recorded cost, or score counts derived for a run that predates the clock."""
    config = _config_for(name, parquet)
    recorded = config.get("cost") or {}
    if recorded.get("first_stage_pairs") is not None and recorded.get("retrieve_s") is not None:
        return recorded
    query, retriever, reranker, filters = _identity(name, config)
    from pipeline.retrieve import load_queries, search_strings
    queries = load_queries(
        ROOT / "data" / "queries_v2.csv",
        filters.get("split") or split,
        filters.get("set"),
        filters.get("limit"),
        quiet=True,
    )
    query_file = "disproof.csv" if query == "disproof" else "rewrite.csv"
    searches = search_strings(queries, query, ROOT / "runs" / query_file, quiet=True)
    derived = counts(retriever, reranker, searches, _ranked_rows(parquet, reranker))
    derived["retrieve_s"] = recorded.get("retrieve_s")
    derived["rerank_s"] = recorded.get("rerank_s")
    derived["gpu_peak_gb"] = recorded.get("gpu_peak_gb")
    return derived


def _ranked_rows(parquet, reranker):
    if reranker == "none":
        return []
    frame = pd.read_parquet(parquet, columns=["query_id"])
    return frame


def section(found, split):
    """Markdown table. found is the (name, parquet, passages, verdicts) list from the report."""
    lines = [
        "## Cost",
        "",
        "Space is the stored dense index. Computation is the number of query–passage scores.",
        "Wall time is retrieval plus rerank, including the model load, and GPU peak is",
        "PyTorch reserved memory. A dash means that run was written before this was recorded.",
        "",
        "| Run | First stage | Rerank | Stored index | GPU peak | Wall time |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for name, parquet, _, _ in found:
        cost = cost_for(name, parquet, split)
        lines.append(
            f"| {label(name)} | {format_stage(cost)} | {format_rerank(cost)} | "
            f"{format_space(cost)} | {format_gpu(cost)} | {format_time(cost)} |"
        )
    lines += [
        "",
        "Dense multiplies each search string by every stored chunk, then drops the other set.",
        "BM25 and a late first stage score only the passages in the claim's set. The reranker",
        "scores the original title against each kept passage. The dense index is one shared file.",
        "BM25 builds its index in memory and does not save it. A late first stage encodes",
        "passages for that run and does not save the vectors. Watts are not sampled.",
        "",
    ]
    return "\n".join(lines)
