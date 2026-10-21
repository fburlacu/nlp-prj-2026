# Data design change: main set (EEAS)

## Before

1. **Leave-one-out exclusion.** The index held claim (summary) and disproof passages for every case. For each query (an EEAS case title), its own case was excluded from the index to avoid self-retrieval.
2. **Inconclusive as a by-product.** Cases with no near-duplicates had nothing left to retrieve once their own case was excluded, so their correct verdict was *inconclusive*. Cases with near-duplicates could still find another case's debunk, so their correct verdict was *disinformation*.

## Why it changed

A BM25 sanity check on the 345 disinformation queries showed:

| Index | R@1 | R@10 | MRR |
|---|---|---|---|
| Claim + disproof, own claim excluded (old setup) | 0.125 | 0.325 | 0.194 |
| Disproof only | 0.197 | 0.400 | 0.272 |

In the old setup the own disproof was still indexed, but other cases' **claim passages** outranked it, because claims look like titles. The low scores came from the claim passages, not from retrieval quality. Without the exclusion, the query just matches its own claim, which is self-retrieval and not a valid result.

## Now

1. **Disproof-only index.** Only EEAS disproof passages are indexed: no claims, summaries, titles or Leite articles. Each passage keeps its `case_id`.
2. **No per-query exclusion.** Every disinformation query's own disproof is in the index and is the strict gold.
3. **Inconclusive as a fixed held-out set.** A sample of singleton cases has its disproofs removed from the index once. Their titles are the *inconclusive* queries, meaning the claim is false but the system has no debunk for it. This simulates unseen claims; they are not genuinely unverifiable.
   - A **singleton** is a case with no near-duplicate claim or disproof, no shared disproof text, and a title not quoted in any other case's disproof.
   - The held-out set is the same size as the disinformation set (345), with a fixed seed.
4. **Singletons on both sides.** Other singletons keep their disproofs indexed and appear among the disinformation queries, so *inconclusive* does not simply mean "is a singleton."
5. **Dev/test split** stratified by label.
6. **BM25 first.** Passages are one per disproof, without chunking. Dense and hybrid will chunk later and pool chunks back to `case_id`, so queries, labels and gold stay the same.

## Unchanged

- The Leite set (fact vs disinformation) and its pipeline.
- Strict vs lenient (near-duplicate) retrieval scoring.

## RQ2 setup

- Main set: disinformation vs inconclusive.
- Leite set: fact vs disinformation.
- Baseline: an LLM given the claim with no retrieved evidence.

## Known limitations

- Many disproofs quote other cases' titles word for word ("similar cases claiming that…"), so they can rank highly for the wrong case. This is left in the index and the number of affected disproofs is reported. It is only filtered when selecting held-out singletons.
- Some disproofs restate the claim they debunk, so some lexical overlap with the query remains. This is realistic for fact-checks.