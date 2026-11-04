"""One comparison report for every system that has a run.

  python main.py report --split dev
  python main.py report --split test

The two finished systems, title + BM25 and title + dense with no reranker, are
read from results/ until a new run of the same name exists under runs/. The
other ten are included after they are written. Paired differences use
title_bm25_none as the baseline when that run is present.

Retrieval uses retrieval/eval_retrieval.py. Verdicts use analysis/eval_detection.py,
and only the files written by generator/generator.py, so every system is scored
with the same prompt.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

from pipeline.cli import ROOT, cells, mode_name

HISTORICAL = {
    "dev": {
        "title_bm25_none": ROOT / "results" / "bm25" / "retrieval" / "v2" / "runs_tune" / "bm25_dev_k1-1.2_b-0.75.parquet",
        "title_dense_none": ROOT / "results" / "dense" / "v2" / "reports" / "dense_v2.parquet",
    },
    "test": {
        "title_bm25_none": ROOT / "results" / "bm25" / "retrieval" / "v2" / "runs_test" / "default" / "bm25_test_k1-1.2_b-0.75.parquet",
        "title_dense_none": ROOT / "results" / "dense" / "v2" / "reports" / "dense_v2.parquet",
    },
}
PASSAGES_FOR_EVAL = ROOT / "results" / "dense" / "v2" / "reports" / "passages_for_eval.parquet"
BASELINE = "title_bm25_none"


def _runs(split):
    found, missing = [], []
    for query, retriever, reranker in cells():
        name = mode_name(query, retriever, reranker)
        folder = ROOT / "runs" / split / name
        parquet = folder / f"{name}.parquet"
        historical = HISTORICAL[split].get(name)
        if parquet.exists():
            found.append((name, parquet, folder / "passages.parquet", folder / "verdicts.csv"))
        elif historical is not None and historical.exists():
            found.append((name, historical, None, None))
        else:
            missing.append(name)
    order = {mode_name(*cell): i for i, cell in enumerate(cells())}
    found.sort(key=lambda item: (item[0] != BASELINE, order[item[0]]))
    return found, missing


def _passages(path):
    frame = pd.read_parquet(path)
    rename = {"source": "doc_type", "case_id": "case_links", "doc_id": "doc_key"}
    frame = frame.rename(columns={old: new for old, new in rename.items() if old in frame.columns})
    if "doc_type" in frame.columns:
        frame["doc_type"] = frame["doc_type"].replace({"leite_article": "article"})
    for column in ("case_links", "doc_key"):
        if column not in frame.columns:
            frame[column] = ""
    return frame[["passage_id", "doc_type", "case_links", "doc_key"]].fillna("")


def _union_passages(found, destination):
    frames = []
    if any(passages is None for _, _, passages, _ in found) and PASSAGES_FOR_EVAL.exists():
        frames.append(_passages(PASSAGES_FOR_EVAL))
    for _, _, passages, _ in found:
        if passages is not None and passages.exists():
            frames.append(_passages(passages))
    if not frames:
        raise SystemExit(f"no passage table for these runs. Expected {PASSAGES_FOR_EVAL}")
    table = pd.concat(frames, ignore_index=True).drop_duplicates("passage_id")
    path = destination / "passages.parquet"
    table.to_parquet(path, index=False)
    return path


def _named_runs(found, destination):
    folder = destination / "runs"
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, source, _, _ in found:
        target = folder / f"{name}.parquet"
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        paths.append(target)
    return paths


def _verdict_files(found, destination):
    queries = pd.read_csv(ROOT / "data" / "queries_v2.csv", dtype=str, keep_default_na=False)
    keep = queries[["query_id", "set", "split", "label"]]
    folder = destination / "predictions"
    paths = []
    for name, _, _, verdicts in found:
        if verdicts is None or not verdicts.exists():
            continue
        frame = pd.read_csv(verdicts, dtype=str, keep_default_na=False)
        frame = frame.rename(columns={"verdict": "pred"})
        frame = frame.merge(keep, on="query_id", how="left")
        path = folder / f"{name}.csv"
        folder.mkdir(parents=True, exist_ok=True)
        frame[["query_id", "set", "split", "label", "pred"]].to_csv(path, index=False)
        paths.append(path)
    return paths


def _run(script, args):
    subprocess.run([sys.executable, str(ROOT / script), *args], check=True, cwd=ROOT)


def report(split, query_set=None):
    found, missing = _runs(split)
    if not found:
        raise SystemExit("no runs to compare. " + ", ".join(missing))
    destination = ROOT / "results" / "comparison" / split
    destination.mkdir(parents=True, exist_ok=True)
    passages = _union_passages(found, destination)
    runs = _named_runs(found, destination)
    retrieval_csv = destination / "retrieval.csv"
    command = [
        "--runs", *map(str, runs),
        "--passages", str(passages),
        "--queries", str(ROOT / "data" / "queries_v2.csv"),
        "--split", split,
        "--output", str(retrieval_csv),
    ]
    if query_set:
        command += ["--set", query_set]
    _run("retrieval/eval_retrieval.py", command)

    verdicts = _verdict_files(found, destination)
    detection_md = ""
    if len(verdicts) >= 1:
        detection_csv = destination / "detection.csv"
        _run("analysis/eval_detection.py", [
            "--preds", *map(str, verdicts),
            "--queries", str(ROOT / "data" / "queries_v2.csv"),
            "--retrieval", str(retrieval_csv.with_suffix(".per_query.csv")),
            "--output", str(detection_csv),
        ])
        detection_md = detection_csv.with_suffix(".md").read_text(encoding="utf-8")

    retrieval_md = retrieval_csv.with_suffix(".md").read_text(encoding="utf-8")
    included = ", ".join(name for name, *_ in found)
    absent = ", ".join(missing) if missing else "none"
    baseline = found[0][0]
    header = [
        f"# Comparison, {split}",
        "",
        f"Included: {included}.",
        f"Not run yet: {absent}.",
        f"Paired differences are against `{baseline}`.",
        "",
        "Retrieval is scored for every included system. Verdicts are scored only when",
        "`generator/generator.py` wrote them, so the prompt is the same for each system.",
        "A run with no rows for a query set is scored as a miss on that set.",
        "The saved dev BM25 run searched the main set only.",
        "",
    ]
    body = "\n".join(header) + retrieval_md
    if detection_md:
        body += "\n" + detection_md
    report_path = destination / "comparison.md"
    report_path.write_text(body, encoding="utf-8")
    print(f"Wrote {report_path}")
    if missing:
        print(f"Still missing: {', '.join(missing)}")
    return report_path
