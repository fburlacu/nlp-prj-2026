"""The 12 retrieval systems: query × first stage × reranker.

query:      title | rewrite
first stage: bm25 | dense
reranker:   none | cross | late
Rewrite stays in this grid. A hypothetical disproof is an extra dev query,
fused with the title and searched by BM25 or dense. Test uses the title only:
BM25 or dense with none, cross, or late, plus late interaction over every
passage and no reranker.
"""
