"""Columns added
  title_entities     all entities in the query, '|'-separated                   (all queries)
  specific_entities  the specific ones                                          (all queries)
  n_entities, n_specific                                                         (all queries)
  entity_overlap     share of the specific entities found in the gold evidence  (gold queries with n_specific >= 1)
  entity_bin         entity       >= 1 specific entity and >= --min_share of them found in the evidence
                     formulation  otherwise: no specific entity, or the evidence does not repeat it,
                                  so retrieval cannot rely on matching names
                     (empty for queries without gold)
"""
import re
import argparse
from collections import defaultdict

import pandas as pd
import spacy
from nltk.stem.snowball import SnowballStemmer

ap = argparse.ArgumentParser()
ap.add_argument("--queries", default="queries.csv")
ap.add_argument("--debunk_pool", default="debunk_pool.csv")
ap.add_argument("--passages", default="passages.parquet")
ap.add_argument("--max_df", type=float, default=0.05, help="entities in more disproofs than this share are generic")
ap.add_argument("--min_share", type=float, default=0.5, help="entity_overlap needed for the 'entity' bin")
a = ap.parse_args()

LABELS = {"PERSON", "NORP", "FAC", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "LAW", "WORK_OF_ART"}
ALIASES = [{"us", "usa", "america", "american", "united states"},
           {"uk", "britain", "british", "great britain", "united kingdom"}, {"eu", "european union"}]
DROP = {"the", "of", "and", "a", "an"}
stem = SnowballStemmer("english").stem
WORD = re.compile(r"[a-z0-9]+")
nlp = spacy.load("en_core_web_lg", disable=["lemmatizer"])

split = lambda s: [x for x in str(s).split("|") if x and x != "nan"]
words = lambda t: [w for w in WORD.findall(t.lower()) if w not in DROP]
stems = lambda t: [stem(w) for w in words(t)]
is_alias = lambda e: any(" ".join(words(e)).removesuffix("s") in g or " ".join(words(e)) in g for g in ALIASES)

# document frequency of entities over all EEAS disproofs (inverted index on stems)
pool = pd.read_csv(a.debunk_pool, dtype=str, keep_default_na=False)
inv = defaultdict(set)
for i, text in enumerate(pool["Information"]):
    for s in {stem(w) for w in WORD.findall(text.lower())}:
        inv[s].add(i)


def df_share(entity):
    s = stems(entity)
    return len(set.intersection(*(inv.get(x, set()) for x in s))) / len(pool) if s else 1.0


def found(entity, ev_stems):
    # prefix match in both directions handles demonyms: russian/russia, ukrainian/ukrain, crimean/crimea
    return all(any(e.startswith(s) or (s.startswith(e) and len(e) >= 4) for e in ev_stems) for s in stems(entity))


q = pd.read_csv(a.queries, dtype=str, keep_default_na=False)
new_cols = ["title_entities", "specific_entities", "n_entities", "n_specific", "entity_overlap", "entity_bin"]
q = q.drop(columns=[c for c in new_cols if c in q.columns])

# gold evidence text per query
info = pool.set_index("Links")["Information"]
p = pd.read_parquet(a.passages, columns=["doc_type", "doc_key", "text"])
art = p[p["doc_type"] == "article"].groupby("doc_key")["text"].apply(" ".join)
evidence = {}
for r in q.itertuples(index=False):
    if r.gold_links:
        evidence[r.query_id] = info.get(r.gold_links, "")
    elif r.gold_doc_keys:
        evidence[r.query_id] = " ".join(art.get(k, "") for k in split(r.gold_doc_keys))

out = {c: [] for c in new_cols}
for qid, doc in zip(q["query_id"], nlp.pipe(q["text"].tolist(), batch_size=256)):
    ents = list(dict.fromkeys(e.text.strip() for e in doc.ents if e.label_ in LABELS and words(e.text)))
    spec = [e for e in ents if not is_alias(e) and df_share(e) < a.max_df]
    out["title_entities"].append("|".join(ents))
    out["specific_entities"].append("|".join(spec))
    out["n_entities"].append(len(ents))
    out["n_specific"].append(len(spec))
    if qid not in evidence:
        out["entity_overlap"].append(None); out["entity_bin"].append("")
        continue
    ev_stems = {stem(w) for w in WORD.findall(evidence[qid].lower())}
    share = sum(found(e, ev_stems) for e in spec) / len(spec) if spec else None
    out["entity_overlap"].append(None if share is None else round(share, 3))
    out["entity_bin"].append("entity" if share is not None and share >= a.min_share else "formulation")

for c in new_cols:
    q[c] = out[c]
q.to_csv(a.queries, index=False)

g = q[q["entity_bin"] != ""]
print(f"Entities in {(q['n_entities'] > 0).mean():.0%} of {len(q)} queries, "
      f"specific entities in {(q['n_specific'] > 0).mean():.0%}")
print("\nentity_bin by set/split (queries with gold):")
print(g.groupby(["set", "split", "entity_bin"]).size().unstack(fill_value=0).to_string())
m = g[g["set"] == "main"]
print("\nmain set: entity_bin x overlap_bin")
print(pd.crosstab(m["entity_bin"], m["overlap_bin"]).reindex(columns=["low", "mid", "high"]).to_string())
f = m[m["entity_bin"] == "formulation"]
print(f"\nformulation queries: {(f['n_specific'] == 0).sum()} without a specific entity, "
      f"{(f['n_specific'] > 0).sum()} whose specific entities are not in the evidence")
print(f"\nSaved {a.queries} (re-run validate.py to refresh data_manifest.json)")
