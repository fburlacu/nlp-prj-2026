"""Score a retrieval run and the generator verdicts.

Usage (from the repo root):
  python analysis/evaluate.py
  python analysis/evaluate.py --retriever dense --split test

Writes analysis/metrics_<retriever>.json with a "dev" and a "test" block.
Pass --split to keep only one of them. Gold rules match data/DATA_PREP.md:
a hit is an eeas_disproof whose case_links is in the query gold, or an article
chunk whose doc_key is in gold_doc_keys. Any chunk of a gold document counts.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KS = (1, 5, 10)
LABELS = ("disinformation", "fact", "inconclusive")


def pipe(value):
    if not value or str(value).lower() == "nan":
        return set()
    return {part for part in str(value).split("|") if part}


def load_queries(path):
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_verdicts(path):
    with path.open(encoding="utf-8", newline="") as f:
        return {row["query_id"]: row for row in csv.DictReader(f)}


def load_run(path):
    out = {}
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                row = json.loads(line)
                out[row["query_id"]] = row["passages"]
    return out


def gold_ranks(passages, links, docs):
    ranks = []
    for i, passage in enumerate(passages, 1):
        kind = passage.get("doc_type")
        if kind == "eeas_disproof" and passage.get("case_links") in links:
            ranks.append(i)
        elif kind == "article" and passage.get("doc_key") in docs:
            ranks.append(i)
    return ranks


def retrieval_block(rows):
    """rows: list of rank lists (empty if no hit)."""
    n = len(rows)
    if not n:
        return None
    first = [r[0] if r else None for r in rows]
    block = {"n": n, "mrr": round(sum((1 / r) if r else 0 for r in first) / n, 4)}
    for k in KS:
        block[f"recall@{k}"] = round(sum(1 for r in first if r and r <= k) / n, 4)
    return block


def group_retrieval(pairs):
    buckets = defaultdict(list)
    for label, ranks in pairs:
        buckets[label].append(ranks)
    return {label: retrieval_block(ranks) for label, ranks in sorted(buckets.items())}


def prf(counts, label):
    tp = counts[(label, label)]
    pred = sum(counts[(gold, label)] for gold in LABELS)
    gold = sum(counts[(label, pred_)] for pred_ in LABELS)
    precision = tp / pred if pred else 0
    recall = tp / gold if gold else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4),
            "support": gold}


def generator_block(pairs):
    """pairs: (gold, verdict, probabilities dict)."""
    counts = defaultdict(int)
    for gold, verdict, _ in pairs:
        counts[(gold, verdict)] += 1
    labels = [lab for lab in LABELS if any(g == lab for g, _, _ in pairs)]
    scored = [prf(counts, lab) for lab in labels]
    macro = round(sum(s["f1"] for s in scored) / len(scored), 4) if scored else 0
    correct = sum(counts[(lab, lab)] for lab in LABELS)
    return {
        "n": len(pairs),
        "accuracy": round(correct / len(pairs), 4) if pairs else 0,
        "macro_f1": macro,
        "per_label": {lab: prf(counts, lab) for lab in labels},
        "confusion": {f"{g}|{p}": counts[(g, p)] for g in labels for p in LABELS if counts[(g, p)]},
            "mean_probability": {
                lab: {name: round(sum(float(pr[name]) for g, _, pr in pairs if g == lab)
                                  / max(1, sum(1 for g, _, _ in pairs if g == lab)), 4)
                      for name in ("p_disinformation", "p_fact", "p_inconclusive")}
                for lab in labels
            },
    }


def score_split(queries, verdicts, run):
    strict_pairs, lenient_pairs, proxy_pairs = [], [], []
    top_types = defaultdict(int)
    gen_pairs = defaultdict(list)
    for query in queries:
        qid = query["query_id"]
        passages = run.get(qid, [])
        if passages:
            top_types[passages[0].get("doc_type") or "unknown"] += 1
        strict = pipe(query.get("gold_links"))
        lenient = pipe(query.get("gold_links_lenient"))
        docs = pipe(query.get("gold_doc_keys"))
        if strict:
            strict_pairs.append((query["overlap_bin"] or "none", gold_ranks(passages, strict, set())))
        if lenient:
            lenient_pairs.append((query["overlap_bin"] or "none", gold_ranks(passages, lenient, set())))
        if docs:
            proxy_pairs.append((query["set"], gold_ranks(passages, set(), docs)))
        verdict = verdicts.get(qid)
        if verdict:
            gen_pairs[query["set"]].append((query["label"], verdict["verdict"], verdict))
    return {
        "n_queries": len(queries),
        "retrieval": {
            "strict_eeas_disproof": {
                "all": retrieval_block([ranks for _, ranks in strict_pairs]),
                "by_overlap_bin": group_retrieval(strict_pairs),
            },
            "lenient_eeas_disproof": {
                "all": retrieval_block([ranks for _, ranks in lenient_pairs]),
                "by_overlap_bin": group_retrieval(lenient_pairs),
            },
            "proxy_article_gold": {
                "all": retrieval_block([ranks for _, ranks in proxy_pairs]),
            },
            "top1_doc_type": dict(top_types),
        },
        "generator": {name: generator_block(pairs) for name, pairs in sorted(gen_pairs.items())},
    }


def main():
    ap = argparse.ArgumentParser(description="Score retrieval and generator outputs")
    ap.add_argument("--retriever", default="dense_v2")
    ap.add_argument("--queries", default=str(ROOT / "data" / "queries_v2.csv"))
    ap.add_argument("--verdicts", default=None)
    ap.add_argument("--run", default=None)
    ap.add_argument("--split", choices=["dev", "test"], default=None,
                    help="score one split; default writes both")
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    verdicts_path = Path(args.verdicts or ROOT / "generator" / f"verdicts_{args.retriever}.csv")
    run_path = Path(args.run or ROOT / "retrieval" / "runs" / f"{args.retriever}.jsonl")
    out_path = Path(args.output or ROOT / "analysis" / f"metrics_{args.retriever}.json")

    queries = load_queries(Path(args.queries))
    verdicts = load_verdicts(verdicts_path)
    run = load_run(run_path)
    splits = [args.split] if args.split else ["dev", "test"]
    report = {
        "retriever": args.retriever,
        "splits": {
            split: score_split([q for q in queries if q["split"] == split], verdicts, run)
            for split in splits
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
