"""Detection evaluation (RQ2): scores prediction files from detect.py, so all retrievers (and the
no-retrieval baseline) are compared on the same queries with the same metrics.

Usage:
  python eval_detection.py --preds preds/noretrieval_dev.csv preds/bm25_dev_k5.csv [...] \
                           --output results/detection_dev.csv \
                           [--retrieval ../sparse_bm25/results/dev/retrieval_dev.per_query.csv]
The first prediction file is the baseline for paired differences.
Per set (label space):  main     disinformation vs inconclusive (abstention when the case is held out)
                        article  disinformation vs fact (real headlines)
Predictions are 3-way; a prediction outside the set's label space (e.g. 'fact' on the main set) is wrong
and reported as the off-label rate.
Metrics: accuracy, macro-F1 (over the set's two classes), precision / recall / F1 per class, 95%
bootstrap CIs. Disinformation recall is also broken down by overlap bin, entity bin and, with
--retrieval, by whether gold evidence was among the k passages the LLM saw (case level for the main
set, proxy level for the article set): this shows whether retrieval gains translate into detection.
Cost per file: prompt tokens, LLM seconds per query, GPU memory (detect.py config) and retrieval
latency (run config).
Writes <output> (summary, long format), <output>.md (report), <output>.per_query.csv,
<output>.paired.csv (if several files), <output>.results.json.
"""
import sys
import json
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

N_BOOT, SEED = 1000, 0
LABELS = {"main": ["disinformation", "inconclusive"], "article": ["disinformation", "fact"]}
BIN_COLS = ["overlap_bin", "entity_bin"]
BIN_LABEL = {"low": "overlap: low", "mid": "overlap: mid", "high": "overlap: high", "entity": "entity-driven",
             "formulation": "formulation-driven", "hit": "gold evidence in top-k", "miss": "gold evidence not in top-k"}
GROUP_ORDER = list(BIN_LABEL)
HIT_LEVEL = {"main": "case", "article": "proxy"}

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--preds", nargs="+", required=True, help="prediction files; the first is the baseline")
ap.add_argument("--queries", default=str(HERE.parent.parent / "data" / "queries.csv"))
ap.add_argument("--retrieval", help="optional per_query.csv from eval_retrieval.py, for the hit/miss breakdown")
ap.add_argument("--output", required=True, help="summary file (.csv)")
a = ap.parse_args()

rng = np.random.default_rng(SEED)
queries = pd.read_csv(a.queries, dtype=str, keep_default_na=False)
retr = pd.read_csv(a.retrieval, dtype={"query_id": str}) if a.retrieval else None


def metrics(y, p, classes):
    m = {"accuracy": float(np.mean(y == p))}
    f1s = []
    for c in classes:
        tp = np.sum((p == c) & (y == c))
        prec = tp / np.sum(p == c) if np.any(p == c) else 0.0
        rec = tp / np.sum(y == c) if np.any(y == c) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        m.update({f"precision_{c}": prec, f"recall_{c}": rec, f"f1_{c}": f1})
        f1s.append(f1)
    m["macro_f1"] = float(np.mean(f1s))
    m["off_label_rate"] = float(np.mean(~np.isin(p, classes)))
    return m


def boot(y, p, classes, y2=None, p2=None):
    """Point estimates and percentile CIs; with y2/p2 the paired difference (2 minus 1)."""
    point = metrics(y, p, classes)
    if p2 is not None:
        point = {k: v - point[k] for k, v in metrics(y2, p2, classes).items()}
    draws = []
    for _ in range(N_BOOT):
        i = rng.integers(0, len(y), len(y))
        d = metrics(y[i], p[i], classes)
        if p2 is not None:
            d = {k: v - d[k] for k, v in metrics(y2[i], p2[i], classes).items()}
        draws.append(d)
    return {k: (v, *np.percentile([d[k] for d in draws], [2.5, 97.5])) for k, v in point.items()}


def load(path):
    path = Path(path)
    p = pd.read_csv(path, dtype={"query_id": str, "passage_ids": str}, keep_default_na=False)
    cfg_path = path.with_suffix(".config.json")
    cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    p = p.merge(queries[["query_id", *BIN_COLS]], on="query_id", how="left")
    p["hit"] = ""
    if retr is not None and cfg.get("mode") == "rag":
        k = cfg["params"]["k"]
        run_name = Path(cfg["inputs"]["run"]).stem
        r = retr[retr["run"] == run_name]
        if r.empty:
            print(f"WARNING {path.name}: run {run_name} not in {a.retrieval}; no hit/miss breakdown")
        for s, lvl in HIT_LEVEL.items():
            fr = r[r["level"] == lvl].set_index("query_id")["first_rank"]
            sel = (p["set"] == s) & p["query_id"].isin(fr.index)
            p.loc[sel, "hit"] = np.where(p.loc[sel, "query_id"].map(fr) <= k, "hit", "miss")
    return path.stem, p, cfg


files = [load(f) for f in a.preds]
names = [n for n, _, _ in files]
if len(set(names)) < len(names):
    sys.exit("prediction files must have distinct names")
common = set.intersection(*(set(p["query_id"]) for _, p, _ in files))
if any(len(p) != len(common) for _, p, _ in files):
    print(f"WARNING: files cover different queries; only the {len(common)} shared queries are evaluated")
files = [(n, p[p["query_id"].isin(common)].sort_values("query_id").reset_index(drop=True), c) for n, p, c in files]

# ---------------- summary ----------------
rows, conf = [], {}
for name, p, _ in files:
    for (s, spl), g in p.groupby(["set", "split"]):
        y, pr = g["label"].to_numpy(), g["pred"].to_numpy()
        for metric, (v, lo, hi) in boot(y, pr, LABELS[s]).items():
            rows.append((name, s, spl, "all", metric, len(g), v, lo, hi))
        conf[(name, s, spl)] = pd.crosstab(g["label"], g["pred"]).reindex(
            columns=[c for c in ["disinformation", "fact", "inconclusive"]], fill_value=0)
        dis = g[g["label"] == "disinformation"]           # breakdowns: recall of disinformation
        for col in BIN_COLS + ["hit"]:
            for b, gb in dis.groupby(col):
                if b:
                    x = (gb["pred"] == "disinformation").to_numpy(dtype=float)
                    lo, hi = np.percentile(x[rng.integers(0, len(x), (N_BOOT, len(x)))].mean(axis=1), [2.5, 97.5])
                    rows.append((name, s, spl, b, "recall_disinformation", len(x), x.mean(), lo, hi))
summary = pd.DataFrame(rows, columns=["preds", "set", "split", "group", "metric", "n", "mean", "ci_lo", "ci_hi"])

paired = []
base_name, base, _ = files[0]
for name, p, _ in files[1:]:
    for (s, spl), g in base.groupby(["set", "split"]):
        g2 = p.loc[g.index]
        for metric, (v, lo, hi) in boot(g["label"].to_numpy(), g["pred"].to_numpy(), LABELS[s],
                                        g2["label"].to_numpy(), g2["pred"].to_numpy()).items():
            paired.append((f"{name} - {base_name}", s, spl, "all", metric, len(g), v, lo, hi))
paired = pd.DataFrame(paired, columns=summary.columns)


def cost(cfg):
    t = cfg.get("timing_this_session", {})
    c = {"mode": cfg.get("mode", "?"), "k": cfg.get("params", {}).get("k"),
         "prompt_tokens_mean": cfg.get("prompt_tokens_mean_all"), "llm_s_per_query": t.get("llm_s_per_query"),
         "gpu_peak_mem_gb": t.get("gpu_peak_mem_gb"), "retrieval_ms_per_query": None}
    run = cfg.get("inputs", {}).get("run")
    if run and Path(run).with_suffix(".config.json").exists():
        c["retrieval_ms_per_query"] = json.loads(Path(run).with_suffix(".config.json").read_text())["timing"]["query_ms_p50"]
    return c


costs = {n: cost(c) for n, _, c in files}

# ---------------- outputs ----------------
out = Path(a.output)
out.parent.mkdir(parents=True, exist_ok=True)
summary.round(4).to_csv(out, index=False)
pd.concat([p.assign(preds=n) for n, p, _ in files]).to_csv(out.with_suffix(".per_query.csv"), index=False)
if len(paired):
    paired.round(4).to_csv(out.with_suffix(".paired.csv"), index=False)


def nest(df):
    res = {}
    for r in df.itertuples(index=False):
        res.setdefault(r.preds, {}).setdefault(f"{r.set}/{r.split}", {}).setdefault(r.group, {})[r.metric] = {
            "n": int(r.n), "mean": round(float(r.mean), 4), "ci95": [round(float(r.ci_lo), 4), round(float(r.ci_hi), 4)]}
    return res


out.with_suffix(".results.json").write_text(json.dumps({
    "config": {"command": " ".join(sys.argv), **vars(a), "labels": LABELS, "n_boot": N_BOOT, "seed": SEED},
    "summary": nest(summary), "paired_vs_first": nest(paired) if len(paired) else {},
    "confusion": {f"{n}|{s}/{spl}": c.to_dict() for (n, s, spl), c in conf.items()}, "cost": costs}, indent=2))

f2 = lambda v: f"{v:.2f}"
cell = lambda r, f=f2: f"{f(r['mean'])} [{f(r['ci_lo'])}, {f(r['ci_hi'])}]"
md = ["# Detection evaluation", "",
      f"Prediction files: {', '.join(f'`{n}`' for n in names)} | {len(common)} queries | "
      f"cells: mean [95% bootstrap CI, {N_BOOT} resamples]", "",
      "Main set: disinformation vs inconclusive (case held out, the model should answer *unknown*). "
      "Article set: disinformation vs fact. Predictions are 3-way; off-label = a class outside the set's label space.", ""]
for name, p, _ in files:
    md += [f"## {name}", ""]
    for (s, spl), g in summary[(summary["preds"] == name) & (summary["group"] == "all")].groupby(["set", "split"]):
        g = g.set_index("metric")
        c0, c1 = LABELS[s]
        md += [f"### {s}/{spl} (n = {int(g['n'].iloc[0])})", "",
               "| Accuracy | Macro-F1 | Off-label |", "|---:|---:|---:|",
               f"| {cell(g.loc['accuracy'])} | {cell(g.loc['macro_f1'])} | {cell(g.loc['off_label_rate'])} |", "",
               "| Class | Precision | Recall | F1 |", "|---|---:|---:|---:|"]
        md += [f"| {c} | {cell(g.loc[f'precision_{c}'])} | {cell(g.loc[f'recall_{c}'])} | {cell(g.loc[f'f1_{c}'])} |"
               for c in (c0, c1)]
        cm = conf[(name, s, spl)]
        md += ["", "Confusion (rows: gold, columns: predicted)", "",
               "| | " + " | ".join(cm.columns) + " |", "|---|" + "---:|" * len(cm.columns)]
        md += [f"| {lab} | " + " | ".join(str(int(v)) for v in row) + " |" for lab, row in cm.iterrows()]
        br = summary[(summary["preds"] == name) & (summary["set"] == s) & (summary["split"] == spl)
                     & (summary["group"] != "all")]
        if len(br):
            md += ["", "Disinformation recall by group", "", "| Group | n | Recall |", "|---|---:|---:|"]
            for _, r in br.sort_values("group", key=lambda x: x.map(GROUP_ORDER.index)).iterrows():
                md.append(f"| {BIN_LABEL[r['group']]} | {int(r['n'])} | {cell(r)} |")
        md.append("")
if len(paired):
    md += [f"## Paired differences (file − `{base_name}`)", "", "\\* = 95% CI excludes 0.", "",
           "| Comparison | Set | Accuracy | Macro-F1 | Recall disinformation |", "|---|---|---:|---:|---:|"]
    sg = lambda v: f"{v:+.2f}"
    for (cmp, s, spl), g in paired.groupby(["preds", "set", "split"], sort=False):
        g = g.set_index("metric")
        star = lambda r: "*" if r["ci_lo"] > 0 or r["ci_hi"] < 0 else ""
        md.append(f"| {cmp} | {s}/{spl} | " + " | ".join(
            f"{sg(g.loc[m, 'mean'])}{star(g.loc[m])} [{sg(g.loc[m, 'ci_lo'])}, {sg(g.loc[m, 'ci_hi'])}]"
            for m in ["accuracy", "macro_f1", "recall_disinformation"]) + " |")
    md.append("")
md += ["## Cost", "", "| File | Mode | k | Prompt tokens (mean) | LLM s / query | GPU peak GB | Retrieval ms / query (p50) |",
       "|---|---|---:|---:|---:|---:|---:|"]
md += [f"| {n} | {c['mode']} | {c['k']} | {c['prompt_tokens_mean']} | {c['llm_s_per_query']} | {c['gpu_peak_mem_gb']} | "
       f"{c['retrieval_ms_per_query'] if c['retrieval_ms_per_query'] is not None else '–'} |" for n, c in costs.items()]
md += ["", f"Command: `{' '.join(sys.argv)}`", ""]
out.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")

view = summary[(summary["group"] == "all") & summary["metric"].isin(["accuracy", "macro_f1", "recall_disinformation"])]
print(view.pivot_table(index=["preds", "set", "split"], columns="metric", values="mean", sort=False).round(3).to_string())
print(f"\nSaved {out} (+ .md, .per_query.csv, .results.json{', .paired.csv' if len(paired) else ''})")
