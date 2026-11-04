"""One command for the 12 systems.

  python -m pipeline list
  python -m pipeline rewrite --split dev --limit 5
  python -m pipeline run --query title --retriever bm25 --reranker none --split dev --retrieve-only
  python -m pipeline run --query rewrite --retriever dense --reranker late --split dev --retrieve-only

python main.py --retriever dense still runs title + dense + no rerank, then the verdict model.
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUERIES = ("title", "rewrite")
RETRIEVERS = ("bm25", "dense")
FIRST_STAGE = (*RETRIEVERS, "late")
OPTIONAL = ("title_late_none", "title_bm25_late_k200", "title_dense_late_k200")
RERANKERS = ("none", "cross", "late")
ALIASES = {"sparse": "bm25", "cross-encoder": "cross", "late-interaction": "late"}


def cells(queries=None):
    for query in QUERIES if queries is None else queries:
        for retriever in RETRIEVERS:
            for reranker in RERANKERS:
                yield query, retriever, reranker


def test_cells():
    """Title only. BM25 and dense take every reranker. Pure late is not reranked."""
    yield from cells(("title",))
    yield "title", "late", "none"


def mode_name(query, retriever, reranker, k=100):
    name = f"{query}_{retriever}_{reranker}"
    if k != 100:
        name += f"_k{k}"
    return name


def _reject_qwen(name):
    if name and "qwen" in name.lower():
        raise SystemExit("use a model other than Qwen; Qwen is the title filter in data/claim_check.py")


def _canonical(value, allowed):
    value = ALIASES.get(value, value)
    if value not in allowed:
        raise SystemExit(f"{value} is not one of: {', '.join(allowed)}")
    return value


def run_cell(args):
    if args.retriever == "hybrid":
        raise SystemExit("hybrid is not one of the 12 systems. Choose bm25 or dense, then a reranker.")
    from pipeline.cost import attach_timing, counts, gpu_reset, summarize
    from pipeline.rerank import CROSS_MODEL, LATE_MODEL, rerank
    from pipeline.retrieve import load_queries, retrieve, search_strings
    from pipeline.store import write_run

    query = _canonical(args.query, QUERIES)
    retriever = _canonical(args.retriever, FIRST_STAGE)
    reranker = _canonical(args.reranker, RERANKERS)
    if retriever == "late" and reranker != "none":
        print("Late interaction already scored every passage. This run keeps that ranking and does not rerank.")
        reranker = "none"
    if retriever == "dense" and args.reindex:
        from retrieval.dense import build_index, query_prompt_for
        model_name = "BAAI/bge-small-en-v1.5"
        build_index(
            ROOT / "data" / "passages_v2.parquet",
            ROOT / "retrieval" / "indexes" / "dense_v2",
            model_name, batch_size=args.batch_size, device=args.device,
            query_prompt=query_prompt_for(model_name),
        )

    queries = load_queries(ROOT / "data" / "queries_v2.csv", args.split, args.set, args.limit)
    searches = search_strings(queries, query, ROOT / "runs" / "rewrite.csv")
    print(f"{mode_name(query, retriever, reranker, args.k)}: {len(queries)} claims, {len(searches)} searches, k={args.k}")
    gpu_reset()
    started = time.perf_counter()
    ranked, lookup = retrieve(
        retriever, searches, args.k,
        passages_path=ROOT / "data" / "passages_v2.parquet",
        index_dir=ROOT / "retrieval" / "indexes" / "dense_v2",
        batch_size=args.batch_size, device=args.device, k1=args.k1, b=args.b,
    )
    retrieve_s = time.perf_counter() - started
    claims = dict(zip(queries["query_id"], queries["text"]))
    texts = dict(zip(lookup["passage_id"], lookup["text"]))
    started = time.perf_counter()
    ranked = rerank(ranked, claims, texts, reranker, device=args.device, batch_size=args.batch_size)
    rerank_s = time.perf_counter() - started
    cost = attach_timing(
        counts(retriever, reranker, searches, ranked),
        retrieve_s, rerank_s,
    )

    name = mode_name(query, retriever, reranker, args.k)
    directory = ROOT / "runs" / (args.split or "all") / name
    rerank_model = {"none": None, "cross": CROSS_MODEL, "late": LATE_MODEL}[reranker]
    config = {
        "query": query,
        "retriever": retriever,
        "reranker": reranker,
        "rerank_model": rerank_model,
        "k": args.k,
        "rrf_k": 60,
        "bm25": {"k1": args.k1, "b": args.b},
        "filters": {"split": args.split, "set": args.set, "limit": args.limit},
        "rewrite": str((ROOT / "runs" / "rewrite.csv").resolve()) if query == "rewrite" else None,
        "word_limit": 400,
        "cost": cost,
        "note": (
            "late searches every v2 passage in the claim's set and keeps the top k. "
            "Each passage is clipped to 400 words. This is not one of the 12 systems."
            if retriever == "late" else
            "The reranker scores the original claim against the first 400 words of each passage. "
            "Rewritten queries are fused into the first-stage list, and the title is one of those queries."
        ),
    }
    print(summarize(cost))
    _, jsonl = write_run(ranked, lookup, claims, directory, name, config)
    if args.retrieve_only:
        _print_score_command(directory, name, args.split)
        return
    _reject_qwen(args.model)
    from generator.generator import DEFAULT_MODEL, run as generate
    generate(
        jsonl,
        directory / "verdicts.csv",
        directory / "verdict_cache.jsonl",
        model=args.model or DEFAULT_MODEL,
        max_passages=args.max_passages,
    )


def _print_score_command(directory, name, split):
    split_flag = f" --split {split}" if split else ""
    print(
        "Score with:\n"
        f"  python retrieval/eval_retrieval.py --runs {directory / (name + '.parquet')} "
        f"--passages {directory / 'passages.parquet'} --queries data/queries_v2.csv"
        f"{split_flag} --output {directory / 'retrieval.csv'}"
    )


def rewrite_cmd(args):
    from pipeline.retrieve import load_queries
    from pipeline.rewrite import rewrite
    _reject_qwen(args.model)
    queries = load_queries(ROOT / "data" / "queries_v2.csv", args.split, args.set, args.limit)
    rewrite(queries, ROOT / "runs" / "rewrite.csv", model_name=args.model, n_questions=args.questions)


def report_cmd(args):
    from pipeline.report import report
    report(args.split or "dev", args.set)


def list_cmd(_args):
    print(f"{'system':<28} {'dev run'}")
    for query, retriever, reranker in cells():
        name = mode_name(query, retriever, reranker)
        parquet = ROOT / "runs" / "dev" / name / f"{name}.parquet"
        mark = "written" if parquet.exists() else "missing"
        print(f"{name:<28} {mark}")
    print("optional:")
    for name in OPTIONAL:
        parquet = ROOT / "runs" / "dev" / name / f"{name}.parquet"
        mark = "written" if parquet.exists() else "missing"
        print(f"{name:<28} {mark}")


def parser():
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--split", choices=["dev", "test"], default=None)
    parent.add_argument("--set", dest="set", choices=["main", "article"], default=None)
    parent.add_argument("--limit", type=int, default=None, help="first N claims after the split filter")
    parent.add_argument("--device", default=None)

    ap = argparse.ArgumentParser(description="Run one cell of the 12-system retrieval grid")
    sub = ap.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", parents=[parent], help="retrieve, optionally rerank, optionally judge")
    run.add_argument("--query", choices=[*QUERIES], default="title")
    run.add_argument("--retriever", default="dense", help="bm25, dense, or late. late searches the whole passage set")
    run.add_argument("--reranker", default="none", help="none, cross, or late")
    run.add_argument("--k", type=int, default=100, help="passages kept. k other than 100 is written to its own folder")
    run.add_argument("--k1", type=float, default=1.2)
    run.add_argument("--b", type=float, default=0.75)
    run.add_argument("--batch-size", type=int, default=16)
    run.add_argument("--reindex", action="store_true", help="embed the v2 passages again before a dense run")
    run.add_argument("--retrieve-only", action="store_true", help="do not run the verdict model")
    run.add_argument("--max-passages", type=int, default=5, help="passages the verdict model reads")
    run.add_argument("--model", default=None, help="verdict model; default is Llama-3.1-8B-Instruct")
    run.set_defaults(func=run_cell)

    rw = sub.add_parser("rewrite", parents=[parent], help="write search queries with an LLM")
    rw.add_argument("--questions", type=int, default=10, help="questions per claim; the paper uses 10")
    rw.add_argument("--model", default=None, help="default is Llama-3.1-8B-Instruct")
    rw.set_defaults(func=rewrite_cmd)

    listed = sub.add_parser("list", help="show which of the 12 dev runs are on disk")
    listed.set_defaults(func=list_cmd)

    compared = sub.add_parser("report", parents=[parent], help="one comparison of every system that has a run")
    compared.set_defaults(func=report_cmd)
    return ap


def _with_default_model(args):
    from pipeline.rewrite import DEFAULT_MODEL
    if not args.model:
        args.model = DEFAULT_MODEL
    return args


def main(argv=None):
    args = parser().parse_args(argv)
    if args.cmd == "rewrite":
        args = _with_default_model(args)
    args.func(args)


if __name__ == "__main__":
    main()
