"""Build the v2 passages file passages_v2.parquet. The `set` column says which query set searches a passage:
  main     EEAS disproofs           (EEAS disinformation + inconclusive queries)
  article  Leite article chunks     (Leite article-set queries)
retrieve.py builds one BM25 index per set; a query never sees passages of the other set.

Usage: python build_index_v2.py [--held_out held_out_links_v2.csv --passages_v1 passages.parquet]
EEAS: one passage per disproof (the `Information` field after repair_boundaries), not chunked, so a dense
encoder can chunk it later. No titles and no summaries (no eeas_claim passages).
Articles: the trustworthy article chunks of passages.parquet, copied unchanged.
Columns
  passage_id   <Links>#disproof | <doc_key>#<n>
  set          main | article
  source       eeas_disproof | leite_article
  case_id      <Links> (EEAS only); gold, held-out and near-duplicate clusters are all defined on this
  doc_id       Leite document doc_key (Leite only)
  text         repaired disproof text | article chunk as in v1
  length       words
  cluster_id   near-duplicate group of the case (EEAS only; dup_group in debunk_pool.csv, a singleton is
               its own cluster)
Excluded: every held-out case (split-level exclusion, asserted) and disproofs < --min_disproof_words
words (placeholders such as "No evidence given."). Main-set queries have no per-query exclusion; Leite
queries keep exclude_doc_key (own document + wire copies), applied by the retriever as a result filter.
"""
import argparse

import pandas as pd

from preprocessing import repair_boundaries, quoted_titles

ap = argparse.ArgumentParser()
ap.add_argument("--debunk_pool", default="debunk_pool.csv")
ap.add_argument("--held_out", default="held_out_links_v2.csv")
ap.add_argument("--queries", default="queries_v2.csv")
ap.add_argument("--passages_v1", default="passages.parquet", help="source of the article chunks")
ap.add_argument("--min_disproof_words", type=int, default=10)
ap.add_argument("--output", default="passages_v2.parquet")
a = ap.parse_args()

pool = pd.read_csv(a.debunk_pool, dtype=str, keep_default_na=False)
held = set(pd.read_csv(a.held_out, dtype=str)["Links"].str.strip())
q = pd.read_csv(a.queries, dtype=str, keep_default_na=False)
text = pool["Information"].map(repair_boundaries)   # idempotent if already repaired
length = text.str.split().str.len().fillna(0).astype(int)
short = length < a.min_disproof_words
keep = ~pool["Links"].isin(held) & ~short

disproof = pd.DataFrame({
    "passage_id": pool.loc[keep, "Links"] + "#disproof",
    "set": "main",
    "source": "eeas_disproof",
    "case_id": pool.loc[keep, "Links"],
    "doc_id": None,
    "text": text[keep],
    "length": length[keep],
    "cluster_id": pool.loc[keep, "dup_group"],
})
print(f"EEAS cases: {len(pool)} | held out: {len(held)} | placeholders < {a.min_disproof_words} words: "
      f"{(short & ~pool['Links'].isin(held)).sum()} | indexed disproofs: {len(disproof)}")

v1 = pd.read_parquet(a.passages_v1)
art = v1[v1["doc_type"] == "article"]
article = pd.DataFrame({"passage_id": art["passage_id"], "set": "article", "source": "leite_article", "case_id": None,
                        "doc_id": art["doc_key"], "text": art["text"], "length": art["n_words"], "cluster_id": None})
print(f"Article chunks (copied from {a.passages_v1}): {len(article)} from {article['doc_id'].nunique()} documents")

# split-level exclusion and held-out definition, all at case level
ids = set(disproof["case_id"])
inc = set(q.loc[(q["set"] == "main") & (q["label"] == "inconclusive"), "case_links"])
assert inc == held, "inconclusive queries and held-out file disagree"
assert not ids & held, "held-out case in the index"
size = pool.set_index("Links")["dup_group_size"]
assert (size.reindex(list(held)) == "1").all(), "held-out case is not a singleton"
quoted = quoted_titles(pool["Links"].tolist(), pool["Title"].tolist(), pool["Information"].tolist())
assert not held & quoted.keys(), "held-out title is quoted in another case's disproof"
assert not held & set(disproof["cluster_id"]), "a near-duplicate of a held-out case is in the index"
assert not disproof["passage_id"].str.endswith("#claim").any(), "claim passage in the main index"
eeas_q = q["source"] == "eeas_title"
assert (q.loc[eeas_q, "exclude_passage_ids"] == "").all(), "main-set queries must have no per-query exclusion"
# gold
dis = q[(q["set"] == "main") & (q["label"] == "disinformation")]
assert dis["gold_links"].isin(ids).all(), "strict gold case missing from the index"
len_gold = [x for s in dis["gold_links_lenient"] for x in s.split("|") if x]
print(f"Lenient gold cases in the index: {sum(x in ids for x in len_gold)} of {len(len_gold)}")
proxy = {k for s in q["gold_doc_keys"] for k in s.split("|") if k}
assert proxy <= set(article["doc_id"]), "proxy gold document missing from the index"
passages = pd.concat([disproof, article], ignore_index=True)
assert passages["passage_id"].is_unique and (passages["length"] > 0).all()
print(f"Disproofs quoting another case's title: {len(set().union(*quoted.values()) & ids)} of {len(disproof)} "
      f"indexed (kept; see DATA_PREP §10)")

print("\nPassages per set, length in words:")
print(passages.groupby(["set", "source"])["length"].describe(percentiles=[.1, .5, .9])
      [["count", "min", "10%", "50%", "90%", "max"]].round(0).astype(int))
print(f"Disproofs over 138 words (~180 wordpieces, ColBERT default doc_maxlen): {(disproof['length'] > 138).mean():.1%}")
print(f"Disproof clusters: {disproof['cluster_id'].nunique()} | disproofs in clusters of size > 1: "
      f"{disproof['cluster_id'].duplicated(keep=False).sum()}")
passages.to_parquet(a.output, index=False)
print(f"\nWrote {a.output}: {len(passages)} passages (main {len(disproof)}, article {len(article)})")
