"""One hypothetical disproof per claim, used only as a search string.

The model writes a short correction in the style of a fact-check paragraph.
That paragraph is not a verdict and is not shown to the verdict model.
The title is added back at retrieval time and the two strings are fused.
"""
import json
import time
from pathlib import Path

from pipeline.rewrite import DEFAULT_MODEL, _generate

SYSTEM = (
    "You write one short paragraph a fact-checker might publish as the correction of a claim. "
    "The paragraph is only a search query. Do not assign a label."
)
EXAMPLE_USER = """Claim: The mayor of Riga banned Russian books in March 2022.
Date: 2022-03-18

Write one paragraph of 40 to 80 words stating the corrected account.
Reply with JSON only, in this shape:
{"disproof": "..."}"""
EXAMPLE_JSON = json.dumps({
    "disproof": (
        "In March 2022 the Riga city council did not adopt an order banning books in Russian. "
        "Municipal libraries continued to hold and lend Russian-language books, and no mayoral "
        "decree removed them from the shelves or from circulation."
    ),
}, ensure_ascii=False)


def user_prompt(claim, date):
    when = date.strip() if date and str(date).strip() not in {"nan", "None"} else "unknown"
    return (
        f"Claim: {claim}\n"
        f"Date: {when}\n\n"
        "Write one paragraph of 40 to 80 words stating the corrected account. "
        "Do not say whether the claim is true, and do not use a label.\n"
        'Reply with JSON only, in this shape:\n'
        '{"disproof": "..."}'
    )


def parse_disproof(text):
    """Return the corrective paragraph. Raises ValueError or JSONDecodeError."""
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
    paragraph = str(data.get("disproof") or "").strip()
    if len(paragraph.split()) < 20:
        raise ValueError("disproof is shorter than 20 words")
    return paragraph


def disproof(queries, output, model_name=DEFAULT_MODEL, max_new_tokens=300):
    """Append one hypothetical disproof for every claim that is not already in output.

    output is a CSV with query_id, disproof. A .raw.jsonl beside it keeps the model text.
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
    print(f"Disproof: {len(queries)} claims | already written: {len(done)} | to do: {len(pending)} | {model_name}")
    if pending.empty:
        print(f"Nothing new. {output}")
        return output

    tok, model = load_model(model_name)
    raw_path = output.with_suffix(".raw.jsonl")
    wrote = 0
    started = time.perf_counter()
    with raw_path.open("a", encoding="utf-8") as raw_file:
        for row in pending.itertuples(index=False):
            messages = [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": EXAMPLE_USER},
                {"role": "assistant", "content": EXAMPLE_JSON},
                {"role": "user", "content": user_prompt(row.text, getattr(row, "date", ""))},
            ]
            reply = _generate(tok, model, messages, max_new_tokens)
            try:
                paragraph = parse_disproof(reply)
                error = ""
            except (ValueError, json.JSONDecodeError) as exc:
                paragraph = ""
                error = str(exc)
                print(f"  {row.query_id}: {error}; this claim will be searched by its title only")
            raw_file.write(json.dumps({
                "query_id": row.query_id, "reply": reply, "error": error,
            }, ensure_ascii=False) + "\n")
            if paragraph:
                frame = pd.DataFrame([{"query_id": row.query_id, "disproof": paragraph}])
                frame.to_csv(output, mode="a", header=not output.exists(), index=False)
            wrote += 1
            print(f"  disproof {wrote}/{len(pending)}", end="\r")
    print()
    elapsed = round(time.perf_counter() - started, 1)
    time_path = output.with_name("disproof.time.json")
    history = []
    if time_path.exists():
        history = json.loads(time_path.read_text(encoding="utf-8"))
    history.append({"model": model_name, "n_claims": wrote, "seconds": elapsed})
    time_path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    print(f"Wrote {output} ({elapsed} s)")
    return output
