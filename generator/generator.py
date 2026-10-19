"""RAG verdict: disinformation, fact, or inconclusive, given retrieved evidence.

Reads the JSONL run written by retrieval/dense.py. Only the claim text and the
passage texts are shown to the model. Gold columns in queries.csv stay out of
this step so they can be joined on query_id afterwards.

This model must be a different family from the Qwen title filter in
data/claim_check.py. The default is Llama-3.1-8B-Instruct.

Scoring is one forward pass per claim. The verdict is the highest of the three
next-token probabilities, with no sampling.

Usage (from the repo root):
  python main.py --retriever dense --limit 5
  python generator/generator.py --retrieval retrieval/runs/dense.jsonl
"""
import argparse
import json
import os
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
VERDICTS = ("disinformation", "fact", "inconclusive")

SYSTEM = (
    "You check a news claim against retrieved evidence. "
    "Reply with exactly one word: disinformation, fact, or inconclusive. "
    "disinformation means the evidence refutes the claim. "
    "fact means the evidence supports the claim. "
    "inconclusive means the evidence is missing, off-topic, or not enough to decide."
)
EXAMPLES = [
    (
        "NATO troops are fighting in Ukraine",
        "[1] NATO has not deployed combat troops to Ukraine. "
        "Member states provide equipment and training only.",
        "disinformation",
    ),
    (
        "The EU adopted a new sanctions package against Russian banks",
        "[1] EU countries agreed a further sanctions package targeting "
        "Russian banks and energy revenue.",
        "fact",
    ),
    (
        "A meteor destroyed the Kerch bridge",
        "[1] The claim that Western biolabs operate in Ukraine is unsupported. "
        "No such laboratories exist.",
        "inconclusive",
    ),
]
INSTRUCTION = "Claim: {claim}\n\nEvidence:\n{evidence}"


def format_evidence(passages, max_passages):
    chosen = passages[:max_passages] if max_passages else passages
    if not chosen:
        return "(no evidence retrieved)"
    blocks = []
    for n, passage in enumerate(chosen, 1):
        blocks.append(f"[{n}] {passage.get('text', '').strip()}")
    return "\n\n".join(blocks)


def build_messages(claim, evidence):
    msgs = [{"role": "system", "content": SYSTEM}]
    for example_claim, example_evidence, answer in EXAMPLES:
        msgs.append({"role": "user", "content": INSTRUCTION.format(claim=example_claim, evidence=example_evidence)})
        msgs.append({"role": "assistant", "content": answer})
    msgs.append({"role": "user", "content": INSTRUCTION.format(claim=claim, evidence=evidence)})
    return msgs


def class_token_ids(tok):
    """First-token ids for each verdict. A token claimed by two labels is dropped."""
    taken = {}
    out = {}
    for name in VERDICTS:
        ids = []
        for word in (name, name.capitalize(), " " + name, " " + name.capitalize()):
            enc = tok.encode(word, add_special_tokens=False)
            if not enc:
                continue
            token_id = enc[0]
            if taken.get(token_id, name) != name:
                continue
            taken[token_id] = name
            if token_id not in ids:
                ids.append(token_id)
        if not ids:
            raise SystemExit(f"tokenizer has no unique first token for {name!r}")
        out[name] = ids
    return out


def load_rows(path, limit):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
            if limit and len(rows) >= limit:
                break
    if not rows:
        raise SystemExit(f"no queries in {path}")
    return rows


def load_model(model_name):
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as e:
        raise SystemExit("pip install torch transformers accelerate") from e

    tok = AutoTokenizer.from_pretrained(model_name)
    # Left padding keeps the answer token at position -1 in a batch.
    tok.padding_side = "left"
    if tok.pad_token is None:
        # Llama 3.1 reserves this id so padding is not also <|eot_id|>.
        pad = "<|finetune_right_pad_id|>"
        tok.pad_token = pad if pad in tok.get_vocab() else tok.eos_token
    if torch.cuda.is_available():
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=dtype, device_map="auto")
    else:
        print("WARNING: no GPU found; running Llama 3.1 on CPU will be very slow")
        model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)
    model.eval()
    print("Device:", model.device)
    return tok, model


def render(tok, claim, evidence):
    """Llama 3.1 chat string. The template already inserts <|begin_of_text|>."""
    messages = build_messages(claim, evidence)
    kwargs = dict(tokenize=False, add_generation_prompt=True)
    try:
        return tok.apply_chat_template(messages, enable_thinking=False, **kwargs)
    except TypeError:
        return tok.apply_chat_template(messages, **kwargs)


def score_batch(tok, model, batch, token_ids):
    import torch

    prompts = [render(tok, row["text"], format_evidence(row.get("passages") or [], None))
               for row in batch]
    # add_special_tokens=False: the chat string already contains <|begin_of_text|>.
    enc = tok(prompts, return_tensors="pt", padding=True, add_special_tokens=False)
    enc = enc.to(model.device)
    with torch.no_grad():
        logits = model(**enc).logits[:, -1, :].float()
    columns = [torch.logsumexp(logits[:, token_ids[name]], dim=-1) for name in VERDICTS]
    probs = torch.softmax(torch.stack(columns, dim=-1), dim=-1)
    winners = probs.argmax(dim=-1).tolist()
    scored = []
    for row, winner, prob in zip(batch, winners, probs.tolist()):
        scored.append({
            "query_id": row["query_id"],
            "text": row["text"],
            "verdict": VERDICTS[winner],
            "p_disinformation": round(prob[0], 4),
            "p_fact": round(prob[1], 4),
            "p_inconclusive": round(prob[2], 4),
            "n_passages": len(row.get("passages") or []),
        })
    return scored


def run(retrieval, output, cache, model=DEFAULT_MODEL, batch_size=1, max_passages=5, limit=None):
    """Score one retrieval run. retrieval, output and cache are filesystem paths."""
    if not os.path.exists(retrieval):
        raise SystemExit(f"not found: {retrieval}\nrun retrieval before the generator")
    rows = load_rows(retrieval, limit)

    done = {}
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                if record.get("model") == model and record.get("max_passages") == max_passages:
                    done[str(record["query_id"])] = record
    todo = [row for row in rows if str(row["query_id"]) not in done]
    print(f"Queries: {len(rows)} | cached: {len(rows) - len(todo)} | to score: {len(todo)} | model: {model}")

    if todo:
        tok, loaded = load_model(model)
        token_ids = class_token_ids(tok)
        cache_path = Path(cache)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("a", encoding="utf-8") as f:
            for start in range(0, len(todo), batch_size):
                batch = todo[start:start + batch_size]
                # max_passages is applied here so the cache matches this run's prompt
                prepared = []
                for row in batch:
                    passages = (row.get("passages") or [])[:max_passages]
                    prepared.append({**row, "passages": passages})
                for record in score_batch(tok, loaded, prepared, token_ids):
                    record["model"] = model
                    record["max_passages"] = max_passages
                    done[str(record["query_id"])] = record
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                print(f"  scored {min(start + batch_size, len(todo))}/{len(todo)}", end="\r")
        print()

    ordered = [done[str(row["query_id"])] for row in rows if str(row["query_id"]) in done]
    out = pd.DataFrame(ordered)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output, index=False)
    print(out["verdict"].value_counts().to_string())
    print(f"Wrote {output}")


def main():
    ap = argparse.ArgumentParser(description="RAG claim check over a retrieval run")
    ap.add_argument("--retrieval", default=str(ROOT / "retrieval" / "runs" / "dense.jsonl"))
    ap.add_argument("--output", default=str(ROOT / "generator" / "verdicts.csv"))
    ap.add_argument("--cache", default=str(ROOT / "generator" / "verdict_cache.jsonl"))
    ap.add_argument("--model", default=DEFAULT_MODEL,
                    help="Llama 3.1 Instruct; keep a different family from data/claim_check.py")
    ap.add_argument("--batch-size", type=int, default=1,
                    help="8B weights leave little room for long evidence prompts")
    ap.add_argument("--max-passages", type=int, default=5,
                    help="how many retrieved passages to place in the prompt")
    ap.add_argument("--limit", type=int, default=None, help="only the first N queries")
    args = ap.parse_args()
    run(args.retrieval, args.output, args.cache, args.model, args.batch_size, args.max_passages, args.limit)


if __name__ == "__main__":
    main()
