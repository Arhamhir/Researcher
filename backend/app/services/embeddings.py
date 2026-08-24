"""Local text embeddings for the novelty similarity check.

Groq's API is chat/audio completions only - it does not expose an
embeddings endpoint - so this does not call any external API. Instead it
computes a deterministic "hashing trick" bag-of-words vector locally: each
token is hashed to a fixed index with a stable sign, weighted by
log-scaled term frequency, and the result is L2-normalized.

This is lexical similarity, not semantic similarity. It reliably catches
near-duplicate or heavily overlapping submissions (the main practical use
of the novelty check) without any API key, rate limit, or network
dependency. It will not recognize paraphrased novelty the way a semantic
embedding model would - that tradeoff is intentional: Groq has nothing to
offer here, and faking semantic similarity through an LLM call per
paper-pair would be slow, expensive, and unreliable at scale.
"""
import hashlib
import math
import re

from app.core.config import EMBEDDING_DIM

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall((text or "").lower())


def _hash_token(token: str) -> int:
    # A stable hash (unlike Python's built-in hash(), which is randomized
    # per-process) so vectors stay comparable across requests and restarts.
    digest = hashlib.md5(token.encode("utf-8")).hexdigest()
    return int(digest, 16)


def get_embedding(text: str, model: str = None) -> list[float]:
    """
    Compute a deterministic local embedding vector for `text`.

    Args:
        text: Text to embed.
        model: Unused; kept for call-site compatibility.

    Returns:
        A list of EMBEDDING_DIM floats, L2-normalized (all zeros for empty text).
    """
    vector = [0.0] * EMBEDDING_DIM
    tokens = _tokenize(text)
    if not tokens:
        return vector

    counts: dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1

    for token, count in counts.items():
        digest = _hash_token(token)
        index = digest % EMBEDDING_DIM
        sign = 1.0 if (digest // EMBEDDING_DIM) % 2 == 0 else -1.0
        vector[index] += sign * (1.0 + math.log(count))

    norm = math.sqrt(sum(v * v for v in vector))
    if norm > 0:
        vector = [v / norm for v in vector]

    return vector
