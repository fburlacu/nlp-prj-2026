"""Reciprocal rank fusion of several ranked lists for the same claim."""


def fuse(lists, k, rrf_k=60):
    """lists is (query_id, [passage_id, ...]) in rank order. One query may occur many times.

    A passage's score is the sum of 1 / (rrf_k + rank) over every list that returned it.
    With a single list the order does not change.
    """
    scores = {}
    for query_id, ranking in lists:
        table = scores.setdefault(query_id, {})
        for rank, passage_id in enumerate(ranking, 1):
            table[passage_id] = table.get(passage_id, 0.0) + 1.0 / (rrf_k + rank)
    rows = []
    for query_id, table in scores.items():
        ordered = sorted(table.items(), key=lambda item: (-item[1], item[0]))[:k]
        for rank, (passage_id, score) in enumerate(ordered, 1):
            rows.append((query_id, rank, passage_id, float(score)))
    return rows
