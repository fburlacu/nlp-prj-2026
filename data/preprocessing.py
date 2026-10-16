"""Shared text preprocessing. Import this in BOTH the query builder and the BM25
retriever, so that overlap statistics measure exactly what BM25 sees."""
import re
from functools import lru_cache

import nltk
from nltk.stem.snowball import SnowballStemmer

try:
    from nltk.corpus import stopwords
    STOP = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords", quiet=True)
    from nltk.corpus import stopwords
    STOP = set(stopwords.words("english"))

_stem = SnowballStemmer("english").stem
TOKEN_RE = re.compile(r"[a-z0-9]+")


def repair_boundaries(text: str) -> str:
    """Insert the space lost where hyperlinks were stripped, e.g. 'Crimea.No' -> 'Crimea. No'.
    Words glued inside a sentence ('issuedstatements') cannot be recovered and are left as is."""
    if not isinstance(text, str):
        return ""
    text = re.sub(r"([a-z0-9)\"'”’][.!?;:])([A-Z\"“])", r"\1 \2", text)
    return re.sub(r"\s+", " ", text).strip()


@lru_cache(maxsize=200_000)
def _stem_cached(w: str) -> str:
    return _stem(w)


def tokenize(text: str) -> list[str]:
    """BM25 tokenizer: lowercase, alphanumeric tokens, English stopwords removed, Snowball stems."""
    if not isinstance(text, str):
        return []
    return [_stem_cached(t) for t in TOKEN_RE.findall(text.lower()) if t not in STOP and len(t) > 1]


def words(text: str) -> list[str]:
    """Plain lowercase word sequence (no stemming); used for near-duplicate shingles."""
    return TOKEN_RE.findall(text.lower()) if isinstance(text, str) else []


def shingles(text: str, n: int = 5) -> set[str]:
    w = words(text)
    if len(w) < n:
        return {" ".join(w)} if w else set()
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


# ---------------- headline helpers (shared by query builder and LLM filter) ----------------
_TITLE_SPLIT = re.compile(r"\s+[|\-–—:]\s+")
_NON_CLAIM = re.compile(r"^(live|watch|video|photos?|in pictures|podcast|opinion|op-ed|analysis|explainer|"
                        r"factbox|timeline|q&a|quiz|how|what|why|who|when|where|which|transcript|"
                        r"full text|statement by|press release)\b", re.I)


def clean_title(t) -> str:
    """Strip site suffixes/prefixes like 'Headline - BBC News' or 'Reuters | Headline'."""
    if not isinstance(t, str):
        return ""
    t = re.sub(r"\s+", " ", t).strip()
    parts = _TITLE_SPLIT.split(t)
    if len(parts) > 1:
        main = max(parts, key=lambda p: len(p.split()))
        if all(len(p.split()) <= 4 for p in parts if p is not main):
            t = main
    return t.strip(" \"'“”")


def rule_claim_like(t: str) -> bool:
    """Cheap pre-filter: at least 5 words, not a question, not a format label."""
    return len(t.split()) >= 5 and not t.endswith("?") and not _NON_CLAIM.search(t)