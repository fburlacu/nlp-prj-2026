# Cost, test

## Cost

Space is the stored dense index. Computation is the number of query–passage scores.
Wall time is the clock from the start of retrieval until reranking finishes, for the
whole split, including the model load or the BM25 index build. It is not CPU time
and it is not the time for one claim. GPU peak here is PyTorch reserved memory of
the retriever. A dash means that run was written before this was recorded.

| Run | First stage | Rerank | Stored index | GPU peak | Wall time |
| --- | --- | --- | ---: | ---: | ---: |
| title · BM25 | 20,742,792 BM25 scores | — | — | — | 9.3 s |
| title · BM25 · cross | 20,742,792 BM25 scores | 110,400 cross-encoder pairs | — | 1.49 GB | 12.9 min |
| title · BM25 · late | 20,742,792 BM25 scores | 110,400 MaxSim pairs | — | 0.29 GB | 5.2 min |
| title · dense | 52,452,144 dot products | — | 70 MB | 0.16 GB | 23.1 s |
| title · dense · cross | 52,452,144 dot products | 110,400 cross-encoder pairs | 70 MB | 1.72 GB | 9.4 min |
| title · dense · late | 52,452,144 dot products | 110,400 MaxSim pairs | 70 MB | 0.43 GB | 4.3 min |
| late only | 20,742,792 MaxSim, 38,595 passages encoded | — | — | 0.40 GB | 13.8 min |

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
| title · BM25 | 8.4 | 1,372 | 376.5 | 16.2 |
| title · BM25 · cross | 8.1 | 1,488 | 410.0 | 16.0 |
| title · BM25 · late | 8.4 | 1,417 | 390.6 | 16.1 |
| title · dense | 20.9 | 1,022 | 283.9 | 16.1 |
| title · dense · cross | 24.3 | 1,052 | 290.2 | 15.9 |
| title · dense · late | 17.9 | 1,066 | 296.0 | 15.8 |
| late only | 750.1 | 1,418 | 390.5 | 16.1 |
