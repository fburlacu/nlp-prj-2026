"""Run one cell of the 12-system grid.

  python main.py --retriever dense --split dev --retrieve-only
  python main.py run --query rewrite --retriever bm25 --reranker cross --split dev --retrieve-only
  python main.py rewrite --split dev
  python main.py list
  python main.py report --split dev

A bare command without run/rewrite/list/report is a run. sparse means bm25.
"""
import sys

from pipeline.cli import main

if __name__ == "__main__":
    argv = sys.argv[1:]
    if not argv or argv[0] not in {"run", "rewrite", "list", "report", "-h", "--help"}:
        argv = ["run", *argv]
    main(argv)
