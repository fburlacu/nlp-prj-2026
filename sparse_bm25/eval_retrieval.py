"""Retrieval evaluation (RQ1). Works on any run file with columns query_id, rank, passage_id, score
(BM25, dense or hybrid), so all retrievers are scored identically.

Usage:
  python eval_retrieval.py --runs runs/bm25_dev.parquet [other runs ...] \
                           --output results/retrieval_dev.csv [--split dev --ks 1 5 10 20 100]
Gold levels (a query is scored on a level only if it has gold for it):
  strict   an eeas_disproof chunk of the query's own case                (gold_links)
  lenient  an eeas_disproof chunk of the own case or a direct near-duplicate (gold_links_lenient)
  case     any eeas_disproof OR eeas_claim passage of those cases          (gold_links_lenient)
           (the query's own claim is already excluded at retrieval time)
  proxy    any chunk of a same-debunk trustworthy article                 (gold_doc_keys)
Metrics per query: rank of the first gold passage, hit@k, reciprocal rank (MRR@mrr_k).
Groups: all queries, each overlap_bin (low/mid/high) and each entity_bin (entity/formulation; from
data/add_entity_overlap.py, which must have been run on queries.csv).
Writes
  <output>                 summary: run, level, set, split, bin, metric, n, mean, ci_lo, ci_hi
  <output>.per_query.csv   one row per run x level x query (input for later significance tests)
  <output>.paired.csv      if several runs: difference to the first run, paired bootstrap CI
  <output>.md              human-readable report: one table per level, bins x metrics, mean [95% CI]
  <output>.results.json    arguments + summary and paired results, nested run > level > set/split > bin > metric
"""
import sys
import json
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--runs", nargs="+", required=True, help="run files; the first is the baseline for paired differences")
ap.add_argument("--passages", default=str(HERE.parent / "data" / "passages.parquet"))
ap.add_argument("--queries", default=str(HERE.parent / "data" / "queries.csv"))
ap.add_argument("--output", required=True, help="summary file (.csv)")
ap.add_argument("--split", choices=["dev", "test"], help="only queries from this split")
ap.add_argument("--ks", type=int, nargs="+", default=[1, 5, 10, 20, 100])
ap.add_argument("--mrr_k", type=int, default=10)
ap.add_argument("--n_boot", type=int, default=1000)
ap.add_argument("--seed", type=int, default=0)
a = ap.parse_args()

split = lambda s: {x for x in str(s).split("|") if x and x != "nan"}

# level -> (gold column in queries.csv, passage types that count, passage column matched against gold)
LEVELS = {
    "strict": ("gold_links", {"eeas_disproof"}, "case_links"),
    "lenient": ("gold_links_lenient", {"eeas_disproof"}, "case_links"),
    "case": ("gold_links_lenient", {"eeas_disproof", "eeas_claim"}, "case_links"),
    "proxy": ("gold_doc_keys", {"article"}, "doc_key"),
}
METRICS = [f"hit@{k}" for k in a.ks] + [f"mrr@{a.mrr_k}"]
BIN_COLS = ["overlap_bin", "entity_bin"]  # entity_bin from data/add_entity_overlap.py
BIN_ORDER = {"low": 0, "mid": 1, "high": 2, "entity": 3, "formulation": 4, "all": 5}

passages = pd.read_parquet(a.passages, columns=["passage_id", "doc_type", "case_links", "doc_key"]).fillna("")
queries = pd.read_csv(a.queries, dtype=str, keep_default_na=False)
if "entity_bin" not in queries.columns:
    sys.exit(f"{a.queries} has no entity_bin column: run data/add_entity_overlap.py first")
if a.split:
    queries = queries[queries["split"] == a.split]
gold = {lvl: {q: g for q, g in zip(queries["query_id"], queries[col].map(split)) if g}
        for lvl, (col, _, _) in LEVELS.items()}


def per_query(path):
    name = Path(path).stem
    run = pd.read_parquet(path)
    run = run[run["query_id"].isin(queries["query_id"])].merge(passages, on="passage_id", how="left")
    if run["doc_type"].isna().any():
        sys.exit(f"{name}: {run['doc_type'].isna().sum()} retrieved passage_ids are not in {a.passages}")
    depth = run.groupby("query_id")["rank"].max()
    if depth.min() < max(a.ks):
        print(f"WARNING {name}: some queries have only {depth.min()} results; hit@{max(a.ks)} is a lower bound")
    out = []
    for lvl, (_, types, key) in LEVELS.items():
        g = gold[lvl]
        if not g:
            continue
        missing = set(g) - set(run["query_id"])
        if missing:
            print(f"WARNING {name}: {len(missing)} {lvl} queries are not in the run (scored as misses)")
        r = run[run["query_id"].isin(g) & run["doc_type"].isin(types)]
        r = r[[v in g[q] for q, v in zip(r["query_id"], r[key])]]
        first = r.groupby("query_id")["rank"].min().reindex(list(g))
        out.append(pd.DataFrame({"run": name, "level": lvl, "query_id": list(g), "first_rank": first.to_numpy()}))
    pq = pd.concat(out, ignore_index=True)
    for k in a.ks:
        pq[f"hit@{k}"] = (pq["first_rank"] <= k).astype(float)
    pq[f"mrr@{a.mrr_k}"] = np.where(pq["first_rank"] <= a.mrr_k, 1 / pq["first_rank"], 0.0)
    return pq.merge(queries[["query_id", "set", "split", "label", *BIN_COLS, "entity_overlap"]], on="query_id")


def groups(pq):
    """All queries of a (run, level, set, split), plus each overlap bin and each entity bin separately."""
    for keys, g in pq.groupby(["run", "level", "set", "split"], sort=False):
        yield (*keys, "all"), g
        for col in BIN_COLS:
            for b, gb in g.groupby(col):
                if b:
                    yield (*keys, b), gb


rng = np.random.default_rng(a.seed)


def boot_ci(x):
    means = x[rng.integers(0, len(x), (a.n_boot, len(x)))].mean(axis=1)
    return np.percentile(means, [2.5, 97.5])


names = [Path(r).stem for r in a.runs]
if len(set(names)) < len(names):
    sys.exit("run files must have distinct names")
pq = pd.concat([per_query(r) for r in a.runs], ignore_index=True)

rows = []
for (run, lvl, qset, spl, b), g in groups(pq):
    for m in METRICS:
        x = g[m].to_numpy()
        lo, hi = boot_ci(x)
        rows.append((run, lvl, qset, spl, b, m, len(x), x.mean(), lo, hi))
summary = pd.DataFrame(rows, columns=["run", "level", "set", "split", "bin", "metric", "n", "mean", "ci_lo", "ci_hi"])

paired = []
for other in names[1:]:
    both = pq[pq["run"] == names[0]].merge(pq[pq["run"] == other][["level", "query_id"] + METRICS],
                                          on=["level", "query_id"], suffixes=("", "_other"))
    for m in METRICS:
        both[m] = both[f"{m}_other"] - both[m]  # other minus baseline, per query
    both["run"] = f"{other} - {names[0]}"
    for (run, lvl, qset, spl, b), g in groups(both):
        for m in METRICS:
            d = g[m].to_numpy()
            lo, hi = boot_ci(d)
            paired.append((run, lvl, qset, spl, b, m, len(d), d.mean(), lo, hi))
paired = pd.DataFrame(paired, columns=summary.columns)

out = Path(a.output)
out.parent.mkdir(parents=True, exist_ok=True)
summary.round(4).to_csv(out, index=False)
pq.to_csv(out.with_suffix(".per_query.csv"), index=False)
if len(paired):
    paired.round(4).to_csv(out.with_suffix(".paired.csv"), index=False)


def nest(df):
    """run -> level -> set/split -> bin -> metric -> {n, mean, ci}"""
    res = {}
    for r in df.itertuples(index=False):
        node = res.setdefault(r.run, {}).setdefault(r.level, {}).setdefault(f"{r.set}/{r.split}", {})
        node.setdefault(r.bin, {})[r.metric] = {"n": int(r.n), "mean": round(float(r.mean), 4),
                                                "ci95": [round(float(r.ci_lo), 4), round(float(r.ci_hi), 4)]}
    return res


out.with_suffix(".results.json").write_text(json.dumps({
    "config": {"command": " ".join(sys.argv), **vars(a),
               "levels": {k: {"gold": c, "types": sorted(t), "match": m} for k, (c, t, m) in LEVELS.items()}},
    "summary": nest(summary),
    "paired_vs_first_run": nest(paired) if len(paired) else {},
}, indent=2))



BIN_LABEL = {"low": "overlap: low", "mid": "overlap: mid", "high": "overlap: high",
             "entity": "entity-driven", "formulation": "formulation-driven", "all": "**all**"}


def md_tables(df, signed=False):
    """One table per run x level x set/split: bins as rows, 'mean [ci_lo, ci_hi]' per metric.
    signed=True (paired differences): '+' signs, and * when the CI excludes 0."""
    f = (lambda v: f"{v:+.2f}") if signed else (lambda v: f"{v:.2f}")
    lines = []
    for (run, lvl, qset, spl), g in df.groupby(["run", "level", "set", "split"], sort=False):
        lines += [f"### {run} · {lvl} · {qset}/{spl}", "",
                  "| Bin | n | " + " | ".join(METRICS) + " |", "|---|---:|" + "---:|" * len(METRICS)]
        for b in sorted(g["bin"].unique(), key=BIN_ORDER.get):
            gb = g[g["bin"] == b].set_index("metric")
            cells = []
            for m in METRICS:
                r = gb.loc[m]
                star = "*" if signed and (r.ci_lo > 0 or r.ci_hi < 0) else ""
                cells.append(f"{f(r['mean'])}{star} [{f(r.ci_lo)}, {f(r.ci_hi)}]")
            lines.append(f"| {BIN_LABEL[b]} | {int(gb['n'].iloc[0])} | " + " | ".join(cells) + " |")
        lines.append("")
    return lines


levels_doc = {"strict": "own disproof", "lenient": "own or near-duplicate disproof",
              "case": "disproof or claim of own / near-duplicate case", "proxy": "same-debunk trustworthy article"}
md = [f"# Retrieval evaluation", "",
      f"Runs: {', '.join(f'`{n}`' for n in names)} | split: {a.split or 'all'} | "
      f"cells: mean [95% bootstrap CI, {a.n_boot} resamples]", "",
      "Gold levels: " + "; ".join(f"**{k}** = {v}" for k, v in levels_doc.items()), "",
      "Rows: all queries, then by title–disproof word overlap (`overlap_bin`) and by entity type (`entity_bin`: "
      "entity-driven = the query's specific named entities occur in the gold evidence; formulation-driven = "
      "no specific entity, or the evidence does not repeat it). The two groupings overlap; each sums to all.", "",
      "## Results", ""] + md_tables(summary)
if len(paired):
    md += [f"## Paired differences (run − `{names[0]}`)", "",
           "\\* = 95% CI excludes 0.", ""] + md_tables(paired, signed=True)
md += [f"Command: `{' '.join(sys.argv)}`", ""]
out.with_suffix(".md").write_text("\n".join(md))

view = summary.assign(o=summary["bin"].map(BIN_ORDER)).sort_values(["run", "level", "set", "split", "o"])
view = view.pivot_table(index=["run", "level", "set", "split", "bin", "n"], columns="metric", values="mean",
                        sort=False)[METRICS]
with pd.option_context("display.width", 200, "display.max_rows", 200, "display.max_columns", 20):
    print(view.round(3))
    if len(paired):
        print("\nPaired differences (other - baseline), all bins:")
        p = paired[paired["bin"] == "all"]
        print(p.assign(ci=p["ci_lo"].round(3).astype(str) + " .. " + p["ci_hi"].round(3).astype(str))
              [["run", "level", "set", "split", "metric", "n", "mean", "ci"]].round(3).to_string(index=False))
print(f"\nSaved {out} (+ .md, .per_query.csv, .results.json{', .paired.csv' if len(paired) else ''})")
