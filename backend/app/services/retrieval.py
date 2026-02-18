import numpy as np
import json
from app.services.vector_store import supabase

def cosine_similarity(a, b):
    if not a or not b:
        return 0.0

    shared = min(len(a), len(b))
    if shared == 0:
        return 0.0

    a = np.array(a[:shared], dtype=float)
    b = np.array(b[:shared], dtype=float)

    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0

    return float(np.dot(a, b) / denom)

def _parse_embedding(embedding):
    """Parse embedding from database (could be list, string, or JSON)."""
    if isinstance(embedding, str):
        try:
            return json.loads(embedding)
        except:
            return []
    elif isinstance(embedding, list):
        return embedding
    return []

def search_sections(query_embedding: list[float], top_k: int = 5):
    """Fetch all embeddings and compute similarity manually."""
    res = supabase.table("paper_sections").select("id, content, embedding").execute()
    sections = res.data

    # Compute similarity
    scored = []
    for sec in sections:
        embedding = _parse_embedding(sec.get('embedding', []))
        if not embedding:
            continue
        score = cosine_similarity(query_embedding, embedding)
        scored.append((score, sec))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [sec for score, sec in scored[:top_k]]

def search_similar_sections(query_embedding: list[float], top_k: int = 5, exclude_paper_id: str = None):
    """Search for similar paper sections, returns with similarity scores.
    
    Args:
        query_embedding: The embedding vector to compare against
        top_k: Number of top results to return
        exclude_paper_id: Optional paper_id to exclude from results (e.g., current paper)
    """
    query = supabase.table("paper_sections").select("id, paper_id, content, embedding")
    normalized_exclude = str(exclude_paper_id).strip().lower() if exclude_paper_id else None
    if normalized_exclude:
        query = query.neq("paper_id", normalized_exclude)

    res = query.execute()
    sections = res.data

    scored = []
    for sec in sections:
        # Skip sections from the excluded paper
        sec_paper_id = str(sec.get("paper_id", "")).strip().lower()
        if normalized_exclude and sec_paper_id == normalized_exclude:
            continue
            
        embedding = _parse_embedding(sec.get('embedding', []))
        if not embedding:
            continue
        similarity = cosine_similarity(query_embedding, embedding)
        scored.append({
            "section_id": sec["id"],
            "paper_id": sec["paper_id"],
            "similarity": similarity,
            "content": sec.get("content", "")
        })

    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]
