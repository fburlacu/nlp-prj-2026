"""One command for retrieval plus the verdict generator.

  python main.py --retriever dense
  python main.py --retriever dense --split dev --limit 5 --retrieve-only

sparse and hybrid share this command and are filled in later. A reranker, when
one exists, sits between retrieval and the generator. Each retriever writes
retrieval/runs/<name>.jsonl. The generator reads that file and does not care
which retriever produced it.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

RETRIEVERS = ("dense", "sparse", "hybrid")


def not_ready(name, detail):
    raise SystemExit(f"{name} is not implemented yet. {detail}")


def run_dense(args, run_path):
    from retrieval.dense import build_index, query_prompt_for, search

    index_dir = ROOT / "retrieval" / "indexes" / "dense"
    model_name = "BAAI/bge-small-en-v1.5"
    if args.reindex or not (index_dir / "config.json").exists():
        build_index(
            ROOT / "data" / "passages.parquet",
            index_dir,
            model_name,
            batch_size=64,
            device=None,
            query_prompt=query_prompt_for(model_name),
        )
    search(
        ROOT / "data" / "queries.csv",
        index_dir,
        run_path,
        k=args.k,
        batch_size=64,
        device=None,
        split=args.split,
        limit=args.limit,
        model_name=None,
    )


def run_sparse(args, run_path):
    not_ready("sparse", "Add retrieval/sparse.py (BM25 over passages.parquet) and call it from here.")


def run_hybrid(args, run_path):
    not_ready(
        "hybrid",
        "Add it when sparse exists: fuse the dense and sparse ranked lists, then optionally rerank.",
    )


RUNNERS = {"dense": run_dense, "sparse": run_sparse, "hybrid": run_hybrid}


def main():
    ap = argparse.ArgumentParser(description="Retrieve evidence and check the claim")
    ap.add_argument("--retriever", choices=RETRIEVERS, default="dense")
    ap.add_argument("--reranker", default="none",
                    help="none for now; a later name runs a reranker on the retrieved list")
    ap.add_argument("--reindex", action="store_true",
                    help="embed the passages again even if an index already exists")
    ap.add_argument("--retrieve-only", action="store_true",
                    help="write the retrieval run and skip the generator")
    ap.add_argument("--split", choices=["dev", "test"], default=None)
    ap.add_argument("--limit", type=int, default=None, help="only the first N queries")
    ap.add_argument("--k", type=int, default=10, help="passages kept per query")
    ap.add_argument("--max-passages", type=int, default=5,
                    help="how many of those passages the generator sees")
    args = ap.parse_args()

    if args.reranker != "none":
        not_ready(f"reranker {args.reranker}", "Call it on the run file before the generator.")

    run_path = ROOT / "retrieval" / "runs" / f"{args.retriever}.jsonl"
    print(f"Retriever: {args.retriever}")
    RUNNERS[args.retriever](args, run_path)
    if args.retrieve_only:
        print(f"Retrieval only. Run file: {run_path}")
        return

    from generator.generator import run as generate
    generate(
        run_path,
        ROOT / "generator" / f"verdicts_{args.retriever}.csv",
        ROOT / "generator" / f"verdict_cache_{args.retriever}.jsonl",
        max_passages=args.max_passages,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
