"""The 12 retrieval systems: query × first stage × reranker.

query:      title | rewrite
first stage: bm25 | dense
reranker:   none | cross | late
A late or cross-encoder first stage, and late reranking at k=200, are optional dev checks outside this grid.
"""
