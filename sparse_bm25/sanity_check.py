"""Pipeline sanity check: own-case retrieval with NO self-exclusion (BM25 only).

Usage (from sparse_bm25/):
  python sanity_check.py
Checks
  IDs            gold links vs debunk pool, passages and query texts
  glued words    sentence-boundary glue left after repair_boundaries, in-sentence glue
  tokenisation   queries and passages use the same data.preprocessing.tokenize
  retrieval      R@1/5/10/100 and MRR@100 of the own case on five indexes (A-E), strict and lenient;
                 E is the v2 main-set index (data/build_index_v2.py), so build it first
  misses         what outranks the own claim passage in index A
  lengths        disproofs above ~180 wordpieces (138 words), for a later dense encoder
Writes results/sanity_check.per_query.csv (first rank of the own case per query and index).
"""
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))  # project root, for data.preprocessing
from data.preprocessing import repair_boundaries, tokenize, jaccard
from bm25 import BM25

sp = lambda s: [x for x in str(s).split("|") if x and x != "nan"]
pool = pd.read_csv(ROOT / "data/debunk_pool.csv", dtype=str, keep_default_na=False)
q = pd.read_csv(ROOT / "data/queries.csv", dtype=str, keep_default_na=False)
q = q[(q["set"] == "main") & (q["label"] == "disinformation")].reset_index(drop=True)
P = pd.read_parquet(ROOT / "data/passages.parquet").fillna("")
V2 = pd.read_parquet(ROOT / "data/passages_v2_main.parquet")
held = set(pd.read_csv(ROOT / "data/held_out_links.csv", dtype=str)["Links"].str.strip())
gold = q["gold_links"].map(lambda s: sp(s)[0])
lex = q["gold_links_lenient"].map(sp)

# ---------------- ID checks ----------------
print("== ID checks ==")
print("pool Links unique:", pool["Links"].is_unique,
      "| whitespace in Links:", (pool["Links"] != pool["Links"].str.strip()).sum())
print("queries: gold == case_links:", (gold == q["case_links"]).all(),
      "| exactly one gold each:", (q["gold_links"].map(lambda s: len(sp(s))) == 1).all())
print("gold in pool:", gold.isin(set(pool["Links"])).mean(), "| gold in held-out:", gold.isin(held).sum())
dlinks = set(P.loc[P["doc_type"] == "eeas_disproof", "case_links"])
clinks = set(P.loc[P["doc_type"] == "eeas_claim", "case_links"])
print("gold with disproof passage:", gold.isin(dlinks).mean(), "| with claim passage:", gold.isin(clinks).mean())
title = pool.set_index("Links")["Title"]
print("query text == pool Title:", (q["text"].values == title.reindex(gold).values).mean())
print("lenient contains strict:", all(g in l for g, l in zip(gold, lex)))

# ---------------- glued words ----------------
print("\n== Glued words ==")
info = pool["Information"]
rep = info.map(repair_boundaries)
pat_sent = re.compile(r"[a-z0-9)][.!?;:][A-Z]")    # boundary glue: 'Crimea.No'
pat_camel = re.compile(r"\b[a-z]{2,}[A-Z][a-z]+")  # glued link text: 'theKremlin'
for name, s in [("raw Information", info), ("after repair_boundaries", rep),
                ("passages.parquet disproofs", P.loc[P["doc_type"] == "eeas_disproof", "text"])]:
    print(f"{name:28s} sentence-glue: {s.str.count(pat_sent).sum():6d} in {(s.str.count(pat_sent) > 0).sum():5d} texts"
          f" | camel-glue: {s.str.count(pat_camel).sum():6d} in {(s.str.count(pat_camel) > 0).sum():5d} texts")
pdis = P.loc[P["doc_type"] == "eeas_disproof", "text"]
print("passages.parquet idempotent under repair:", (pdis.map(repair_boundaries) == pdis).mean())
ex = rep[rep.str.contains(pat_camel)].str.extract(r"(\S*\b[a-z]{2,}[A-Z][a-z]+\S*)")[0].head(12).tolist()
print("camel-glue examples:", ex)
# in-sentence glue ('issuedstatements'): long alphabetic tokens that occur in only one disproof
cnt = Counter(t for s in rep for t in set(re.findall(r"[a-z]{16,}", s.lower())))
print("lowercase tokens >= 16 chars occurring once:", sum(v == 1 for v in cnt.values()),
      "e.g.", [t for t, v in cnt.items() if v == 1][:10])
qt = q["text"].map(lambda s: set(tokenize(s)))
dr = pool.set_index("Links")["Information"].reindex(gold)
for name, f in [("raw", lambda s: s), ("repaired", repair_boundaries)]:
    ov = [len(a & set(tokenize(f(b)))) / max(len(a), 1) for a, b in zip(qt, dr)]
    print(f"mean query-stem overlap with own disproof ({name}): {np.mean(ov):.4f}")

# ---------------- tokenisation ----------------
print("\n== BM25 preprocessing ==")
src = (HERE / "bm25.py").read_text()
print("BM25 index and queries both use data.preprocessing.tokenize:",
      "tokenize(query)" in src and "tokenize(t) for t in texts" in src)
print("example:", q["text"][0], "->", tokenize(q["text"][0]))


# ---------------- retrieval ----------------
def evaluate(bm, case_of, gold_sets):
    """First rank (top 100) of a passage whose case is in the gold set; inf if missing."""
    case_of = np.asarray(case_of)
    first = []
    for t, g in zip(q["text"], gold_sets):
        s = bm.scores(t)
        top = np.argsort(-s, kind="stable")[:100]
        hit = [r for r, i in enumerate(top, 1) if case_of[i] in g]
        first.append(hit[0] if hit else np.inf)
    return np.array(first, float)


pool_r = pool.assign(Disinformation=pool["Disinformation"].map(repair_boundaries), Information=rep)
runs = {
    "A": ("current passages.parquet (title + summary claims, disproof chunks, articles)",
          P["text"].tolist(), P["case_links"].tolist()),
    "B": ("full pool, one passage per case = summary + disproof",
          (pool_r["Disinformation"] + " " + pool_r["Information"]).tolist(), pool_r["Links"].tolist()),
    "C": ("full pool, summary only", pool_r["Disinformation"].tolist(), pool_r["Links"].tolist()),
    "D": ("full pool, disproof only (unchunked)", pool_r["Information"].tolist(), pool_r["Links"].tolist()),
    "E": ("passages_v2_main.parquet (disproofs without held-out cases and placeholders)",
          V2["text"].tolist(), V2["case_id"].tolist()),
}
rows, firsts, indexes = [], {}, {}
for key, (desc, texts, case) in runs.items():
    bm = indexes[key] = BM25(texts)
    for lvl, g in [("strict", [{x} for x in gold]), ("lenient", [set(l) for l in lex])]:
        f = firsts[(key, lvl)] = evaluate(bm, case, g)
        rows.append({"index": f"{key} {desc}", "gold": lvl, "n_passages": len(texts),
                     "R@1": (f <= 1).mean(), "R@5": (f <= 5).mean(), "R@10": (f <= 10).mean(),
                     "R@100": (f <= 100).mean(), "MRR@100": np.where(f <= 100, 1 / f, 0).mean()})
print(f"\n== Retrieval ({len(q)} main disinformation queries, dev + test) ==")
with pd.option_context("display.width", 250, "display.max_colwidth", 90):
    print(pd.DataFrame(rows).round(3).to_string(index=False))

f = firsts[("B", "strict")]
miss = q.assign(first=f)[f > 1]
print(f"\nB strict misses at rank 1: {len(miss)} | by overlap bin:", miss.groupby("overlap_bin").size().to_dict())

# ---------------- what outranks the own claim passage in A ----------------
print("\n== Index A: rank-1 passage when the own case is missed ==")
pool_i = pool.set_index("Links")
own_row = {p: i for i, p in enumerate(P["passage_id"])}
mA = q[firsts[("A", "strict")] > 1]
kinds = []
for r in mA.itertuples():
    s = indexes["A"].scores(r.text)
    i = int(np.argmax(s))
    top, own = P.iloc[i], own_row[r.case_links + "#claim"]
    jt = jaccard(set(tokenize(r.text)), set(tokenize(pool_i["Title"].get(top["case_links"], ""))))
    kinds.append((top["doc_type"], jt, s[i] - s[own], len(P["text"][own].split()), len(top["text"].split())))
k = pd.DataFrame(kinds, columns=["top_type", "title_jacc", "score_gap", "own_claim_words", "top_words"])
print(f"misses: {len(mA)} | rank-1 type:", k["top_type"].value_counts().to_dict())
print("rank-1 case has the same title (stem Jaccard = 1):", (k["title_jacc"] == 1).sum())
print("median words: own claim", k["own_claim_words"].median(), "vs rank-1 passage", k["top_words"].median())
for r in mA.head(5).itertuples():
    i = int(np.argmax(indexes["A"].scores(r.text)))
    print(f" Q: {r.text}\n   TOP [{P['doc_type'][i]}]: {P['text'][i][:150]}")

# ---------------- lengths for a later dense encoder ----------------
print("\n== Lengths ==")
w = pool["Information"].str.split().str.len()
w = w[w >= 10]
c = P.loc[P["doc_type"] == "eeas_disproof", "n_words"]
print(f"unchunked disproofs (>= 10 words): {len(w)} | > 138 words (~180 wordpieces): {(w > 138).mean():.3f} "
      f"| median {w.median():.0f} words")
print(f"current disproof chunks > 138 words: {(c > 138).mean():.3f}")

out = HERE / "results" / "sanity_check.per_query.csv"
out.parent.mkdir(parents=True, exist_ok=True)
q.assign(**{f"first_{key}_strict": firsts[(key, "strict")] for key in runs})[
    ["query_id", "text", "split", "overlap_bin", "entity_bin", *[f"first_{key}_strict" for key in runs]]
].to_csv(out, index=False)
print(f"\nSaved {out}")
