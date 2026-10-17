"""Build the retrieval index: passages.parquet.

Usage:
  python build_index.py --debunk_pool debunk_pool.csv --held_out held_out_links.csv \
                           --leite sources/euvsdisinfo_en_clean.csv [--drop_doc_keys drop.txt]
Passages:
  <Links>#claim        EEAS claim:    Title + Disinformation summary
  <Links>#disproof-<n> EEAS disproof: Information only (titles are used as queries), chunked
                       when longer than --max_chunk_words. Gold matching uses case_links +
                       doc_type, so any chunk of the gold disproof counts.
  <doc_key>#<n>        article chunk: cleaned title + ~150-word chunk of a trustworthy document,
                       at most --max_chunks_per_doc chunks per document
Excluded: held-out cases, disproofs < --min_disproof_words words (placeholders),
disinformation articles, and all labels.
"""
import re
import argparse
import pandas as pd

from preprocessing import repair_boundaries, clean_title

ap = argparse.ArgumentParser()
ap.add_argument("--debunk_pool", default="debunk_pool.csv")
ap.add_argument("--held_out", default="held_out_links.csv")
ap.add_argument("--leite", default="leite_en_clean.csv")
ap.add_argument("--drop_doc_keys", help="optional text file with one doc_key per line to leave out")
ap.add_argument("--min_disproof_words", type=int, default=10)
ap.add_argument("--chunk_words", type=int, default=150, help="target chunk size")
ap.add_argument("--max_chunk_words", type=int, default=220, help="hard cap; long sentences are split")
ap.add_argument("--min_chunk_words", type=int, default=30, help="shorter tail chunks are merged back")
ap.add_argument("--max_chunks_per_doc", type=int, default=20,
                help="keep only the first N chunks of an article (legal codes, reports, live blogs)")
ap.add_argument("--no_chunk_disproofs", action="store_true",
                help="keep each disproof as one passage instead of chunking long ones")
ap.add_argument("--output", default="passages.parquet")
a = ap.parse_args()


def join_title(title, body):
    """'Title. Body' without doubling punctuation ('Is it true?. ...')."""
    title, body = (title or "").strip(), (body or "").strip()
    if not title:
        return body
    if not body:
        return title
    return f"{title} {body}" if title[-1] in ".!?…:;\"'”’" else f"{title}. {body}"


SENT = re.compile(r"(?<=[.!?…])[\"'”’)]*\s+(?=[\"'“‘(]?[A-Z0-9])")


def chunk(text):
    """Sentence-aware chunks of ~chunk_words words; sentences longer than the cap are split."""
    sents = []
    for para in re.split(r"\n\s*\n|\n", text):
        for s in SENT.split(para.strip()):
            w = s.split()
            while len(w) > a.max_chunk_words:            # overly long "sentence" (lists, no punctuation)
                sents.append(w[:a.chunk_words]); w = w[a.chunk_words:]
            if w:
                sents.append(w)
    chunks, cur = [], []
    for w in sents:
        if cur and len(cur) + len(w) > a.chunk_words and len(cur) >= a.min_chunk_words:
            chunks.append(cur); cur = []
        cur = cur + w
        if len(cur) >= a.max_chunk_words:
            chunks.append(cur[:a.max_chunk_words]); cur = cur[a.max_chunk_words:]
    if cur:
        if chunks and len(cur) < a.min_chunk_words:
            chunks[-1] = chunks[-1] + cur                 # merge short tail
        else:
            chunks.append(cur)
    return [" ".join(c) for c in chunks]


# EEAS passages
eeas = pd.read_csv(a.debunk_pool, dtype={"Links": str})
held = set(pd.read_csv(a.held_out, dtype=str)["Links"].str.strip())
n_all = len(eeas)
eeas = eeas[~eeas["Links"].isin(held)].copy()
for c in ["Title", "Disinformation", "Information"]:
    eeas[c] = eeas[c].fillna("").astype(str).map(repair_boundaries)   # idempotent if already repaired
print(f"EEAS cases: {n_all} | held out (not indexed): {len(held)} | indexed: {len(eeas)}")

claim = pd.DataFrame({
    "passage_id": eeas["Links"] + "#claim",
    "doc_type": "eeas_claim",
    "text": [join_title(t, d) for t, d in zip(eeas["Title"], eeas["Disinformation"])],
    "case_links": eeas["Links"], "doc_key": "", "chunk_idx": 0,
})
claim = claim[claim["text"].str.len() > 0]

eeas["dlen"] = eeas["Information"].str.split().str.len().fillna(0).astype(int)
short = eeas["dlen"] < a.min_disproof_words
drows = []
for links, info in zip(eeas.loc[~short, "Links"], eeas.loc[~short, "Information"]):
    parts = [info] if a.no_chunk_disproofs else chunk(info)
    for i, c in enumerate(parts):
        drows.append({"passage_id": f"{links}#disproof-{i}", "doc_type": "eeas_disproof", "text": c,
                      "case_links": links, "doc_key": "", "chunk_idx": i})
disproof = pd.DataFrame(drows)
print(f"EEAS claim passages: {len(claim)} | disproof passages: {len(disproof)} from "
      f"{(~short).sum()} disproofs (skipped {short.sum()} disproofs < {a.min_disproof_words} words)")

# article passages
leite = pd.read_csv(a.leite, dtype={"doc_key": str, "debunk_id": str})
docs = leite[leite["class"] == "trustworthy"].drop_duplicates("doc_key").copy()
if a.drop_doc_keys:
    drop = {l.strip() for l in open(a.drop_doc_keys) if l.strip()}
    print(f"Dropping {len(drop & set(docs['doc_key']))} documents listed in {a.drop_doc_keys}")
    docs = docs[~docs["doc_key"].isin(drop)]

rows = []
for k, title, text in zip(docs["doc_key"], docs["article_title"], docs["article_text"]):
    t = clean_title(title)
    body = re.sub(r"[ \t]+", " ", str(text or "")).strip()
    for i, c in enumerate(chunk(body)[:a.max_chunks_per_doc]):
        rows.append({"passage_id": f"{k}#{i}", "doc_type": "article",
                     "text": join_title(t, c), "case_links": "", "doc_key": k, "chunk_idx": i})
art = pd.DataFrame(rows)
cpd = art.groupby("doc_key").size()
full_words = docs["article_text"].fillna("").str.split().str.len()
print(f"Trustworthy documents indexed: {art['doc_key'].nunique()} of {len(docs)} | article chunks: {len(art)} "
      f"(per document: median {cpd.median():.0f}, max {cpd.max()})")
print(f"Documents truncated to their first {a.max_chunks_per_doc} chunks: {(cpd == a.max_chunks_per_doc).sum()} "
      f"(longest document: {full_words.max()} words)")

# assemble
passages = pd.concat([claim, disproof, art], ignore_index=True)
passages["n_words"] = passages["text"].str.split().str.len()
assert passages["passage_id"].is_unique, "duplicate passage_id"
assert (passages["n_words"] > 0).all(), "empty passage"

print("\nPassages per type:")
print(passages.groupby("doc_type")["n_words"].describe(percentiles=[.1, .5, .9])
      [["count", "min", "10%", "50%", "90%", "max"]].round(0).astype(int))
top = cpd.sort_values(ascending=False).head(3)
print("Largest documents (chunks):", top.to_dict())

try:
    passages.to_parquet(a.output, index=False)
except ImportError as e:
    a.output = a.output.replace(".parquet", ".csv")
    passages.to_csv(a.output, index=False)
    print(f"(could not write parquet: {e}\n wrote CSV instead)")
print(f"\nWrote {a.output}: {len(passages)} passages")