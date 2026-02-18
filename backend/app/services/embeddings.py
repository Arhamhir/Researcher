from openai import AzureOpenAI, NotFoundError
from app.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_EMBEDDING_API_VERSION,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
)

MAX_EMBED_CHARS_PER_CHUNK = 12000


def _get_client(api_version: str) -> AzureOpenAI:
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=api_version,
    )


def _candidate_api_versions() -> list[str]:
    versions = [
        AZURE_OPENAI_EMBEDDING_API_VERSION,
        "2024-10-21",
        "2024-02-01",
    ]
    deduped = []
    for version in versions:
        if version and version not in deduped:
            deduped.append(version)
    return deduped


def _split_text_for_embedding(text: str, max_chars: int = MAX_EMBED_CHARS_PER_CHUNK) -> list[str]:
    if not text:
        return [""]

    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = []
    current_len = 0

    for word in text.split():
        word_len = len(word) + 1
        if current and current_len + word_len > max_chars:
            chunks.append(" ".join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len += word_len

    if current:
        chunks.append(" ".join(current))

    return chunks or [text[:max_chars]]


def _embed_single_text(text: str, deployment: str) -> list[float]:
    last_error = None

    for api_version in _candidate_api_versions():
        try:
            client = _get_client(api_version)
            response = client.embeddings.create(
                model=deployment,
                input=text,
            )
            return response.data[0].embedding
        except NotFoundError as e:
            last_error = e
            continue
        except Exception as e:
            last_error = e
            break

    tried = ", ".join(_candidate_api_versions())
    raise RuntimeError(
        f"Azure embeddings failed for deployment '{deployment}' at endpoint '{AZURE_OPENAI_ENDPOINT}'. "
        f"Tried API versions: {tried}. "
        f"Original error: {last_error}"
    )


def get_embedding(text: str, model: str = None) -> list[float]:
    """
    Generate embeddings using Azure OpenAI.

    Args:
        text: Text to embed
        model: Optional deployment override. Defaults to AZURE_OPENAI_EMBEDDING_DEPLOYMENT.

    Returns:
        List of floats representing the embedding vector.
    """
    deployment = model or AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    chunks = _split_text_for_embedding(text)

    if len(chunks) == 1:
        return _embed_single_text(chunks[0], deployment)

    weighted_vectors = []
    weights = []

    for chunk in chunks:
        vector = _embed_single_text(chunk, deployment)
        weighted_vectors.append(vector)
        weights.append(max(len(chunk), 1))

    total_weight = float(sum(weights))
    vector_dim = len(weighted_vectors[0])
    merged = [0.0] * vector_dim

    for vector, weight in zip(weighted_vectors, weights):
        for index in range(vector_dim):
            merged[index] += float(vector[index]) * (weight / total_weight)

    return merged
