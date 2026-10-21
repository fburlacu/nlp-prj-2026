"""Grid search over BM25 k1 and b on DEV queries only.

Usage:
  python tune.py [--passages ... --queries ... --runs_dir runs_tune --output results/tune_dev.csv]
  v2:  python tune.py --passages ../data/passages_v2.parquet --queries ../data/queries_v2.csv --set main \
                      --select lenient:mrr@10 --runs_dir v2_results/runs_tune --output v2_results/results/tune_dev.csv
The grid and baseline are set in the constants below; the selection metric with --select.
Steps
  1. retrieve.py --split dev for every (k1, b)  -> <runs_dir>/bm25_dev_k1-<k1>_b-<b>.parquet
  2. eval_retrieval.py on all runs, baseline first -> <output> (+ .md, .paired.csv, ...)
  3. ranking of the configurations by --select (main set, all bins), with the paired
     difference to the baseline   -> <output>.ranking.md / .ranking.csv
A configuration only replaces the baseline if its paired 95% CI on the selection metric excludes 0:
with 45 dev queries, smaller differences are noise.
"""
import sys
import argparse
import itertools
import subprocess
from pathlib import Path

import pandas as pd

K1_GRID = [0.6, 0.9, 1.2, 1.5, 2.0]
B_GRID = [0.3, 0.5, 0.75, 0.9]
BASELINE = (1.2, 0.75)     # standard defaults; replaced only by a significantly better config
SKIP_EXISTING = False      # True: reuse run files already in runs_dir (e.g. after extending the grid)

HERE = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("--passages", default=str(HERE.parent / "data" / "passages.parquet"))
ap.add_argument("--queries", default=str(HERE.parent / "data" / "queries.csv"))
ap.add_argument("--runs_dir", default=str(HERE / "runs_tune"), help="where the dev run files are written")
ap.add_argument("--output", default=str(HERE / "results" / "tune_dev.csv"), help="evaluation summary (.csv)")
ap.add_argument("--set", dest="qset", choices=["main", "article"], help="only queries from this set (v2: main)")
ap.add_argument("--select", default="case:mrr@10",
                help="level:metric that ranks the configurations (v1: case:mrr@10; v2 has no case level)")
a = ap.parse_args()

SELECT = a.select
sel_level, sel_metric = SELECT.split(":")
# columns shown in the ranking besides the selection metric
SHOW = [(sel_level, "mrr@10"), (sel_level, "hit@10"), ("strict", "mrr@10"), ("strict", "hit@10"), ("strict", "hit@100")]

name = lambda k1, b: f"bm25_dev_k1-{k1:g}_b-{b:g}"
base = BASELINE
configs = [base] + [c for c in itertools.product(K1_GRID, B_GRID) if c != base]
data = ["--passages", a.passages, "--queries", a.queries, "--split", "dev"] + (["--set", a.qset] if a.qset else [])

# 1. one dev run per configuration
paths = []
for i, (k1, b) in enumerate(configs, 1):
    path = Path(a.runs_dir) / f"{name(k1, b)}.parquet"
    paths.append(path)
    if SKIP_EXISTING and path.exists():
        print(f"[{i}/{len(configs)}] k1={k1:g} b={b:g}: exists, skipped")
        continue
    print(f"[{i}/{len(configs)}] k1={k1:g} b={b:g}", flush=True)
    subprocess.run([sys.executable, str(HERE / "retrieve.py"), *data, "--k1", str(k1), "--b", str(b),
                    "--output", str(path)], check=True, stdout=subprocess.DEVNULL)

# 2. evaluate all runs together, baseline first (paired differences are relative to it)
print("Evaluating ...", flush=True)
subprocess.run([sys.executable, str(HERE / "eval_retrieval.py"), "--runs", *map(str, paths), *data,
                "--output", a.output], check=True, stdout=subprocess.DEVNULL)

# 3. rank configurations on the main set (all bins)
out = Path(a.output)
main = lambda df: df[(df["set"] == "main") & (df["bin"] == "all")].set_index(["run", "level", "metric"])
summary = main(pd.read_csv(out))
paired = main(pd.read_csv(out.with_suffix(".paired.csv")))
cols = list(dict.fromkeys([(sel_level, sel_metric)] + SHOW))

rows = []
for k1, b in configs:
    run = name(k1, b)
    row = {"k1": k1, "b": b, "baseline": (k1, b) == base}
    for lvl, m in cols:
        row[f"{lvl} {m}"] = summary.loc[(run, lvl, m), "mean"]
    if (k1, b) != base:
        d = paired.loc[(f"{run} - {name(*base)}", sel_level, sel_metric)]
        row.update(diff=d["mean"], diff_lo=d["ci_lo"], diff_hi=d["ci_hi"], significant=d["ci_lo"] > 0 or d["ci_hi"] < 0)
    rows.append(row)
rank = pd.DataFrame(rows).sort_values(f"{sel_level} {sel_metric}", ascending=False, kind="stable")
rank.round(4).to_csv(out.with_suffix(".ranking.csv"), index=False)

best = rank.iloc[0]
n = int(summary.loc[(name(*base), sel_level, sel_metric), "n"])
if best["baseline"]:
    verdict = f"The baseline (k1={base[0]:g}, b={base[1]:g}) scores best: keep it."
elif best["significant"] and best["diff"] > 0:
    verdict = (f"**Switch to k1={best.k1:g}, b={best.b:g}**: {SELECT} +{best['diff']:.3f} "
               f"[{best.diff_lo:+.3f}, {best.diff_hi:+.3f}] over the baseline, CI excludes 0.")
else:
    verdict = (f"Best is k1={best.k1:g}, b={best.b:g} ({SELECT} {best['diff']:+.3f} "
               f"[{best.diff_lo:+.3f}, {best.diff_hi:+.3f}]), but the CI includes 0: "
               f"**keep the baseline k1={base[0]:g}, b={base[1]:g}**.")

head = ["k1", "b"] + [f"{l} {m}" for l, m in cols] + [f"Δ {SELECT} vs baseline [95% CI]"]
md = [f"# BM25 tuning (dev)", "",
      f"{len(configs)} configurations | ranked by **{SELECT}** on main/dev disinformation queries "
      f"(n = {n}, all bins) | Δ = paired difference to the baseline, * = CI excludes 0", "",
      verdict, "",
      "| " + " | ".join(head) + " |", "|" + "---:|" * len(head)]
for _, r in rank.iterrows():
    vals = [f"{r['k1']:g}", f"{r['b']:g}"] + [f"{r[f'{l} {m}']:.3f}" for l, m in cols]
    if r["baseline"]:
        vals.append("baseline")
    else:
        vals.append(f"{r['diff']:+.3f}{'*' if r['significant'] else ''} [{r['diff_lo']:+.3f}, {r['diff_hi']:+.3f}]")
    md.append("| " + " | ".join(vals) + " |")
md += ["", f"Full per-bin results: `{out.with_suffix('.md').name}`. Command: `{' '.join(sys.argv)}`", ""]
out.with_suffix(".ranking.md").write_text("\n".join(md))

with pd.option_context("display.width", 200, "display.max_columns", 20):
    print(rank.drop(columns=["baseline"]).round(3).to_string(index=False))
print(f"\n{verdict.replace('**', '')}\nSaved {out.with_suffix('.ranking.md')}")
