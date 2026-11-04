# Retrieval, test

Main set, 300 disinformation claims. Strict gold is the claim's own disproof. Lenient gold is that disproof or a near-duplicate. Rank is Hit@5, then Hit@10, then Hit@1. The bin tables keep that order.

The seven runs use the title. BM25 and dense are paired with no reranker, the cross-encoder, or late interaction. Pure late is not reranked.

Source: results/comparison/test/retrieval.csv. Intervals are in that file and in results/comparison/test/retrieval.md.

## Strict

### Rank by Hit@5

| Rank | Run | Hit@1 | Hit@5 | Hit@10 | Hit@100 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | late only | 0.253 | 0.420 | 0.530 | 0.793 |
| 2 | title · BM25 · late | 0.250 | 0.413 | 0.517 | 0.720 |
| 3 | title · dense · late | 0.230 | 0.377 | 0.463 | 0.720 |
| 4 | title · BM25 | 0.207 | 0.340 | 0.410 | 0.720 |
| 5 | title · dense | 0.213 | 0.337 | 0.437 | 0.720 |
| 6 | title · BM25 · cross | 0.177 | 0.327 | 0.427 | 0.720 |
| 7 | title · dense · cross | 0.137 | 0.270 | 0.367 | 0.720 |

### Title-disproof overlap

100 claims in each bin. Low overlap is 0.00-0.44 of title stems in the disproof, mid 0.46-0.67, high 0.70-1.00.

| Rank | Run | low @1 | low @5 | low @10 | mid @1 | mid @5 | mid @10 | high @1 | high @5 | high @10 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | late only | 0.090 | 0.200 | 0.300 | 0.170 | 0.360 | 0.500 | 0.500 | 0.700 | 0.790 |
| 2 | title · BM25 · late | 0.090 | 0.180 | 0.240 | 0.160 | 0.350 | 0.520 | 0.500 | 0.710 | 0.790 |
| 3 | title · dense · late | 0.080 | 0.170 | 0.230 | 0.150 | 0.310 | 0.450 | 0.460 | 0.650 | 0.710 |
| 4 | title · BM25 | 0.050 | 0.100 | 0.130 | 0.110 | 0.280 | 0.360 | 0.460 | 0.640 | 0.740 |
| 5 | title · dense | 0.090 | 0.170 | 0.220 | 0.140 | 0.310 | 0.410 | 0.410 | 0.530 | 0.680 |
| 6 | title · BM25 · cross | 0.060 | 0.120 | 0.160 | 0.100 | 0.230 | 0.380 | 0.370 | 0.630 | 0.740 |
| 7 | title · dense · cross | 0.030 | 0.080 | 0.150 | 0.130 | 0.250 | 0.350 | 0.250 | 0.480 | 0.600 |

### Disproof length

Short is 30-129 words (n = 101), medium 130-223 (n = 103), long 224-562 (n = 96).

| Rank | Run | short @1 | short @5 | short @10 | medium @1 | medium @5 | medium @10 | long @1 | long @5 | long @10 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | late only | 0.337 | 0.485 | 0.584 | 0.252 | 0.447 | 0.524 | 0.167 | 0.323 | 0.479 |
| 2 | title · BM25 · late | 0.337 | 0.495 | 0.594 | 0.243 | 0.427 | 0.505 | 0.167 | 0.312 | 0.448 |
| 3 | title · dense · late | 0.337 | 0.475 | 0.554 | 0.194 | 0.349 | 0.437 | 0.156 | 0.302 | 0.396 |
| 4 | title · BM25 | 0.297 | 0.426 | 0.495 | 0.194 | 0.330 | 0.408 | 0.125 | 0.260 | 0.323 |
| 5 | title · dense | 0.317 | 0.446 | 0.505 | 0.194 | 0.320 | 0.427 | 0.125 | 0.240 | 0.375 |
| 6 | title · BM25 · cross | 0.238 | 0.366 | 0.465 | 0.194 | 0.291 | 0.388 | 0.094 | 0.323 | 0.427 |
| 7 | title · dense · cross | 0.188 | 0.317 | 0.406 | 0.136 | 0.243 | 0.379 | 0.083 | 0.250 | 0.312 |

### Entity and formulation

Entity-driven means the title's specific names occur in the gold evidence (n = 125). Formulation-driven means they do not (n = 175).

| Rank | Run | entity @1 | entity @5 | entity @10 | formulation @1 | formulation @5 | formulation @10 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | late only | 0.320 | 0.544 | 0.680 | 0.206 | 0.331 | 0.423 |
| 2 | title · BM25 · late | 0.312 | 0.560 | 0.672 | 0.206 | 0.309 | 0.406 |
| 3 | title · dense · late | 0.272 | 0.480 | 0.624 | 0.200 | 0.303 | 0.349 |
| 4 | title · BM25 | 0.280 | 0.480 | 0.560 | 0.154 | 0.240 | 0.303 |
| 5 | title · dense | 0.248 | 0.392 | 0.504 | 0.189 | 0.297 | 0.389 |
| 6 | title · BM25 · cross | 0.208 | 0.408 | 0.520 | 0.154 | 0.269 | 0.360 |
| 7 | title · dense · cross | 0.168 | 0.336 | 0.464 | 0.114 | 0.223 | 0.297 |

## Lenient

### Rank by Hit@5

| Rank | Run | Hit@1 | Hit@5 | Hit@10 | Hit@100 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | late only | 0.260 | 0.420 | 0.533 | 0.797 |
| 2 | title · BM25 · late | 0.257 | 0.413 | 0.520 | 0.723 |
| 3 | title · dense · late | 0.237 | 0.377 | 0.470 | 0.727 |
| 4 | title · dense | 0.213 | 0.340 | 0.440 | 0.727 |
| 5 | title · BM25 | 0.213 | 0.340 | 0.410 | 0.723 |
| 6 | title · BM25 · cross | 0.183 | 0.330 | 0.430 | 0.723 |
| 7 | title · dense · cross | 0.140 | 0.273 | 0.370 | 0.727 |

### Title-disproof overlap

| Rank | Run | low @1 | low @5 | low @10 | mid @1 | mid @5 | mid @10 | high @1 | high @5 | high @10 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | late only | 0.100 | 0.200 | 0.300 | 0.180 | 0.360 | 0.510 | 0.500 | 0.700 | 0.790 |
| 2 | title · BM25 · late | 0.100 | 0.180 | 0.240 | 0.170 | 0.350 | 0.530 | 0.500 | 0.710 | 0.790 |
| 3 | title · dense · late | 0.090 | 0.170 | 0.230 | 0.160 | 0.310 | 0.460 | 0.460 | 0.650 | 0.720 |
| 4 | title · dense | 0.090 | 0.170 | 0.230 | 0.140 | 0.320 | 0.410 | 0.410 | 0.530 | 0.680 |
| 5 | title · BM25 | 0.050 | 0.100 | 0.130 | 0.130 | 0.280 | 0.360 | 0.460 | 0.640 | 0.740 |
| 6 | title · BM25 · cross | 0.070 | 0.120 | 0.160 | 0.110 | 0.240 | 0.380 | 0.370 | 0.630 | 0.750 |
| 7 | title · dense · cross | 0.030 | 0.080 | 0.160 | 0.140 | 0.260 | 0.350 | 0.250 | 0.480 | 0.600 |

### Disproof length

| Rank | Run | short @1 | short @5 | short @10 | medium @1 | medium @5 | medium @10 | long @1 | long @5 | long @10 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | late only | 0.337 | 0.485 | 0.584 | 0.252 | 0.447 | 0.524 | 0.188 | 0.323 | 0.490 |
| 2 | title · BM25 · late | 0.337 | 0.495 | 0.594 | 0.243 | 0.427 | 0.505 | 0.188 | 0.312 | 0.458 |
| 3 | title · dense · late | 0.337 | 0.475 | 0.554 | 0.194 | 0.349 | 0.456 | 0.177 | 0.302 | 0.396 |
| 4 | title · dense | 0.317 | 0.446 | 0.505 | 0.194 | 0.330 | 0.427 | 0.125 | 0.240 | 0.385 |
| 5 | title · BM25 | 0.307 | 0.426 | 0.495 | 0.194 | 0.330 | 0.408 | 0.135 | 0.260 | 0.323 |
| 6 | title · BM25 · cross | 0.238 | 0.376 | 0.475 | 0.194 | 0.291 | 0.388 | 0.115 | 0.323 | 0.427 |
| 7 | title · dense · cross | 0.188 | 0.317 | 0.406 | 0.136 | 0.252 | 0.379 | 0.094 | 0.250 | 0.323 |

### Entity and formulation

| Rank | Run | entity @1 | entity @5 | entity @10 | formulation @1 | formulation @5 | formulation @10 |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | late only | 0.336 | 0.544 | 0.688 | 0.206 | 0.331 | 0.423 |
| 2 | title · BM25 · late | 0.328 | 0.560 | 0.680 | 0.206 | 0.309 | 0.406 |
| 3 | title · dense · late | 0.288 | 0.480 | 0.640 | 0.200 | 0.303 | 0.349 |
| 4 | title · dense | 0.248 | 0.392 | 0.512 | 0.189 | 0.303 | 0.389 |
| 5 | title · BM25 | 0.296 | 0.480 | 0.560 | 0.154 | 0.240 | 0.303 |
| 6 | title · BM25 · cross | 0.224 | 0.408 | 0.528 | 0.154 | 0.274 | 0.360 |
| 7 | title · dense · cross | 0.176 | 0.344 | 0.464 | 0.114 | 0.223 | 0.303 |

## Article proxy

53 article queries have a trustworthy article marked as a proxy for the debunk. A hit is that article anywhere in the top k.

| Rank | Run | Hit@1 | Hit@5 | Hit@10 | Hit@100 |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | title · BM25 · late | 0.283 | 0.434 | 0.509 | 0.717 |
| 2 | late only | 0.283 | 0.415 | 0.453 | 0.736 |
| 3 | title · BM25 · cross | 0.207 | 0.396 | 0.491 | 0.717 |
| 4 | title · dense · late | 0.264 | 0.396 | 0.453 | 0.698 |
| 5 | title · dense · cross | 0.207 | 0.377 | 0.434 | 0.698 |
| 6 | title · dense | 0.207 | 0.377 | 0.434 | 0.698 |
| 7 | title · BM25 | 0.245 | 0.358 | 0.415 | 0.717 |
