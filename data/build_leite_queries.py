"""Leite queries (fact + disinformation article titles), merged with the EEAS queries.
Usage:
  python build_leite_queries.py --leite leite_en_clean.csv --eeas_queries queries_eeas.csv \
                                --claim_like_file claim_like.csv [--out_dir .]
Outputs (in --out_dir):
  fact_candidates.csv             trustworthy candidates with cleaned titles and rule verdict
  excluded_factcheck_titles.csv   fact-check / claim-reporting titles removed from fact candidates
  queries_leite.csv               Leite queries
  queries.csv                     EEAS + Leite queries combined

"""
import os
import re
import argparse
from collections import defaultdict
import numpy as np
import pandas as pd
from datasketch import MinHash, MinHashLSH

from preprocessing import words, jaccard, clean_title, rule_claim_like

ap = argparse.ArgumentParser()
ap.add_argument("--leite", default="leite_en_clean.csv")
ap.add_argument("--eeas_queries", default="queries_eeas.csv")
ap.add_argument("--claim_like_file")
ap.add_argument("--no_rule", action="store_true",
                help="with --claim_like_file: do NOT additionally require the rule-based filter")
ap.add_argument("--max_per_debunk", type=int, default=1)
ap.add_argument("--main_fact_test", type=int, default=300)
ap.add_argument("--main_fact_dev", type=int, default=45)
ap.add_argument("--dev_frac", type=float, default=0.15, help="share of groups assigned to dev")
ap.add_argument("--title_dup_threshold", type=float, default=0.9)
ap.add_argument("--out_dir", default=".")
ap.add_argument("--seed", type=int, default=13)
a = ap.parse_args()
os.makedirs(a.out_dir, exist_ok=True)
out = lambda name: os.path.join(a.out_dir, name)
rng = np.random.default_rng(a.seed)
 
# documents (all debunk links kept) 
leite = pd.read_csv(a.leite, dtype={"doc_key": str, "debunk_id": str})
leite["year"] = pd.to_datetime(leite["debunk_date"], format="%d-%m-%Y", errors="coerce").dt.year
doc_debunks = leite.groupby("doc_key")["debunk_id"].agg(lambda s: sorted(set(s)))
docs = leite.sort_values("year").drop_duplicates("doc_key").copy()   # earliest dated row
docs["debunks"] = docs["doc_key"].map(doc_debunks)
docs["title_clean"] = docs["article_title"].map(clean_title)
docs = docs[docs["title_clean"].str.len() > 0].reset_index(drop=True)
print("Documents with a usable title:", docs.groupby("class").size().to_dict())
print("Documents cited in more than one debunk:", (docs["debunks"].str.len() > 1).sum())
print("Documents without a parseable year:", docs["year"].isna().sum())
 
# near-identical titles 
title_sets = {k: set(words(t)) for k, t in zip(docs["doc_key"], docs["title_clean"])}
lsh, mh = MinHashLSH(threshold=a.title_dup_threshold, num_perm=128), {}
for k, s in title_sets.items():
    m = MinHash(num_perm=128, seed=a.seed)
    for w in s:
        m.update(w.encode())
    mh[k] = m
    lsh.insert(k, m)
near = {k: [c for c in lsh.query(m) if c != k and jaccard(title_sets[k], title_sets[c]) >= a.title_dup_threshold]
        for k, m in mh.items()}
docs["exclude_doc_key"] = docs["doc_key"].map(lambda k: "|".join([k] + near[k]))
print("Documents with near-identical titles:", sum(1 for v in near.values() if v))
 
# leakage groups: shared debunk OR near-identical title 
parent = {k: k for k in docs["doc_key"]}
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x
by_debunk = defaultdict(list)
for k, debs in zip(docs["doc_key"], docs["debunks"]):
    for d in debs:
        by_debunk[d].append(k)
for members in by_debunk.values():
    for m in members[1:]:
        parent[find(m)] = find(members[0])
for k, ns in near.items():
    for c in ns:
        parent[find(k)] = find(c)
docs["group"] = docs["doc_key"].map(find)
gs = docs["group"].value_counts()
print(f"Leakage groups: {len(gs)} (largest {gs.max()} documents, {(gs > 1).sum()} with > 1)")
 
# one split per group
groups = docs["group"].unique()
dev_groups = set(rng.choice(groups, size=int(round(len(groups) * a.dev_frac)), replace=False))
docs["split"] = np.where(docs["group"].isin(dev_groups), "dev", "test")
 
# fact candidates 
fact = docs[docs["class"] == "trustworthy"].copy()
fact["claim_like_rule"] = fact["title_clean"].map(rule_claim_like)
 
# Fact-check / debunk articles often carry the FALSE claim in their title ("Fact check: ...").
# Checked on the RAW title, because clean_title() strips short prefixes such as "Fact check:".
FACTCHECK = re.compile(r"(?:fact[\s-]?check|\bfakes?\b|\bfalse\b|\bmyths?\b|debunk|hoax|misleading|"
                       r"disinformation|propaganda|\bclaims?\b|\bno,|not true|stopfake|conspiracy|fabricat)", re.I)
fc = fact["article_title"].fillna("").str.contains(FACTCHECK)
fact.loc[fc, ["doc_key", "article_title", "title_clean"]].to_csv(out("excluded_factcheck_titles.csv"), index=False)
print(f"Fact candidates excluded as fact-check/claim-reporting titles: {fc.sum()}")
fact = fact[~fc]
 
fact[["doc_key", "debunk_id", "year", "article_title", "title_clean", "claim_like_rule"]] \
    .to_csv(out("fact_candidates.csv"), index=False)
if a.claim_like_file:
    cl = pd.read_csv(a.claim_like_file, dtype={"doc_key": str})[["doc_key", "claim_like"]]
    fact = fact.merge(cl, on="doc_key", how="left")
    fact["claim_like"] = fact["claim_like"].fillna(False).astype(bool)
    if not a.no_rule:
        fact["claim_like"] &= fact["claim_like_rule"]
    print(f"Claim filter: LLM file {a.claim_like_file}{'' if a.no_rule else ' AND rule-based filter'}")
else:
    fact["claim_like"] = fact["claim_like_rule"]
    print("Claim filter: rule-based only (pass --claim_like_file for the LLM filter)")
fact = fact[fact["claim_like"]]
 
# cap per debunk over ALL debunks of a document (greedy over a shuffled order)
fact = fact.sample(frac=1, random_state=a.seed)
count, keep = defaultdict(int), []
for idx, debs in zip(fact.index, fact["debunks"]):
    if all(count[d] < a.max_per_debunk for d in debs):
        keep.append(idx)
        for d in debs:
            count[d] += 1
fact = fact.loc[keep]
print(f"Fact candidates after claim filter and <= {a.max_per_debunk} per debunk: {len(fact)} "
      f"(dev {(fact.split == 'dev').sum()}, test {(fact.split == 'test').sum()})")
 
def sample_like(pool, n, year_dist, what):
    """Sample n rows matching a target year distribution (largest-remainder allocation),
    capped by availability, topped up from any year (incl. undated), then shuffled."""
    if n <= 0:
        return pool.iloc[0:0]
    raw = year_dist * n
    want = np.floor(raw).astype(int)
    want[(raw - want).sort_values(ascending=False).index[: n - want.sum()]] += 1
    parts = [pool[pool["year"] == y].sample(min(c, int((pool["year"] == y).sum())), random_state=a.seed)
             for y, c in want.items() if c > 0]
    got = pd.concat(parts) if parts else pool.iloc[0:0]
    if len(got) < n:
        extra = pool.drop(got.index)
        got = pd.concat([got, extra.sample(min(n - len(got), len(extra)), random_state=a.seed)])
    if len(got) < n:
        print(f"WARNING: {what}: only {len(got)} available (wanted {n})")
    return got.sample(frac=1, random_state=a.seed)
 
# disinformation article queries 
dis = docs[docs["class"] == "disinformation"].copy()
print(f"Disinformation article queries: {len(dis)} (dev {(dis.split == 'dev').sum()}, "
      f"test {(dis.split == 'test').sum()}; {(~dis['title_clean'].map(rule_claim_like)).sum()} "
      f"would fail the rule-based claim filter, kept)")
 
# proxy gold: trustworthy documents cited in the same debunk(s), minus the query's own exclusions.
# Uses ALL cleaned trustworthy documents (they are all in the index), not only titled ones.
trust_by_debunk = (leite[leite["class"] == "trustworthy"].groupby("debunk_id")["doc_key"]
                   .agg(lambda s: set(s)))
def proxy_gold(row):
    g = set().union(*(trust_by_debunk.get(d, set()) for d in row["debunks"]))
    return "|".join(sorted(g - set(row["exclude_doc_key"].split("|"))))
dis["gold_doc_keys"] = dis.apply(proxy_gold, axis=1)
n_g = dis["gold_doc_keys"].str.len().gt(0)
sizes = dis.loc[n_g, "gold_doc_keys"].str.split("|").str.len()
print(f"Proxy gold: {n_g.sum()} of {len(dis)} disinformation article queries have >= 1 same-debunk "
      f"trustworthy document (dev {(n_g & (dis.split == 'dev')).sum()}, test {(n_g & (dis.split == 'test')).sum()}); "
      f"gold documents per query: mean {sizes.mean():.1f}, max {sizes.max() if len(sizes) else 0}")
 
# article set: fact queries per split, year-matched to the disinformation articles of that split
art_fact = pd.concat([
    sample_like(fact[fact.split == sp], int((dis.split == sp).sum()),
                dis.loc[dis.split == sp, "year"].value_counts(normalize=True), f"article fact {sp}")
    for sp in ["dev", "test"]])
 
# main set: fact queries from groups NOT used in the article set (either class)
used = set(dis["group"]) | set(art_fact["group"])
rest = fact[~fact["group"].isin(used)]
eq = pd.read_csv(a.eeas_queries)
eeas_years = pd.to_datetime(eq.loc[eq["label"] == "disinformation", "date"], errors="coerce").dt.year
ydist = eeas_years.value_counts(normalize=True)
main_fact = pd.concat([
    sample_like(rest[rest.split == "dev"], a.main_fact_dev, ydist, "main fact dev"),
    sample_like(rest[rest.split == "test"], a.main_fact_test, ydist, "main fact test")])
 
# leakage checks 
sets = {"art_dis": dis, "art_fact": art_fact, "main_fact": main_fact}
for name, d in sets.items():
    assert d.groupby("group")["split"].nunique().max() <= 1, f"{name}: group spans splits"
assert not (set(main_fact["group"]) & used), "main fact shares a group with the article set"
print("Leakage checks passed: no group spans dev/test, no group shared between main and article set")
 
def rows(df, label, set_name, prefix):
    return pd.DataFrame({
        "query_id": [f"{prefix}_{i:04d}" for i in range(len(df))],
        "text": df["title_clean"].values, "label": label, "set": set_name,
        "split": df["split"].values, "source": "leite_title",
        "gold_links": "", "gold_links_lenient": "", "exclude_passage_ids": "",
        "exclude_doc_key": df["exclude_doc_key"].values, "case_links": "",
        "overlap": np.nan, "overlap_bin": "", "disproof_len": np.nan,
        "date": pd.to_datetime(df["debunk_date"], format="%d-%m-%Y", errors="coerce").dt.date.values,
        "doc_key": df["doc_key"].values, "debunk_id": df["debunks"].map("|".join).values,
        "leak_group": df["group"].values,
        "gold_doc_keys": df["gold_doc_keys"].values if "gold_doc_keys" in df else "",
    })
 
ql = pd.concat([rows(main_fact, "fact", "main", "leite_fact_main"),
                rows(art_fact, "fact", "article", "leite_fact_art"),
                rows(dis, "disinformation", "article", "leite_dis_art")])
ql.to_csv(out("queries_leite.csv"), index=False)
allq = pd.concat([eq, ql], ignore_index=True)
allq.to_csv(out("queries.csv"), index=False)
print("\nAll queries (set / label / split):")
print(allq.groupby(["set", "label", "split"]).size().unstack(fill_value=0))
 
# style-shortcut check
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    print("\nStyle-shortcut check (TF-IDF + logistic regression on query text only, 5-fold macro-F1):")
    for s, pair in [("main", ["disinformation", "fact"]), ("main", ["disinformation", "inconclusive"]),
                    ("main", ["disinformation", "fact", "inconclusive"]), ("article", ["disinformation", "fact"])]:
        d = allq[(allq["set"] == s) & allq["label"].isin(pair)]
        X = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True).fit_transform(d["text"])
        f1 = cross_val_score(LogisticRegression(max_iter=1000), X, d["label"], cv=5, scoring="f1_macro")
        print(f"  {s:<8} {'/'.join(pair):<36} {f1.mean():.2f} (chance ~{1 / len(pair):.2f})")
except ImportError:
    print("\n(style check skipped: pip install scikit-learn)")
print(f"\nWrote outputs to {os.path.abspath(a.out_dir)}")