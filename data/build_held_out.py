"""Re-select the held-out (inconclusive) cases at case level, keeping the disinformation queries fixed.

Usage: python build_held_out.py
A case is eligible for the held-out set if it is in the query pool (title present, disproof >= 30 words),
is a singleton (dup_group_size == 1: no near-duplicate disproof or title), and its title (normalised:
lowercase, punctuation stripped, whole words) does not occur in any other case's disproof. Held-out cases
that are no longer eligible are replaced by an eligible case from the same year (nearest year if none),
which takes over the replaced query's split under a new query_id. Kept queries keep their query_id.
Reads the v1 files and writes new ones (the v1 files are not changed):
  held_out_links_v2.csv  held-out case links
  queries_v2.csv         queries.csv with new inconclusive rows; adds len_bin (disproof length tertile) to EEAS
                         queries; empties exclude_passage_ids (v2 has no per-query exclusion for EEAS queries)
  queries_debunk_v2.csv  queries_debunk.csv with new inconclusive rows
Run `add_entity_overlap.py --queries queries_v2.csv` afterwards to fill the entity columns of the new rows.
"""
import argparse

import numpy as np
import pandas as pd

from preprocessing import quoted_titles

ap = argparse.ArgumentParser()
ap.add_argument("--debunk_pool", default="debunk_pool.csv")
ap.add_argument("--queries", default="queries.csv")
ap.add_argument("--queries_debunk", default="queries_debunk.csv")
ap.add_argument("--held_out", default="held_out_links.csv")
ap.add_argument("--min_disproof_words", type=int, default=30)
ap.add_argument("--seed", type=int, default=13)
ap.add_argument("--suffix", default="_v2", help="added to the output file names")
a = ap.parse_args()
rng = np.random.default_rng(a.seed)

pool = pd.read_csv(a.debunk_pool, dtype=str, keep_default_na=False)
pool["disproof_len"] = pool["disproof_len"].astype(int)
pool["year"] = pd.to_datetime(pool["Date"], errors="coerce", dayfirst=True).dt.year
q = pd.read_csv(a.queries, dtype=str, keep_default_na=False)
held = pd.read_csv(a.held_out, dtype=str)["Links"].str.strip().tolist()

# title quoted in another case's disproof (all 14,497 cases are searched)
quoted = quoted_titles(pool["Links"].tolist(), pool["Title"].tolist(), pool["Information"].tolist())
quoting = set().union(*quoted.values())
print(f"Titles quoted in another case's disproof: {len(quoted)} | "
      f"disproofs quoting another case's title: {len(quoting)} of {len(pool)}")

in_pool = (pool["Title"].str.strip() != "") & (pool["disproof_len"] >= a.min_disproof_words)
singleton = in_pool & (pool["dup_group_size"] == "1")
eligible = singleton & ~pool["Links"].isin(quoted)
print(f"Pool singletons: {singleton.sum()} | removed by the title-quote rule: {(singleton & ~eligible).sum()} "
      f"| eligible for held-out: {eligible.sum()}")

ok = set(pool.loc[eligible, "Links"])
dis_cases = set(q.loc[q["label"] == "disinformation", "case_links"])
dropped = [h for h in held if h not in ok]
print(f"Current held-out cases: {len(held)} | no longer eligible: {len(dropped)}")

# replace each dropped case by an eligible case of the same (or nearest) year
year = pool.set_index("Links")["year"]
free = pool[eligible & ~pool["Links"].isin(set(held) | dis_cases)]
replacement = {}
for h in dropped:
    cand = free[~free["Links"].isin(replacement.values())]
    gap = (cand["year"] - year[h]).abs()
    pick = cand[gap == gap.min()]
    replacement[h] = pick["Links"].iloc[rng.integers(len(pick))]
new_held = [replacement.get(h, h) for h in held]

assert len(set(new_held)) == len(new_held) == len(held), "held-out cases must be unique"
assert set(new_held) <= ok, "held-out case is not an eligible singleton"
assert not set(new_held) & quoted.keys(), "held-out title is quoted in another case's disproof"
assert not set(new_held) & dis_cases, "held-out case is a disinformation query"
lenient = {x for s in q["gold_links_lenient"] for x in s.split("|") if x}
assert not set(new_held) & lenient, "held-out case is a lenient gold case"
same_year = sum(year[h] == year[r] for h, r in replacement.items())
print(f"Replacements: {len(replacement)} ({same_year} from the same year)")

# rewrite the inconclusive queries
case = pool.set_index("Links")
next_id = max(int(x.rsplit("_", 1)[1]) for x in q.loc[q["label"] == "inconclusive", "query_id"]) + 1
new_id = {}
for h in dropped:
    new_id[h] = f"eeas_inc_{next_id:04d}"
    next_id += 1


def rewrite(df):
    df = df.copy()
    for h, r in replacement.items():
        i = df.index[(df["label"] == "inconclusive") & (df["case_links"] == h)]
        assert len(i) == 1, h
        c = case.loc[r]
        df.loc[i, ["query_id", "text", "case_links", "overlap", "overlap_bin", "disproof_len", "date"]] = [
            new_id[h], c["Title"], r, str(round(float(c["overlap"]), 3)), c["overlap_bin"], str(c["disproof_len"]),
            str(pd.to_datetime(c["Date"], dayfirst=True).date())]
        for col in ["title_entities", "specific_entities", "n_entities", "n_specific"]:
            if col in df.columns:
                df.loc[i, col] = ""
    return df


q = rewrite(q)
eeas = q["source"] == "eeas_title"
q["len_bin"] = ""
q.loc[eeas, "len_bin"] = q.loc[eeas, "case_links"].map(case["len_tertile"])
q.loc[eeas, "exclude_passage_ids"] = ""   # v1 own-claim exclusion; v2 excludes held-out cases at split level
assert (q.loc[eeas, "len_bin"] != "").all()
assert set(q.loc[q["label"] == "inconclusive", "case_links"]) == set(new_held)
assert q["query_id"].is_unique

out = {f: f.replace(".csv", f"{a.suffix}.csv") for f in [a.held_out, a.queries, a.queries_debunk]}
assert all(o != f for f, o in out.items()), "--suffix must not be empty (v1 files stay unchanged)"
pd.DataFrame({"Links": new_held}).to_csv(out[a.held_out], index=False)
q.to_csv(out[a.queries], index=False)
qd = pd.read_csv(a.queries_debunk, dtype=str, keep_default_na=False)
rewrite(qd).to_csv(out[a.queries_debunk], index=False)

print("\nInconclusive queries per split:", q[q["label"] == "inconclusive"].groupby("split").size().to_dict())
print("len_bin of disinformation queries:", q[q["label"] == "disinformation"]["len_bin"].value_counts().to_dict())
print("Wrote", ", ".join(out.values()))
print(f"Next: python add_entity_overlap.py --queries {out[a.queries]}")
