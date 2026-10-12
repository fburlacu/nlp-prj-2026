"""Clean the crawled English Leite EUvsDisinfo data.

Usage: python clean_leite.py --base euvsdisinfo_base.csv --crawled euvsdisinfo_en.csv
       (--crawled also accepts cache.jsonl)
Outputs:
  leite_en_clean.csv      all (debunk, article) rows that survive cleaning, with text
  suspect_trustworthy.csv trustworthy rows from mostly-disinfo domains (inspect manually)
  cleaning_log.csv        rows/articles remaining after each step (for the report)
"""
import re
import argparse
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--base", default="euvsdisinfo_base.csv")
ap.add_argument("--crawled", default="euvsdisinfo_en.csv", help="crawl output (.csv or .jsonl)")
ap.add_argument("--min_chars", type=int, default=700)
a = ap.parse_args()

log = []
def step(name, df):
    key = "doc_key" if "doc_key" in df else "article_id"
    log.append({"step": name, "rows": len(df), "documents": df[key].nunique(),
                **df.drop_duplicates(key)["class"].value_counts().to_dict()})
    print(f"{name:<38} rows={len(df):>6}  documents={df[key].nunique():>6}")
    return df

base = pd.read_csv(a.base)
is_en = base["article_language"].astype(str).str.strip().str.lower().isin(["english", "en"])

# 0. Domain statistics come from the FULL base file (all languages) for the suspect check
dom_dis = base.groupby("article_domain")["class"].apply(lambda s: (s == "disinformation").mean())

# 1. All English (debunk, article) rows; attach crawled text by article_id.
#    (The crawler kept one row per article_id, so repeated articles lost their other
#    debunk links; merging onto the base rows restores them.)
en = step("1. English rows in base",
          base[is_en].drop(columns=["article_text", "article_title"], errors="ignore"))
crawled = (pd.read_json(a.crawled, lines=True) if a.crawled.endswith(".jsonl")
           else pd.read_csv(a.crawled))
texts = crawled[["article_id", "article_text", "article_title"]].drop_duplicates("article_id")
df = step("2. Crawled successfully", en.merge(texts, on="article_id", how="inner"))

# 3. Length filter (as in Leite et al.: < 700 characters = error page / stub)
df["article_text"] = df["article_text"].fillna("").str.strip()
df = step(f"3. Text >= {a.min_chars} chars", df[df["article_text"].str.len() >= a.min_chars])

# 4. Boilerplate / paywall / error pages (lexicon rules on the start of the text)
BAD = re.compile(r"(?:enable javascript|access denied|subscribe to (?:continue|read)|"
                 r"404 not found|page not found|are you a robot|verify you are human|"
                 r"this content is not available|cookies? (?:policy|settings) .{0,40}accept)", re.I)
df = step("4. No boilerplate/paywall", df[~df["article_text"].str[:600].str.contains(BAD)])

# 5./6. Same article under several rows. article_id is unique per (debunk, article) row,
#       so the same article cited in several debunks gets several ids. Identify documents
#       by normalised text instead (doc_key), and keep ALL rows (each carries a debunk link).
df["_norm"] = df["article_text"].str.lower().str.replace(r"\W+", " ", regex=True).str[:2000]
df["doc_key"] = pd.util.hash_pandas_object(df["_norm"], index=False).astype(str)
n_cls = df.groupby("doc_key")["class"].nunique()
df = step("5. Drop documents with both labels", df[df["doc_key"].map(n_cls) == 1])
n_docs = df["doc_key"].nunique()
print(f"6. Unique documents (doc_key): {n_docs}  (rows kept: {len(df)}; "
      f"{len(df) - n_docs} rows are repeats of a document under another debunk)")

# 7. Optional: check the text is really English (trustworthy languages were auto-detected)
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    lang = df.drop_duplicates("doc_key").set_index("doc_key")["article_text"] \
             .str[:1000].apply(lambda t: detect(t) if t else "unk")
    df = step("7. Text detected as English", df[df["doc_key"].map(lang) == "en"])
except ImportError:
    print("7. (skipped: pip install langdetect to verify text language)")

# 8. Diagnostic only: trustworthy rows from domains that are mostly disinformation
suspect = df[(df["class"] == "trustworthy") & (df["article_domain"].map(dom_dis) > 0.8)]
suspect[["article_id", "article_domain", "article_title", "article_url"]] \
    .drop_duplicates("article_id").to_csv("suspect_trustworthy.csv", index=False)
print(f"8. Suspect trustworthy articles (inspect, not removed): {suspect['article_id'].nunique()}")

df.drop(columns="_norm").to_csv("leite_en_clean.csv", index=False)
pd.DataFrame(log).fillna(0).to_csv("cleaning_log.csv", index=False)
print("\nFinal unique documents per class:")
print(df.drop_duplicates("doc_key")["class"].value_counts())