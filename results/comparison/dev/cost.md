# Cost, dev

## Cost

Space is the stored dense index. Computation is the number of query–passage scores.
Wall time is the clock from the start of retrieval until reranking finishes, for the
whole split, including the model load or the BM25 index build. It is not CPU time
and it is not the time for one claim. GPU peak here is PyTorch reserved memory of
the retriever. A dash means that run was written before this was recorded.

| Run | First stage | Rerank | Stored index | GPU peak | Wall time |
| --- | --- | --- | ---: | ---: | ---: |
| title · BM25 | 3,775,326 BM25 scores | — | — | — | — |
| title · BM25 · cross | 3,775,326 BM25 scores | 19,200 cross-encoder pairs | — | — | — |
| title · BM25 · late | 3,775,326 BM25 scores | 19,200 MaxSim pairs | — | — | — |
| title · dense | 9,122,112 dot products | — | 70 MB | — | — |
| title · dense · cross | 9,122,112 dot products | 19,200 cross-encoder pairs | 70 MB | — | — |
| title · dense · late | 9,122,112 dot products | 19,200 MaxSim pairs | 70 MB | — | — |
| rewrite · BM25 | 40,510,444 BM25 scores (2,065 strings) | — | — | — | — |
| rewrite · BM25 · cross | 40,510,444 BM25 scores (2,065 strings) | 19,200 cross-encoder pairs | — | — | — |
| rewrite · BM25 · late | 40,510,444 BM25 scores (2,065 strings) | 19,200 MaxSim pairs | — | — | — |
| rewrite · dense | 98,110,215 dot products (2,065 strings) | — | 70 MB | — | — |
| rewrite · dense · cross | 98,110,215 dot products (2,065 strings) | 19,200 cross-encoder pairs | 70 MB | — | — |
| rewrite · dense · late | 98,110,215 dot products (2,065 strings) | 19,200 MaxSim pairs | 70 MB | — | — |
| late only | 3,775,326 MaxSim, 38,595 passages encoded | — | — | — | — |
| title · BM25 · late · k200 | 3,775,326 BM25 scores | 38,400 MaxSim pairs | — | — | — |
| title · dense · late · k200 | 9,122,112 dot products | 38,400 MaxSim pairs | 70 MB | — | — |
| disproof · BM25 | 7,486,909 BM25 scores (381 strings) | — | — | — | 8.1 s |
| disproof · dense | 18,101,691 dot products (381 strings) | — | 70 MB | 0.20 GB | 25.4 s |

Dense multiplies each search string by every stored chunk, then drops the other set.
BM25 and a late first stage score only the passages in the claim's set. The reranker
scores the original title against each kept passage. The dense index is one shared file.
BM25 builds its index in memory and does not save it. A late first stage encodes
passages for that run and does not save the vectors. Watts are not sampled.

## Per claim

Same four figures as a detector-cost table. Retrieval (ms) is the retrieval-stage
wall time divided by the number of claims, so one index build or model load is
spread across the split. Prompt tokens are the mean length of the verdict prompt.
LLM (ms) is the verdict forward pass per claim, excluding the weight load.
GPU peak in this table is PyTorch allocated memory while that model runs.
Prompt tokens, LLM time, and that GPU peak stay empty until the verdict model runs.

| Run | Retrieval (ms) | Prompt tokens | LLM (ms) | GPU peak (GB) |
| --- | ---: | ---: | ---: | ---: |
| title · BM25 | — | — | — | — |
| title · BM25 · cross | — | — | — | — |
| title · BM25 · late | — | — | — | — |
| title · dense | — | — | — | — |
| title · dense · cross | — | — | — | — |
| title · dense · late | — | — | — | — |
| rewrite · BM25 | — | — | — | — |
| rewrite · BM25 · cross | — | — | — | — |
| rewrite · BM25 · late | — | — | — | — |
| rewrite · dense | — | — | — | — |
| rewrite · dense · cross | — | — | — | — |
| rewrite · dense · late | — | — | — | — |
| late only | — | — | — | — |
| title · BM25 · late · k200 | — | — | — | — |
| title · dense · late · k200 | — | — | — | — |
| disproof · BM25 | 42.2 | — | — | — |
| disproof · dense | 132.6 | — | — | — |
