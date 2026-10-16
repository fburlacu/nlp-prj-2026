"""LLM filter: does a title assert a checkable factual claim?

pip install torch transformers accelerate pandas
Usage:
  python llm_claim_filter.py --input leite_en_clean.csv --limit 20     # dry run, prints examples
  python llm_claim_filter.py --input leite_en_clean.csv                # full run -> claim_like.csv
(--input also accepts fact_candidates.csv from build_leite_queries.py)

Scoring: one forward pass per title; p(yes) = softmax over the 'Yes'/'No' answer tokens.
"""
import os
import json
import argparse
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from preprocessing import clean_title, rule_claim_like

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="leite_en_clean.csv")
ap.add_argument("--title_col", default="title_clean")
ap.add_argument("--classes", nargs="*", default=["trustworthy"],
                help="if the input has a class column, only score these classes")
ap.add_argument("--output", default="claim_like.csv")
ap.add_argument("--cache", default="claim_like_cache.jsonl")
ap.add_argument("--model", default="Qwen/Qwen2.5-7B-Instruct",
                help="use a different model family than the RAG generator")
ap.add_argument("--batch_size", type=int, default=16)
ap.add_argument("--threshold", type=float, default=0.5)
ap.add_argument("--limit", type=int, help="only process the first N titles (dry run)")
ap.add_argument("--require_rule", action="store_true",
                help="claim_like = LLM verdict AND rule-based filter (drops questions/format labels)")
a = ap.parse_args()

SYSTEM = (
    "You decide whether a news headline asserts a checkable factual claim: a specific statement "
    "about events, actions, people, organisations, numbers or states of affairs that could be "
    "verified or refuted with evidence. Answer only Yes or No."
)
EXAMPLES = [
    ("NATO denies plans to deploy troops in Ukraine", "Yes"),
    ("EU agrees new sanctions package against Russian banks", "Yes"),
    ("Ukraine's grain exports fell by 30% in March", "Yes"),
    ("The week in pictures from Kyiv and beyond", "No"),
    ("EU leaders gather in Brussels for two-day summit", "No"),
    ("What we know so far about the pipeline explosion", "No"),
    ("Opinion: Europe must wake up", "No"),
]
INSTRUCTION = ("Does this headline assert a checkable factual claim? A headline that only announces "
               "a meeting, a report, a live feed, pictures or an opinion piece does not.\n\nHeadline: {t}")


def build_messages(title):
    msgs = [{"role": "system", "content": SYSTEM}]
    for t, ans in EXAMPLES:
        msgs += [{"role": "user", "content": INSTRUCTION.format(t=t)}, {"role": "assistant", "content": ans}]
    msgs.append({"role": "user", "content": INSTRUCTION.format(t=title)})
    return msgs


def answer_ids(tok, words):
    ids = set()
    for w in words:
        enc = tok.encode(w, add_special_tokens=False)
        if enc:
            ids.add(enc[0])
    return sorted(ids)


df = pd.read_csv(a.input, dtype={"doc_key": str})
if "class" in df.columns and a.classes:
    df = df[df["class"].isin(a.classes)]
if a.title_col not in df.columns:            # raw Leite file: clean titles here
    df[a.title_col] = df["article_title"].map(clean_title)
if "claim_like_rule" not in df.columns:
    df["claim_like_rule"] = df[a.title_col].fillna("").map(rule_claim_like)
df = df[df[a.title_col].fillna("").str.len() > 0].drop_duplicates("doc_key")
if a.limit:
    df = df.head(a.limit)

#if there is a cache file, load it and skip already scored titles
done = {}
if os.path.exists(a.cache):
    with open(a.cache) as f:
        for line in f:
            r = json.loads(line)
            done[str(r["doc_key"])] = r
todo = df[~df["doc_key"].astype(str).isin(done)]
print(f"Titles: {len(df)} | cached: {len(df) - len(todo)} | to score: {len(todo)} | model: {a.model}")

if len(todo):
    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    if torch.cuda.is_available():
        model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.bfloat16, device_map="auto")
    else:
        print("WARNING: no GPU found; running on CPU will be very slow for a 7B model")
        model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.float32)
    print("Device:", model.device)
    model.eval()
    yes_ids = answer_ids(tok, ["Yes", " Yes", "yes", " yes"])
    no_ids = answer_ids(tok, ["No", " No", "no", " no"])

    def render(title):
        kw = dict(tokenize=False, add_generation_prompt=True)
        try:  # Qwen3-style templates: disable thinking
            return tok.apply_chat_template(build_messages(title), enable_thinking=False, **kw)
        except TypeError:
            return tok.apply_chat_template(build_messages(title), **kw)

#scoring
    rows = list(todo[["doc_key", a.title_col]].itertuples(index=False, name=None))
    with open(a.cache, "a") as f:
        for i in range(0, len(rows), a.batch_size):
            batch = rows[i:i + a.batch_size]
            enc = tok([render(t) for _, t in batch], return_tensors="pt", padding=True).to(model.device)
            with torch.no_grad(): 
                hidden = model.model(**enc).last_hidden_state[:, -1, :]
                hidden = hidden.to(model.lm_head.weight.device)
                logits = model.lm_head(hidden).float()
            ly = torch.logsumexp(logits[:, yes_ids], dim=-1)
            ln = torch.logsumexp(logits[:, no_ids], dim=-1)
            p_yes = torch.sigmoid(ly - ln).tolist()
            for (k, t), p in zip(batch, p_yes):
                r = {"doc_key": str(k), "title": t, "p_yes": round(p, 4)}
                done[str(k)] = r
                f.write(json.dumps(r) + "\n")
            print(f"  scored {min(i + a.batch_size, len(rows))}/{len(rows)}", end="\r")
    print()

#results

res = pd.DataFrame([done[str(k)] for k in df["doc_key"].astype(str) if str(k) in done])
res["claim_like"] = res["p_yes"] >= a.threshold
if a.require_rule:
    rule = df.set_index(df["doc_key"].astype(str))["claim_like_rule"]
    res["claim_like"] &= res["doc_key"].astype(str).map(rule).fillna(False).astype(bool)
res["model"] = a.model
res.to_csv(a.output, index=False)

print(f"Claim-like: {res['claim_like'].sum()} of {len(res)} ({res['claim_like'].mean():.0%}) "
      f"at threshold {a.threshold}{' + rule filter' if a.require_rule else ''}")
print("p_yes distribution:", res["p_yes"].quantile([.1, .25, .5, .75, .9]).round(3).to_dict())
if "claim_like_rule" in df.columns:
    m = res.merge(df[["doc_key", "claim_like_rule"]].astype({"doc_key": str}), on="doc_key")
    print("Agreement with rule-based filter:")
    print(pd.crosstab(m["claim_like_rule"], m["claim_like"], rownames=["rule"], colnames=["llm"]))
pd.set_option("display.max_colwidth", 90)
band = res[(res["p_yes"] >= 0.05) & (res["p_yes"] < 0.5)]
if len(band):
    print(f"\nBorderline titles (0.05 <= p_yes < 0.5): {len(band)}")
    print(band.sample(min(15, len(band)), random_state=0)[["p_yes", "title"]].to_string(index=False))
for lab in [True, False]:
    print(f"\nExamples judged claim_like={lab}:")
    print(res[res["claim_like"] == lab].sample(min(8, (res["claim_like"] == lab).sum()),
                                                random_state=0)[["p_yes", "title"]].to_string(index=False))
print(f"\nWrote {a.output}")