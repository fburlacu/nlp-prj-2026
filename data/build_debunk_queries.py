"""
Usage: python build_debunk_queries.py --eeas eeas.csv
Outputs:
  debunk_pool.csv        cleaned EEAS cases + overlap, bins, near-duplicate groups (reused for the index)
  queries_debunk.csv     EEAS-title queries (disinformation + inconclusive), with splits and exclusions
  held_out_links.csv   cases that must NOT be put in the index (inconclusive queries)
"""
import argparse
import numpy as np
import pandas as pd
from datasketch import MinHash, MinHashLSH

from preprocessing import repair_boundaries, tokenize, shingles, words, jaccard

ap = argparse.ArgumentParser()
ap.add_argument("--debunks", default="euvsdisinfo_debunks.csv")
#min length for a disproof to be included in the pool (short placeholders like "No evidence given." are skipped)
ap.add_argument("--min_disproof_words", type=int, default=30) 
ap.add_argument("--dis_test_per_bin", type=int, default=100)
ap.add_argument("--dis_dev_per_bin", type=int, default=15)
ap.add_argument("--inc_test", type=int, default=300)
ap.add_argument("--inc_dev", type=int, default=45)
ap.add_argument("--dup_threshold", type=float, default=0.8)
ap.add_argument("--min_dup_words", type=int, default=10,
                help="disproofs shorter than this (placeholders like 'No evidence given.') are skipped in near-duplicate detection")
ap.add_argument("--max_neighbors", type=int, default=10,
                help="exclude disinformation queries with more near-duplicates than this")
ap.add_argument("--seed", type=int, default=13)
a = ap.parse_args()
rng = np.random.default_rng(a.seed)

# debunk pool 
debunks = pd.read_csv(a.debunks)
n0 = len(debunks)
debunks["Links"] = debunks["Links"].astype(str).str.strip()
debunks = debunks.drop_duplicates("Links")
debunks["Information"] = debunks["Information"].map(repair_boundaries)
debunks["Disinformation"] = debunks["Disinformation"].map(repair_boundaries)
debunks["Title"] = debunks["Title"].fillna("").astype(str).str.strip()
debunks["disproof_len"] = debunks["Information"].str.split().str.len().fillna(0).astype(int)
debunks["date"] = pd.to_datetime(debunks["Date"], errors="coerce", dayfirst=True)

pool = debunks[(debunks["Title"] != "") & (debunks["disproof_len"] >= a.min_disproof_words)].copy()
print(f"Debunk cases: {n0} | in query pool (title present, disproof >= {a.min_disproof_words} words): {len(pool)}")

# overlap = share of title tokens present in own disproof
T = pool["Title"].map(lambda s: set(tokenize(s)))
D = pool["Information"].map(lambda s: set(tokenize(s)))
pool["overlap"] = [len(t & d) / len(t) if t else 0.0 for t, d in zip(T, D)]
rand = D.sample(frac=1, random_state=a.seed).to_numpy()
print(f"Mean overlap (BM25 tokens): own disproof {pool['overlap'].mean():.2f} | "
      f"random disproof {np.mean([len(t & d) / len(t) if t else 0 for t, d in zip(T, rand)]):.2f}")
try:   # value-based tertiles (ties stay in one bin); fall back to rank-based if edges collapse
    pool["overlap_bin"] = pd.qcut(pool["overlap"], 3, labels=["low", "mid", "high"])
except ValueError:
    pool["overlap_bin"] = pd.qcut(pool["overlap"].rank(method="first"), 3, labels=["low", "mid", "high"])
pool["len_tertile"] = pd.qcut(pool["disproof_len"].rank(method="first"), 3, labels=["short", "medium", "long"])
print(pool.groupby("overlap_bin", observed=True)
          .agg(overlap_min=("overlap", "min"), overlap_max=("overlap", "max"),
               cases=("Links", "size"), median_disproof_len=("disproof_len", "median")))

# near-duplicate groups (MinHash LSH): disproofs on word 5-gram shingles, titles on word sets
def minhashes(sets):
    out = []
    for s in sets:
        m = MinHash(num_perm=128, seed=a.seed)
        for x in s:
            m.update(x.encode())
        out.append(m)
    return out

parent = {k: k for k in debunks["Links"]}
neighbors = {k: set() for k in debunks["Links"]}   # DIRECT near-duplicates (no chaining)
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

def link_near_dups(keys, sets, label):
    lsh, mh = MinHashLSH(threshold=a.dup_threshold, num_perm=128), minhashes(sets)
    for k, m in zip(keys, mh):
        lsh.insert(k, m)
    lookup, n_pairs = dict(zip(keys, sets)), 0
    for k, m in zip(keys, mh):
        for c in lsh.query(m):
            if c != k and jaccard(lookup[k], lookup[c]) >= a.dup_threshold:  # verify exactly
                parent[find(k)] = find(c)
                neighbors[k].add(c)
                n_pairs += 1
    print(f"Near-duplicate {label} pairs (Jaccard >= {a.dup_threshold}): {n_pairs // 2}")

keys = debunks["Links"].tolist()
real = debunks[debunks["disproof_len"] >= a.min_dup_words]
print(f"Disproofs skipped in near-duplicate detection (< {a.min_dup_words} words): {len(debunks) - len(real)}")
link_near_dups(real["Links"].tolist(), [shingles(s, 5) for s in real["Information"]], "disproof")
link_near_dups(keys, [set(words(s)) for s in debunks["Title"]], "title")
debunks["dup_group"] = debunks["Links"].map(find)
debunks["dup_group_size"] = debunks["dup_group"].map(debunks["dup_group"].value_counts())
debunks["n_neighbors"] = debunks["Links"].map(lambda k: len(neighbors[k]))
debunks["lenient_links"] = debunks["Links"].map(lambda k: "|".join(sorted({k} | neighbors[k])))
pool = pool.merge(debunks[["Links", "dup_group", "dup_group_size", "n_neighbors", "lenient_links"]], on="Links")
print("Direct near-duplicates per case (pool):", pool["n_neighbors"].describe()[["mean", "max"]].round(2).to_dict(),
      f"| cases with > {a.max_neighbors}: {(pool['n_neighbors'] > a.max_neighbors).sum()}")
print(f"Cases with >= 1 near-duplicate: {(debunks['dup_group_size'] > 1).sum()} "
      f"in {debunks.loc[debunks['dup_group_size'] > 1, 'dup_group'].nunique()} groups")

# inconclusive (held-out) cases 
# Only cases without any near-duplicate (dup_group_size == 1), so no copy of their evidence stays in the index.
# Stratified over years to cover the whole time span.
cand = pool[pool["dup_group_size"] == 1].copy()
cand["year"] = cand["date"].dt.year
n_inc = a.inc_test + a.inc_dev
per_year = (cand["year"].value_counts(normalize=True) * n_inc).round().astype(int)
inc = pd.concat([g.sample(min(len(g), per_year.get(y, 0)), random_state=a.seed)
                 for y, g in cand.groupby("year")])
if len(inc) < n_inc:  # top up rounding shortfall
    inc = pd.concat([inc, cand.drop(inc.index).sample(n_inc - len(inc), random_state=a.seed)])
inc = inc.sample(frac=1, random_state=a.seed).head(n_inc)
inc["split"] = ["dev"] * a.inc_dev + ["test"] * (len(inc) - a.inc_dev)
print(f"\nInconclusive (held-out) cases: {len(inc)} "
      f"(test {(inc.split == 'test').sum()}, dev {(inc.split == 'dev').sum()})")

# disinformation queries 
# Stratified by overlap bin x disproof-length tertile, so bins have comparable lengths.
rest = pool[~pool["Links"].isin(inc["Links"]) & (pool["n_neighbors"] <= a.max_neighbors)]
need = a.dis_test_per_bin + a.dis_dev_per_bin
parts, shortfalls = [], []
for b, gb in rest.groupby("overlap_bin", observed=True):
    cells = {l: gl for l, gl in gb.groupby("len_tertile", observed=True)}
    quota = {l: need // 3 + (1 if i < need % 3 else 0) for i, l in enumerate(["short", "medium", "long"])}
    for l in quota:
        g = cells.get(l, gb.iloc[0:0])
        if len(g) < quota[l]:
            shortfalls.append(f"{b}/{l}: {len(g)} of {quota[l]}")
        parts.append(g.sample(min(len(g), quota[l]), random_state=a.seed))
dis = pd.concat(parts)
dis["split"] = "test"
for b, idx in dis.groupby("overlap_bin", observed=True).groups.items():
    dev_idx = rng.choice(idx, size=min(a.dis_dev_per_bin, len(idx)), replace=False)
    dis.loc[dev_idx, "split"] = "dev"
if shortfalls:
    print("Length-cell shortfalls (cell: available of quota):", "; ".join(shortfalls))
print(f"Disinformation queries: {len(dis)} (test {(dis.split == 'test').sum()}, dev {(dis.split == 'dev').sum()})")
print("Median disproof length per bin in the sample:",
      dis.groupby("overlap_bin", observed=True)["disproof_len"].median().to_dict())

# outputs 
def rows(df, label, prefix):
    return pd.DataFrame({
        "query_id": [f"{prefix}_{i:04d}" for i in range(len(df))],
        "text": df["Title"].values,
        "label": label,
        "set": "main",
        "split": df["split"].values,
        "source": "eeas_title",
        "gold_links": df["Links"].values if label == "disinformation" else "",
        "gold_links_lenient": df["lenient_links"].values if label == "disinformation" else "",
        "exclude_passage_ids": (df["Links"] + "#claim").values if label == "disinformation" else "",
        "exclude_doc_key": "",
        "case_links": df["Links"].values,
        "overlap": df["overlap"].round(3).values,
        "overlap_bin": df["overlap_bin"].astype(str).values,
        "disproof_len": df["disproof_len"].values,
        "date": df["date"].dt.date.values,
    })

queries = pd.concat([rows(dis, "disinformation", "eeas_dis"), rows(inc, "inconclusive", "eeas_inc")])
queries.to_csv("queries_eeas.csv", index=False)
inc[["Links"]].to_csv("held_out_links.csv", index=False)
eeas.merge(pool[["Links", "overlap", "overlap_bin", "len_tertile"]], on="Links", how="left") \
    .drop(columns=["date"]).to_csv("eeas_pool.csv", index=False)

print("\nQueries per label/split:")
print(queries.groupby(["label", "split"]).size().unstack(fill_value=0))
print("\nWrote eeas_pool.csv, queries_eeas.csv, held_out_links.csv")