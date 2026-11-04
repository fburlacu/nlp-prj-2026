"""Write a run in the two shapes the rest of the project already reads.

<name>.parquet is query_id, rank, passage_id, score for retrieval/eval_retrieval.py.
<name>.jsonl is one claim plus its passages, text only, for generator/generator.py.
passages.parquet holds the retrieved passage metadata the scorer joins on.
"""
import json
from pathlib import Path

import pandas as pd


def write_run(ranked, lookup, claims, directory, name, config):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    ranked = ranked.sort_values(["query_id", "rank"]) if len(ranked) else ranked
    parquet_path = directory / f"{name}.parquet"
    ranked.to_parquet(parquet_path, index=False)

    retrieved = set(ranked["passage_id"]) if len(ranked) else set()
    passages = lookup[lookup["passage_id"].isin(retrieved)].drop_duplicates("passage_id")
    texts = dict(zip(passages["passage_id"], passages["text"]))
    passages.drop(columns=["text"]).to_parquet(directory / "passages.parquet", index=False)

    grouped = {qid: group for qid, group in ranked.groupby("query_id", sort=False)} if len(ranked) else {}
    jsonl_path = directory / f"{name}.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as handle:
        for query_id, claim in claims.items():
            rows = grouped.get(query_id)
            found = []
            if rows is not None:
                for record in rows.itertuples(index=False):
                    found.append({
                        "passage_id": record.passage_id,
                        "score": round(float(record.score), 6),
                        "text": texts.get(record.passage_id, ""),
                    })
            handle.write(json.dumps({
                "query_id": query_id, "text": claim, "passages": found,
            }, ensure_ascii=False) + "\n")

    config_path = directory / f"{name}.config.json"
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"Wrote {parquet_path} ({len(ranked)} rows, {len(claims)} claims)")
    return parquet_path, jsonl_path
