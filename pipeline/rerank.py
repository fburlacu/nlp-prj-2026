"""Rerank one first-stage list. The query is the original claim, not a rewritten string.

cross: a cross-encoder scores the concatenated claim and passage.
late:  late interaction scores token vectors with MaxSim.
"""
import numpy as np
import pandas as pd

CROSS_MODEL = "BAAI/bge-reranker-base"
LATE_MODEL = "answerdotai/answerai-colbert-small-v1"
RERANKERS = ("none", "cross", "late")


def clip_words(text, limit):
    words = str(text).split()
    if len(words) <= limit:
        return str(text)
    return " ".join(words[:limit])


def _as_scores(value):
    if hasattr(value, "detach"):
        value = value.detach().float().cpu().numpy()
    return np.asarray(value, dtype=np.float32).reshape(-1)


def _cross_scores(model, claim, documents, batch_size):
    pairs = [(claim, document) for document in documents]
    return _as_scores(model.predict(pairs, batch_size=batch_size, show_progress_bar=False))


def _late_scores(model, claim, documents, batch_size):
    query = model.encode_query(claim, show_progress_bar=False)
    docs = model.encode_document(documents, batch_size=batch_size, show_progress_bar=False)
    return _as_scores(model.similarity(query, docs))


def load_reranker(kind, device):
    if kind == "cross":
        from sentence_transformers import CrossEncoder
        return CrossEncoder(CROSS_MODEL, device=device), _cross_scores
    if kind == "late":
        from sentence_transformers import MultiVectorEncoder
        # The checkpoint class is HF_ColBERT, defined in the model repository.
        return MultiVectorEncoder(LATE_MODEL, device=device, trust_remote_code=True), _late_scores
    raise SystemExit(f"unknown reranker {kind}")


def rerank(ranked, claims, texts, kind, device=None, batch_size=16, word_limit=400):
    """Reorder every claim's passages. kind='none' returns ranked unchanged."""
    if kind == "none" or ranked.empty:
        return ranked
    model, score_fn = load_reranker(kind, device)
    rows = []
    groups = list(ranked.groupby("query_id", sort=False))
    for done, (query_id, group) in enumerate(groups, 1):
        passage_ids = group["passage_id"].tolist()
        documents = [clip_words(texts.get(pid, ""), word_limit) for pid in passage_ids]
        scores = score_fn(model, claims[query_id], documents, batch_size)
        if len(scores) != len(passage_ids):
            raise SystemExit(f"{kind} returned {len(scores)} scores for {len(passage_ids)} passages")
        order = np.argsort(-scores, kind="stable")
        for rank, index in enumerate(order, 1):
            rows.append((query_id, rank, passage_ids[index], float(scores[index])))
        print(f"  reranked {done}/{len(groups)}", end="\r")
    print()
    return pd.DataFrame(rows, columns=["query_id", "rank", "passage_id", "score"])
