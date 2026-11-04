"""Fact versus disinformation verdicts on the Leite articles.

The EEAS main set is disinformation versus inconclusive, so it is left out.
The verdict model is asked for one of two words. Rankings already written under
runs/<split>/ are reused. Results go to runs/binary/ so the three-way runs stay as they are.
"""
import json
from pathlib import Path

import pandas as pd

from pipeline.cli import ROOT, mode_name, test_cells

PASSAGES = ROOT / "data" / "passages_v2.parquet"
QUERIES = ROOT / "data" / "queries_v2.csv"
LABELS = ("disinformation", "fact")


def kept_queries(split):
    """Leite articles labeled fact or disinformation."""
    frame = pd.read_csv(QUERIES, dtype=str, keep_default_na=False)
    frame = frame[frame["split"] == split]
    frame = frame[frame["set"] == "article"]
    frame = frame[frame["label"].isin(LABELS)]
    frame = frame[frame["text"].str.len() > 0]
    if frame.empty:
        raise SystemExit(f"no fact or disinformation claims in {split}")
    return frame.reset_index(drop=True)


def _from_jsonl(path, keep):
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if str(row["query_id"]) in keep:
                rows.append(row)
    return rows


def _from_parquet(path, queries):
    ranked = pd.read_parquet(path)
    ranked = ranked[ranked["query_id"].astype(str).isin(queries.index)]
    needed = set(ranked["passage_id"].astype(str))
    passages = pd.read_parquet(PASSAGES, columns=["passage_id", "text"])
    passages = passages[passages["passage_id"].astype(str).isin(needed)]
    texts = dict(zip(passages["passage_id"].astype(str), passages["text"]))
    rows = []
    for query_id, claim in queries["text"].items():
        group = ranked[ranked["query_id"].astype(str) == query_id]
        found = []
        if len(group):
            group = group.sort_values("rank")
            for record in group.itertuples(index=False):
                found.append({
                    "passage_id": record.passage_id,
                    "score": round(float(record.score), 6),
                    "text": texts.get(str(record.passage_id), ""),
                })
        rows.append({"query_id": query_id, "text": claim, "passages": found})
    return rows


def retrieval_rows(split, name):
    queries = kept_queries(split).set_index("query_id", drop=False)
    folder = ROOT / "runs" / split / name
    jsonl = folder / f"{name}.jsonl"
    parquet = folder / f"{name}.parquet"
    if jsonl.exists():
        rows = _from_jsonl(jsonl, set(queries.index))
    elif parquet.exists():
        rows = _from_parquet(parquet, queries)
    else:
        raise SystemExit(
            f"no ranking at {folder}. Run the title retrieval for {split} before the binary verdicts."
        )
    if len(rows) != len(queries):
        raise SystemExit(f"{name} has {len(rows)} binary claims, expected {len(queries)}")
    return rows


def run_split(split, model, max_passages=5):
    queries = kept_queries(split)
    counts = queries["label"].value_counts().to_dict()
    print(
        f"Binary {split}: {len(queries)} Leite articles | "
        f"disinformation {counts.get('disinformation', 0)} | fact {counts.get('fact', 0)}"
    )
    from generator.generator import run as generate

    for query, retriever, reranker in test_cells():
        name = mode_name(query, retriever, reranker)
        directory = ROOT / "runs" / "binary" / split / name
        directory.mkdir(parents=True, exist_ok=True)
        source = directory / "retrieval.jsonl"
        rows = retrieval_rows(split, name)
        with source.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(name)
        generate(
            source,
            directory / "verdicts.csv",
            directory / "verdict_cache.jsonl",
            model=model,
            max_passages=max_passages,
            binary=True,
        )
