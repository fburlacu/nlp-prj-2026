"""The 12 retrieval systems: query × first stage × reranker.

query:      title | rewrite
first stage: bm25 | dense
reranker:   none | cross | late
Rewrite stays in this grid. Test uses the title only: BM25 or dense with
none, cross, or late, plus late interaction over every passage and no reranker.
"""
