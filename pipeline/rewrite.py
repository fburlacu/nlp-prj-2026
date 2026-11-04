"""LLM search-query writing, the first three retrieval stages of INFACT.

The model rewrites the claim, writes the questions a fact-check needs, and
writes one search query per question. It does not see evidence and it does not
give a verdict. The original title is added back later, at retrieval time.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"

SYSTEM = (
    "You prepare searches that can find a published fact-check of a claim. "
    "You do not decide whether the claim is true."
)
EXAMPLE_USER = """Claim: The mayor of Riga banned Russian books in March 2022.
Date: 2022-03-18

Write exactly 2 questions a fact-checker must answer. For each question write one short search query.
Reply with JSON only, in this shape:
{"interpretation": "...", "questions": [{"question": "...", "query": "..."}]}"""
EXAMPLE_JSON = json.dumps({
    "interpretation": "In March 2022 the mayor of Riga is said to have banned books in Russian.",
    "questions": [
        {"question": "Did the mayor of Riga order a ban on Russian books in March 2022?",
         "query": "Riga mayor ban Russian books March 2022"},
        {"question": "Which official, if any, announced a restriction on Russian-language books in Latvia?",
         "query": "Latvia Russian language books restriction 2022 announcement"},
    ],
}, ensure_ascii=False)


def user_prompt(claim, date, n_questions):
    when = date.strip() if date and date.strip() not in {"nan", "None"} else "unknown"
    return (
        f"Claim: {claim}\n"
        f"Date: {when}\n\n"
        f"Write exactly {n_questions} questions a fact-checker must answer. "
        "For each question write one short search query. "
        "The example had 2 questions; that number is not yours.\n"
        'Reply with JSON only, in this shape:\n'
        '{"interpretation": "...", "questions": [{"question": "...", "query": "..."}]}'
    )


def parse_rewrite(text, n_questions):
    """Pull interpretation and search queries out of a model reply. Raises ValueError."""
    raw = text.strip()
    if "```" in raw:
        fenced = raw.split("```", 2)[1]
        if fenced.startswith("json"):
            fenced = fenced[4:]
        raw = fenced.split("```", 1)[0]
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("reply has no JSON object")
    data = json.loads(raw[start:end + 1])
    found = []
    for item in data.get("questions") or []:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question") or "").strip()
        query = item.get("query") or item.get("queries") or ""
        if isinstance(query, list):
            query = query[0] if query else ""
        query = str(query).strip()
        if question and query:
            found.append({"question": question, "query": query})
    if not found:
        raise ValueError("JSON has no question with a search query")
    return {
        "interpretation": str(data.get("interpretation") or "").strip(),
        "questions": found[:n_questions],
    }


def _generate(tok, model, messages, max_new_tokens):
    import torch

    kwargs = dict(tokenize=False, add_generation_prompt=True)
    try:
        prompt = tok.apply_chat_template(messages, enable_thinking=False, **kwargs)
    except TypeError:
        prompt = tok.apply_chat_template(messages, **kwargs)
    enc = tok(prompt, return_tensors="pt", add_special_tokens=False)
    enc = {key: value.to(model.device) for key, value in enc.items()}
    with torch.no_grad():
        out = model.generate(
            **enc, max_new_tokens=max_new_tokens, do_sample=False,
            pad_token_id=tok.pad_token_id,
        )
    new_tokens = out[0, enc["input_ids"].shape[1]:]
    return tok.decode(new_tokens, skip_special_tokens=True)


def rewrite(queries, output, model_name=DEFAULT_MODEL, n_questions=10, max_new_tokens=800):
    """Append search queries for every claim that is not already in output.

    output is a CSV with query_id, question, search_query, interpretation.
    A .raw.jsonl beside it keeps the model text, including replies that did not parse.
    """
    import pandas as pd
    from generator.generator import load_model

    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if output.exists():
        previous = pd.read_csv(output, dtype=str, keep_default_na=False)
        done = set(previous["query_id"])
    pending = queries[~queries["query_id"].isin(done)]
    print(f"Rewrite: {len(queries)} claims | already written: {len(done)} | to do: {len(pending)} | {model_name}")
    if pending.empty:
        print(f"Nothing new. {output}")
        return output

    tok, model = load_model(model_name)
    raw_path = output.with_suffix(".raw.jsonl")
    wrote = 0
    with raw_path.open("a", encoding="utf-8") as raw_file:
        for row in pending.itertuples(index=False):
            messages = [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": EXAMPLE_USER},
                {"role": "assistant", "content": EXAMPLE_JSON},
                {"role": "user", "content": user_prompt(row.text, getattr(row, "date", ""), n_questions)},
            ]
            reply = _generate(tok, model, messages, max_new_tokens)
            try:
                parsed = parse_rewrite(reply, n_questions)
                error = ""
            except (ValueError, json.JSONDecodeError) as exc:
                parsed = {"interpretation": "", "questions": []}
                error = str(exc)
                print(f"  {row.query_id}: {error}; this claim will fall back to its title")
            raw_file.write(json.dumps({
                "query_id": row.query_id, "reply": reply, "error": error,
            }, ensure_ascii=False) + "\n")
            if parsed["questions"]:
                records = [{
                    "query_id": row.query_id,
                    "question": item["question"],
                    "search_query": item["query"],
                    "interpretation": parsed["interpretation"],
                } for item in parsed["questions"]]
                frame = pd.DataFrame(records)
                frame.to_csv(output, mode="a", header=not output.exists(), index=False)
            wrote += 1
            print(f"  rewritten {wrote}/{len(pending)}", end="\r")
    print()
    print(f"Wrote {output}")
    return output
